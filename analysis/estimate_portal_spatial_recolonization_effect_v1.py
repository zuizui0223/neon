#!/usr/bin/env python3
"""Frozen Portal spatial recolonization endpoint. Requires authorized support gate."""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

COHORTS={"kr_return":(6,13,18),"rodent_return":(5,7,24),"control":(4,11,14,17)}
TREATMENT={p:g for g,plots in COHORTS.items() for p in plots}
KR={"DM","DO","DS"}
STAKE_SET={r*10+c for r in range(1,8) for c in range(1,8)}
START=2015*12+3
RESAMPLES=500
BOOTSTRAPS=5000
SEED=20261008

def num(v):
    try:return int(float(str(v).strip()))
    except (ValueError,TypeError):return None

def records(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def quantile(a,p):
    xs=sorted(a)
    if not xs:return None
    h=(len(xs)-1)*p
    j=int(h)
    return xs[j]+(h-j)*(xs[min(j+1,len(xs)-1)]-xs[j])

def xy(stake):
    s=num(stake)
    return ((s%10-1)*6.25,(s//10-1)*6.25)

def mpd10(stakes):
    pos=[xy(s) for s in stakes]
    ds=[math.dist(a,b) for a,b in itertools.combinations(pos,2)]
    return sum(ds)/len(ds)

def comparison(means,groupA,groupB):
    a=[x for p,x in means.items() if TREATMENT[p]==groupA]
    b=[x for p,x in means.items() if TREATMENT[p]==groupB]
    return statistics.mean(a)-statistics.mean(b) if a and b else None

def main():
    ap=argparse.ArgumentParser()
    for k in ("captures","trapping","gate","output"):
        ap.add_argument("--"+k,type=Path,required=True)
    args=ap.parse_args()

    gate=json.loads(args.gate.read_text(encoding="utf-8"))
    if gate["status"]!="effect_blind_support_gate" or \
       gate["gate"]["decision"]!="authorize_frozen_spatial_dispersion_test" or \
       not gate["gate"]["authorize_spatial_response"]:
        raise RuntimeError("frozen effect-blind support gate did not authorize opening spatial locations")
    cap=records(args.captures)
    trp=records(args.trapping)

    sampled=set()
    for r in trp:
        y,m,period,p=[num(r[k]) for k in ("year","month","period","plot")]
        if None in (y,m,period,p) or period<1:
            continue
        if num(r["sampled"])==1 and num(r["qcflag"])==1 and (num(r["effort"]) or 0)>=47:
            sampled.add((y,m,period,p))
    sites=defaultdict(list)
    for r in cap:
        y,m,period,p,stake=[num(r.get(k)) for k in ("year","month","period","plot","stake")]
        if None in (y,m,period,p) or (y,m,period,p) not in sampled or p not in TREATMENT:
            continue
        if str(r.get("species","")).strip().upper() not in KR or stake not in STAKE_SET:
            continue
        win=(y*12+m-1-START)//6
        if 0<=win<8:
            sites[(p,win)].append(stake)

    # Assert that the effect-stage input still matches the effect-blind support counts.
    for g,plots in COHORTS.items():
        for p in plots:
            expected=gate["support"][g][str(p)]["sixmonth_capture_counts"]
            observed=[len(sites[(p,w)]) for w in range(8)]
            if observed!=expected:
                raise RuntimeError(f"capture support mismatch for plot {p}: {observed} != {expected}")
    rng=random.Random(SEED)
    by_plot={}
    cells=[]
    for g,plots in COHORTS.items():
        for p in plots:
            by_plot[p]={}
            for w in range(8):
                points=sites[(p,w)]
                if len(points)<10:
                    continue
                sims=[mpd10(rng.sample(points,10)) for _ in range(RESAMPLES)]
                cell={
                    "cohort":g,"plot":p,"window":w,"n_captures":len(points),
                    "count_standardized_mpd_mean_m":statistics.mean(sims),
                    "mpd_q025_m":quantile(sims,.025),
                    "mpd_q975_m":quantile(sims,.975),
                    "resamples":RESAMPLES
                }
                cells.append(cell)
                by_plot[p][w]=cell["count_standardized_mpd_mean_m"]

    window_cohorts=[]
    for w in range(8):
        item={"window":w}
        for g,plots in COHORTS.items():
            vals=[by_plot[p][w] for p in plots if w in by_plot[p]]
            item[g]={
                "plots":len(vals),
                "mean_mpd_m":statistics.mean(vals) if vals else None,
                "plot_values_m":dict((str(p),by_plot[p][w]) for p in plots if w in by_plot[p])
            }
        if item["kr_return"]["plots"]>=2 and item["rodent_return"]["plots"]>=2:
            item["kr_minus_rodent_mpd_m"]=item["kr_return"]["mean_mpd_m"]-item["rodent_return"]["mean_mpd_m"]
        else:
            item["kr_minus_rodent_mpd_m"]=None
        window_cohorts.append(item)

    # Plot is the unit of independent replication. Early windows 0–1;
    # later 2–5 as declared before viewing spatial locations.
    paired={}
    for p,values in by_plot.items():
        early=[values[w] for w in (0,1) if w in values]
        late=[values[w] for w in (2,3,4,5) if w in values]
        if early and late:
            paired[p]={"cohort":TREATMENT[p],
                        "early_mpd_m":statistics.mean(early),
                        "later_mpd_m":statistics.mean(late),
                        "change_mpd_m":statistics.mean(late)-statistics.mean(early),
                        "early_window_count":len(early),"later_window_count":len(late)}
    eligibleKR={p:v for p,v in paired.items() if v["cohort"]=="kr_return"}
    eligibleRD={p:v for p,v in paired.items() if v["cohort"]=="rodent_return"}
    did=None
    if len(eligibleKR)>=2 and len(eligibleRD)>=2:
        def stat(A,B):
            mean=lambda x,key:statistics.mean(d[key] for d in x.values())
            early=mean(A,"early_mpd_m")-mean(B,"early_mpd_m")
            late=mean(A,"later_mpd_m")-mean(B,"later_mpd_m")
            return early,late,late-early
        early,late,delta=stat(eligibleKR,eligibleRD)
        A=list(eligibleKR.values());B=list(eligibleRD.values())
        boot=[]
        for _ in range(BOOTSTRAPS):
            aa={i:rng.choice(A) for i in range(len(A))}
            bb={i:rng.choice(B) for i in range(len(B))}
            boot.append(stat(aa,bb))
        nA=len(A);pooled=A+B
        perm_early=[];perm_delta=[]
        for idxs in itertools.combinations(range(len(pooled)),nA):
            inds=set(idxs)
            aa={i:pooled[i] for i in inds}
            bb={i:pooled[i] for i in range(len(pooled)) if i not in inds}
            e,l,d=stat(aa,bb)
            perm_early.append(e)
            perm_delta.append(d)
        did={
            "kr_plots":sorted(eligibleKR),
            "rodent_plots":sorted(eligibleRD),
            "early_kr_minus_rodent_mpd_m":early,
            "later_kr_minus_rodent_mpd_m":late,
            "difference_in_differences_m":delta,
            "early_difference_plot_bootstrap95_m":[quantile([z[0] for z in boot],.025),quantile([z[0] for z in boot],.975)],
            "difference_in_differences_plot_bootstrap95_m":[quantile([z[2] for z in boot],.025),quantile([z[2] for z in boot],.975)],
            "exact_plot_label_randomization":{
                "number_of_labelings":len(perm_early),
                "one_sided_p_early_kr_smaller":sum(x<=early+1e-12 for x in perm_early)/len(perm_early),
                "one_sided_p_catchup_positive":sum(x>=delta-1e-12 for x in perm_delta)/len(perm_delta)
            }
        }

    output={
        "schema":"neon.portal_spatial_recolonization_effect.v1",
        "status":"exploratory_frozen_endpoint_after_effect_blind_gate",
        "gate_decision":gate["gate"]["decision"],
        "seed":SEED,"draws_per_plot_window":RESAMPLES,"plot_bootstrap_replicates":BOOTSTRAPS,
        "capture_plot_windows":[str(p)+"_"+str(w) for p,w in sites],
        "plot_window_results":cells,
        "cohort_window_results":window_cohorts,
        "paired_plot_early_later":dict((str(k),v) for k,v in paired.items()),
        "primary_plot_level_comparison":did,
        "claim_boundary":{
            "primary_endpoint_frozen_prior_to_spatial_response":True,
            "observation":"Capture-position dispersion from exactly 10 sampled records; not natural movement, home-range size or competition mechanism",
            "treatments":"KR-return versus rodent-return versus long-term control",
            "early_period":"windows 0 and 1, April 2015–March 2016",
            "later_period":"windows 2–5, April 2016–March 2018",
            "limitations":"Tiny number of independent plots and time-dependent effort/habitat; exact label permutation is coarse",
            "no_link_to_san_jacinto_previous_occupant_causality":True
        }
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "gate":output["gate_decision"],
        "plot_windows_supported":len(cells),
        "cohort_window_results":window_cohorts,
        "primary_plot_level_comparison":did,
    },indent=2,sort_keys=True))


if __name__=="__main__":
    main()
