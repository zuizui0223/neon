#!/usr/bin/env python3
"""Pure fixed-effects estimators for the frozen multiscale-density model.

No NEON data access occurs here. The model is deliberately simple:
Frisch-Waugh-Lovell residualization against frozen categorical nuisance terms,
followed by a single weighted slope. Primary weights give each frozen genus
equal total weight.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from math import sqrt
from typing import Iterable, Sequence

import numpy as np


@dataclass(frozen=True)
class SlopeFit:
    beta: float
    se_two_way_cluster: float | None
    n: int
    residual_predictor_ss: float
    genus_clusters: int
    site_clusters: int
    nuisance_rank: int


def _design(rows: Sequence[dict], nuisance: Sequence[str]) -> np.ndarray:
    """Build intercept + treatment-coded categorical nuisance matrix."""
    n = len(rows)
    cols = [np.ones(n, dtype=float)]
    for key in nuisance:
        levels = sorted({str(row[key]) for row in rows})
        for level in levels[1:]:
            cols.append(
                np.asarray([1.0 if str(row[key]) == level else 0.0 for row in rows])
            )
    return np.column_stack(cols)


def _weights(rows: Sequence[dict], genus_balanced: bool) -> np.ndarray:
    if not genus_balanced:
        return np.ones(len(rows), dtype=float)
    counts = Counter(str(row["genus"]) for row in rows)
    if not counts:
        raise ValueError("no genus labels")
    return np.asarray([1.0 / counts[str(row["genus"])] for row in rows], dtype=float)


def _residualize(v: np.ndarray, Z: np.ndarray, w: np.ndarray) -> tuple[np.ndarray, int]:
    sw = np.sqrt(w)
    Zw = Z * sw[:, None]
    vw = v * sw
    coef, *_ = np.linalg.lstsq(Zw, vw, rcond=None)
    fitted = Z @ coef
    rank = int(np.linalg.matrix_rank(Zw))
    return v - fitted, rank


def _cluster_meat(scores: np.ndarray, keys: Sequence[object]) -> float:
    sums: dict[object, float] = defaultdict(float)
    for score, key in zip(scores, keys):
        sums[key] += float(score)
    return sum(v * v for v in sums.values())


def fit_slope(
    rows: Sequence[dict],
    *,
    response: str,
    predictor: str = "mnka",
    nuisance: Sequence[str] = ("series_id", "site_month", "year"),
    genus_balanced: bool = True,
) -> SlopeFit:
    if len(rows) < 3:
        raise ValueError("at least three rows are required")
    y = np.asarray([float(row[response]) for row in rows], dtype=float)
    x = np.asarray([float(row[predictor]) for row in rows], dtype=float)
    if not np.all(np.isfinite(y)) or not np.all(np.isfinite(x)):
        raise ValueError("non-finite model value")

    w = _weights(rows, genus_balanced)
    Z = _design(rows, nuisance)
    xr, rank_x = _residualize(x, Z, w)
    yr, rank_y = _residualize(y, Z, w)
    nuisance_rank = max(rank_x, rank_y)

    sxx = float(np.sum(w * xr * xr))
    if not np.isfinite(sxx) or sxx <= 1e-10:
        raise ValueError("predictor has no residual variation after nuisance adjustment")
    beta = float(np.sum(w * xr * yr) / sxx)
    resid = yr - beta * xr

    # Two-way cluster sandwich sensitivity. With a scalar residualized regressor,
    # bread = 1 / sum(w*x^2), and each cluster score is sum(w*x*u).
    scores = w * xr * resid
    genus_keys = [str(row["genus"]) for row in rows]
    site_keys = [str(row["site"]) for row in rows]
    intersection_keys = list(zip(genus_keys, site_keys))
    meat = (
        _cluster_meat(scores, genus_keys)
        + _cluster_meat(scores, site_keys)
        - _cluster_meat(scores, intersection_keys)
    )
    variance = meat / (sxx * sxx)
    se = sqrt(max(0.0, variance)) if np.isfinite(variance) else None

    return SlopeFit(
        beta=beta,
        se_two_way_cluster=se,
        n=len(rows),
        residual_predictor_ss=sxx,
        genus_clusters=len(set(genus_keys)),
        site_clusters=len(set(site_keys)),
        nuisance_rank=nuisance_rank,
    )


def genus_specific_slopes(
    rows: Sequence[dict],
    *,
    response: str,
    frozen_genera: Sequence[str],
) -> list[dict]:
    out = []
    for genus in frozen_genera:
        subset = [row for row in rows if str(row["genus"]) == genus]
        if not subset:
            out.append({"genus": genus, "status": "missing"})
            continue
        try:
            fit = fit_slope(
                subset,
                response=response,
                nuisance=("series_id", "site_month", "year"),
                genus_balanced=False,
            )
            adjustment = "series+site_month+year"
        except ValueError:
            fit = fit_slope(
                subset,
                response=response,
                nuisance=("series_id",),
                genus_balanced=False,
            )
            adjustment = "series_only_fallback"
        out.append({
            "genus": genus,
            "status": "fit",
            "beta": fit.beta,
            "n": fit.n,
            "sites": len({str(row["site"]) for row in subset}),
            "adjustment": adjustment,
        })
    return out


def leave_one_genus_out(
    rows: Sequence[dict],
    *,
    response: str,
    frozen_genera: Sequence[str],
) -> list[dict]:
    out = []
    for genus in frozen_genera:
        subset = [row for row in rows if str(row["genus"]) != genus]
        fit = fit_slope(subset, response=response, genus_balanced=True)
        out.append({
            "left_out_genus": genus,
            "beta": fit.beta,
            "n": fit.n,
        })
    return out


def evaluate_frozen_model(
    rows: Sequence[dict],
    *,
    frozen_genera: Sequence[str],
) -> dict:
    allowed = set(frozen_genera)
    rows = [row for row in rows if str(row["genus"]) in allowed]
    if not rows:
        raise ValueError("no rows in frozen genera")

    primary = fit_slope(rows, response="D_m2", genus_balanced=True)
    beta_w = fit_slope(rows, response="W_m2", genus_balanced=True)
    beta_b = fit_slope(rows, response="B_debiased_m2", genus_balanced=True)

    genus_delta = genus_specific_slopes(
        rows, response="D_m2", frozen_genera=frozen_genera
    )
    fitted_genus = [x for x in genus_delta if x.get("status") == "fit"]
    positive_genera = sum(float(x["beta"]) > 0 for x in fitted_genus)

    loo = leave_one_genus_out(
        rows, response="D_m2", frozen_genera=frozen_genera
    )
    all_loo_positive = all(float(x["beta"]) > 0 for x in loo)

    unweighted = fit_slope(
        rows, response="D_m2", genus_balanced=False
    )
    raw_b_rows = [
        {**row, "D_raw_m2": float(row["B_observed_m2"]) - float(row["W_m2"])}
        for row in rows
    ]
    raw_b = fit_slope(
        raw_b_rows, response="D_raw_m2", genus_balanced=True
    )
    no_site_month = fit_slope(
        rows,
        response="D_m2",
        nuisance=("series_id", "year"),
        genus_balanced=True,
    )

    development_supported = (
        primary.beta > 0
        and all_loo_positive
        and positive_genera >= 6
    )
    strong_form = beta_w.beta < 0 and beta_b.beta >= 0

    return {
        "primary_delta": {
            "beta": primary.beta,
            "se_two_way_cluster": primary.se_two_way_cluster,
            "n": primary.n,
            "genus_clusters": primary.genus_clusters,
            "site_clusters": primary.site_clusters,
            "nuisance_rank": primary.nuisance_rank,
        },
        "secondary_slopes": {
            "beta_W": beta_w.beta,
            "beta_B_debiased": beta_b.beta,
            "difference_identity_check": beta_b.beta - beta_w.beta,
        },
        "genus_specific_delta": genus_delta,
        "positive_genus_count": positive_genera,
        "frozen_genus_count": len(frozen_genera),
        "leave_one_genus_out": loo,
        "all_leave_one_genus_out_positive": all_loo_positive,
        "sensitivities": {
            "unweighted_delta_beta": unweighted.beta,
            "raw_B_delta_beta": raw_b.beta,
            "no_site_month_delta_beta": no_site_month.beta,
        },
        "decision": {
            "development_cross_scale_support": development_supported,
            "strong_form_supported": development_supported and strong_form,
            "guard": (
                "primary delta > 0 AND every leave-one-genus-out delta > 0 "
                "AND at least 6/8 genus-specific deltas > 0"
            ),
        },
    }
