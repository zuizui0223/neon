#!/usr/bin/env python3
"""Exploratory temporal-rewiring uncertainty for San Jacinto trap sequences.

Post-result diagnostic: signs were inspected before this audit. The bootstrap
quantifies uncertainty and does NOT turn the observed hierarchy into a
prospectively tested ecological mechanism.

Same detector/date-shuffle reference as the original sequence lane, but
restricted to grid-dates with all three check labels represented. Thus EMPTY
is inferred only where at least one capture documents each check was made.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

SPECIES = ("CHFA", "DKR", "LAPM", "PEER", "PEMA", "SKR")
PAIR_NAMES = ("EARLY-MIDDLE", "MIDDLE-LATE")
ALL_BINS = ("EARLY", "MIDDLE", "LATE")
FLAGS = tuple(f"{letter}{n}" for letter in "ABCDEFG" for n in range(1,8))
KR = ("DKR", "SKR")
REPS = 5000
SEED = 20261008

def up(v):
    return (v or "").strip().upper()

def dt(s):
    for fmt in ("%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(s).strip(), fmt).date()
        except ValueError:
            pass
    raise ValueError("bad date: "+repr(s))

def quantile(v, p):
    q = sorted(v)
    if not q:
        return None
    x=(len(q)-1)*p
    a=int(math.floor(x))
    b=int(math.ceil(x))
    return q[a] if a == b else q[a]*(b-x)+q[b]*(x-a)

def bh_ps(pvals):
    order=sorted(range(len(pvals)), key=lambda i:pvals[i])
    out=[1.0]*len(pvals); last=1.0
    for rank in range(len(order)-1,-1,-1):
        idx=order[rank]
        last=min(last, pvals[idx]*len(order)/(rank+1))
        out[idx]=last
    return out

def read_data(src):
    with src.open(newline="",encoding="utf-8-sig") as fh:
        raw=list(csv.DictReader(fh))
    dates=defaultdict(set)
    bins=defaultdict(set)
    cells=defaultdict(list)
    for r in raw:
        g=up(r.get("grid"))
        d=str(r.get("date","")).strip()
        b=up(r.get("time_bin"))
        flag=up(r.get("flag"))
        sp=up(r.get("species"))
        if not g or not d:
            continue
        dates[g].add(d)
        if b in ALL_BINS:
            bins[(g,d)].add(b)
            if flag in FLAGS:
                cells[(g,d,flag,b)].append(sp)
    bout={}
    bout_size={}
    for g, dd in dates.items():
        current=1; prev=None; sub=[]
        for d in sorted(dd,key=dt):
            if prev is not None and (dt(d)-dt(prev)).days>7:
                bout_size[(g,current)]=len(sub)
                current+=1; sub=[]
            bout[(g,d)]=current
            sub.append(d)
            prev=d
        bout_size[(g,current)]=len(sub)
    complete={key for key,x in bins.items() if all(v in x for v in ALL_BINS)}
    invalid=0
    multi=0
    def state(g,d,flag,b):
        nonlocal invalid,multi
        v=cells.get((g,d,flag,b),[])
        if not v:
            return "EMPTY"
        z=set(v)
        if len(z)!=1 or not next(iter(z)) in SPECIES:
            return None
        return next(iter(z))

    trans=[]
    for g,d in sorted(complete):
        for flag in FLAGS:
            for a,b in zip(ALL_BINS,ALL_BINS[1:]):
                p=state(g,d,flag,a)
                q=state(g,d,flag,b)
                if p is None or q is None:
                    invalid+=1
                    continue
                trans.append({
                    "grid":g, "date":d, "flag":flag,
                    "bout":bout[(g,d)],"bout_size":bout_size[(g,bout[(g,d)])],
                    "interval":a+"-"+b,"prev":p,"next":q
                })
    return raw, trans, {"complete_grid_dates":len(complete),
         "valid_transitions":len(trans),
         "excluded_transitions_ambiguous_or_nonfocal":invalid,
         "bout_block_count":len(set((x["grid"],x["bout"]) for x in trans))}

def blank_metric():
    return [0.0, 0.0]

def contribute(trans, only_bout_size_3=False):
    # Conditional date-shuffle expectation preserves grid, trap, trapping bout,
    # check transition, and the within-stratum marginal counts of each species.
    grouped=defaultdict(list)
    for r in trans:
        if only_bout_size_3 and r["bout_size"] != 3:
            continue
        key=(r["grid"],r["flag"],r["bout"],r["interval"])
        grouped[key].append(r)
    block=defaultdict(lambda:defaultdict(blank_metric))
    used_groups=0
    for (g,flag,b,interval),rows in grouped.items():
        n=len(rows)
        if n < 2:
            continue
        used_groups+=1
        pc=Counter(r["prev"] for r in rows)
        nc=Counter(r["next"] for r in rows)
        pairs=Counter((r["prev"],r["next"]) for r in rows)
        out=block[(g,b)]
        for a in SPECIES:
            for c in SPECIES:
                if a==c:
                    continue
                key=(interval,a,c)
                z=out[key]
                z[0] += pairs[(a,c)]
                z[1] += pc[a]*nc[c]/n
        for kr in ("KR", "LAPM"):
            if kr == "KR":
                obs=sum(pairs[(s,"LAPM")] for s in KR)
                ev=sum(pc[s]*nc["LAPM"]/n for s in KR)
                key=(interval,"KR","LAPM")
            else:
                obs=sum(pairs[("LAPM",s)] for s in KR)
                ev=sum(pc["LAPM"]*nc[s]/n for s in KR)
                key=(interval,"LAPM","KR")
            z=out[key]
            z[0]+=obs
            z[1]+=ev
    return block, used_groups

def add_metrics(keys,block):
    out=defaultdict(blank_metric)
    for k in keys:
        for edge,(o,e) in block[k].items():
            z=out[edge]
            z[0]+=o
            z[1]+=e
    return out

def effect(metric, interval, source, target):
    o,e=metric.get((interval,source,target),(0.0,0.0))
    return {"observed":o,"expected":e,"oe":o/e if e>0 else None}

def smooth_logoe(metric, interval, a, b):
    o,e=metric.get((interval,a,b),(0.0,0.0))
    return math.log((o+0.5)/(e+0.5))

def directed_asym(metric,interval,a,b):
    return smooth_logoe(metric,interval,a,b)-smooth_logoe(metric,interval,b,a)

def compute_metric_observables(metric):
    focal={}
    for interval in PAIR_NAMES:
        focal[interval]={
          "KR_to_LAPM":effect(metric,interval,"KR","LAPM"),
          "LAPM_to_KR":effect(metric,interval,"LAPM","KR"),
        }
    # log-O/E ratio of KR -> LAPM in the two intervals, with
    # +0.5/(expected+0.5) smoothing for bootstrap zero counts.
    fl= smooth_logoe(metric,PAIR_NAMES[0],"KR","LAPM") - smooth_logoe(metric,PAIR_NAMES[1],"KR","LAPM")
    dyads={}
    for a,b in itertools.combinations(SPECIES,2):
        d1=directed_asym(metric,PAIR_NAMES[0],a,b)
        d2=directed_asym(metric,PAIR_NAMES[1],a,b)
        dyads[a+"-"+b]=(d1,d2,d1-d2)
    return focal,fl,dyads

def audit(trans,only3=False):
    block,used=contribute(trans, only_bout_size_3=only3)
    keys=sorted(block)
    totals=add_metrics(keys,block)
    focal,fl,dyads=compute_metric_observables(totals)
    rng=random.Random(SEED + int(only3))
    series_fl=[]
    series_d={key:[] for key in dyads}
    sign_agree=[]
    for _ in range(REPS):
        sampled=[keys[rng.randrange(len(keys))] for _ in range(len(keys))]
        m=add_metrics(sampled,block)
        _,f,d=compute_metric_observables(m)
        series_fl.append(f)
        sign_agree.append(sum(x[0]*x[1]>0 for x in d.values()))
        for key, vals in d.items():
            series_d[key].append(vals[2])
    directional_summary=[]
    pvals=[]
    for key,(x1,x2,shift) in dyads.items():
        vals=series_d[key]
        ci=(quantile(vals,.025),quantile(vals,.975))
        z=shift/statistics.stdev(vals) if statistics.stdev(vals)>0 else 0
        p=math.erfc(abs(z)/math.sqrt(2))
        pvals.append(p)
        directional_summary.append({
          "dyad":key,
          "log_asymmetry_early_middle":x1,
          "log_asymmetry_middle_late":x2,
          "sign_conserved": x1*x2>0,
          "delta_log_asymmetry":shift,
          "bootstrap95":ci,
          "interval_contrast_excludes_zero":ci[0]>0 or ci[1]<0,
          "approx_normal_two_sided_p":p
        })
    qvals=bh_ps(pvals)
    for r,q in zip(directional_summary,qvals):
        r["q_bh_exploratory"]=q
    observed_agree=sum(d[0]*d[1]>0 for d in dyads.values())
    cfl=(quantile(series_fl,.025), quantile(series_fl,.975))
    return {
        "scope":"exact_three_night_bouts" if only3 else "all_complete_check_label_nights",
        "strata_date_shuffle_groups_used":used,
        "grid_bout_bootstrap_blocks":len(keys),
        "focal":focal,
        "KR_to_LAPM_interval_logOE_difference":{
            "point_smoothed_logOEratiodifference":fl,
            "bootstrap95":cfl,
            "excludes_zero":cfl[0]>0 or cfl[1]<0,
            "bootstrap_fraction_nonnegative":sum(v>=0 for v in series_fl)/REPS
        },
        "directional_dyad_agreement":{
            "point_conserved":observed_agree,
            "point_nonconserved":len(dyads)-observed_agree,
            "dyads":len(dyads),
            "bootstrap_conserved95":[quantile(sign_agree,.025),quantile(sign_agree,.975)],
            "bootstrap_median_conserved":quantile(sign_agree,.5),
            "n_dyads_interval_difference_ci_excludes_zero":sum(r["interval_contrast_excludes_zero"] for r in directional_summary),
            "n_dyads_bh_q_lt_0_10":sum(r["q_bh_exploratory"]<.1 for r in directional_summary),
        },
        "dyads":directional_summary
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    raw,trans,support=read_data(args.input)
    result={
      "schema":"neon.trap_sequence_interval_rewiring_audit.v1",
      "status":"post_result_exploratory_non_rescuing",
      "source_checksum_expected":"ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301",
      "support":support,
      "bootstrap":{"unit":"grid_x_trapping_bout","n_replicates":REPS,
                   "seed":SEED,"smoothing":"(observed+0.5)/(expected+0.5) for log contrasts",
                   "date_shuffle_strata":"grid x trap x bout x check pair"},
      "full":audit(trans,False),
      "exact_three_night_bouts":audit(trans,True),
      "claim_boundary":{
         "identifies_causal_community_interactions":False,
         "time_varying_biological_hierarchy_proven":False,
         "formal_confirmatory_test":False,
         "interpretation":"This post-result block bootstrap quantifies whether inferred within-night directional changes exceed sampling uncertainty. A shifted ranking alone is not evidence of a time-varying biological dominance hierarchy."
       }
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "schema":result["schema"],
      "status":result["status"],
      "support":support,
      "full_focal":result["full"]["focal"],
      "full_KR_LAPM_interval_difference":result["full"]["KR_to_LAPM_interval_logOE_difference"],
      "full_dyad_agreement":result["full"]["directional_dyad_agreement"],
      "exact3_KR_LAPM_interval_difference":result["exact_three_night_bouts"]["KR_to_LAPM_interval_logOE_difference"],
      "exact3_dyad_agreement":result["exact_three_night_bouts"]["directional_dyad_agreement"]
     },indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
