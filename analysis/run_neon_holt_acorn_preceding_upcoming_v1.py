"""One frozen preceding/upcoming resource spatial contrast, not seed fate."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from io import BytesIO, StringIO
from math import ceil, isfinite
from pathlib import Path
from statistics import mean
from zipfile import ZipFile
import csv,json,re
from analysis.audit_neon_seasonal_seed_role_source_v1 import verified_file, DRI_SHA
from analysis.audit_neon_direct_resource_groundcover_source_v1 import require

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_holt_acorn_preceding_upcoming_20261124.json"
REF_YEARS=tuple(range(1988,1998))
CAPTURE_YEARS=tuple(range(1999,2014))
RESOURCE_YEARS=tuple(range(1988,2014))
MIN_YEARS=10
MIN_GROUPS_YEAR=3
MIN_GROUPS_TOTAL=60

def read_csv(z,name,expected_n):
    raw=z.read("Data_and_code/Data/"+name)
    rdr=csv.DictReader(StringIO(raw.decode("utf-8-sig"),newline=""))
    fields=rdr.fieldnames
    require(fields is not None and len(set(fields))==len(fields),"SOURCE_HEADER_INVALID")
    rows=list(rdr)
    require(len(rows)==expected_n and all(None not in row and all(v is not None for v in row.values()) for row in rows),"SOURCE_ROW_COUNT_OR_WIDTH_CHANGED")
    return rows

def integer(s):
    require(bool(re.fullmatch(r"[0-9]+",s.strip())),"NONINTEGER_YEAR")
    return int(s)

def resource_map(rows):
    out={}
    for row in rows:
        y=integer(row["year"])
        if y not in RESOURCE_YEARS:continue
        t=row["STRAPSTAT"].strip()
        require(bool(t),"MISSING_SEED_STATION")
        x=Decimal(row["ROkcal"])
        require(x.is_finite() and x>=0,"INVALID_ACORN_ENERGY")
        require((y,t) not in out,"DUPLICATE_SEED_STATION_YEAR")
        out[y,t]=x
    return out

def make_rank_maps(raw):
    result={}
    for y in RESOURCE_YEARS:
        a={t:x for (yr,t),x in raw.items() if yr==y}
        require(len(a)==144,"NOT_144_DIRECT_STATIONS_EACH_YEAR")
        if result:require(set(a)==set(next(iter(result.values()))),"DIRECT_STATION_ROSTER_CHANGED")
        result[y]=midranks(a)
    return result

def midranks(a):
    s=sorted(a.items(),key=lambda p:p[1])
    n=len(s);out={};i=0
    while i<n:
        j=i+1
        while j<n and s[j][1]==s[i][1]:j+=1
        for k in range(i,j):out[s[k][0]]=(i+j)/(2*n)
        i=j
    return out

def summer_date(v,y):
    v=v.strip()
    # ISO or unambiguous author-format US calendar date; no yearless or 2-digit year.
    for fmt in ("%Y-%m-%d","%Y/%m/%d","%m/%d/%Y","%Y-%m-%d %H:%M:%S"):
        try:
            d=datetime.strptime(v,fmt)
        except ValueError:
            continue
        return d.year==y and d.month in (6,7,8)
    return False

def groups_for_window(rows,history,roster):
    counts=Counter();groups=defaultdict(lambda:{0:set(),1:set()})
    seen=defaultdict(set);invalid_groups=set()
    h=set((integer(x["year"]),x["id_new"].strip()) for x in history)
    for row in rows:
        y=integer(row["year"])
        if y not in CAPTURE_YEARS:continue
        counts["source_rows_in_capture_window"]+=1
        ident=row["id_new"].strip();t=row["STRAPSTAT"].strip();lab=row["used"].strip()
        require(ident and t and lab in {"0","1"},"SOURCE_ID_STATION_OR_USED_CODE_UNVERIFIED")
        key=(y,ident);used=int(lab)
        groups[key][used].add(t)
        counts["source_used_rows" if used else "source_available_rows"]+=1
        if used:
            if not summer_date(row["date"],y):
                counts["used_date_unverified"]+=1
            else:counts["used_date_summer_year_verified"]+=1
            seen[ident].add(y)
        if t not in roster:invalid_groups.add(key);counts["station_rows_without_direct_resource"]+=1
    counts["original_ID_year_groups"]=len(groups)
    counts["history_exact_ID_year_groups"]=sum(k in h for k in groups)
    counts["repeated_ID_across_target_years"]=sum(len(ys)>1 for ys in seen.values())
    if counts["used_date_unverified"]:
        return None,dict(counts),"STOP_ORIGINAL_SUMMER_DATE_ONTOLOGY"
    out=defaultdict(list)
    for key,g in sorted(groups.items()):
        y,ident=key
        if not g[0] or not g[1]:
            counts["groups_without_both_labels"]+=1;continue
        if key in invalid_groups:
            counts["groups_missing_original_resource_station"]+=1;continue
        if key not in h:
            counts["groups_without_exact_history_ID_year"]+=1;continue
        counts["groups_used_station_also_available"]+=bool(g[0]&g[1])
        out[y].append(g)
        counts["complete_ID_year_groups"]+=1
    counts["eligible_years_before_min_group_gate"]=len(out)
    counts["all_group_counts_by_year"]={str(y):len(out[y]) for y in sorted(out)}
    return out,dict(counts),None

def contrast(g,rank,baseline):
    def avg(labels):return mean(rank[t]-baseline[t] for t in labels)
    return avg(g[1])-avg(g[0])

def evaluate(rankmaps,byyear,ref_years=REF_YEARS,min_years=MIN_YEARS,min_groups_year=MIN_GROUPS_YEAR,min_total=MIN_GROUPS_TOTAL):
    eligible={y:g for y,g in sorted(byyear.items()) if len(g)>=min_groups_year}
    n=sum(map(len,eligible.values()))
    gate={"informative_capture_years":len(eligible),"informative_ID_year_groups":n,
          "min_years":min_years,"min_groups_each_year":min_groups_year,"min_total_groups":min_total}
    if len(eligible)<min_years or n<min_total:
        return {**gate,"status":"STOP_INSUFFICIENT_PAIRED_YEAR_SUPPORT","effect":None}
    base={t:mean(rankmaps[y][t] for y in ref_years) for t in rankmaps[ref_years[0]]}
    rows=[]
    for y,g in eligible.items():
        past=mean(contrast(x,rankmaps[y-1],base) for x in g)
        upcoming=mean(contrast(x,rankmaps[y],base) for x in g)
        rows.append({"capture_year":y,"ID_year_groups":len(g),"preceding":past,"upcoming":upcoming,"difference":past-upcoming})
    a=mean(x["preceding"] for x in rows);b=mean(x["upcoming"] for x in rows);d=mean(x["difference"] for x in rows)
    pos=sum(x["difference"]>0 for x in rows)
    loo=[mean(x["difference"] for k,x in enumerate(rows) if k!=j) for j in range(len(rows))]
    ok=a>0 and d>0 and pos>=ceil(2*len(rows)/3) and min(loo)>0
    return {**gate,"status":"DESCRIPTIVE_PAST_RESOURCE_ASYMMETRY_SUPPORTED" if ok else "DESCRIPTIVE_PAST_RESOURCE_ASYMMETRY_NOT_SUPPORTED",
            "effect":{"equal_year_preceding":a,"equal_year_upcoming":b,"equal_year_difference":d,
                      "positive_difference_years":pos,"leave_one_year_out_difference_min":min(loo),
                      "leave_one_year_out_difference_max":max(loo),"annual_aggregates":rows,
                      "not_significance_or_causal_estimate":True}}

def run():
    raw=verified_file(15029247,1,36110309,2277102,"5f5263ba55a2d72c886d170ec5d38c43",DRI_SHA)
    with ZipFile(BytesIO(raw)) as z:
        small=read_csv(z,"seeds_sm.csv",4464)
        broad=read_csv(z,"seed_traps.csv",5184)
        cap=read_csv(z,"peroUS_AV_AG.csv",6351)
        hist=read_csv(z,"PerohistAG_group.csv",4433)
    sm=resource_map(small);br=resource_map(broad)
    require(len(sm)==144*len(RESOURCE_YEARS),"DIRECT_RESOURCE_WINDOW_INCOMPLETE")
    require(set(sm)==set(br) and all(sm[k]==br[k] for k in sm),"DIRECT_SOURCE_REDCROP_TABLE_MISMATCH")
    ranks=make_rank_maps(sm)
    groups,counts,stop=groups_for_window(cap,hist,set(ranks[1988]))
    out={"source_SHA256":DRI_SHA,"direct_resource_window":[1988,2013],
         "direct_station_years":len(sm),"station_roster_size":144,"reference_resource_years":[1988,1997],
         "target_capture_years":[1999,2013],"source_ontology_counts":counts,
         "same_station_year_acorn_crosscheck_pass":True,"original_NEON_effects_unchanged":True,
         "not_seed_dispersal_or_remaining_food_or_detection_corrected":True,"submission_hold":True}
    if stop:out.update(status=stop,effect=None)
    else:out.update(evaluate(ranks,groups))
    return out

def main():
    try:out=run()
    except Exception as exc:out={"status":"STOP_ORIGINAL_HOLT_SOURCE_OR_SCHEMA","error_class":type(exc).__name__,
                               "reason":str(exc) if type(exc) is ValueError and re.fullmatch("[A-Z0-9_]+",str(exc)) else "UNEXPORTED_ERROR",
                               "effect":None,"submission_hold":True}
    out["schema"]="neon.holt.preceding_upcoming_acorn_spatial_use.v1"
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
