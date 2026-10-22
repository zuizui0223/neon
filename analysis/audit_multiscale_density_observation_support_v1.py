#!/usr/bin/env python3
"""Post-result observation-support audit for the frozen development fit.

This audit does not change, rescue, or re-fit the primary ecological result.
It quantifies a predeclared observation-process concern: whether the fraction
of individuals eligible for W/B changes systematically with genus-level MNKA.

The same frozen analysis rows and nuisance adjustment are used only to describe
selection/support variables. No new inclusion threshold is introduced.
"""
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

from analysis.multiscale_density_fixed_effects_v1 import fit_slope
from analysis.run_multiscale_density_development_fit_v1 import (
    FROZEN_GENERA,
    run as run_development,
)

ROOT = Path(__file__).resolve().parents[1]
FROZEN_RESULT = ROOT / "results" / "multiscale_density_development_result_v1.json"
OUT = ROOT / "build" / "multiscale_density_observation_support_audit_v1.json"
TOL = 1e-8


def _summary(values: list[float]) -> dict:
    x = sorted(float(v) for v in values)
    if not x:
        return {"n": 0}
    def q(p: float) -> float:
        if len(x) == 1:
            return x[0]
        pos = (len(x) - 1) * p
        lo = int(pos)
        hi = min(lo + 1, len(x) - 1)
        f = pos - lo
        return x[lo] * (1 - f) + x[hi] * f
    return {
        "n": len(x),
        "min": x[0],
        "q10": q(0.10),
        "median": statistics.median(x),
        "q90": q(0.90),
        "max": x[-1],
    }


def _fit(rows: list[dict], response: str, genus_balanced: bool = True) -> dict:
    fit = fit_slope(
        rows,
        response=response,
        nuisance=("series_id", "site_month", "year"),
        genus_balanced=genus_balanced,
    )
    return {
        "beta_per_mnka": fit.beta,
        "se_two_way_cluster": fit.se_two_way_cluster,
        "n": fit.n,
        "genus_clusters": fit.genus_clusters,
        "site_clusters": fit.site_clusters,
    }


def _genus_fits(rows: list[dict], response: str) -> list[dict]:
    out = []
    for genus in FROZEN_GENERA:
        sub = [row for row in rows if row["genus"] == genus]
        try:
            fit = fit_slope(
                sub,
                response=response,
                nuisance=("series_id", "site_month", "year"),
                genus_balanced=False,
            )
            adjustment = "series+site_month+year"
        except ValueError:
            fit = fit_slope(
                sub,
                response=response,
                nuisance=("series_id",),
                genus_balanced=False,
            )
            adjustment = "series_only_fallback"
        out.append({
            "genus": genus,
            "beta_per_mnka": fit.beta,
            "sessions": len(sub),
            "sites": len({row["site"] for row in sub}),
            "adjustment": adjustment,
        })
    return out


def run() -> dict:
    frozen = json.loads(FROZEN_RESULT.read_text(encoding="utf-8"))
    dev = run_development()

    observed_primary = float(dev["model"]["primary_delta"]["beta"])
    frozen_primary = float(frozen["primary"]["delta_beta_m2_per_mnka"])
    if abs(observed_primary - frozen_primary) > TOL:
        raise RuntimeError(
            f"development result drifted: {observed_primary} vs {frozen_primary}"
        )

    rows = dev["analysis_rows"]
    if len(rows) != int(frozen["support"]["analysis_sessions"]):
        raise RuntimeError("analysis-session count drifted")

    enriched = []
    for row in rows:
        unique = int(row["unique_tagged_individuals"])
        coord = int(row["coordinate_supported_individuals"])
        repeat_struct = int(row["repeat_supported_individuals_structural"])
        metric_n = int(row["n_individuals"])
        if unique <= 0:
            raise RuntimeError("nonpositive unique-tagged denominator")
        enriched.append({
            **row,
            "coordinate_supported_fraction": coord / unique,
            "repeat_supported_fraction_check": repeat_struct / unique,
            "metric_cohort_fraction": metric_n / unique,
            "metric_minus_structural_repeat": metric_n - repeat_struct,
        })

    # Confirm the carried structural fraction is internally identical.
    max_fraction_error = max(
        abs(
            float(row["repeat_supported_fraction"])
            - float(row["repeat_supported_fraction_check"])
        )
        for row in enriched
    )
    if max_fraction_error > TOL:
        raise RuntimeError(
            f"repeat-supported fraction mismatch: {max_fraction_error}"
        )

    responses = [
        "unique_tagged_individuals",
        "coordinate_supported_individuals",
        "repeat_supported_individuals_structural",
        "n_individuals",
        "coordinate_supported_fraction",
        "repeat_supported_fraction",
        "metric_cohort_fraction",
        "all_capture_trap_night_fraction",
    ]

    primary_fits = {name: _fit(enriched, name) for name in responses}
    unweighted_fits = {
        name: _fit(enriched, name, genus_balanced=False)
        for name in (
            "repeat_supported_fraction",
            "metric_cohort_fraction",
            "n_individuals",
        )
    }

    genus_repeat_fraction = _genus_fits(
        enriched, "repeat_supported_fraction"
    )
    genus_metric_fraction = _genus_fits(
        enriched, "metric_cohort_fraction"
    )

    by_genus = defaultdict(list)
    for row in enriched:
        by_genus[row["genus"]].append(row)

    genus_summaries = []
    for genus in FROZEN_GENERA:
        sub = by_genus[genus]
        genus_summaries.append({
            "genus": genus,
            "sessions": len(sub),
            "sites": len({row["site"] for row in sub}),
            "mnka": _summary([row["mnka"] for row in sub]),
            "repeat_supported_fraction": _summary(
                [row["repeat_supported_fraction"] for row in sub]
            ),
            "metric_cohort_fraction": _summary(
                [row["metric_cohort_fraction"] for row in sub]
            ),
            "metric_cohort_size": _summary(
                [row["n_individuals"] for row in sub]
            ),
        })

    metric_loss = [
        row["repeat_supported_individuals_structural"] - row["n_individuals"]
        for row in enriched
    ]

    return {
        "schema": "neon.multiscale_density.observation_support_audit.v1",
        "date": "2026-10-06",
        "status": "POST_RESULT_RELIABILITY_DIAGNOSTIC_ONLY",
        "frozen_primary_result": str(FROZEN_RESULT.relative_to(ROOT)),
        "primary_result_reestimated_or_changed": False,
        "support": {
            "analysis_sessions": len(enriched),
            "genera": len({row["genus"] for row in enriched}),
            "sites": len({row["site"] for row in enriched}),
            "max_carried_fraction_identity_error": max_fraction_error,
        },
        "distributions": {
            "unique_tagged_individuals": _summary(
                [row["unique_tagged_individuals"] for row in enriched]
            ),
            "repeat_supported_individuals": _summary(
                [row["repeat_supported_individuals_structural"] for row in enriched]
            ),
            "metric_cohort_size": _summary(
                [row["n_individuals"] for row in enriched]
            ),
            "repeat_supported_fraction": _summary(
                [row["repeat_supported_fraction"] for row in enriched]
            ),
            "metric_cohort_fraction": _summary(
                [row["metric_cohort_fraction"] for row in enriched]
            ),
            "metric_individuals_lost_after_strict_coordinate_qc": _summary(
                metric_loss
            ),
        },
        "genus_balanced_within_series_slopes": primary_fits,
        "unweighted_within_series_sensitivities": unweighted_fits,
        "genus_specific_repeat_supported_fraction_slopes": genus_repeat_fraction,
        "genus_specific_metric_cohort_fraction_slopes": genus_metric_fraction,
        "genus_summaries": genus_summaries,
        "interpretation_boundary": {
            "purpose": (
                "quantify whether W/B observation support changes with MNKA; "
                "this audit cannot alter the frozen ecological guard or select "
                "a new adjustment variable"
            ),
            "no_new_pass_fail_threshold": True,
            "forbidden_uses": [
                "lower or raise the structural m threshold",
                "change the primary abundance predictor",
                "add repeat-supported fraction as a post-hoc primary covariate",
                "drop genera because their support fraction changes with MNKA",
                "reclassify the failed 6/8 generality guard as passed",
            ],
        },
    }


def main() -> int:
    result = run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "support": result["support"],
        "distributions": result["distributions"],
        "genus_balanced_within_series_slopes": result[
            "genus_balanced_within_series_slopes"
        ],
        "genus_specific_repeat_supported_fraction_slopes": result[
            "genus_specific_repeat_supported_fraction_slopes"
        ],
        "interpretation_boundary": result["interpretation_boundary"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
