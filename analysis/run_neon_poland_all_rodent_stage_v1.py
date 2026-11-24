"""Distinct all-rodent recorded stage contrast, preserving v1 mouse-only STOP.

Source-defined day of experiment, no imputed species or date. Reconstruct
complete four-day sessions before opening grouped outcomes. All 7055
source records remain accounted for; use the 7054 binary-removal records.
"""
from collections import Counter, defaultdict
from datetime import datetime,timezone
from fractions import Fraction
from statistics import mean
import json,re
from analysis.run_neon_poland_density_stage_v1 import ROOT,fetch_all,number,req
OUT=ROOT/"build/neon_poland_all_rodent_stage_20261125.json"
REQUIRED={"year","plot","date","day","abundance","seed_status","removal","cached","eaten","surface","missing"}
# All published 2999 rodent removals; source flag totals, not attribution.
EXPECTED={"offered":7054,"harvest":2999,"cache":560,"eaten":896,"surface":290,"unlocated":1253}

def literal(x):
    return str(x).strip()
def unknown(x):return literal(x).lower() in {"","na","nan"}
def positive(x):
    t=literal(x)
    req(t in {"0","1"} or unknown(t),"UNEXPECTED_BINARY_FLAG")
    return t=="1"

def structure(rows):
    dates=defaultdict(lambda:defaultdict(set))
    daily=defaultdict(list)
    excluded=[]
    for j,x in enumerate(rows):
        y=number(x["year"]);s=literal(x["plot"]);day=number(x["day"])
        a=number(x["abundance"]);dt=literal(x["date"])
        req(y in {2020,2021,2022} and s and dt,"ORIGINAL_CONTEXT_INVALID")
        # A day can repeat across different sites but must not refer to
        # multiple actual date strings within a site-year.
        dates[y,s][day].add(dt)
        rem=literal(x["removal"])
        if unknown(rem):
            req(unknown(x["seed_status"]) and all(not positive(x[k]) for k in ("cached","eaten","surface","missing")),"AMBIGUOUS_EXTRA_ROW")
            excluded.append(j)
        else:
            req(rem in {"0","1"},"INVALID_REMOVAL")
            daily[y,s,day].append((j,a))
    req(len(excluded)==1 and sum(len(v) for v in daily.values())==7054,"ORIGINAL_BINARY_REMOVAL_SUPPORT_DRIFT")
    req(all(len(d)==1 for days in dates.values() for d in days.values()),"DAY_DATE_NOT_UNIQUE")
    req(all(len({next(iter(v)) for v in d.values()})==len(d) for d in dates.values()),"DATE_DAY_NOT_ONE_TO_ONE")
    by=defaultdict(list)
    for y,s,d in daily:by[y,s].append(d)
    diag={"site_years":len(by),"sites":len({s for y,s in by}),"years":sorted({y for y,s in by}),
          "source_rows":len(rows),"excluded_one_unresolved_removal_row":len(excluded),
          "day_date_bijection":True,"days_per_site_year_histogram":dict(Counter(len(v) for v in by.values()))}
    sessions={};ab={};hist=Counter();spans=Counter();bad=Counter()
    for (y,s),ds in sorted(by.items()):
        chunks=[]
        for d in sorted(ds):
            if not chunks or d-chunks[-1][-1]>=10:chunks.append([d])
            else:chunks[-1].append(d)
        hist[len(chunks)]+=1
        if len(chunks)!=5:bad["not_five_sessions"]+=1
        for k,days in enumerate(chunks):
            spans[days[-1]-days[0]]+=1
            group=[v for d in days for v in daily[y,s,d]]
            if days[-1]-days[0]>3 or len(days)>4:bad["outside_four_day_window"]+=1
            if len(group)>80:bad["over_80_release_rows"]+=1
            vals={a for j,a in group}
            if len(vals)!=1:bad["nonconstant_abundance"]+=1
            key=(y,s,k)
            sessions[key]=[j for j,a in group]
            if len(vals)==1:ab[key]=next(iter(vals))
    diag.update(sessions=len(sessions),session_count_histogram=dict(hist),
                session_span_histogram=dict(spans),structure_failures=dict(bad))
    ok=(len(by)==18 and diag["sites"]==6 and diag["years"]==[2020,2021,2022] and len(sessions)==90 and not bad)
    return sessions,ab,diag,ok

def stage_counts(rows,sessions):
    groups={};tot=Counter();cross=Counter();issues=Counter()
    for key,ix in sessions.items():
        a=Counter()
        for j in ix:
            x=rows[j];a["offered"]+=1
            rem=literal(x["removal"])=="1"
            a["harvest"]+=int(rem)
            z={name:positive(x[col]) for name,col in (("cache","cached"),("eaten","eaten"),("surface","surface"))}
            # Literal M in the source denotes unlocated. The parallel flag
            # is checked as well, but not substituted for the literal.
            z["unlocated"]=literal(x["seed_status"]).upper()=="M"
            cross["/".join([literal(x["seed_status"]),str(int(rem)),*(str(int(z[k])) for k in ("cache","eaten","surface","unlocated"))])]+=1
            if rem and sum(z.values())!=1:issues["removed_not_exhaustive"]+=1
            if not rem and (any(z.values()) or literal(x["seed_status"])!="IS"):issues["unremoved_conflict"]+=1
            if positive(x["missing"])!=z["unlocated"]:issues["missing_flag_vs_M"]+=1
            for k,v in z.items():a[k]+=int(v)
        groups[key]=a;tot.update(a)
    return groups,{"source_totals":dict(tot),"joint_status_flag_counts":dict(cross),
                   "flag_issues":dict(issues),"expected_totals":EXPECTED},dict(tot)==EXPECTED and not issues

def merge(xs):
    ans=Counter()
    for x in xs:ans.update(x)
    return ans

def pair(lo,hi):
    def parts(c):
        n,h,k,u=(c[a] for a in ("offered","harvest","cache","unlocated"))
        req(n>0 and h>0 and 0<=k<=h<=n and 0<=u<=h-k,"INVALID_STAGE")
        return Fraction(h,n),Fraction(k,h),Fraction(k,n),Fraction(k+u,n),Fraction(k+u,h)
    a,b=parts(lo),parts(hi)
    harvest=(b[0]-a[0])*(a[1]+b[1])/2
    post=(b[1]-a[1])*(a[0]+b[0])/2
    d=b[2]-a[2];req(d==harvest+post,"DECOMPOSITION_MISMATCH")
    return {"harvest_RD":b[0]-a[0],"conditional_recorded_cache_RD":b[1]-a[1],
            "recorded_cache_per_offered_RD":d,"harvest_component":harvest,
            "post_harvest_component":post,
            "cache_RD_lower":b[2]-a[3],"cache_RD_upper":b[3]-a[2],
            "conditional_RD_lower":b[1]-a[4],"conditional_RD_upper":b[4]-a[1]}

def compare(groups,ab):
    sy=defaultdict(list)
    for k in groups:sy[k[:2]].append(k)
    results=[];stops=Counter()
    for (y,s),keys in sorted(sy.items()):
        low=min(ab[k] for k in keys);high=max(ab[k] for k in keys)
        if low==high:stops["constant_abundance"]+=1;continue
        a=merge(groups[k] for k in keys if ab[k]==low);b=merge(groups[k] for k in keys if ab[k]==high)
        if not a["harvest"] or not b["harvest"]:stops["zero_harvest"]+=1;continue
        results.append((y,s,pair(a,b)))
    out={"eligible_site_years":len(results),"excluded_site_years":dict(stops),"effect":None}
    if len(results)<12 or len({s for y,s,v in results})!=6 or len({y for y,s,v in results})!=3:
        return {**out,"status":"STOP_EXTREME_PAIR_SUPPORT"}
    names=list(results[0][2])
    sites={s:{k:mean(v[k] for y,t,v in results if t==s) for k in names} for s in sorted({s for y,s,v in results})}
    bal={k:mean(v[k] for v in sites.values()) for k in names}
    nopp=sum(v["harvest_component"]>0 and v["post_harvest_component"]<0 for v in sites.values())
    ok=bal["harvest_component"]>0 and bal["post_harvest_component"]<0 and nopp>=5
    return {**out,"status":"ALL_RODENT_DESCRIPTIVE_OFFSET_SUPPORTED" if ok else "ALL_RODENT_DESCRIPTIVE_OFFSET_NOT_SUPPORTED",
            "effect":{"equal_site_mean":{k:float(v) for k,v in bal.items()},
                "equal_site_year_mean":{k:float(mean(v[k] for y,s,v in results)) for k in names},
                "sites_opposite_components":nopp,
                "cache_direction_identified_under_unlocated_bound":bal["cache_RD_lower"]>0 or bal["cache_RD_upper"]<0,
                "conditional_direction_identified_under_unlocated_bound":bal["conditional_RD_lower"]>0 or bal["conditional_RD_upper"]<0,
                "all_rodent_outcome_mouse_abundance_index_not_species_specific":True,
                "density_day_confounded_no_causal_or_germination_claim":True}}

def author_aggregate_support(header,raw,rows,sessions,ab):
    # Exact year/site/day membership plus abundance, using author summary
    # only to document overlap, never to select extreme sessions.
    required={"Year","Site","Day","Abundance","No. of seeds","Removed"}
    if not required<=set(header):return {"status":"AGGREGATE_HEADER_UNRESOLVED"}
    index=defaultdict(set)
    for key,ix in sessions.items():
        for j in ix:
            x=rows[j]
            index[key[0],key[1],number(x["day"]),number(x["abundance"])].add(key)
    counts=Counter();matched=set()
    for v in raw:
        x=dict(zip(header,v))
        try:keys=index.get((number(x["Year"]),literal(x["Site"]),number(x["Day"]),number(x["Abundance"])),set())
        except ValueError:counts["unresolved_summary_key"]+=1;continue
        if len(keys)!=1:counts["unmatched_or_ambiguous"]+=1;continue
        k=next(iter(keys));matched.add(k);counts["unique_session_match"]+=1
        try:
            counts["exact_offered_count_match"]+=int(number(x["No. of seeds"])==len(sessions[k]))
            counts["exact_removed_count_match"]+=int(number(x["Removed"])==sum(literal(rows[j]["removal"])=="1" for j in sessions[k]))
        except ValueError:counts["unresolved_summary_count"]+=1
    return {"author_aggregate_rows":len(raw),"matched_unique_sessions":len(matched),"crosswalk_counts":dict(counts),"not_used_for_session_selection":True}

def run():
    files=fetch_all()
    sep,h,rr=files["dispersal & abundance data.csv"]
    req(sep==";" and REQUIRED<=set(h) and len(rr)==7055,"ORIGINAL_SCHEMA_DRIFT")
    rows=[dict(zip(h,r)) for r in rr]
    sessions,ab,diag,ok=structure(rows)
    out={"structure":diag,"effect":None}
    if not ok:return {**out,"status":"STOP_SESSION_RECONSTRUCTION"}
    groups,flags,good=stage_counts(rows,sessions)
    out["stage_checks"]=flags
    _,h2,r2=files["abundances and interactions 25.12.2023.csv"]
    out["author_aggregate_support"]=author_aggregate_support(h2,r2,rows,sessions,ab)
    if not good:return {**out,"status":"STOP_ALL_RODENT_FATE_PARTITION"}
    out.update(compare(groups,ab));return out
def main():
    out={"schema":"neon.poland.all_rodent_stage_decomposition.v1","submission_hold":True,
         "original_mouse_only_v1_stop_preserved":True,"no_seasonal_fit":True}
    try:out.update(run())
    except Exception as e:out.update(status="STOP_SOURCE_OR_ONTOLOGY",effect=None,error_class=type(e).__name__,reason=str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR")
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
