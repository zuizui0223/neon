#!/usr/bin/env python3
"""Post-result descriptive heterogeneity audit.

This script does not alter or re-evaluate the frozen primary development guard.
It re-runs the frozen development pipeline, verifies the already frozen primary
result, and then describes how W, B, and Delta differ among the eight genera.

The diagnostics cannot be used to drop genera, relax the 6/8 guard, introduce
post-hoc moderators, or relabel the failed generality test as a success.
"""
from __future__ import annotations

import json
from pathlib import Path

from analysis.multiscale_density_fixed_effects_v1 import fit_slope
from analysis.run_multiscale_density_development_fit_v1 import (
    FROZEN_GENERA,
    run as run_development,
)

ROOT = Path(__file__).resolve().parents[1]
FROZEN_RESULT = ROOT / "results" / "multiscale_density_development_result_v1.json"
OUT = ROOT / "build" / "multiscale_density_heterogeneity_diagnostic_v1.json"
TOL = 1e-8


def _fit_genus(rows: list[dict], response: str) -> tuple[float, str]:
    try:
        fit = fit_slope(
            rows,
            response=response,
            nuisance=("series_id", "site_month", "year"),
            genus_balanced=False,
        )
        return fit.beta, "series+site_month+year"
    except ValueError:
        fit = fit_slope(
            rows,
            response=response,
            nuisance=("series_id",),
            genus_balanced=False,
        )
        return fit.beta, "series_only_fallback"


def _same_sign(values: list[float], reference: float) -> bool | None:
    if not values:
        return None
    if reference > 0:
        return all(x > 0 for x in values)
    if reference < 0:
        return all(x < 0 for x in values)
    return all(abs(x) <= TOL for x in values)


def run() -> dict:
    frozen = json.loads(FROZEN_RESULT.read_text(encoding="utf-8"))
    dev = run_development()

    observed_primary = float(dev["model"]["primary_delta"]["beta"])
    frozen_primary = float(frozen["primary"]["delta_beta_m2_per_mnka"])
    if abs(observed_primary - frozen_primary) > TOL:
        raise RuntimeError(
            f"primary result drifted: {observed_primary} vs {frozen_primary}"
        )
    observed_positive = int(dev["model"]["positive_genus_count"])
    frozen_positive = int(
        frozen["preregistered_guard"]["observed_positive_genus_count"]
    )
    if observed_positive != frozen_positive:
        raise RuntimeError(
            f"positive-genus count drifted: {observed_positive} vs {frozen_positive}"
        )

    rows = dev["analysis_rows"]
    diagnostics = []

    for genus in FROZEN_GENERA:
        sub = [row for row in rows if row["genus"] == genus]
        if not sub:
            raise RuntimeError(f"missing frozen genus {genus}")

        delta, adjustment = _fit_genus(sub, "D_m2")
        beta_w, _ = _fit_genus(sub, "W_m2")
        beta_b, _ = _fit_genus(sub, "B_debiased_m2")

        raw_rows = [
            {
                **row,
                "D_raw_m2": float(row["B_observed_m2"]) - float(row["W_m2"]),
            }
            for row in sub
        ]
        delta_raw, _ = _fit_genus(raw_rows, "D_raw_m2")

        sites = sorted({row["site"] for row in sub})
        site_loo = []
        for site in sites:
            kept = [row for row in sub if row["site"] != site]
            if len(kept) < 3:
                continue
            try:
                beta, adj = _fit_genus(kept, "D_m2")
            except ValueError:
                continue
            site_loo.append({
                "left_out_site": site,
                "beta_delta": beta,
                "n": len(kept),
                "adjustment": adj,
            })

        taxon_rows = []
        for taxon in sorted({row["taxon"] for row in sub}):
            trows = [row for row in sub if row["taxon"] == taxon]
            if len(trows) < 3:
                continue
            try:
                beta, adj = _fit_genus(trows, "D_m2")
            except ValueError:
                continue
            taxon_rows.append({
                "taxon": taxon,
                "beta_delta": beta,
                "sessions": len(trows),
                "sites": len({row["site"] for row in trows}),
                "adjustment": adj,
            })

        if beta_w < 0 and beta_b >= 0:
            sign_quadrant = "W_DOWN_B_UP_OR_FLAT"
        elif beta_w < 0 and beta_b < 0:
            sign_quadrant = "W_DOWN_B_DOWN"
        elif beta_w >= 0 and beta_b >= 0:
            sign_quadrant = "W_UP_OR_FLAT_B_UP_OR_FLAT"
        else:
            sign_quadrant = "W_UP_OR_FLAT_B_DOWN"

        diagnostics.append({
            "genus": genus,
            "sessions": len(sub),
            "series": len({row["series_id"] for row in sub}),
            "sites": len(sites),
            "beta_delta": delta,
            "beta_W": beta_w,
            "beta_B_debiased": beta_b,
            "beta_delta_raw_B": delta_raw,
            "adjustment": adjustment,
            "sign_quadrant": sign_quadrant,
            "raw_B_delta_same_sign_as_primary_delta": (
                (delta_raw > 0 and delta > 0)
                or (delta_raw < 0 and delta < 0)
                or (abs(delta_raw) <= TOL and abs(delta) <= TOL)
            ),
            "site_leave_one_out": site_loo,
            "site_leave_one_out_all_same_sign_as_genus_delta": _same_sign(
                [x["beta_delta"] for x in site_loo], delta
            ),
            "taxon_specific_delta_descriptive": taxon_rows,
        })

    robust_multisite = [
        x for x in diagnostics
        if x["sites"] >= 3
        and x["sessions"] >= 30
        and x["raw_B_delta_same_sign_as_primary_delta"]
        and x["site_leave_one_out_all_same_sign_as_genus_delta"] is True
    ]

    return {
        "schema": "neon.multiscale_density.heterogeneity_diagnostic.v1",
        "date": "2026-10-06",
        "status": "POST_RESULT_DESCRIPTIVE_ONLY",
        "frozen_primary_result": str(FROZEN_RESULT.relative_to(ROOT)),
        "primary_guard_remains_failed": True,
        "primary_guard_may_not_be_relaxed": True,
        "diagnostics": diagnostics,
        "descriptive_robust_multisite_genera": [
            {
                "genus": x["genus"],
                "beta_delta": x["beta_delta"],
                "beta_W": x["beta_W"],
                "beta_B_debiased": x["beta_B_debiased"],
                "sign_quadrant": x["sign_quadrant"],
                "sessions": x["sessions"],
                "sites": x["sites"],
            }
            for x in robust_multisite
        ],
        "interpretation_boundary": {
            "allowed": (
                "describe repeated positive and negative spatial-response modes "
                "that survive raw-B and leave-one-site-out diagnostics"
            ),
            "not_allowed": [
                "redefine the primary 6/8 generality guard",
                "drop negative genera from the primary claim",
                "select habitat/body-size/sociality moderators from these results",
                "claim a lineage mechanism without independent confirmation",
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
        "primary_guard_remains_failed": result["primary_guard_remains_failed"],
        "diagnostics": [
            {
                k: row[k]
                for k in (
                    "genus","sessions","sites","beta_delta","beta_W",
                    "beta_B_debiased","beta_delta_raw_B","sign_quadrant",
                    "raw_B_delta_same_sign_as_primary_delta",
                    "site_leave_one_out_all_same_sign_as_genus_delta",
                )
            }
            for row in result["diagnostics"]
        ],
        "descriptive_robust_multisite_genera": result[
            "descriptive_robust_multisite_genera"
        ],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
