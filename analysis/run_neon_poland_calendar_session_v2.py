"""Calendar-based source diagnosis and frozen all-rodent contrast.

No response-dependent date interpretation. Preserve original day/date STOP.
Use exact original data, explicit calendar date strings, fixed 4-day windows,
and a distinct independent author aggregate crosswalk. No inferred actor.
"""
from collections import Counter,defaultdict
from datetime import date,datetime,timezone
from statistics import mean
import json,re
from analysis.run_neon_poland_density_stage_v1 import ROOT,fetch_all,number,req
from analysis.run_neon_poland_all_rodent_stage_v1 import (
    REQUIRED,EXPECTED,literal,unknown,positive,stage_counts,compare)
OUT=ROOT/"build/neon_poland_calendar_session_v2_20261125.json"
# Explicit calendar representations only. A numeric field is NOT converted
# from Excel or R epoch without documentation. Pick a global representation
# only when all admissible interpretations yield the identical date vector.
YEAR_FIRST=("%Y-%m-%d","%Y/%m/%d","%Y.%m.%d","%Y%m%d")
DAY_FIRST=("%d.%m.%Y","%d/%m/%Y","%d-%m-%Y","%d.%m.%y","%d/%m/%y","%d-%m-%y")
MONTH_FIRST=("%m.%d.%Y","%m/%d/%Y","%m-%d-%Y","%m.%d.%y","%m/%d/%y","%m-%d-%y")
NAMED=("%d-%b-%Y","%d-%b-%y","%d %b %Y","%d %b %y","%d-%B-%Y","%d %B %Y","%b %d %Y","%b %d, %Y")
DATE_MODES={"day_first":YEAR_FIRST+DAY_FIRST+NAMED,"month_first":YEAR_FIRST+MONTH_FIRST+NAMED}
def date_shape(v):
    return re.sub(r"[A-Za-z]+|\d+",lambda m:("D" if m.group().isdigit() else "A")+str(len(m.group())),literal(v))[:80]

def decode(v,y,mode):
    s=literal(v)
    # An explicitly midnight time suffix contains no calendar ambiguity.
    s=re.sub(r"(?:T| )00:00(?::00(?:\.0+)?)?$","",s)
    ds=set()
    for fmt in DATE_MODES[mode]:
        try:d=datetime.strptime(s,fmt).date()
        except (ValueError,OverflowError):continue
        if "%y" in fmt:
            if d.year%100!=y%100:continue
            try:d=date(y,d.month,d.day)
            except ValueError:continue
        if d.year==y:ds.add(d)
    return next(iter(ds)) if len(ds)==1 else None

def calendar_vector(rows,field="date",year="year"):
    keys={(number(x[year]),literal(x[field])) for x in rows}
    choices={};counts={}
    for mode in DATE_MODES:
        m={k:decode(k[1],k[0],mode) for k in keys}
        n=sum(v is None for v in m.values());counts[mode]=n
        if n==0:choices[mode]=m
    diag={"literal_shapes":dict(Counter(date_shape(x[field]) for x in rows)),
          "distinct_year_literal_dates":len(keys),"unresolved_distinct_literals_by_mode":counts,
          "globally_valid_modes":sorted(choices)}
    if not choices:return None,diag
    vals=list(choices.values())
    if any(x!=vals[0] for x in vals[1:]):
        diag["ambiguous_global_mode"]=True;return None,diag
    return vals[0],diag

def reconstruct(rows):
    cv,diag=calendar_vector(rows)
    out={"date_parse":diag,"source_rows":len(rows)}
    if cv is None:return None,None,out,None
    daily=defaultdict(list);dates=defaultdict(set);days=defaultdict(set)
    extra=[];counts=Counter()
    for j,x in enumerate(rows):
        y=number(x["year"]);s=literal(x["plot"]);a=number(x["abundance"])
        d=cv[y,literal(x["date"])]
        day=literal(x["day"])
        req(y in {2020,2021,2022} and s and day,"INVALID_SOURCE_CONTEXT")
        dates[y,s,day].add(d);days[y,s,d].add(day)
        counts["month_"+str(d.month)]+=1
        if unknown(x["removal"]):
            req(unknown(x["seed_status"]) and all(not positive(x[k]) for k in ("cached","eaten","surface","missing")),"AMBIGUOUS_EXTRA_ROW")
            extra.append(j);continue
        req(literal(x["removal"]) in {"0","1"},"INVALID_REMOVAL")
        daily[y,s,d].append((j,a))
    out.update(day_code_multiple_calendar_dates=sum(len(v)>1 for v in dates.values()),
        calendar_date_multiple_day_codes=sum(len(v)>1 for v in days.values()),
        day_code_cardinality_per_site_year_histogram=dict(Counter(len(v) for v in _day_sets(dates).values())),
        literal_month_counts=dict(counts),unresolved_removal_rows=len(extra))
    req(len(extra)==1 and sum(map(len,daily.values()))==7054,"BINARY_REMOVAL_COHORT_DRIFT")
    by=defaultdict(list)
    for y,s,d in daily:by[y,s].append(d)
    sessions={};ab={};bounds={};hist=Counter();spans=Counter();gaps=Counter();bad=Counter()
    for (y,s),ds in sorted(by.items()):
        chunks=[]
        for d in sorted(ds):
            if not chunks or (d-chunks[-1][-1]).days>=10:chunks.append([d])
            else:chunks[-1].append(d)
        hist[len(chunks)]+=1
        if len(chunks)!=5:bad["not_five_sessions"]+=1
        for k,dd in enumerate(chunks):
            span=(dd[-1]-dd[0]).days
            spans[span]+=1
            if k:gaps[(dd[0]-chunks[k-1][0]).days]+=1
            group=[v for d in dd for v in daily[y,s,d]]
            if span>3 or len(dd)>4:bad["outside_four_day_window"]+=1
            if len(group)>80:bad["over_80_release_rows"]+=1
            if any(d.month not in (6,7,8,9) for d in dd):bad["outside_documented_season"]+=1
            vals={a for j,a in group}
            if len(vals)!=1:bad["nonconstant_abundance"]+=1
            key=(y,s,k);sessions[key]=[j for j,a in group];bounds[key]=(dd[0],dd[-1])
            if len(vals)==1:ab[key]=next(iter(vals))
    out.update(site_years=len(by),sites=len({s for y,s in by}),years=sorted({y for y,s in by}),
       sessions=len(sessions),sessions_per_site_year_histogram=dict(hist),
       session_span_days_histogram=dict(spans),session_start_gap_days_histogram=dict(gaps),structure_failures=dict(bad))
    ok=(len(by)==18 and out["sites"]==6 and out["years"]==[2020,2021,2022] and len(sessions)==90 and not bad)
    return sessions,ab,out,bounds if ok else None

def _day_sets(dates):
    v=defaultdict(set)
    for y,s,k in dates:v[y,s].add(k)
    return v

def summary_crosswalk(header,raw,sessions,ab,bounds,rows):
    req({"Year","Site","Day","Abundance","No. of seeds","Removed","Date","Date2","Date3"}<=set(header),"AUTHOR_AGGREGATE_HEADER_DRIFT")
    rs=[dict(zip(header,x)) for x in raw]
    req(len(rs)==77,"AUTHOR_AGGREGATE_ROW_COUNT_DRIFT")
    hit=Counter();seen=Counter();relations=Counter();example_shape=Counter()
    day_index=defaultdict(set)
    for k,ids in sessions.items():
        for j in ids:
            x=rows[j];day_index[k[0],k[1],literal(x["day"])].add(k)
    for x in rs:
        y=number(x["Year"]);s=literal(x["Site"]);a=number(x["Abundance"])
        options={k for k in sessions if k[:2]==(y,s) and ab[k]==a}
        # Independent author summary day literal and unambiguous calendar
        # fields are compared, not used to construct or select sessions.
        dkeys=day_index.get((y,s,literal(x["Day"])),set())
        dates=set()
        for f in ("Date","Date2","Date3"):
            example_shape[f+":"+date_shape(x[f])]+=1
            if unknown(x[f]):continue
            ds={decode(x[f],y,m) for m in DATE_MODES}
            ds.discard(None)
            if len(ds)==1:dates.update(ds)
        calendar_keys={k for k in options if any(bounds[k][0]<=d<=bounds[k][1] for d in dates)}
        day_keys=options&dkeys
        # Allow either exact Day match or explicit calendar match, but not
        # conflicting unique anchor mappings, and never count-only matching.
        if calendar_keys and day_keys and not calendar_keys&day_keys:
            hit["contradictory_anchor"]+=1;continue
        chosen=(calendar_keys&day_keys) if calendar_keys and day_keys else (calendar_keys or day_keys)
        if len(chosen)!=1:
            hit["unmatched_or_ambiguous"]+=1;continue
        k=next(iter(chosen));seen[k]+=1;hit["unique_anchor_match"]+=1
        relations["calendar_and_day" if calendar_keys and day_keys else "calendar_only" if calendar_keys else "day_only"]+=1
        actual_n=len(sessions[k]);actual_r=sum(literal(rows[j]["removal"])=="1" for j in sessions[k])
        try:n=number(x["No. of seeds"]);r=number(x["Removed"])
        except ValueError:
            hit["unresolved_summary_count"]+=1;continue
        hit["offered_exact"]+=int(actual_n==n)
        hit["removed_exact"]+=int(actual_r==r)
        hit["both_exact"]+=int(actual_n==n and actual_r==r)
    diag={"author_rows":len(rs),"unique_matched_sessions":len(seen),
          "duplicate_matched_session_excess":sum(n-1 for n in seen.values()),
          "crosswalk_counts":dict(hit),"anchor_match_types":dict(relations),
          "author_date_literal_shapes":dict(example_shape)}
    # Pre-effect independent anchor requirement: at least 70/77 exact
    # denominator matches, unique session matches, no contradictory anchors.
    go=(hit["both_exact"]>=70 and hit["unique_anchor_match"]==len(seen)
        and hit["contradictory_anchor"]==0)
    return diag,go

def run():
    f=fetch_all();sep,h,rr=f["dispersal & abundance data.csv"]
    req(sep==";" and REQUIRED<=set(h) and len(rr)==7055,"ORIGINAL_SCHEMA_DRIFT")
    rows=[dict(zip(h,r)) for r in rr]
    sessions,ab,d,bounds=reconstruct(rows)
    out={"calendar_source_diagnosis":d,"effect":None}
    if bounds is None:return {**out,"status":"STOP_CALENDAR_SESSION_SOURCE"}
    _,h2,r2=f["abundances and interactions 25.12.2023.csv"]
    cross,go=summary_crosswalk(h2,r2,sessions,ab,bounds,rows)
    out["author_aggregate_crosswalk"]=cross
    groups,flags,good=stage_counts(rows,sessions);out["stage_checks"]=flags
    if not go:return {**out,"status":"STOP_AUTHOR_AGGREGATE_SESSION_CROSSWALK"}
    if not good:return {**out,"status":"STOP_ALL_RODENT_FATE_PARTITION"}
    out.update(compare(groups,ab));return out
def main():
    out={"schema":"neon.poland.calendar_session_diagnosis.v2","submission_hold":True,
         "v1_day_date_stop_preserved":True,"mouse_species_stop_preserved":True,
         "no_new_seasonal_effect":True}
    try:out.update(run())
    except Exception as e:out.update(status="STOP_SOURCE_OR_ONTOLOGY",effect=None,error_class=type(e).__name__,reason=str(e) if type(e) is ValueError and re.fullmatch(r"[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR")
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
