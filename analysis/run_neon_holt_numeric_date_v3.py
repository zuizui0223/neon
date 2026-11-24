"""Validate numeric capture calendar encoding using original named-month anchors."""
from collections import Counter
from datetime import date,timedelta,datetime,timezone
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import json,re
from analysis.run_neon_holt_acorn_preceding_upcoming_v1 import (
    read_csv,resource_map,make_rank_maps,groups_for_window,evaluate,
    RESOURCE_YEARS,CAPTURE_YEARS,DRI_SHA,verified_file,require,integer)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_holt_numeric_date_v3_20261124.json"
MONTHS={m:i for i,m in enumerate(("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"),1)}

def anchor(v,y):
    m=re.fullmatch(r"(\d{2})([A-Za-z]{3})_(\d{4})(\d)",str(v or "").strip())
    if not m or int(m[3])!=y or m[2].title() not in MONTHS:return None
    try:return date(y,MONTHS[m[2].title()],int(m[1]))
    except ValueError:return None

def numeric(v):
    v=str(v or "").strip()
    return int(v) if re.fullmatch(r"[0-9]{1,4}",v) else None

def decode(n,y,mode):
    if n is None:return None
    try:
        if mode=="MMDD":return date(y,n//100,n%100)
        if mode=="DOY" and n>=1:
            d=date(y,1,1)+timedelta(days=n-1)
            return d if d.year==y else None
    except (ValueError,OverflowError):pass
    return None

def calibrate(hist,years=CAPTURE_YEARS,min_rows=100):
    stats=Counter();mismatch=Counter();byyear=Counter();mapping={};conflicts=0;months=Counter()
    for row in hist:
        y=integer(row["year"])
        if y not in years:continue
        stats["history_rows"]+=1
        n=numeric(row["date"]);d=anchor(row.get("date2"),y)
        if n is None:
            stats["nonnumeric_history_date"]+=1;continue
        stats["numeric_history_rows"]+=1
        if d is None:
            stats["missing_or_invalid_named_anchor"]+=1;continue
        stats["anchor_rows"]+=1;byyear[y]+=1;months[d.month]+=1
        for mode in ("MMDD","DOY"):
            mismatch[mode]+=decode(n,y,mode)!=d
        k=(y,n)
        if k in mapping and mapping[k]!=d:conflicts+=1
        mapping[k]=d
    good=[m for m in ("MMDD","DOY") if mismatch[m]==0]
    ready=(stats["anchor_rows"]>=min_rows and set(byyear)==set(years)
           and stats["anchor_rows"]==stats["numeric_history_rows"]
           and conflicts==0 and len(good)==1)
    return (good[0] if ready else None),mapping,{
        "history_counts":dict(stats),"anchor_year_counts":dict(sorted(byyear.items())),
        "anchor_month_counts":dict(sorted(months.items())),
        "candidate_mismatches":dict(mismatch),"contradictory_year_code_keys":conflicts,
        "distinct_year_code_keys":len(mapping),"unique_all_anchor_decoder":good[0] if ready else None}

def repair(cap,mapping,mode,years=CAPTURE_YEARS):
    out=[];counts=Counter();months=Counter()
    for row in cap:
        y=integer(row["year"])
        if y not in years or row["used"].strip()!="1":
            out.append(row);continue
        counts["used_rows"]+=1;n=numeric(row["date"]);d=decode(n,y,mode)
        if d is None or mapping.get((y,n))!=d:
            counts["unverified_used_dates"]+=1;out.append(row);continue
        counts["verified_used_dates"]+=1;months[d.month]+=1
        counts["outside_frozen_summer"]+=int(d.month not in (6,7,8))
        out.append({**row,"date":d.isoformat()})
    return out,{"counts":dict(counts),"verified_month_counts":dict(sorted(months.items()))}

def run():
    raw=verified_file(15029247,1,36110309,2277102,"5f5263ba55a2d72c886d170ec5d38c43",DRI_SHA)
    with ZipFile(BytesIO(raw)) as z:
        small=read_csv(z,"seeds_sm.csv",4464);broad=read_csv(z,"seed_traps.csv",5184)
        cap=read_csv(z,"peroUS_AV_AG.csv",6351);hist=read_csv(z,"PerohistAG_group.csv",4433)
    sm=resource_map(small);br=resource_map(broad)
    require(len(sm)==144*len(RESOURCE_YEARS),"DIRECT_RESOURCE_WINDOW_INCOMPLETE")
    require(set(sm)==set(br) and all(sm[k]==br[k] for k in sm),"DIRECT_SOURCE_REDCROP_TABLE_MISMATCH")
    ranks=make_rank_maps(sm)
    mode,mapping,diag=calibrate(hist)
    out={"schema":"neon.holt.date_code_anchor.v3","history_date_diagnosis":diag,
         "source_SHA256":DRI_SHA,"direct_station_years":len(sm),"effect":None,
         "same_frozen_v1_contrast":True,"submission_hold":True}
    if mode is None:
        out["status"]="STOP_UNVERIFIED_NUMERIC_DATE_ONTOLOGY";return out
    repaired,d=repair(cap,mapping,mode);out["used_date_diagnosis"]=d
    require(d["counts"]["used_rows"]==1168,"USED_DENOMINATOR_DRIFT")
    if d["counts"].get("unverified_used_dates") or d["counts"].get("outside_frozen_summer"):
        out["status"]="STOP_UNVERIFIED_OR_NON_SUMMER_USED_DATE";return out
    groups,counts,stop=groups_for_window(repaired,hist,set(ranks[1988]))
    out["source_ontology_counts"]=counts
    if stop:out.update(status=stop,effect=None)
    else:out.update(evaluate(ranks,groups))
    return out

def main():
    try:out=run()
    except Exception as exc:out={"schema":"neon.holt.date_code_anchor.v3","status":"STOP_SOURCE","error_class":type(exc).__name__,"effect":None,"submission_hold":True}
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
