#!/usr/bin/env python3
"""Mechanical checks for multiscale density-accommodation metrics.

No biological data are read. The purpose is to verify that the preferred
between-individual footprint statistic is not mechanically inflated merely
because more individuals are sampled from an unchanged centre distribution.
"""
from __future__ import annotations

import itertools
import json
import math
from typing import Iterable, Sequence

Point = tuple[float, ...]


def _check(points: Sequence[Point]) -> None:
    if len(points) < 2:
        raise ValueError("at least two points are required")
    d = len(points[0])
    if d == 0 or any(len(p) != d for p in points):
        raise ValueError("points must have a common positive dimension")


def squared_distance(a: Point, b: Point) -> float:
    if len(a) != len(b):
        raise ValueError("dimension mismatch")
    return sum((x - y) ** 2 for x, y in zip(a, b))


def half_mean_pairwise_squared(points: Sequence[Point]) -> float:
    """Half the mean squared pairwise distance over unordered pairs.

    This equals the trace of the unbiased sample covariance matrix.
    """
    _check(points)
    n = len(points)
    total = 0.0
    pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += squared_distance(points[i], points[j])
            pairs += 1
    return 0.5 * total / pairs


def trace_unbiased_sample_covariance(points: Sequence[Point]) -> float:
    _check(points)
    n = len(points)
    d = len(points[0])
    mean = [sum(p[q] for p in points) / n for q in range(d)]
    return sum(
        sum((p[q] - mean[q]) ** 2 for p in points) / (n - 1)
        for q in range(d)
    )


def trace_population_denominator_variance(points: Sequence[Point]) -> float:
    """Trace variance using denominator n rather than n-1."""
    _check(points)
    n = len(points)
    d = len(points[0])
    mean = [sum(p[q] for p in points) / n for q in range(d)]
    return sum(
        sum((p[q] - mean[q]) ** 2 for p in points) / n
        for q in range(d)
    )


def within_individual_variance(captures: Sequence[Point]) -> float:
    """Trace of the unbiased within-individual covariance."""
    return half_mean_pairwise_squared(captures)


def centroid(captures: Sequence[Point]) -> Point:
    if not captures:
        raise ValueError("captures must not be empty")
    d = len(captures[0])
    if d == 0 or any(len(p) != d for p in captures):
        raise ValueError("captures must have a common positive dimension")
    n = len(captures)
    return tuple(sum(p[q] for p in captures) / n for q in range(d))


def observed_between_variance(individual_captures: Sequence[Sequence[Point]]) -> float:
    """Between-individual variance of estimated session centroids."""
    if len(individual_captures) < 2:
        raise ValueError("at least two individuals are required")
    return half_mean_pairwise_squared([centroid(x) for x in individual_captures])


def centroid_noise_correction(individual_captures: Sequence[Sequence[Point]]) -> float:
    """Mean W_i/k_i centroid-uncertainty contribution.

    For iid captures around individual-specific centres with finite second
    moments, W_i is unbiased for the within-individual covariance trace and
    the sample-centroid error contributes E[W_i]/k_i in expectation.
    """
    if len(individual_captures) < 2:
        raise ValueError("at least two individuals are required")
    vals = []
    for captures in individual_captures:
        if len(captures) < 2:
            raise ValueError("each primary individual requires at least two captures")
        vals.append(within_individual_variance(captures) / len(captures))
    return sum(vals) / len(vals)


def debiased_between_variance(individual_captures: Sequence[Sequence[Point]]) -> float:
    """Observed between-centroid variance minus mean centroid-noise contribution."""
    return (
        observed_between_variance(individual_captures)
        - centroid_noise_correction(individual_captures)
    )


def iid_pair_target(support: Sequence[Point]) -> float:
    """E[||X-X'||^2]/2 for iid draws from a finite uniform support."""
    if not support:
        raise ValueError("support must not be empty")
    vals = [
        0.5 * squared_distance(a, b)
        for a in support
        for b in support
    ]
    return sum(vals) / len(vals)


def exact_iid_expectation(
    support: Sequence[Point],
    sample_size: int,
    statistic,
) -> float:
    if sample_size < 2:
        raise ValueError("sample_size must be at least two")
    state_count = len(support) ** sample_size
    if state_count > 200_000:
        raise ValueError("exact enumeration intentionally capped at 200000 states")
    total = 0.0
    n = 0
    for idx in itertools.product(range(len(support)), repeat=sample_size):
        sample = [support[i] for i in idx]
        total += float(statistic(sample))
        n += 1
    return total / n


def mechanical_receipt() -> dict:
    # A simple fixed 2-D support. Drawing more individuals changes sample size
    # only; it does not change the underlying footprint distribution.
    support: list[Point] = [
        (0.0, 0.0),
        (10.0, 0.0),
        (0.0, 10.0),
        (10.0, 10.0),
    ]
    target = iid_pair_target(support)
    rows = []
    for m in (2, 3, 4, 5):
        u = exact_iid_expectation(support, m, half_mean_pairwise_squared)
        raw = exact_iid_expectation(
            support, m, trace_population_denominator_variance
        )
        rows.append(
            {
                "sample_size": m,
                "expected_half_pairwise_squared": u,
                "expected_raw_denominator_n_variance": raw,
                "u_minus_target": u - target,
                "raw_minus_target": raw - target,
            }
        )
    # Exact finite-state check of centroid-noise decomposition.
    # Two true centres are separated by 20 m; each individual is observed twice
    # with symmetric ±5 m x-error. Enumerating all observation combinations
    # allows an exact expectation check without biological data.
    true_centres: list[Point] = [(0.0, 0.0), (20.0, 0.0)]
    error_support: list[Point] = [(-5.0, 0.0), (5.0, 0.0)]
    true_between = half_mean_pairwise_squared(true_centres)
    obs_vals = []
    corr_vals = []
    deb_vals = []
    for e in itertools.product(range(len(error_support)), repeat=4):
        captures = []
        for i, mu in enumerate(true_centres):
            a = error_support[e[2 * i]]
            b = error_support[e[2 * i + 1]]
            captures.append([
                (mu[0] + a[0], mu[1] + a[1]),
                (mu[0] + b[0], mu[1] + b[1]),
            ])
        obs_vals.append(observed_between_variance(captures))
        corr_vals.append(centroid_noise_correction(captures))
        deb_vals.append(debiased_between_variance(captures))

    centroid_check = {
        "true_between_variance": true_between,
        "expected_observed_between_variance": sum(obs_vals) / len(obs_vals),
        "expected_centroid_noise_correction": sum(corr_vals) / len(corr_vals),
        "expected_debiased_between_variance": sum(deb_vals) / len(deb_vals),
    }

    return {
        "schema": "neon.multiscale_density.metric_mechanics.v1",
        "status": "synthetic_mechanical_check_only",
        "support_points": support,
        "iid_target": target,
        "sample_size_checks": rows,
        "centroid_noise_check": centroid_check,
        "conclusion": (
            "half mean pairwise squared distance is an unbiased sample-variance "
            "U-statistic whose expectation is invariant to sample size under an "
            "unchanged iid centre distribution; denominator-n variance is not. "
            "Subtracting mean W_i/k_i exactly removes centroid-noise inflation "
            "in the iid repeated-location benchmark."
        ),
        "biological_effect_values_opened": False,
    }


def main() -> int:
    receipt = mechanical_receipt()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
