#!/usr/bin/env python3
"""Post-result geometry audit; original Δ, W and B inference remains frozen.

The reference distributions are descriptive observation-geometry diagnostics.
Neither implies individual territorial exclusion or causal density dependence.
"""
from __future__ import annotations

import json
import math
import random
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from analysis.audit_multiscale_density_mnka_variation_v1 import run as run_mnka
from analysis.multiscale_density_fixed_effects_v1 import fit_slope
from analysis.multiscale_density_metrics_v1 import half_mean_pairwise_squared
from analysis.run_multiscale_density_development_fit_v1 import (
    FROZEN_GENERA,
    _eligible_series,
)
from analysis.run_multiscale_density_metric_qc_v1 import run as run_metric_qc

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "multiscale_density_centroid_geometry_v1.json"
FROZEN = ROOT / "results" / "multiscale_density_development_result_v1.json"
SEED = 20261008
REPLICATES = 199
MODE_GENERA = ("Chaetodipus", "Myodes", "Peromyscus", "Dipodomys", "Sigmodon")
EXPECTED_N = 1326
TOL = 1e-8


def raw_nearest_neighbor_squared(points: list[tuple[float, float]]) -> float:
    if len(points) < 2:
        raise ValueError("at least two centroids required")
    return sum(
        min(
            (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
            for j, b in enumerate(points) if i != j
        )
        for i, a in enumerate(points)
    ) / len(points)


def edge_fraction(points: list[tuple[float, float]]) -> float:
    if not points:
        raise ValueError("empty centroid cohort")
    return sum(
        x <= 10 or x >= 80 or y <= 10 or y >= 80
        for x, y in points
    ) / len(points)


def spatial_nulls(
    points: list[tuple[float, float]],
    pool_elsewhere: list[tuple[float, float]],
    *,
    rng: random.Random,
    replicates: int = REPLICATES,
) -> dict:
    """Shuffle x/y while fixing B; separately draw from other-event series pool."""
    if replicates < 1:
        raise ValueError("replicates must be positive")
    m = len(points)
    observed_nn = raw_nearest_neighbor_squared(points)
    xx = [x for x, _ in points]
    yy = [y for _, y in points]
    xy_nn = []
    pooled_nn = []
    for _ in range(replicates):
        yperm = list(yy)
        rng.shuffle(yperm)
        permuted = list(zip(xx, yperm))
        if abs(half_mean_pairwise_squared(permuted)
               - half_mean_pairwise_squared(points)) > TOL:
            raise AssertionError("XY shuffle failed B-preservation invariant")
        xy_nn.append(raw_nearest_neighbor_squared(permuted))
        if len(pool_elsewhere) >= m:
            sampled = rng.sample(pool_elsewhere, k=m)
            pooled_nn.append(raw_nearest_neighbor_squared(sampled))
    return {
        "nn_squared_m2": observed_nn,
        "edge_fraction": edge_fraction(points),
        "nn_expected_xy_m2": sum(xy_nn) / len(xy_nn),
        "nn_excess_xy_m2": observed_nn - sum(xy_nn) / len(xy_nn),
        "nn_expected_series_m2": (
            sum(pooled_nn) / len(pooled_nn) if pooled_nn else None
        ),
        "nn_excess_series_m2": (
            observed_nn - sum(pooled_nn) / len(pooled_nn)
            if pooled_nn else None
        ),
        "series_reference_eligible": bool(pooled_nn),
    }


def prepare_rows(metric_sessions: list[dict], mnka_sessions: list[dict]) -> list[dict]:
    def key(r: dict) -> tuple:
        return (r["taxon"], r["site"], r["plot_id"], r["event_id"])

    mlookup = {key(m): m for m in metric_sessions}
    nlookup = {key(n): n for n in mnka_sessions}
    if len(mlookup) != len(metric_sessions) or len(nlookup) != len(mnka_sessions):
        raise RuntimeError("duplicate frozen session key")
    if not set(mlookup).issubset(nlookup):
        raise RuntimeError("missing MNKA for geometry-scored sessions")
    joined = []
    for k, m in mlookup.items():
        n = nlookup[k]
        if m["genus"] != n["genus"]:
            raise RuntimeError("genus mismatch")
        t = date.fromisoformat(n["event_date"][:10])
        coords = [tuple(float(v) for v in item)
                  for item in m["individual_centroid_coordinates_m"]]
        if len(coords) != m["n_individuals"]:
            raise RuntimeError("centroid cohort does not match metric cohort")
        bcalc = half_mean_pairwise_squared(coords)
        if abs(bcalc - m["B_observed_m2"]) > TOL:
            raise RuntimeError("centroid-derived B differs from frozen B")
        if any(not 0 <= q <= 90 for xy in coords for q in xy):
            raise RuntimeError("centroids outside frozen 10x10 geometry")
        joined.append({
            "taxon": m["taxon"], "site": m["site"], "plot_id": m["plot_id"],
            "event_id": m["event_id"], "genus": m["genus"],
            "series_id": "|".join((m["taxon"], m["site"], m["plot_id"])),
            "mnka": int(n["mnka"]),
            "site_month": f"{m['site']}|{t.month:02d}",
            "year": str(t.year),
            "m": m["n_individuals"],
            "W_m2": float(m["W_m2"]),
            "B_debiased_m2": float(m["B_debiased_m2"]),
            "B_observed_m2": float(m["B_observed_m2"]),
            "D_m2": float(m["B_debiased_m2"]) - float(m["W_m2"]),
            "centroids": coords,
        })
    chosen = [r for r in joined if r["genus"] in set(FROZEN_GENERA)]
    supported = _eligible_series(chosen)
    rows = [r for r in chosen if r["series_id"] in supported]
    return rows


def fit_or_status(rows: list[dict], response: str) -> dict:
    a = [r for r in rows if r.get(response) is not None]
    support = {
        "n": len(a),
        "sites": len({r["site"] for r in a}),
        "series": len({r["series_id"] for r in a}),
    }
    if len(a) < 30 or support["sites"] < 3 or support["series"] < 5:
        return {**support, "status": "INSUFFICIENT_SUPPORT"}
    try:
        model = fit_slope(
            a, response=response, genus_balanced=False,
            nuisance=("series_id", "site_month", "year")
        )
        return {**support, "status": "DESCRIPTIVE", "slope": model.beta,
                "adjustment": "series_site_month_year"}
    except ValueError:
        try:
            model = fit_slope(
                a, response=response, genus_balanced=False,
                nuisance=("series_id",)
            )
            return {**support, "status": "DESCRIPTIVE_REDUCED_ADJUSTMENT",
                    "slope": model.beta, "adjustment": "series_only"}
        except ValueError:
            return {**support, "status": "NO_RESIDUAL_ABUNDANCE_VARIATION"}


def post_result_robustness(rows: list[dict], responses: tuple[str, ...]) -> dict:
    """Post-hoc site and taxon sensitivity; NEVER prospective confirmation."""
    site_names = sorted({r["site"] for r in rows})
    omissions = {}
    for site in site_names:
        subset = [r for r in rows if r["site"] != site]
        omissions[site] = {k: fit_or_status(subset, k) for k in responses}
    taxa = {}
    for taxon in sorted({r["taxon"] for r in rows}):
        sub = [r for r in rows if r["taxon"] == taxon]
        taxa[taxon] = {
            "sessions": len(sub),
            "sites": len({r["site"] for r in sub}),
            "fits": {k: fit_or_status(sub, k) for k in responses},
        }
    summary = {}
    for response in responses:
        values = [
            v[response]["slope"] for v in omissions.values()
            if v[response].get("slope") is not None
        ]
        summary[response] = {
            "estimable_site_omissions": len(values),
            "total_site_omissions": len(site_names),
            "positive_count": sum(z > 0 for z in values),
            "negative_count": sum(z < 0 for z in values),
            "min_slope": min(values) if values else None,
            "max_slope": max(values) if values else None,
        }
    return {
        "state": "POST_RESULT_DESCRIPTIVE_NOT_CONFIRMATORY",
        "leave_one_site_out": summary,
        "taxon_descriptive": taxa,
        "claim_boundary": "No independent site or future-release confirmation.",
    }


def analyze(rows: list[dict], *, seed: int = SEED, replicates: int = REPLICATES) -> dict:
    if len(rows) != EXPECTED_N:
        raise RuntimeError(f"drift in frozen development population: {len(rows)}")
    baseline = fit_slope(rows, response="D_m2", genus_balanced=True)
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    expected = float(frozen["primary"]["delta_beta_m2_per_mnka"])
    if abs(baseline.beta - expected) > TOL:
        raise RuntimeError(f"frozen Δ drifted: {baseline.beta} vs {expected}")

    pool = defaultdict(list)
    for row in rows:
        pool[row["series_id"]].extend(row["centroids"])

    rng = random.Random(seed)
    results = []
    for r in rows:
        # Remove every centroid from this EVENT by using only other events.
        alternatives = [
            point for other in rows
            if (other["series_id"] == r["series_id"]
                and other["event_id"] != r["event_id"])
            for point in other["centroids"]
        ]
        # A row-per-series index would be faster for enormous datasets; with
        # 1326 sessions this is bounded and avoids simplifying the exclusion.
        summary = spatial_nulls(
            r["centroids"], alternatives, rng=rng, replicates=replicates
        )
        results.append({
            **{k: v for k, v in r.items() if k != "centroids"},
            **summary,
        })

    per_genus = {}
    for genus in MODE_GENERA:
        subset = [r for r in results if r["genus"] == genus]
        fits = {
            var: fit_or_status(subset, var)
            for var in (
                "m", "B_observed_m2", "edge_fraction", "nn_squared_m2",
                "nn_excess_xy_m2", "nn_excess_series_m2",
            )
        }
        x = fits["nn_excess_xy_m2"]
        y = fits["nn_excess_series_m2"]
        status = (
            "EXPLORATORY_BOTH_REFERENCES_POSITIVE"
            if x.get("slope", 0) > 0 and y.get("slope", 0) > 0
            else "NO_COHERENT_POSITIVE_SPACING_EVIDENCE"
        ) if x.get("slope") is not None and y.get("slope") is not None else "NO_DUAL_NULL_TEST"
        per_genus[genus] = {
            "post_result_robustness": (
                post_result_robustness(
                    subset, ("nn_excess_xy_m2", "nn_excess_series_m2")
                ) if genus == "Peromyscus" else None
            ),
            "sessions": len(subset),
            "nullB_coverage_fraction": (
                sum(r["series_reference_eligible"] for r in subset) / len(subset)
                if subset else 0
            ),
            "fits": fits,
            "local_spacing_diagnostic": status,
        }
    return {
        "schema": "neon.multiscale_density.centroid_geometry_v1",
        "status": "POST_RESULT_EXPLORATORY_NOT_CONFIRMATORY",
        "analysis_sessions": len(rows),
        "baseline_delta_reproduced": baseline.beta,
        "geometry_match": "ALL_CENTROID_B_OBS_AND_COHORT_COUNTS_MATCH",
        "rng_seed": seed, "null_replicates": replicates,
        "num_series": len({r["series_id"] for r in rows}),
        "num_sites": len({r["site"] for r in rows}),
        "nullB_coverage": sum(r["series_reference_eligible"] for r in results),
        "genera": per_genus,
        "session_diagnostics": results,
        "frozen_6_of_8_development_guard": "FAILED_UNCHANGED",
        "biological_claim_boundary": (
            "Capture-session centroids are not true centers of undisturbed animal "
            "home ranges. Neither XY permutation nor series-pool sampling controls "
            "all detection and population turnover processes. Positive slopes are "
            "exploratory, not territoriality or causation."
        ),
    }


def run() -> dict:
    metric = run_metric_qc(include_centroid_coordinates=True)
    if not metric["decision"]["metric_qc_passed"]:
        raise RuntimeError("frozen metric QC failed")
    abundance = run_mnka()
    rows = prepare_rows(metric["sessions"], abundance["paired_sessions"])
    return analyze(rows)


if __name__ == "__main__":
    result = run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    row_diagnostics = result.pop("session_diagnostics")
    row_file = OUT.parent / "multiscale_density_centroid_session_diagnostics_v1.json"
    row_file.write_text(
        json.dumps(row_diagnostics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8"
    )
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
