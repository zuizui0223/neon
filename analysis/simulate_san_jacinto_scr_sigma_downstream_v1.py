from __future__ import annotations

# AI assistance disclosure: This file was drafted or refactored with OpenAI ChatGPT (GPT-5.6 Sol, October 2026); it remains under author responsibility and is verified by repository tests/workflows.

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp

TRAP_SPACING_M = 6.25
GRID_SIDE = 7
TRAPS = np.array(
    [(c * TRAP_SPACING_M, r * TRAP_SPACING_M) for r in range(GRID_SIDE) for c in range(GRID_SIDE)],
    dtype=float,
)
GRID_MAX_M = (GRID_SIDE - 1) * TRAP_SPACING_M
MASK_BUFFER_M = 100.0
MASK_STEP_M = 10.0
MASK_AXIS = np.arange(-MASK_BUFFER_M, GRID_MAX_M + MASK_BUFFER_M + 1e-9, MASK_STEP_M)
MASK = np.array([(x, y) for x in MASK_AXIS for y in MASK_AXIS], dtype=float)
MASK_D2 = ((MASK[:, None, :] - TRAPS[None, :, :]) ** 2).sum(axis=2)


@dataclass(frozen=True)
class SimulationConfig:
    true_sigma_m: float = 12.5
    lambda0_check: float = 0.04
    population_n: int = 1000
    nights: int = 5
    checks_per_night: int = 4
    stay_probability: float = 0.30


def capture_probabilities(center: np.ndarray, sigma_m: float, lambda0: float) -> tuple[float, np.ndarray]:
    d2 = ((TRAPS - center) ** 2).sum(axis=1)
    weights = np.exp(-d2 / (2.0 * sigma_m * sigma_m))
    total = float(weights.sum())
    p_none = math.exp(-lambda0 * total)
    return p_none, weights / total


def simulate_capture_array(
    seed: int,
    handling_median_m: float,
    config: SimulationConfig,
) -> np.ndarray:
    """Simulate repeated-check live-trap detections.

    The pre-capture detector process is a half-normal spatial competing-hazard
    process around a fixed activity centre. After the first capture of a night,
    the effective centre may be displaced for the remainder of that night by a
    random vector whose magnitude is Rayleigh distributed with the requested
    median. The displacement resets before the next night.

    A phenomenological same-trap persistence term represents short-time
    positional autocorrelation. stay_probability=0.30 was fixed because, under
    zero handling displacement and the focal geometry, it yields a repeat-night
    first-to-last change frequency close to the ~0.70 observed in the San
    Jacinto held-out species. It is a calibration device, not a biological
    estimate of a movement parameter.
    """
    rng = np.random.default_rng(seed)
    centers = rng.uniform(
        [-MASK_BUFFER_M, -MASK_BUFFER_M],
        [GRID_MAX_M + MASK_BUFFER_M, GRID_MAX_M + MASK_BUFFER_M],
        size=(config.population_n, 2),
    )
    detections = np.full(
        (config.population_n, config.nights, config.checks_per_night),
        -1,
        dtype=np.int16,
    )

    if handling_median_m < 0:
        raise ValueError("handling_median_m must be nonnegative")
    rayleigh_scale = (
        handling_median_m / math.sqrt(2.0 * math.log(2.0))
        if handling_median_m > 0
        else 0.0
    )

    for i, base_center in enumerate(centers):
        for night in range(config.nights):
            shift = np.zeros(2, dtype=float)
            shift_drawn = False
            previous_trap: int | None = None

            for check in range(config.checks_per_night):
                effective_center = base_center + shift
                p_none, trap_probs = capture_probabilities(
                    effective_center,
                    config.true_sigma_m,
                    config.lambda0_check,
                )
                if rng.random() <= p_none:
                    continue

                if previous_trap is not None and rng.random() < config.stay_probability:
                    trap = previous_trap
                else:
                    trap = int(rng.choice(len(TRAPS), p=trap_probs))

                detections[i, night, check] = trap
                previous_trap = trap

                if not shift_drawn and handling_median_m > 0:
                    magnitude = float(rng.rayleigh(rayleigh_scale))
                    angle = float(rng.uniform(0.0, 2.0 * math.pi))
                    shift = magnitude * np.array([math.cos(angle), math.sin(angle)])
                    shift_drawn = True

    return detections


def collapse_representations(detections: np.ndarray) -> dict[str, np.ndarray]:
    n, nights, checks = detections.shape
    first = np.full((n, nights), -1, dtype=np.int16)
    last = np.full((n, nights), -1, dtype=np.int16)

    for night in range(nights):
        block = detections[:, night, :]
        present = block >= 0
        for i in np.where(present.any(axis=1))[0]:
            idx = np.where(present[i])[0]
            first[i, night] = block[i, idx[0]]
            last[i, night] = block[i, idx[-1]]

    return {
        "first_nightly": first,
        "last_nightly": last,
        "check_level": detections.reshape(n, nights * checks),
    }


def prepare_history(history: np.ndarray) -> tuple[int, np.ndarray, np.ndarray]:
    history = history[(history >= 0).any(axis=1)]
    if history.shape[0] < 5:
        raise RuntimeError("fewer than five detected individuals")

    occasions = int(history.shape[1])
    no_capture = (history < 0).sum(axis=1).astype(float)
    counts = np.zeros((history.shape[0], len(TRAPS)), dtype=float)
    for i, row in enumerate(history):
        observed = row[row >= 0]
        counts[i] = np.bincount(observed, minlength=len(TRAPS))
    return occasions, no_capture, counts


def conditional_scr_fit(history: np.ndarray) -> dict[str, float | bool | int]:
    """Fit a static conditional SCR-like half-normal model.

    The detector model is a competing-hazard multi-catch model. Activity
    centres are integrated numerically over a common 100-m trap buffer. The
    likelihood is conditional on an individual being detected at least once,
    so the target is the detection spatial scale sigma rather than density.
    """
    occasions, no_capture, counts = prepare_history(history)
    n_individuals = len(no_capture)

    def objective(par: np.ndarray) -> float:
        lambda0 = math.exp(float(par[0]))
        sigma_m = math.exp(float(par[1]))
        weights = np.exp(-MASK_D2 / (2.0 * sigma_m * sigma_m))
        total = weights.sum(axis=1)
        hazard = lambda0 * total
        p_none = np.exp(-hazard)
        p_any = -np.expm1(-hazard)

        log_p_detector = (
            np.log(np.maximum(p_any, 1e-300))[:, None]
            - MASK_D2 / (2.0 * sigma_m * sigma_m)
            - np.log(np.maximum(total, 1e-300))[:, None]
        )
        log_history_by_mask = (
            np.log(np.maximum(p_none, 1e-300))[:, None] * no_capture[None, :]
            + log_p_detector @ counts.T
        )
        log_numerator = logsumexp(log_history_by_mask, axis=0) - math.log(len(MASK))
        detection_probability = 1.0 - p_none**occasions
        mean_detection_probability = float(detection_probability.mean())
        if mean_detection_probability <= 0:
            return 1e100
        log_denominator = math.log(mean_detection_probability)
        return -float(log_numerator.sum() - n_individuals * log_denominator)

    fit = minimize(
        objective,
        x0=np.log([0.04, 12.5]),
        method="L-BFGS-B",
        bounds=[(math.log(1e-4), math.log(2.0)), (math.log(2.0), math.log(60.0))],
        options={"maxiter": 150, "ftol": 1e-9},
    )
    return {
        "sigma_m": float(math.exp(float(fit.x[1]))),
        "lambda0": float(math.exp(float(fit.x[0]))),
        "converged": bool(fit.success),
        "detected_individuals": int(n_individuals),
        "negative_loglik": float(fit.fun),
    }


def aliasing_summary(detections: np.ndarray) -> dict[str, float | int | None]:
    distances: list[float] = []
    for i in range(detections.shape[0]):
        for night in range(detections.shape[1]):
            checks = np.where(detections[i, night] >= 0)[0]
            if len(checks) < 2:
                continue
            first = int(detections[i, night, checks[0]])
            last = int(detections[i, night, checks[-1]])
            distances.append(float(np.linalg.norm(TRAPS[first] - TRAPS[last])))

    if not distances:
        return {
            "repeat_capture_nights": 0,
            "one_spacing_change_fraction": None,
            "median_changed_distance_m": None,
            "median_all_distance_m": None,
        }
    changed = [d for d in distances if d >= TRAP_SPACING_M - 1e-12]
    return {
        "repeat_capture_nights": len(distances),
        "one_spacing_change_fraction": float(len(changed) / len(distances)),
        "median_changed_distance_m": float(np.median(changed)) if changed else None,
        "median_all_distance_m": float(np.median(distances)),
    }


def run_replicate(seed: int, handling_median_m: float, config: SimulationConfig) -> dict:
    detections = simulate_capture_array(seed, handling_median_m, config)
    representations = collapse_representations(detections)
    return {
        "seed": seed,
        "handling_median_m": handling_median_m,
        "handling_over_sigma": handling_median_m / config.true_sigma_m,
        "aliasing": aliasing_summary(detections),
        "fits": {
            name: conditional_scr_fit(history)
            for name, history in representations.items()
        },
    }


def mean(values: list[float]) -> float:
    return float(np.mean(np.asarray(values, dtype=float)))


def quantile(values: list[float], q: float) -> float:
    return float(np.quantile(np.asarray(values, dtype=float), q))


def summarize_cell(rows: list[dict], config: SimulationConfig) -> dict:
    out: dict[str, object] = {
        "handling_median_m": rows[0]["handling_median_m"],
        "handling_over_sigma": rows[0]["handling_over_sigma"],
        "replicates": len(rows),
    }

    alias_fraction = [r["aliasing"]["one_spacing_change_fraction"] for r in rows]
    alias_fraction = [float(x) for x in alias_fraction if x is not None]
    changed_median = [r["aliasing"]["median_changed_distance_m"] for r in rows]
    changed_median = [float(x) for x in changed_median if x is not None]
    repeat_n = [float(r["aliasing"]["repeat_capture_nights"]) for r in rows]
    out["aliasing"] = {
        "mean_one_spacing_change_fraction": mean(alias_fraction),
        "mean_repeat_capture_nights": mean(repeat_n),
        "median_of_replicate_changed_distance_medians": quantile(changed_median, 0.5),
    }

    fit_summary: dict[str, object] = {}
    for representation in ("first_nightly", "last_nightly", "check_level"):
        sigmas = [float(r["fits"][representation]["sigma_m"]) for r in rows]
        rel = [x / config.true_sigma_m - 1.0 for x in sigmas]
        fit_summary[representation] = {
            "mean_sigma_m": mean(sigmas),
            "median_sigma_m": quantile(sigmas, 0.5),
            "q025_sigma_m": quantile(sigmas, 0.025),
            "q975_sigma_m": quantile(sigmas, 0.975),
            "mean_relative_bias": mean(rel),
            "rmse_m": float(math.sqrt(mean([(x - config.true_sigma_m) ** 2 for x in sigmas]))),
            "material_abs_bias_fraction": mean([abs(x) >= 0.10 for x in rel]),
            "convergence_fraction": mean([bool(r["fits"][representation]["converged"]) for r in rows]),
        }
    out["fits"] = fit_summary

    first = [float(r["fits"]["first_nightly"]["sigma_m"]) for r in rows]
    last = [float(r["fits"]["last_nightly"]["sigma_m"]) for r in rows]
    check = [float(r["fits"]["check_level"]["sigma_m"]) for r in rows]
    out["contrasts"] = {
        "mean_last_vs_first_relative_difference": mean([l / f - 1.0 for f, l in zip(first, last)]),
        "mean_check_vs_first_relative_difference": mean([c / f - 1.0 for f, c in zip(first, check)]),
        "material_last_vs_first_fraction": mean([abs(l / f - 1.0) >= 0.10 for f, l in zip(first, last)]),
        "material_check_vs_first_fraction": mean([abs(c / f - 1.0) >= 0.10 for f, c in zip(first, check)]),
    }
    return out


def run_benchmark(replicates: int, seed: int) -> dict:
    config = SimulationConfig()
    handling_grid_m = [0.0, 3.125, 6.25, 9.375, 12.5, 15.625, 18.75]
    cells = []
    for cell_index, handling_median_m in enumerate(handling_grid_m):
        rows = [
            run_replicate(
                seed + cell_index * 1_000_003 + replicate,
                handling_median_m,
                config,
            )
            for replicate in range(replicates)
        ]
        cells.append(summarize_cell(rows, config))

    null_cell = cells[0]
    empirical_scale_cells = [c for c in cells if c["handling_median_m"] in (6.25, 12.5)]
    crossing = next(
        (
            c
            for c in cells
            if abs(c["contrasts"]["mean_last_vs_first_relative_difference"]) >= 0.10
        ),
        None,
    )

    return {
        "schema": "neon.san_jacinto_scr_sigma_downstream_simulation.v1",
        "seed": seed,
        "replicates_per_cell": replicates,
        "config": {
            "true_sigma_m": config.true_sigma_m,
            "trap_spacing_m": TRAP_SPACING_M,
            "lambda0_check": config.lambda0_check,
            "population_n": config.population_n,
            "nights": config.nights,
            "checks_per_night": config.checks_per_night,
            "stay_probability": config.stay_probability,
            "mask_buffer_m": MASK_BUFFER_M,
            "mask_step_m": MASK_STEP_M,
            "material_relative_difference": 0.10,
        },
        "empirical_reference": {
            "heldout_change_fraction": "approximately 0.69-0.73 among repeat-capture nights",
            "changed_night_median_first_last_distance_m": "approximately 12.5-14.0",
            "interpretation": "used to choose the trap-scale sensitivity range, not to identify handling displacement",
        },
        "cells": cells,
        "decision_summary": {
            "null_last_vs_first_abs_mean_difference_below_5pct": abs(
                null_cell["contrasts"]["mean_last_vs_first_relative_difference"]
            ) < 0.05,
            "first_material_crossing_handling_median_m": (
                crossing["handling_median_m"] if crossing else None
            ),
            "first_material_crossing_handling_over_sigma": (
                crossing["handling_over_sigma"] if crossing else None
            ),
            "one_spacing_cell": empirical_scale_cells[0],
            "two_spacing_cell": empirical_scale_cells[1],
        },
        "claim_boundary": {
            "simulation_establishes_empirical_handling_mechanism": False,
            "simulation_demonstrates_possible_downstream_sigma_distortion_under_capture_associated_displacement": True,
            "check_level_occasion_definition_is_not_assumed_to_remove_post_capture_state_change": True,
            "first_nightly_is_not_claimed_biologically_correct": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replicates", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20261003)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.replicates < 2:
        raise ValueError("replicates must be >=2")
    result = run_benchmark(args.replicates, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["decision_summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
