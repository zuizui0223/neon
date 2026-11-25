"""Final pre-effect source diagnosis. Preserve the original distance STOP.

Do not repair labels or infer geometry. Only a complete, exact within-grid
distance-key partition may support a separate nominal SITE-label contrast
if the problem is confined to metric values. All other original capture,
occasion and cohort gates stay unchanged. No new endpoint after failure.
"""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path
import math,re,json
from analysis.run_neon_maine_deposited_grid_recurrence_v1 import (
    source,read,clean,build_pairs,summarize,MIN_PAIRS,MIN_GRIDS,COUNTS,
)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_maine_station_key_diagnosis_20261125.json"

def metric(x):
    try:v=float(x)
    except (ValueError,TypeError):return None
    return v if math.isfinite(v) and v>=0 else None

def distance_profile(sites,grids,dist):
    want={(a,b) for ss in grids.values() for a in ss for b in ss}
    seen=Counter();values=defaultdict(set);issues=Counter();aids=set();bids=set()
    for x in dist:
        a,b=clean(x["SITE1"]),clean(x["SITE2"]);v=metric(x["DISTANCE"])
        aids.add(a);bids.add(b);seen[a,b]+=1
        values[a,b].add(v)
        if a not in sites or b not in sites:issues["unknown_endpoint_rows"]+=1
        elif sites[a][0]!=sites[b][0]:issues["cross_grid_rows"]+=1
        if v is None:issues["nonfinite_negative_or_non_numeric_rows"]+=1
        elif (a==b)!=(v==0):issues["zero_identity_conflict_rows"]+=1
    missing=want-set(seen);extra=set(seen)-want
    issues["duplicate_pair_excess"]=sum(n-1 for n in seen.values())
    issues["missing_expected_pairs"]=len(missing);issues["unexpected_pairs"]=len(extra)
    issues["conflicting_duplicate_values"]=sum(len(v)>1 for v in values.values())
    issues["reciprocal_value_mismatch_unordered_pairs"]=sum(
        1 for (a,b),v in values.items() if (b,a) in values and str(a)<str(b) and v!=values[b,a])
    issues["endpoint1_not_in_microhabitat"]=len(aids-set(sites))
    issues["endpoint2_not_in_microhabitat"]=len(bids-set(sites))
    issues["microhabitat_not_in_endpoint1"]=len(set(sites)-aids)
    issues["microhabitat_not_in_endpoint2"]=len(set(sites)-bids)
    issues["unique_site1_keys"]=len(aids);issues["unique_site2_keys"]=len(bids)
    keys_ok=(set(seen)==want and len(want)==80000 and all(n==1 for n in seen.values()))
    # An invalid metric alone cannot establish metric geometry, but
    # does not invalidate unique nominal SITE labels. Contradictory
    # zero distance between distinct labels DOES challenge identity.
    identity_ok=keys_ok and not issues["zero_identity_conflict_rows"]
    return {"rows":len(dist),"unique_pairs":len(seen),"expected_pairs":len(want),
            "issue_counts":dict(issues),"exact_within_grid_key_partition":keys_ok,
            "no_explicit_zero_identity_conflict":not bool(issues["zero_identity_conflict_rows"]),
            "nominal_station_identity_gate":identity_ok,
            "full_metric_geometry_gate":identity_ok and not any(issues[k] for k in
                 ("nonfinite_negative_or_non_numeric_rows","reciprocal_value_mismatch_unordered_pairs"))}

def run():
    raw=source()
    with ZipFile(BytesIO(raw)) as z:
        micro=read(z,"microhabitat.csv",{"SITE","GRID","TRT"})
        dist=read(z,"GRID_trap_dist.csv",{"SITE1","SITE2","DISTANCE"})
        occ=read(z,"16_19_GRID_occup.csv",{"SITE","UNIQUE_OCC","OCCUP"})
        cap=[(label,x) for name,label in (("mg.csv","MG"),("pm.csv","PM"))
             for x in read(z,name,{"SITE","GRID","TRT","PIT","SPP","SEASON","YEAR","SESSION","UNIQUE_OCC"})]
    sites={};grids=defaultdict(set);issues=Counter()
    for x in micro:
        s,g,t=(clean(x[k]) for k in ("SITE","GRID","TRT"))
        if not s or not g or not t or s in sites:
            issues["micro_site_missing_or_duplicate"]+=1;continue
        sites[s]=(g,t);grids[g].add(s)
    micro_ok=(not issues["micro_site_missing_or_duplicate"] and len(sites)==800 and len(grids)==8 and all(len(v)==100 for v in grids.values()))
    dd=distance_profile(sites,grids,dist)
    oo={};occasion=set();occ_keys=Counter()
    for x in occ:
        s,o,v=(clean(x[k]) for k in ("SITE","UNIQUE_OCC","OCCUP"))
        if s not in sites:issues["occupancy_unknown_site"]+=1
        if not o:issues["occupancy_unknown_occasion"]+=1
        if v not in {"0","1"}:issues["occupancy_nonbinary_literal"]+=1
        if s in sites and o and v in {"0","1"}:
            occ_keys[s,o]+=1;oo[s,o]=int(v);occasion.add(o)
    issues["occupancy_duplicate_key_excess"]=sum(n-1 for n in occ_keys.values())
    occ_ok=(len(oo)==800*59 and len(occasion)==59 and not any(issues[k] for k in
         ("occupancy_unknown_site","occupancy_unknown_occasion","occupancy_nonbinary_literal","occupancy_duplicate_key_excess")))
    byocc=defaultdict(set);obs=set();pits=defaultdict(set);tagocc=defaultdict(set)
    for expected,x in cap:
        s,g,t,tag,sp,o=(clean(x[k]) for k in ("SITE","GRID","TRT","PIT","SPP","UNIQUE_OCC"))
        bad=False
        if s not in sites:issues["capture_unknown_site"]+=1;bad=True
        elif sites[s]!=(g,t):
            issues["capture_grid_or_treatment_mismatch"]+=1;bad=True
        if not tag or sp!=expected:issues["capture_tag_or_species_mismatch"]+=1;bad=True
        if o not in occasion:issues["capture_occasion_unmatched"]+=1;bad=True
        try:y=int(x["YEAR"]);m=int(x["SESSION"])
        except ValueError:y=m=-1
        if y not in range(16,20) or m not in range(1,6) or clean(x["SEASON"])!=f"{y}_{m}":
            issues["capture_calendar_mismatch"]+=1;bad=True
        if oo.get((s,o))!=1:issues["capture_not_occupied_cell"]+=1;bad=True
        if bad:
            issues["invalid_capture_rows"]+=1;continue
        byocc[o].add((y,m));pits[tag].add(sp);tagocc[tag,o].add((s,sp))
        key=(g,s,o,y,m,tag,sp)
        if key in obs:issues["duplicate_capture_key_rows"]+=1
        obs.add(key)
    issues["occasion_missing_capture_calendar"]=len(occasion-set(byocc))
    issues["occasion_multiple_calendar_contexts"]=sum(len(v)!=1 for v in byocc.values())
    # Also distinguish partial target table from a complete capture roster.
    captured_cells={(s,o) for g,s,o,y,m,t,sp in obs}
    occpos={k for k,v in oo.items() if v==1}
    diag={"source_rows":COUNTS,"microhabitat_unique_station_keys":len(sites),"grid_count":len(grids),
          "grid_size_histogram":dict(Counter(map(len,grids.values()))),"distance":dd,
          "occupancy_unique_cells":len(oo),"occupancy_occasions":len(occasion),"occupancy_positive_cells":len(occpos),
          "occupied_cells_without_deposited_target_capture":len(occpos-captured_cells),
          "deposited_capture_cells":len(captured_cells),"issue_counts":dict(issues),
          "micro_identity_gate":micro_ok,"occupancy_key_gate":occ_ok,
          "capture_calendar_and_parent_gate":not any(issues[k] for k in
            ("invalid_capture_rows","occasion_missing_capture_calendar","occasion_multiple_calendar_contexts")),
          "occupancy_not_independent_operability":True}
    # Do not let distance failure hide additional source problems.
    if not (micro_ok and occ_ok and diag["capture_calendar_and_parent_gate"] and dd["nominal_station_identity_gate"]):
        return {"status":"STOP_UNRESOLVED_SOURCE_KEYS","source_diagnosis":diag,"effect":None}
    conflict={t for t,v in pits.items() if len(v)!=1}
    ambig={t for (t,o),v in tagocc.items() if len(v)!=1}
    obs={v for v in obs if v[5] not in conflict|ambig}
    mo=defaultdict(set)
    for o,v in byocc.items():mo[next(iter(v))].add(o)
    diag.update(cross_species_conflicting_tags=len(conflict),same_occasion_multistation_tags=len(ambig),
                eligible_capture_keys=len(obs),occasion_count_per_session_histogram=dict(Counter(map(len,mo.values()))))
    # Unchanged fixed time windows, same tag exclusion, exact margins,
    # and minimum sample support. No ecological effect computed above.
    pairs,diagpair=build_pairs(grids,obs,mo)
    n=len(pairs);ng=len({v[0] for v in pairs})
    out={"source_diagnosis":diag,"pair_support":diagpair,"effect_support":{"informative_pairs":n,"grids":ng,"minimum_pairs":MIN_PAIRS,"minimum_grids":MIN_GRIDS},
         "effect":None,"nominal_only_not_metric_geometry":True}
    if n<MIN_PAIRS or ng<MIN_GRIDS:return {**out,"status":"STOP_REGIONAL_PAIR_SUPPORT"}
    ef=summarize(pairs)
    ok=ef["equal_grid_mean_Z"]>0 and ef["positive_grid_means"]>=math.ceil(.75*ng) and ef["leave_one_grid_out_mean_range"][0]>0
    return {**out,"status":"REGIONAL_DESCRIPTIVE_DIRECTION_SUPPORTED" if ok else "REGIONAL_DESCRIPTIVE_DIRECTION_NOT_SUPPORTED","effect":ef}

def main():
    out={"schema":"neon.maine.station_key_diagnosis.v2","submission_hold":True,
         "original_distance_source_stop_preserved":True,"no_source_label_repair":True,
         "no_metric_geometry_or_habitat_claim":True}
    try:out.update(run())
    except Exception as e:out.update(status="STOP_SOURCE_OR_SCHEMA",effect=None,error_class=type(e).__name__,reason=str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR")
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
