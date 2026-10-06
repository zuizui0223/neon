#!/usr/bin/env python3
"""Post-result single-catch observation-process null simulation.

The ecological development result is already frozen and is not reclassified by
this simulation. The simulation asks a narrower reliability question:

Can a density-invariant spatial system, observed for three nights with single-
catch traps and the frozen m>=5 metric gate, generate W/B density slopes as
large as those observed in RELEASE-2026?

No parameter is fitted to W, B, Delta, or genus-specific ecological outcomes.
The grid, three-night design, metric, and m threshold come from frozen contracts.
A broad capture-probability and movement-scale grid is used rather than tuning
one observation model to the observed slope.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from analysis.multiscale_density_metrics_v1 import session_metrics

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "multiscale_density_single_catch_null_v1.json"

SEED = 20261006
N_LEVELS = (10, 15, 20, 25, 30, 35, 40)
CAPTURE_PROBABILITIES = (0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
SIGMA_M = (8.0, 12.5, 20.0)
REPLICATES_PER_N = 500
MIN_REPEAT = 5

OBSERVED = {
    "beta_W": -4.394825896684285,
    "beta_B_debiased": 4.976939575783388,
    "beta_D": 9.37176547246767,
    "repeat_supported_fraction_slope": -0.008288709569018633,
    "capture_trap_night_fraction_slope": 0.00395472174740231,
}


def trap_label(index: int) -> str:
    row = index // 10
    col = index % 10 + 1
    return f"{chr(ord('A') + row)}{col}"


TRAPS = np.asarray(
    [(i * 10.0, j * 10.0) for i in range(10) for j in range(10)],
    dtype=float,
)
TRAP_LABELS = [trap_label(i) for i in range(100)]


def centre_pool(name: str) -> np.ndarray:
    if name == "full_10x10":
        return TRAPS.copy()
    if name == "central_8x8":
        return np.asarray(
            [(i * 10.0, j * 10.0) for i in range(1, 9) for j in range(1, 9)],
            dtype=float,
        )
    raise ValueError(name)


def detection_probabilities(pool: np.ndarray, sigma: float) -> np.ndarray:
    out = []
    for mu in pool:
        d2 = np.sum((TRAPS - mu) ** 2, axis=1)
        p = np.exp(-d2 / (2.0 * sigma * sigma))
        p /= p.sum()
        out.append(p)
    return np.asarray(out)


def simulate_session(
    rng: np.random.Generator,
    *,
    n_individuals: int,
    pool: np.ndarray,
    trap_probs: np.ndarray,
    p_capture: float,
    single_catch: bool,
) -> dict | None:
    centre_indices = rng.integers(0, len(pool), size=n_individuals)
    records: dict[str, list[tuple[str, str]]] = defaultdict(list)
    captured_ids: set[int] = set()
    occupied_trap_nights = 0

    for night in range(3):
        proposals: list[tuple[int, int]] = []
        for individual in range(n_individuals):
            if rng.random() >= p_capture:
                continue
            trap = int(
                rng.choice(
                    len(TRAPS),
                    p=trap_probs[centre_indices[individual]],
                )
            )
            proposals.append((individual, trap))

        if single_catch:
            by_trap: dict[int, list[int]] = defaultdict(list)
            for individual, trap in proposals:
                by_trap[trap].append(individual)
            accepted: list[tuple[int, int]] = []
            for trap in sorted(by_trap):
                individuals = by_trap[trap]
                winner = int(rng.choice(individuals))
                accepted.append((winner, trap))
        else:
            accepted = proposals

        occupied_trap_nights += len({trap for _, trap in accepted})
        for individual, trap in accepted:
            captured_ids.add(individual)
            records[f"i{individual}"].append(
                (f"n{night + 1}", TRAP_LABELS[trap])
            )

    repeat_supported = sum(
        len({night for night, _ in recs}) >= 2
        for recs in records.values()
    )
    unique_observed = len(captured_ids)
    if repeat_supported < MIN_REPEAT:
        return None

    try:
        metric = session_metrics(records, minimum_individuals=MIN_REPEAT)
    except ValueError:
        return None

    return {
        "W_m2": float(metric["W_m2"]),
        "B_debiased_m2": float(metric["B_debiased_m2"]),
        "D_m2": float(metric["B_debiased_m2"] - metric["W_m2"]),
        "B_observed_m2": float(metric["B_observed_m2"]),
        "repeat_supported_individuals": int(metric["n_individuals"]),
        "unique_observed_individuals": unique_observed,
        "repeat_supported_fraction": (
            metric["n_individuals"] / unique_observed
            if unique_observed else 0.0
        ),
        "capture_trap_night_fraction": occupied_trap_nights / 300.0,
    }


def linear_slope(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("need matched x/y vectors")
    return float(np.polyfit(np.asarray(x), np.asarray(y), 1)[0])


def summarize_cell(
    rng: np.random.Generator,
    *,
    scenario: str,
    sigma: float,
    p_capture: float,
    single_catch: bool,
    replicates: int,
) -> dict:
    pool = centre_pool(scenario)
    probs = detection_probabilities(pool, sigma)
    by_n = []

    for n in N_LEVELS:
        vals = []
        for _ in range(replicates):
            row = simulate_session(
                rng,
                n_individuals=n,
                pool=pool,
                trap_probs=probs,
                p_capture=p_capture,
                single_catch=single_catch,
            )
            if row is not None:
                vals.append(row)

        if vals:
            mean = {
                key: float(np.mean([row[key] for row in vals]))
                for key in (
                    "W_m2",
                    "B_debiased_m2",
                    "D_m2",
                    "B_observed_m2",
                    "repeat_supported_individuals",
                    "unique_observed_individuals",
                    "repeat_supported_fraction",
                    "capture_trap_night_fraction",
                )
            }
        else:
            mean = {}

        by_n.append({
            "N": n,
            "replicates": replicates,
            "eligible_replicates": len(vals),
            "eligible_fraction": len(vals) / replicates,
            **mean,
        })

    complete = [
        row for row in by_n
        if row["eligible_replicates"] > 0
    ]
    if len(complete) < 4:
        slopes = None
    else:
        x = [row["N"] for row in complete]
        slopes = {
            "beta_W": linear_slope(x, [row["W_m2"] for row in complete]),
            "beta_B_debiased": linear_slope(
                x, [row["B_debiased_m2"] for row in complete]
            ),
            "beta_D": linear_slope(x, [row["D_m2"] for row in complete]),
            "repeat_supported_fraction_slope": linear_slope(
                x, [row["repeat_supported_fraction"] for row in complete]
            ),
            "capture_trap_night_fraction_slope": linear_slope(
                x, [row["capture_trap_night_fraction"] for row in complete]
            ),
        }

    return {
        "scenario": scenario,
        "sigma_m": sigma,
        "p_capture_per_individual_night": p_capture,
        "single_catch": single_catch,
        "by_N": by_n,
        "slopes": slopes,
        "minimum_eligible_fraction": min(
            row["eligible_fraction"] for row in by_n
        ),
    }


def run(replicates: int = REPLICATES_PER_N, seed: int = SEED) -> dict:
    rng = np.random.default_rng(seed)
    cells = []

    for scenario in ("full_10x10", "central_8x8"):
        for sigma in SIGMA_M:
            for p_capture in CAPTURE_PROBABILITIES:
                for single_catch in (False, True):
                    cells.append(
                        summarize_cell(
                            rng,
                            scenario=scenario,
                            sigma=sigma,
                            p_capture=p_capture,
                            single_catch=single_catch,
                            replicates=replicates,
                        )
                    )

    single = [
        cell for cell in cells
        if cell["single_catch"] and cell["slopes"] is not None
    ]
    multi = [
        cell for cell in cells
        if not cell["single_catch"] and cell["slopes"] is not None
    ]

    def selection_distance(cell: dict) -> float:
        slopes = cell["slopes"]
        return (
            abs(
                slopes["repeat_supported_fraction_slope"]
                - OBSERVED["repeat_supported_fraction_slope"]
            )
            / abs(OBSERVED["repeat_supported_fraction_slope"])
            + abs(
                slopes["capture_trap_night_fraction_slope"]
                - OBSERVED["capture_trap_night_fraction_slope"]
            )
            / OBSERVED["capture_trap_night_fraction_slope"]
        )

    closest_selection = sorted(
        single, key=selection_distance
    )[:10]

    max_single_delta = max(
        cell["slopes"]["beta_D"] for cell in single
    )
    min_single_w = min(
        cell["slopes"]["beta_W"] for cell in single
    )
    max_single_b = max(
        cell["slopes"]["beta_B_debiased"] for cell in single
    )

    return {
        "schema": "neon.multiscale_density.single_catch_null.v1",
        "date": "2026-10-06",
        "status": "POST_RESULT_OBSERVATION_PROCESS_FALSIFICATION",
        "seed": seed,
        "replicates_per_N_cell": replicates,
        "design": {
            "grid": "standard 10x10, 10 m spacing",
            "nights": 3,
            "minimum_repeat_supported_individuals": MIN_REPEAT,
            "N_levels": list(N_LEVELS),
            "centre_scenarios": ["full_10x10", "central_8x8"],
            "sigma_m": list(SIGMA_M),
            "capture_probabilities": list(CAPTURE_PROBABILITIES),
            "single_catch_rule": (
                "each individual proposes at most one trap per night; when "
                "multiple individuals propose the same trap, one is chosen at "
                "random and the rest are unobserved"
            ),
            "ecological_null": (
                "latent centre distribution, detection kernel and individual "
                "capture probability do not change with N"
            ),
            "multicatch_comparator": True,
        },
        "observed_release2026_slopes": OBSERVED,
        "single_catch_envelope": {
            "cell_count": len(single),
            "maximum_beta_D": max_single_delta,
            "minimum_beta_W": min_single_w,
            "maximum_beta_B_debiased": max_single_b,
            "observed_beta_D_exceeds_all_simulated_cells": (
                OBSERVED["beta_D"] > max_single_delta
            ),
            "observed_beta_W_more_negative_than_all_simulated_cells": (
                OBSERVED["beta_W"] < min_single_w
            ),
        },
        "closest_cells_by_observation_support_slopes": [
            {
                "scenario": cell["scenario"],
                "sigma_m": cell["sigma_m"],
                "p_capture_per_individual_night": cell[
                    "p_capture_per_individual_night"
                ],
                "minimum_eligible_fraction": cell[
                    "minimum_eligible_fraction"
                ],
                "selection_distance": selection_distance(cell),
                "slopes": cell["slopes"],
            }
            for cell in closest_selection
        ],
        "cells": cells,
        "interpretation_boundary": {
            "allowed": (
                "test whether a simple density-dependent single-catch selection "
                "mechanism, with no true spatial density response, can reproduce "
                "the observed slope magnitudes"
            ),
            "not_allowed": [
                "treat this simplified simulation as a complete NEON detection model",
                "use the simulation to reclassify the preregistered 5/8 generality failure",
                "tune simulation parameters to individual genera after viewing their slopes",
                "claim causality from a failure of this null alone",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replicates", type=int, default=REPLICATES_PER_N)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    result = run(replicates=args.replicates, seed=args.seed)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "single_catch_envelope": result["single_catch_envelope"],
        "closest_cells_by_observation_support_slopes": result[
            "closest_cells_by_observation_support_slopes"
        ][:5],
        "interpretation_boundary": result["interpretation_boundary"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
