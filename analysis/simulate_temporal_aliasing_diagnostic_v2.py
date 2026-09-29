"""Corrected simulation benchmark for temporal positional aliasing.

Version 2 separates three targets:
1. the generating all-occasion material-shift probability;
2. the finite realized all-occasion fraction in a simulated dataset;
3. the repeat-observation-conditioned fraction.

Wilson coverage is evaluated against the generating probability. The directly
observed all-occasion fraction is evaluated as a deterministic lower bound on
the realized all-occasion fraction.
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
    if n<=0 or k<0 or k>n:
        raise ValueError("invalid binomial counts")
    p=k/n
    z2=z*z
    den=1+z2/n
    centre=(p+z2/(2*n))/den
    half=z*math.sqrt((p*(1-p)+z2/(4*n))/n)/den
    low=0.0 if k==0 else max(0.0,centre-half)
    high=1.0 if k==n else min(1.0,centre+half)
    return low,high


def latent_material_probability(
    shift_sigma: float,
    material_scale: float=1.0,
) -> float:
    sigma=float(shift_sigma)
    scale=float(material_scale)
    if not math.isfinite(sigma) or sigma<=0:
        raise ValueError("shift_sigma must be finite and positive")
    if not math.isfinite(scale) or scale<=0:
        raise ValueError("material_scale must be finite and positive")
    # dx,dy ~ iid Normal(0,sigma^2): radial span is Rayleigh(sigma).
    return math.exp(-(scale*scale)/(2*sigma*sigma))


def one_replicate(
    rng: random.Random,
    *,
    n: int,
    shift_sigma: float,
    repeat_base: float,
    repeat_beta: float,
    material_scale: float=1.0,
) -> dict:
    latent_probability=latent_material_probability(
        shift_sigma,material_scale
    )
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

    latent_k=sum(latent)
    realized_latent_fraction=latent_k/n
    repeat_n=len(observed)
    repeat_k=sum(observed)
    conditional=repeat_k/repeat_n if repeat_n else None
    directly_observed_all_fraction=repeat_k/n

    if repeat_n:
        lo,hi=wilson(repeat_k,repeat_n)
        covers_probability=lo<=latent_probability<=hi
    else:
        lo=hi=None
        covers_probability=None

    return {
        "latent_probability":latent_probability,
        "realized_latent_fraction":realized_latent_fraction,
        "repeat_n":repeat_n,
        "repeat_conditioned_fraction":conditional,
        "repeat_conditioned_bias_vs_probability":(
            conditional-latent_probability
            if conditional is not None else None
        ),
        "repeat_conditioned_difference_vs_realized_fraction":(
            conditional-realized_latent_fraction
            if conditional is not None else None
        ),
        "wilson_low":lo,
        "wilson_high":hi,
        "wilson_covers_latent_probability":covers_probability,
        "all_night_directly_observed_fraction":
            directly_observed_all_fraction,
        "lower_bound_exceeds_realized_latent_fraction":(
            directly_observed_all_fraction
            > realized_latent_fraction + 1e-15
        ),
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
            rng,
            n=n,
            shift_sigma=shift_sigma,
            repeat_base=repeat_base,
            repeat_beta=repeat_beta,
        )
        for _ in range(replicates)
    ]
    coverage=[
        int(x["wilson_covers_latent_probability"])
        for x in rows
        if x["wilson_covers_latent_probability"] is not None
    ]
    latent_probability=latent_material_probability(shift_sigma)
    return {
        "n":n,
        "shift_sigma_over_material_scale":shift_sigma,
        "repeat_base":repeat_base,
        "repeat_beta":repeat_beta,
        "replicates":replicates,
        "latent_material_shift_probability":latent_probability,
        "mean_realized_latent_fraction":mean(
            [x["realized_latent_fraction"] for x in rows]
        ),
        "mean_repeat_n":mean([x["repeat_n"] for x in rows]),
        "mean_repeat_conditioned_fraction":mean(
            [x["repeat_conditioned_fraction"] for x in rows]
        ),
        "mean_repeat_conditioned_bias_vs_probability":mean(
            [x["repeat_conditioned_bias_vs_probability"] for x in rows]
        ),
        "mean_repeat_conditioned_difference_vs_realized_fraction":mean(
            [
                x["repeat_conditioned_difference_vs_realized_fraction"]
                for x in rows
            ]
        ),
        "wilson_coverage_latent_probability":mean(coverage),
        "mean_all_night_directly_observed_fraction":mean(
            [x["all_night_directly_observed_fraction"] for x in rows]
        ),
        "lower_bound_realized_violation_count":sum(
            x["lower_bound_exceeds_realized_latent_fraction"]
            for x in rows
        ),
        "repeat_empty_count":sum(x["repeat_n"]==0 for x in rows),
    }


def benchmark(seed: int=20260930,replicates: int=400) -> dict:
    cells=[]
    index=0
    for n in (100,500):
        for sigma in (0.25,0.5,1.0,2.0):
            for q in (0.25,0.5,0.75):
                for beta in (-1.0,0.0,1.0):
                    cells.append(
                        run_cell(
                            seed=seed+index*100003,
                            replicates=replicates,
                            n=n,
                            shift_sigma=sigma,
                            repeat_base=q,
                            repeat_beta=beta,
                        )
                    )
                    index+=1

    mcar=[x for x in cells if x["repeat_beta"]==0.0]
    enriched=[x for x in cells if x["repeat_beta"]==1.0]
    depleted=[x for x in cells if x["repeat_beta"]==-1.0]

    mcar_cover=[
        x["wilson_coverage_latent_probability"] for x in mcar
    ]
    return {
        "schema":
            "temporal_aliasing_diagnostic.simulation_benchmark.v2",
        "seed":seed,
        "replicates_per_cell":replicates,
        "cells":cells,
        "summary":{
            "mcar_mean_abs_bias_vs_latent_probability":mean(
                [
                    abs(x["mean_repeat_conditioned_bias_vs_probability"])
                    for x in mcar
                ]
            ),
            "mcar_mean_wilson_coverage_latent_probability":
                mean(mcar_cover),
            "mcar_min_wilson_coverage_latent_probability":
                min(mcar_cover),
            "mcar_max_wilson_coverage_latent_probability":
                max(mcar_cover),
            "span_enriched_mean_bias_vs_latent_probability":mean(
                [
                    x["mean_repeat_conditioned_bias_vs_probability"]
                    for x in enriched
                ]
            ),
            "span_depleted_mean_bias_vs_latent_probability":mean(
                [
                    x["mean_repeat_conditioned_bias_vs_probability"]
                    for x in depleted
                ]
            ),
            "total_lower_bound_realized_violations":sum(
                x["lower_bound_realized_violation_count"]
                for x in cells
            ),
        },
        "target_definition":{
            "wilson_coverage_target":
                "analytic generating probability P(span>=material_scale)",
            "bias_target":
                "analytic generating probability P(span>=material_scale)",
            "lower_bound_target":
                "finite realized all-occasion material-shift fraction",
        },
        "claim_boundary":{
            "conditional_fraction_identifies_generating_probability_only_under_noninformative_repeat_observation":
                True,
            "all_night_directly_observed_fraction_is_a_lower_bound_on_the_realized_all_occasion_fraction":
                True,
        },
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--replicates",type=int,default=400)
    args=parser.parse_args()
    out=benchmark(replicates=args.replicates)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out["summary"],indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
