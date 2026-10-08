#!/usr/bin/env python3
"""Effect-blind support audit; never inspect within-plot spatial dispersion here."""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path

COHORTS={"kr_return":(6,13,18),"rodent_return":(5,7,24),"control":(4,11,14,17)}
KR={"DM","DO","DS"}
VALID_STAKES={r*10+c for r in range(1,8) for c in range(1,8)}
START=2015*12+3
END=2018*12+11

def load(p):
    with p.open(encoding="utf-8-sig",newline="") as h:
        reader=csv.DictReader(h)
        return set(reader.fieldnames or []),list(reader)

def n(v):
    try:return int(float(str(v).strip()))
    except (ValueError,TypeError):return None

def main():
    ap=argparse.ArgumentParser()
    for k in ("captures","trapping","plots","output"):
        ap.add_argument("--"+k,required=True,type=Path)
    a=ap.parse_args()
    cc,cap=load(a.captures);tc,trp=load(a.trapping);pc,plot=load(a.plots)
    for schema,required in [(cc,{"year","month","period","plot","stake","species"}),
     (tc,{"year","month","period","plot","sampled","effort","qcflag"}),
     (pc,{"year","month","plot","treatment"})]:
        if not required.issubset(schema):
            raise RuntimeError("schema missing fields: "+repr(sorted(required-schema)))
    tr={(n(r["year"]),n(r["month"]),n(r["plot"])):str(r["treatment"]).strip().lower()
        for r in plot}
    expected_pre={"kr_return":"exclosure","rodent_return":"removal","control":"control"}
    treatment_validation={}
    for cohort,plots in COHORTS.items():
        treatment_validation[cohort]={}
        for p in plots:
            pre=tr.get((2015,3,p));post=tr.get((2015,4,p))
            ok=pre==expected_pre[cohort] and post=="control"
            treatment_validation[cohort][str(p)]={"pre":pre,"post":post,"matched":ok}
            if not ok:
                raise RuntimeError("Frozen treatment cohorts do not match Portal plot metadata")
    sampled=set()
    for r in trp:
        y,m,period,p=(n(r[k]) for k in ("year","month","period","plot"))
        if None in (y,m,period,p) or not(2013<=y<=2018 and 1<=m<=12 and period>=1):
            continue
        if n(r["sampled"])==1 and n(r["qcflag"])==1 and (n(r["effort"]) or 0)>=47:
            sampled.add((y,m,period,p))
    counts=Counter()
    exclusions=Counter()
    for r in cap:
        y,m,per,p,stake=(n(r.get(k)) for k in ("year","month","period","plot","stake"))
        if None in (y,m,per,p) or not (START<=y*12+m-1<=END and per>=1):
            exclusions["out_of_period"]+=1;continue
        if not any(p in plots for plots in COHORTS.values()):
            exclusions["out_of_cohort"]+=1;continue
        if (y,m,per,p) not in sampled:
            exclusions["unsampled_or_low_effort"]+=1;continue
        sp=str(r.get("species","")).strip().upper()
        if sp not in KR:
            exclusions["not_identified_Dipodomys"]+=1;continue
        if stake not in VALID_STAKES:
            exclusions["invalid_stake"]+=1;continue
        win=(y*12+m-1-START)//6
        counts[(p,win)]+=1
    cohort_support={}
    gate={}
    for group,plots in COHORTS.items():
        cohort_support[group]={}
        for p in plots:
            x=[counts[(p,w)] for w in range(8)]
            cohort_support[group][str(p)]={"sixmonth_capture_counts":x,
              "supported_windows":[w for w,k in enumerate(x) if k>=10]}
        gate[group]=sum(len(z["supported_windows"])>=2 for z in cohort_support[group].values())>=2
    authorized=all(gate.values())
    output={
      "schema":"neon.portal_spatial_recolonization_support.v1",
      "status":"effect_blind_support_gate",
      "portal_data_commit":"171f9441c02c5a95e7dd1a6fafe3e4b063c36c14",
      "captures_total_rows":len(cap),
      "sampling_periods_2013_2018_full_qc":len(sampled),
      "treatment_metadata":treatment_validation,
      "support":cohort_support,
      "exclusions":dict(exclusions),
      "gate":{"per_cohort":gate,
        "authorize_spatial_response":authorized,
        "decision":"authorize_frozen_spatial_dispersion_test" if authorized else "stop_insufficient_spatial_capture_support"},
      "claim_boundary":{"spatial_capture_pattern_inspected":False,
          "species_response_estimated":False,
          "primary_directionality_tested":False}
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:output[k] for k in ("status","treatment_metadata","support","gate")},indent=2,sort_keys=True))
if __name__=="__main__":
    main()
