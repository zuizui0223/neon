#!/usr/bin/env python3
"""Synthetic support audit for multiscale density-accommodation metrics.

No biological data are read. The simulation uses the standard NEON 10x10 detector grid at 10 m spacing,
a fixed Gaussian detector kernel, and an unchanged latent centre distribution.
It asks how repeat-supported individual count affects the finite-sample
stability of the raw and centroid-debiased between-centre variance metrics.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from analysis.validate_multiscale_density_metrics_v1 import (
    centroid_noise_correction,
    debiased_between_variance,
    half_mean_pairwise_squared,
    observed_between_variance,
    within_individual_variance,
)


def detector_grid(n_rows: int, n_cols: int, spacing: float = 10.0) -> np.ndarray:
    return np.asarray(
        [(i * spacing, j * spacing) for i in range(n_rows) for j in range(n_cols)],
        dtype=float,
    )


def expected_detector_centre(
    latent_centre: np.ndarray,
    detectors: np.ndarray,
    sigma: float,
) -> tuple[np.ndarray, np.ndarray]:
    d2 = np.sum((detectors - latent_centre) ** 2, axis=1)
    p = np.exp(-d2 / (2.0 * sigma**2))
    p = p / p.sum()
    return np.sum(detectors * p[:, None], axis=0), p


def one_session(
    rng: np.random.Generator,
    *,
    n_individuals: int,
    detectors: np.ndarray,
    latent_pool: np.ndarray,
    sigma: float,
    min_captures: int,
    max_captures: int,
) -> dict[str, float]:
    idx = rng.integers(0, len(latent_pool), size=n_individuals)
    latent = latent_pool[idx]
    captures: list[list[tuple[float, float]]] = []
    expected_centres: list[tuple[float, float]] = []

    for mu in latent:
        q, p = expected_detector_centre(mu, detectors, sigma)
        expected_centres.append((float(q[0]), float(q[1])))
        k = int(rng.integers(min_captures, max_captures + 1))
        picked = rng.choice(len(detectors), size=k, replace=True, p=p)
        xs = detectors[picked]
        captures.append([(float(x), float(y)) for x, y in xs])

    raw_b = observed_between_variance(captures)
    correction = centroid_noise_correction(captures)
    debiased_b = debiased_between_variance(captures)
    target_b = half_mean_pairwise_squared(expected_centres)
    mean_w = float(np.mean([within_individual_variance(x) for x in captures]))

    return {
        "raw_b": float(raw_b),
        "centroid_noise_correction": float(correction),
        "debiased_b": float(debiased_b),
        "target_b": float(target_b),
        "mean_w": mean_w,
    }


def summarize(values: list[dict[str, float]]) -> dict:
    raw = np.asarray([x["raw_b"] for x in values], dtype=float)
    deb = np.asarray([x["debiased_b"] for x in values], dtype=float)
    target = np.asarray([x["target_b"] for x in values], dtype=float)
    correction = np.asarray(
        [x["centroid_noise_correction"] for x in values], dtype=float
    )

    raw_error = raw - target
    deb_error = deb - target
    valid = target > 0
    deb_abs_rel = np.abs(deb_error[valid] / target[valid])

    return {
        "replicates": int(len(values)),
        "mean_target_b": float(np.mean(target)),
        "mean_raw_b": float(np.mean(raw)),
        "mean_debiased_b": float(np.mean(deb)),
        "mean_raw_bias": float(np.mean(raw_error)),
        "mean_debiased_bias": float(np.mean(deb_error)),
        "mean_centroid_noise_correction": float(np.mean(correction)),
        "fraction_debiased_b_nonpositive": float(np.mean(deb <= 0)),
        "median_absolute_relative_error_debiased": float(np.median(deb_abs_rel)),
        "q90_absolute_relative_error_debiased": float(
            np.quantile(deb_abs_rel, 0.90)
        ),
    }


MECHANICAL_ACCEPTANCE = {
    "max_abs_mean_bias_fraction_of_target": 0.05,
    "max_fraction_debiased_b_nonpositive": 0.01,
    "max_median_absolute_relative_error": 0.25,
    "max_q90_absolute_relative_error": 0.50,
}


def cell_passes_mechanical_gate(cell: dict) -> bool:
    target = abs(float(cell["mean_target_b"]))
    if target <= 0:
        return False
    return (
        abs(float(cell["mean_debiased_bias"])) / target
        <= MECHANICAL_ACCEPTANCE["max_abs_mean_bias_fraction_of_target"]
        and float(cell["fraction_debiased_b_nonpositive"])
        <= MECHANICAL_ACCEPTANCE["max_fraction_debiased_b_nonpositive"]
        and float(cell["median_absolute_relative_error_debiased"])
        <= MECHANICAL_ACCEPTANCE["max_median_absolute_relative_error"]
        and float(cell["q90_absolute_relative_error_debiased"])
        <= MECHANICAL_ACCEPTANCE["max_q90_absolute_relative_error"]
    )


def choose_minimum_support(cells: list[dict]) -> dict:
    by_n: dict[int, list[dict]] = {}
    for cell in cells:
        by_n.setdefault(int(cell["n_repeat_supported_individuals"]), []).append(cell)
    candidates = sorted(by_n)
    decisions = []
    selected = None
    for n in candidates:
        rows = by_n[n]
        passed = len(rows) >= 2 and all(cell_passes_mechanical_gate(x) for x in rows)
        decisions.append({
            "n_repeat_supported_individuals": n,
            "scenario_count": len(rows),
            "all_scenarios_pass": passed,
        })
        if passed and selected is None:
            selected = n
    return {
        "acceptance_criteria": MECHANICAL_ACCEPTANCE,
        "candidate_minima": candidates,
        "per_minimum_decision": decisions,
        "selected_minimum_repeat_supported_individuals": selected,
        "rule": (
            "choose the smallest candidate m passing every mechanical criterion "
            "in every prespecified latent-centre scenario; if none pass, STOP"
        ),
    }


def run(
    *,
    replicates: int = 2000,
    seed: int = 20261005,
    sigma: float = 12.5,
) -> dict:
    rng = np.random.default_rng(seed)
    cells = []

    geometry_specs = [
        {
            "geometry": "standard_10x10",
            "primary_geometry": True,
            "detectors": detector_grid(10, 10),
            "latent_pools": [
                ("full_10x10_latent_centres", detector_grid(10, 10)),
                (
                    "central_8x8_latent_centres",
                    np.asarray(
                        [
                            (i * 10.0, j * 10.0)
                            for i in range(1, 9)
                            for j in range(1, 9)
                        ],
                        dtype=float,
                    ),
                ),
            ],
        },
        {
            "geometry": "srer_7x7_exception",
            "primary_geometry": False,
            "detectors": detector_grid(7, 7),
            "latent_pools": [
                ("full_7x7_latent_centres", detector_grid(7, 7)),
                (
                    "central_5x5_latent_centres",
                    np.asarray(
                        [
                            (i * 10.0, j * 10.0)
                            for i in range(1, 6)
                            for j in range(1, 6)
                        ],
                        dtype=float,
                    ),
                ),
            ],
        },
    ]

    for spec in geometry_specs:
        detectors = spec["detectors"]
        for scenario, pool in spec["latent_pools"]:
            for n_individuals in (3, 5, 8, 10, 15, 20):
                vals = [
                    one_session(
                        rng,
                        n_individuals=n_individuals,
                        detectors=detectors,
                        latent_pool=pool,
                        sigma=sigma,
                        min_captures=2,
                        max_captures=4,
                    )
                    for _ in range(replicates)
                ]
                cells.append(
                    {
                        "geometry": spec["geometry"],
                        "primary_geometry": spec["primary_geometry"],
                        "scenario": scenario,
                        "n_repeat_supported_individuals": n_individuals,
                        **summarize(vals),
                    }
                )

    primary_cells = [x for x in cells if x["primary_geometry"]]
    support_decision = choose_minimum_support(primary_cells)
    srer_support_decision = choose_minimum_support(
        [x for x in cells if x["geometry"] == "srer_7x7_exception"]
    )

    return {
        "schema": "neon.multiscale_density.metric_support_simulation.v1",
        "status": "synthetic_mechanical_support_only",
        "seed": seed,
        "replicates_per_cell": replicates,
        "primary_detector_grid": "standard NEON 10x10, 10 m spacing (90 x 90 m)",
        "secondary_exception_grid": "SRER 7x7, 10 m spacing",
        "geometry_policy": (
            "primary threshold is selected from standard 10x10 scenarios only; "
            "SRER is retained as a separately calibrated geometry and may not "
            "define or lower the standard-grid support threshold"
        ),
        "detector_kernel_sigma_m": sigma,
        "captures_per_individual": "discrete uniform 2..4",
        "cells": cells,
        "mechanical_support_decision": support_decision,
        "srer_mechanical_support_decision": srer_support_decision,
        "boundary": {
            "biological_data_read": False,
            "density_effects_estimated": False,
            "purpose": (
                "choose a structurally defensible minimum repeat-supported "
                "individual count before any ecological density response is opened"
            ),
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--replicates", type=int, default=2000)
    p.add_argument("--seed", type=int, default=20261005)
    p.add_argument(
        "--out",
        type=Path,
        default=Path("build/multiscale_density_metric_support_v1.json"),
    )
    a = p.parse_args()
    result = run(replicates=a.replicates, seed=a.seed)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
