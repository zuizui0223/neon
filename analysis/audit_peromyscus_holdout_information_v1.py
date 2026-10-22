#!/usr/bin/env python3
"""Post-result inferential information audit for NEON Peromyscus.

This evaluates whether the original positive RELEASE-2026 Δ slope is excluded
by the first 2025-2026 provisional event-heldout confidence interval. It is
NOT an equivalence test, is NOT independent animals (230 tags cross release
boundaries), and is NOT an ecological temporal regime-change test.

Uses immutable already-inspected source artifacts; no NEON API/downloads.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from analysis.multiscale_density_fixed_effects_v1 import (
    _design, _residualize, fit_slope,
)
from analysis.audit_peromyscus_site_uncertainty_v1 import site_sandwich

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_DEV_N=956
EXPECTED_FUTURE_N=127
EXPECTED_DEV_BETA=15.93005706925735
EXPECTED_NEW_BETA=-7.072964939150511
TOL=1e-7
NUISANCE=("series_id","site_month","year")


def information(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("no rows in information audit")
    x=np.asarray([float(r["mnka"]) for r in rows])
    y=np.asarray([float(r["D_m2"]) for r in rows])
    z=_design(rows,NUISANCE)
    xr,rank=_residualize(x,z,np.ones(len(rows)))
    yr,_=_residualize(y,z,np.ones(len(rows)))
    ss=float(xr@xr)
    if ss<=1e-10: raise ValueError("not enough within-design MNKA variation")
    beta=float((xr@yr)/ss)
    error=yr-beta*xr
    df=len(rows)-rank-1
    if df<2:raise ValueError("insufficient model residual degrees of freedom")
    return {
        "sessions":len(rows),
        "sites":len({r["site"] for r in rows}),
        "taxon_plot_series":len({r["series_id"] for r in rows}),
        "nuisance_rank":rank,
        "residual_df":df,
        "mnka_min":int(min(x)),"mnka_max":int(max(x)),
        "mnka_residual_sum_squares":ss,
        "mnka_residual_information_root":math.sqrt(ss),
        "mnka_residual_SD":math.sqrt(ss/(len(rows)-1)),
        "model_residual_RMSE":math.sqrt(float(error@error)/df),
        "beta_D_MNKA":beta,
    }


def audit(development, metrics, predictors):
    # Reproduce the same strict 287-key artifact join used BEFORE heldout effects.
    from analysis.run_future_neon_provisional_holdout_v1 import (
        join_sealed_rows,temporal_series_subset,
    )
    if len(development)!=1326:raise RuntimeError("frozen 1326 response cohort drift")
    dev=[r for r in development if r["genus"]=="Peromyscus"]
    new_all=join_sealed_rows(metrics,predictors,{"status":"FUTURE_METRIC_QC_PASS"})
    new=[r for r in temporal_series_subset(new_all) if r["genus"]=="Peromyscus"]
    if len(dev)!=EXPECTED_DEV_N or len(new)!=EXPECTED_FUTURE_N:
        raise RuntimeError("fixed old/new Peromyscus cohort drift")
    d=information(dev)
    n=information(new)
    if abs(d["beta_D_MNKA"]-EXPECTED_DEV_BETA)>TOL:
        raise RuntimeError("original development Δ slope drift")
    if abs(n["beta_D_MNKA"]-EXPECTED_NEW_BETA)>TOL:
        raise RuntimeError("new provisional Δ slope drift")
    d_se=site_sandwich(dev,"D_m2")
    n_se=site_sandwich(new,"D_m2")
    from scipy.stats import t,nct
    df=n["sites"]-1
    crit=float(t.ppf(.975,df))
    ci=[n["beta_D_MNKA"]-crit*n_se["se_site_cluster"],
        n["beta_D_MNKA"]+crit*n_se["se_site_cluster"]]
    se=n_se["se_site_cluster"]
    oldbeta=d["beta_D_MNKA"]
    if se<=0:raise RuntimeError("no estimable site-cluster uncertainty")
    # Conditional on the empirical (post-outcome) standard error and a
    # guessed true slope equal to the exploratory development point slope.
    # These are design-diagnostic benchmarks, not prospectively achieved power.
    from statistics import NormalDist
    norm=NormalDist()
    mde80=(crit+norm.inv_cdf(.8))*se
    signal=oldbeta/se
    conditional_two_sided_power=float(
        nct.cdf(-crit,df,signal)+nct.sf(crit,df,signal))
    sign_negative_if_oldtrue=norm.cdf(-signal)
    return {
        "schema":"neon.peromyscus_holdout_information_compatibility.v1",
        "date":"2026-10-11",
        "status":"POST_RESULT_DESIGN_PRECISION_DIAGNOSTIC_NO_ECOLOGICAL_RESCUE",
        "source": {
            "development_geometry_workflow":37793401501,
            "future_metric_only_workflow":38046250920,
            "future_MNKA_manifest_workflow":38046339017,
            "first_prospective_provisional_holdout_workflow":38046615310,
        },
        "development":d,
        "future_provisional":n,
        "post_result_precision": {
            "development_site_cluster_CR1_se":d_se["se_site_cluster"],
            "future_site_cluster_CR1_se":se,
            "future_sites":n["sites"],
            "future_site_cluster_t_df":df,
            "future_beta95_t_interval":ci,
            "development_point_slope_inside_future_interval":
                ci[0]<=oldbeta<=ci[1],
            "raw_MNKA_information_ratio_future_to_development":
                n["mnka_residual_sum_squares"]/d["mnka_residual_sum_squares"],
            "future_to_development_point_slope_difference":
                n["beta_D_MNKA"]-oldbeta,
            "normal_approx_80pct_MDE_at_post_result_future_SE":mde80,
            "old_exploratory_beta_divided_by_future_SE":signal,
            "conditional_detectability_of_old_point_effect":conditional_two_sided_power,
            "conditional_probability_of_negative_estimate_if_old_beta_true_normal_approx":
                sign_negative_if_oldtrue,
            "power_interpretation_boundary":
                "Power calculations plug in the already observed provisional SE and "
                "selected development slope. They are explanatory benchmarks, "
                "NOT genuine pre-data study power or an endorsement of the old effect.",
        },
        "ecology_decision": {
            "new_beta_direction_matches_development":False,
            "new_data_precisely_exclude_old_effect":False,
            "temporal_shift_identified":False,
            "original_6_of_8_genus_guard":"FAILED_UNCHANGED",
            "original_5_genus_future_mode_test":"NOT_ESTIMABLE",
            "interpretation":
                "The future point estimate is negative whereas development is "
                "positive, but the new period has only about 6% of the residual "
                "MNKA information and the future interval includes the original "
                "positive effect. Failure of sign replication cannot be read as "
                "evidence of an opposing ecological space-use mechanism.",
        },
        "no_new_habitat_taxon_year_subgroup_selected":True,
        "source_still_provisional":True,
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--development",type=Path,required=True)
    p.add_argument("--future-metric",type=Path,required=True)
    p.add_argument("--future-mnka",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    v=p.parse_args()
    try:
        result=audit(
            json.loads(v.development.read_text()),
            json.loads(v.future_metric.read_text()),
            json.loads(v.future_mnka.read_text()))
    except (RuntimeError,ValueError) as e:
        result={
            "schema":"neon.peromyscus_holdout_information_compatibility.v1",
            "status":"STOP_FROZEN_SOURCE_OR_DESIGN_DRIFT",
            "error":str(e),
            "ecological_success_claim":False}
    v.output.parent.mkdir(parents=True,exist_ok=True)
    v.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    if result["status"]!="POST_RESULT_DESIGN_PRECISION_DIAGNOSTIC_NO_ECOLOGICAL_RESCUE":
        raise SystemExit(3)
