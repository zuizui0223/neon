"""Date-ontology-only repair of the original Holt fixed acorn contrast.

Preserve v1 source, years, taxa, resource variable, station and ID-year
eligibility, statistic and thresholds. Audit dates before opening effects.
A source STOP is not an ecological null.
"""
from collections import Counter,defaultdict
from datetime import date,datetime,timezone
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import json,re
from analysis.run_neon_holt_acorn_preceding_upcoming_v1 import (
    read_csv,resource_map,make_rank_maps,groups_for_window,evaluate,
    RESOURCE_YEARS,CAPTURE_YEARS,REF_YEARS,DRI_SHA,verified_file,require,integer,
)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_holt_acorn_date_repair_20261124.json"

def literal_shape(v):
    # Shape rather than actual original calendar/animal records.
    v=str(v or "").strip()
    return re.sub(r"[A-Za-z]+","A",re.sub(r"\d+",
        lambda m:"D"+str(len(m.group())),v))[:80] if False else re.sub(
        r"[A-Za-z]+|\d+",lambda m:("D" if m.group().isdigit() else "A")+str(len(m.group())),v)[:80]

def literal_candidates(value,y):
    """No season-based disambiguation, serial-date guesses or inferred day."""
    v=str(value or "").strip()
    if re.fullmatch(r"\d{4}-\d{1,2}-\d{1,2} 00:00:00",v):
        v=v.split()[0]
    found=set()
    for fmt in ("%Y-%m-%d","%Y/%m/%d","%Y%m%d","%m/%d/%Y","%d/%m/%Y",
                "%m-%d-%Y","%d-%m-%Y","%m/%d/%y","%d/%m/%y",
                "%m-%d-%y","%d-%m-%y","%d-%b-%Y","%d-%b-%y",
                "%d-%B-%Y","%d-%B-%y","%d %b %Y","%d %b %y",
                "%b %d %Y","%b %d %y","%b %d, %Y","%d.%m.%Y",
                "%m.%d.%Y","%d.%m.%y","%m.%d.%y"):
        try:
            d=datetime.strptime(v,fmt).date()
            if "%y" in fmt:
                if d.year%100 != y%100: continue
                d=date(y,d.month,d.day)
        except (ValueError,OverflowError):
            continue
        if d.year==y:
            found.add(d)
    return found

def row_key(row):
    return (integer(row["year"]),row["id_new"].strip(),row["STRAPSTAT"].strip())

def history_date_index(history):
    out=defaultdict(list)
    for row in history:
        y,ident,station=row_key(row)
        if y not in CAPTURE_YEARS:continue
        original=row["date"].strip()
        # Only exact date-string identity at the same year, individual and trap.
        out[(y,ident,station,original)].append(row.get("date2","").strip())
    return out

def date_diagnosis(cap,history):
    index=history_date_index(history)
    shapes=Counter();hist_shapes=Counter();resolved=Counter();months=Counter()
    counts=Counter();byyear=defaultdict(Counter);repaired=[]
    for row in cap:
        y=integer(row["year"])
        if y not in CAPTURE_YEARS or row["used"].strip()!="1":
            repaired.append(row);continue
        counts["original_used_rows"]+=1
        original=row["date"].strip()
        shapes[literal_shape(original)]+=1
        k=(*row_key(row),original)
        dates=index.get(k,[])
        counts["used_rows_with_exact_history_ID_station_year_date_literal"]+=bool(dates)
        for d in dates:hist_shapes[literal_shape(d)]+=1
        hist_c=set()
        ambiguous_hist=False
        for d in dates:
            c=literal_candidates(d,y)
            if len(c)>1:ambiguous_hist=True
            hist_c.update(c)
        direct=literal_candidates(original,y)
        candidate=None
        if len(direct)==1:
            candidate=next(iter(direct))
            # A unique explicit history date cannot contradict the original.
            if len(hist_c)==1 and candidate not in hist_c:
                candidate=None;label="CONFLICT_WITH_EXACT_HISTORY_DATE2"
            else:label="UNAMBIGUOUS_LITERAL"
        elif len(direct)>1 and len(hist_c)==1 and hist_c<=direct and not ambiguous_hist:
            candidate=next(iter(hist_c));label="AMBIGUOUS_LITERAL_RESOLVED_BY_EXACT_HISTORY_DATE2"
        elif not direct and len(hist_c)==1 and not ambiguous_hist:
            candidate=next(iter(hist_c));label="EXACT_HISTORY_DATE2_WITH_LITERAL_CROSSWALK"
        else:
            label="UNRESOLVED_OR_AMBIGUOUS"
        resolved[label]+=1
        byyear[y][label]+=1
        new=dict(row)
        if candidate is None:
            counts["unresolved_used_dates"]+=1
        else:
            counts["resolved_used_dates"]+=1
            months[str(candidate.month)]+=1
            if candidate.month not in (6,7,8):
                counts["resolved_outside_frozen_summer"]+=1
            new["date"]=candidate.isoformat()
        repaired.append(new)
    return repaired,{"original_used_date_literal_shapes":dict(shapes),
        "matched_history_date2_literal_shapes":dict(hist_shapes),
        "resolution_method_counts":dict(resolved),"resolved_month_counts":dict(months),
        "counts":dict(counts),"resolution_by_year":{str(y):dict(c) for y,c in sorted(byyear.items())}}

def author_date_ontology(z):
    # Author code is inspected, not executed; export date-format specifiers
    # and counts only. Do not infer a numeric date origin from a guess.
    report={}
    for name in sorted(z.namelist()):
        if not name.lower().endswith(".r"):continue
        s=z.read(name).decode("utf-8",errors="replace")
        date_lines=[x for x in s.splitlines() if re.search(
            r"as\.Date\s*\(|strptime\s*\(|\b[mdy]+_?[mdy]*\s*\(|\bdate2\b|\btrapsess\b",x)]
        fmt=sorted(set(re.findall(r"""['"]([^'"]*%[YymdBb][^'"]*)['"]""","\n".join(date_lines))))
        report[name]={"date_or_session_code_line_count":len(date_lines),
                      "explicit_date_format_strings":fmt[:30]}
    return report

def run():
    raw=verified_file(15029247,1,36110309,2277102,"5f5263ba55a2d72c886d170ec5d38c43",DRI_SHA)
    with ZipFile(BytesIO(raw)) as z:
        small=read_csv(z,"seeds_sm.csv",4464)
        broad=read_csv(z,"seed_traps.csv",5184)
        cap=read_csv(z,"peroUS_AV_AG.csv",6351)
        hist=read_csv(z,"PerohistAG_group.csv",4433)
        author=author_date_ontology(z)
    sm=resource_map(small);br=resource_map(broad)
    require(len(sm)==144*len(RESOURCE_YEARS),"DIRECT_RESOURCE_WINDOW_INCOMPLETE")
    require(set(sm)==set(br) and all(sm[k]==br[k] for k in sm),"DIRECT_SOURCE_REDCROP_TABLE_MISMATCH")
    ranks=make_rank_maps(sm)
    repaired,diagnosis=date_diagnosis(cap,hist)
    cnt=diagnosis["counts"]
    out={"source_SHA256":DRI_SHA,"direct_station_years":len(sm),
         "original_source_window":[1988,2013],"target_capture_years":[1999,2013],
         "reference_resource_years":[1988,1997],"date_source_diagnosis":diagnosis,
         "author_date_code_inventory":author,"source_used_rows_expected":1168,
         "historical_v1_status":"STOP_ORIGINAL_SUMMER_DATE_ONTOLOGY",
         "source_date_fix_only_no_new_hypothesis":True,"effect":None,
         "not_seed_dispersal_or_net_recruitment":True,"submission_hold":True}
    require(cnt.get("original_used_rows",0)==1168,"ORIGINAL_USED_DENOMINATOR_CHANGED")
    if cnt.get("unresolved_used_dates",0) or cnt.get("resolved_outside_frozen_summer",0):
        out["status"]="STOP_DATE_SOURCE_UNRESOLVED_OR_OUTSIDE_FROZEN_WINDOW"
        return out
    groups,counts,stop=groups_for_window(repaired,hist,set(ranks[1988]))
    out["source_ontology_counts"]=counts
    if stop:out.update(status=stop,effect=None)
    else:out.update(evaluate(ranks,groups))
    return out

def main():
    try:out=run()
    except Exception as exc:
        out={"status":"STOP_ORIGINAL_HOLT_DATE_REPAIR_SOURCE","effect":None,
             "error_class":type(exc).__name__,
             "reason":str(exc) if type(exc) is ValueError and re.fullmatch("[A-Z0-9_]+",str(exc)) else "UNEXPORTED_ERROR",
             "submission_hold":True}
    out["schema"]="neon.holt.preceding_upcoming_acorn_spatial_use.date_repair.v2"
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
