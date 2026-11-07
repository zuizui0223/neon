#!/usr/bin/env python3
"""Post-result, site-cluster uncertainty audit from previously generated artifact.

No NEON data download; no ecological reclassification or prospective claim.
Uses exact frozen covariate design; a one-genus-only site sandwich replaces
the inappropriate two-way genus x site covariance (genus has one cluster).
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from analysis.multiscale_density_fixed_effects_v1 import _design, _residualize, fit_slope

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "results/multiscale_density_centroid_geometry_exploratory_result_v1.json"
EXPECTED = {
    "nn_excess_xy_m2": 2.5574127652829035,
    "nn_excess_series_m2": 4.1715808096880975,
}
TOL = 1e-8


def site_sandwich(rows: list[dict], response: str, extra_controls: tuple[str, ...] = ()) -> dict:
    """Descriptive site-cluster sandwich with normal-approx 95% interval.

    This is not a confirmatory p-value or a causal effect interval; the genus
    and both null baselines were chosen after inspecting development effects.
    """
    a = [r for r in rows if r.get(response) is not None and all(r.get(k) is not None for k in extra_controls)]
    if len(a) < 80:
        raise ValueError("insufficient support")
    sites = sorted({r["site"] for r in a})
    g = len(sites)
    if g < 10:
        raise ValueError("fewer than ten site clusters")

    n = len(a)
    x = np.asarray([float(r["mnka"]) for r in a])
    y = np.asarray([float(r[response]) for r in a])
    Z = _design(a, ("series_id", "site_month", "year"))
    if extra_controls:
        Z = np.column_stack([Z] + [np.asarray([float(r[k]) for r in a]) for k in extra_controls])
    w = np.ones(n, dtype=float)
    xr, rank_x = _residualize(x, Z, w)
    yr, rank_y = _residualize(y, Z, w)
    rank = max(rank_x, rank_y)
    sxx = float(np.sum(xr * xr))
    if sxx <= 1e-10:
        raise ValueError("nonidentified abundance slope")
    beta = float(np.dot(xr, yr) / sxx)
    residual = yr - beta * xr
    score = xr * residual
    by_site = defaultdict(float)
    for r, s in zip(a, score):
        by_site[r["site"]] += float(s)
    factor = (g / (g - 1)) * ((n - 1) / (n - rank - 1))
    variance = factor * sum(v * v for v in by_site.values()) / (sxx*sxx)
    se = math.sqrt(max(0.0, variance))
    z = 1.96
    return {
        "n": n, "sites": g, "series": len({r["series_id"] for r in a}),
        "nuisance_rank": rank, "beta": beta,
        "se_site_cluster": se,
        "ci95_normal_approx": [beta-z*se, beta+z*se],
        "ci_method": "site clustered CR1 sandwich, normal approximation",
        "posthoc_selection_warning": True,
        "posthoc_numeric_controls": list(extra_controls),
    }


def abundance_level_summaries(rows: list[dict]) -> dict:
    """Plain descriptive levels of NN excess by within-series MNKA order.

    Observed E>0 is still NOT evidence of calibrated biological repulsion.
    Ties are kept in the middle; unlike a regression this is not adjusted.
    """
    by_series=defaultdict(list)
    for r in rows:
        if r["genus"] == "Peromyscus":
            by_series[r["series_id"]].append(r)
    low=[];high=[]
    for series, arr in by_series.items():
        ns=sorted({int(r["mnka"]) for r in arr})
        if len(ns) < 2: continue
        lo=ns[(len(ns)-1)//3]
        hi=ns[(len(ns)*2)//3]
        for r in arr:
            if int(r["mnka"]) <= lo: low.append(r)
            if int(r["mnka"]) >= hi: high.append(r)
    out={}
    for v in EXPECTED:
        def stats(a):
            vv=[float(r[v]) for r in a if r.get(v) is not None]
            return {
                "n":len(vv),
                "mean_excess_m2":sum(vv)/len(vv) if vv else None,
                "fraction_excess_gt_zero":sum(x>0 for x in vv)/len(vv) if vv else None,
            }
        out[v]={"lower_within_series_mnka":stats(low),
                "upper_within_series_mnka":stats(high)}
    return out


def run(rows: list[dict]) -> dict:
    frozen=json.loads(FROZEN.read_text(encoding="utf-8"))
    if len(rows) != 1326:
        raise RuntimeError("1326-session frozen geometry cohort drift")
    p=[r for r in rows if r["genus"]=="Peromyscus"]
    if len(p)!=956 or len({r["site"] for r in p})!=33:
        raise RuntimeError("Peromyscus support drift")
    fits={}
    for response,expected in EXPECTED.items():
        beta=fit_slope(p if response=="nn_excess_xy_m2" else
                       [r for r in p if r.get(response) is not None],
                       response=response,
                       nuisance=("series_id","site_month","year"),
                       genus_balanced=False).beta
        if abs(beta-expected)>TOL:
            raise RuntimeError(f"source slope mismatch {response} {beta} vs {expected}")
        fits[response]=site_sandwich(p,response)
        if abs(fits[response]["beta"]-expected)>TOL:
            raise RuntimeError("site covariance check changed fixed slope")
    # Added after the initial Peromyscus effect was opened. This check
    # deliberately controls the number of repeat-supported individuals m,
    # which rises with MNKA and mechanically changes nearest-neighbor spacing.
    # m is partly a product of detection and can be a mediator/collider:
    # these are associational sensitivities, not causal mediation fits.
    controls = {}
    for response in ("nn_squared_m2", *EXPECTED):
        controls[response] = {
            "unadjusted": site_sandwich(p, response),
            "m_adjusted": site_sandwich(p, response, ("m",)),
            "m_B_adjusted": site_sandwich(p, response, ("m", "B_observed_m2")),
        }
        for variant, data in controls[response].items():
            if not all(math.isfinite(data[k]) for k in ("beta","se_site_cluster")):
                raise RuntimeError(f"nonfinite {response} {variant}")
    return {
        "schema":"neon.multiscale_density.peromyscus_site_uncertainty_v1",
        "status":"POST_RESULT_DESCRIPTIVE_SAME_RELEASE2026_DATA",
        "source_run":37793401501,
        "geometry_rows":len(rows),"peromyscus_sessions":len(p),
        "validation":"EXACTLY_REPRODUCED_BOTH_FROZEN_SLOPES",
        "site_cluster_uncertainty":fits,
        "posthoc_cohort_size_sensitivity": controls,
        "cohort_size_scope": "m is capture-selected and adjusts a possible artefact; controlling for m does not identify causal density effects",
        "abundance_level_summaries":abundance_level_summaries(p),
        "claim_boundary":"Not independent, not causal, and raw levels are not a validated spatial-repulsion test.",
    }


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--sessions",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    rows=json.loads(args.sessions.read_text(encoding="utf-8"))
    result=run(rows)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
