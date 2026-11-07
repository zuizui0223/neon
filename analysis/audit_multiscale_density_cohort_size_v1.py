#!/usr/bin/env python3
"""Post-result, capture-cohort-size sensitivity of frozen NEON W/B model.

Inputs are the already-published 1326-session centroid geometry artifact
generated from RELEASE-2026; no new NEON response or source-data download.
This cannot rescue or modify the failed primary 6/8 genus generality test.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
import numpy as np
from analysis.multiscale_density_fixed_effects_v1 import _design, _residualize, fit_slope

ROOT=Path(__file__).resolve().parents[1]
TOL=1e-8
EXPECTED_N=1326
EXPECTED_DELTA=9.37176547246767
FROZEN_GENERA=[
    "Chaetodipus","Dipodomys","Microtus","Myodes",
    "Napaeozapus","Onychomys","Peromyscus","Sigmodon",
]
RESPONSES=("W_m2","B_debiased_m2","D_m2")


def adjusted_slope(rows:list[dict], response:str, *, balanced:bool) -> dict:
    if len(rows)<10:
        raise ValueError("insufficient sessions")
    y=np.asarray([float(r[response]) for r in rows])
    x=np.asarray([float(r["mnka"]) for r in rows])
    m=np.asarray([float(r["m"]) for r in rows])
    Z=_design(rows,("series_id","site_month","year"))
    counts=Counter(str(r["genus"]) for r in rows)
    w=np.asarray([1/counts[str(r["genus"])] for r in rows]) if balanced else np.ones(len(rows))
    sw=np.sqrt(w)
    residualized=[]
    nuisance_rank=None
    for a in (x,m,y):
        v,rank=_residualize(a,Z,w)
        residualized.append(v)
        nuisance_rank=rank
    rx,rm,ry=residualized
    X=np.column_stack((rx,rm))
    coefficients, _, rank, _=np.linalg.lstsq(X*sw[:,None],ry*sw,rcond=None)
    if rank != 2:
        raise ValueError("MNKA and cohort m cannot be independently estimated")
    beta_n,beta_m=map(float,coefficients)
    residual=ry-X@coefficients
    bread=np.linalg.inv(X.T@(w[:,None]*X))
    scores=w[:,None]*X*residual[:,None]
    def meat(keys):
        sums={}
        for k,v in zip(keys,scores):
            sums[k]=sums.get(k,np.zeros(2))+v
        return sum((np.outer(v,v) for v in sums.values()),np.zeros((2,2)))
    site=[r["site"] for r in rows]
    genus=[r["genus"] for r in rows]
    if balanced:
        sandwich=meat(site)+meat(genus)-meat(list(zip(site,genus)))
        method="site+genus-intersection two-way cluster, uncorrected descriptive"
    else:
        sandwich=meat(site)
        method="site-only cluster, uncorrected descriptive"
    variance=bread@sandwich@bread
    se=float(np.sqrt(variance[0,0])) if variance[0,0]>=0 else None
    return {"n":len(rows),"sites":len(set(site)),"genera":len(counts),
            "beta_MNKA":beta_n,"beta_m":beta_m,"se_MNKA_cluster_unadjusted":se,
            "cluster_covariance_method":method,"nuisance_rank":nuisance_rank,
            "state":"POST_RESULT_SENSITIVITY_NOT_CONFIRMATORY"}


def run(rows:list[dict]) -> dict:
    if len(rows)!=EXPECTED_N:
        raise RuntimeError(f"frozen cohort size drift: {len(rows)} != {EXPECTED_N}")
    if set(r["genus"] for r in rows)!=set(FROZEN_GENERA):
        raise RuntimeError("unexpected frozen genus roster")
    frozen=fit_slope(rows,response="D_m2",genus_balanced=True)
    if abs(frozen.beta-EXPECTED_DELTA)>TOL:
        raise RuntimeError("primary frozen coefficient no longer matches")
    for r in rows:
        if abs(float(r["D_m2"])-(float(r["B_debiased_m2"])-float(r["W_m2"])))>TOL:
            raise RuntimeError("D = B - W violation")

    result={}
    for resp in RESPONSES:
        base=fit_slope(rows,response=resp,genus_balanced=True)
        adj=adjusted_slope(rows,resp,balanced=True)
        result[resp]={"original_beta_MNKA":base.beta,"posthoc_m_adjusted":adj}
    adjusted_diff=(result["B_debiased_m2"]["posthoc_m_adjusted"]["beta_MNKA"]
                   -result["W_m2"]["posthoc_m_adjusted"]["beta_MNKA"])
    if abs(adjusted_diff-result["D_m2"]["posthoc_m_adjusted"]["beta_MNKA"])>TOL:
        raise RuntimeError("adjusted Delta identity failed")
    gen={}
    for genus in FROZEN_GENERA:
        sub=[r for r in rows if r["genus"]==genus]
        if len(sub)<30 or len({r["site"] for r in sub})<3:
            gen[genus]={"n":len(sub),"status":"INSUFFICIENT_MULTISITE_SUPPORT"}
        else:
            try:
                base=fit_slope(sub,response="D_m2",genus_balanced=False)
                adj=adjusted_slope(sub,"D_m2",balanced=False)
                gen[genus]={"n":len(sub),"sites":len({r["site"] for r in sub}),
                            "original_D_beta":base.beta,"posthoc_m_adjusted_D":adj}
            except ValueError as exc:
                gen[genus]={"n":len(sub),"status":"NO_ADJUSTED_ESTIMATE","reason":str(exc)}
    return {
        "schema":"neon.multiscale_density.cohort_size_sensitivity.v1",
        "status":"POST_RESULT_EXPLORATORY",
        "source":"RELEASE-2026 frozen 1326-session geometry artifact from workflow 37793401501",
        "original_general_6_of_8_guard":"FAILED_UNCHANGED",
        "n":len(rows),"source_delta_exactly_reproduced":frozen.beta,
        "response_slopes":result,
        "adjusted_delta_identity":adjusted_diff,
        "genus_descriptive":gen,
        "interpretation_limit":(
            "m is repeat-capture-selected and may be a mediator or collider; "
            "conditioning on m does not distinguish detection bias from animal behavior. "
            "This analysis was introduced AFTER MNKA and W/B effects were observed."
        ),
        "biological_status":"DESCRIPTIVE_ONLY_NO_TERRITORIAL_OR_ADAPTIVE_MECHANISM",
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--sessions",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    result=run(json.loads(args.sessions.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
