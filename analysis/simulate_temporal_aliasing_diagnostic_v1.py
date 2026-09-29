"""Simulation benchmark for the temporal positional-aliasing diagnostic.

Used by the unified paper-validation workflow; no empirical data are read here.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

Z95=1.959963984540054

def logistic(x: float) -> float:
    if x>=0:
        z=math.exp(-x)
        return 1/(1+z)
    z=math.exp(x)
    return z/(1+z)

def logit(p: float) -> float:
    if not 0<p<1:
        raise ValueError("p must lie in (0,1)")
    return math.log(p/(1-p))

def wilson(k: int,n: int,z: float=Z95) -> tuple[float,float]:
    if n<=0: raise ValueError("n must be positive")
    p=k/n; z2=z*z; den=1+z2/n
    centre=(p+z2/(2*n))/den
    half=z*math.sqrt((p*(1-p)+z2/(4*n))/n)/den
    return max(0.0,centre-half),min(1.0,centre+half)

def one_replicate(
    rng: random.Random,
    *,
    n: int,
    shift_sigma: float,
    repeat_base: float,
    repeat_beta: float,
    material_scale: float=1.0,
) -> dict:
    latent=[]
    observed=[]
    for _ in range(n):
        dx=rng.gauss(0,shift_sigma)
        dy=rng.gauss(0,shift_sigma)
        span=math.hypot(dx,dy)
        material=span>=material_scale
        latent.append(material)
        p_repeat=logistic(
            logit(repeat_base)
            + repeat_beta*(span/material_scale-1.0)
        )
        if rng.random()<p_repeat:
            observed.append(material)

    true_k=sum(latent)
    true_p=true_k/n
    repeat_n=len(observed)
    repeat_k=sum(observed)
    cond=(repeat_k/repeat_n) if repeat_n else None
    lower=repeat_k/n
    if repeat_n:
        lo,hi=wilson(repeat_k,repeat_n)
        covered=lo<=true_p<=hi
    else:
        lo=hi=None
        covered=None
    return {
        "true_fraction":true_p,
        "repeat_n":repeat_n,
        "repeat_conditioned_fraction":cond,
        "repeat_conditioned_bias":(
            cond-true_p if cond is not None else None
        ),
        "wilson_low":lo,
        "wilson_high":hi,
        "wilson_covers_true":covered,
        "all_night_observed_lower_bound":lower,
        "lower_bound_exceeds_true":lower>true_p+1e-15,
    }

def mean(values):
    xs=[x for x in values if x is not None]
    return sum(xs)/len(xs) if xs else None

def run_cell(
    *,
    seed: int,
    replicates: int,
    n: int,
    shift_sigma: float,
    repeat_base: float,
    repeat_beta: float,
) -> dict:
    rng=random.Random(seed)
    rows=[
        one_replicate(
            rng,n=n,shift_sigma=shift_sigma,
            repeat_base=repeat_base,repeat_beta=repeat_beta,
        )
        for _ in range(replicates)
    ]
    cover=[int(x["wilson_covers_true"]) for x in rows if x["wilson_covers_true"] is not None]
    return {
        "n":n,
        "shift_sigma_over_material_scale":shift_sigma,
        "repeat_base":repeat_base,
        "repeat_beta":repeat_beta,
        "replicates":replicates,
        "mean_true_fraction":mean([x["true_fraction"] for x in rows]),
        "mean_repeat_n":mean([x["repeat_n"] for x in rows]),
        "mean_repeat_conditioned_fraction":mean([x["repeat_conditioned_fraction"] for x in rows]),
        "mean_repeat_conditioned_bias":mean([x["repeat_conditioned_bias"] for x in rows]),
        "wilson_coverage":mean(cover),
        "mean_all_night_observed_lower_bound":mean([x["all_night_observed_lower_bound"] for x in rows]),
        "lower_bound_violation_count":sum(x["lower_bound_exceeds_true"] for x in rows),
        "repeat_empty_count":sum(x["repeat_n"]==0 for x in rows),
    }

def benchmark(seed: int=20260929,replicates: int=400) -> dict:
    cells=[]
    index=0
    for n in (100,500):
        for sigma in (0.25,0.5,1.0,2.0):
            for q in (0.25,0.5,0.75):
                for beta in (-1.0,0.0,1.0):
                    cells.append(run_cell(
                        seed=seed+index*100003,
                        replicates=replicates,
                        n=n,shift_sigma=sigma,
                        repeat_base=q,repeat_beta=beta,
                    ))
                    index+=1

    mcar=[x for x in cells if x["repeat_beta"]==0.0]
    enriched=[x for x in cells if x["repeat_beta"]==1.0]
    depleted=[x for x in cells if x["repeat_beta"]==-1.0]
    return {
        "schema":"temporal_aliasing_diagnostic.simulation_benchmark.v1",
        "seed":seed,
        "replicates_per_cell":replicates,
        "cells":cells,
        "summary":{
            "mcar_mean_abs_bias":mean([abs(x["mean_repeat_conditioned_bias"]) for x in mcar]),
            "mcar_mean_wilson_coverage":mean([x["wilson_coverage"] for x in mcar]),
            "span_enriched_mean_bias":mean([x["mean_repeat_conditioned_bias"] for x in enriched]),
            "span_depleted_mean_bias":mean([x["mean_repeat_conditioned_bias"] for x in depleted]),
            "total_lower_bound_violations":sum(x["lower_bound_violation_count"] for x in cells),
        },
        "claim_boundary":{
            "conditional_fraction_identifies_latent_all_night_fraction_only_under_noninformative_repeat_observation":True,
            "all_night_directly_observed_fraction_is_always_a_lower_bound":True,
        },
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--replicates",type=int,default=400)
    a=ap.parse_args()
    out=benchmark(replicates=a.replicates)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out["summary"],indent=2,sort_keys=True))
if __name__=="__main__": main()
