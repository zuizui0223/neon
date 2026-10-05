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
    return {
        "schema": "neon.multiscale_density.metric_mechanics.v1",
        "status": "synthetic_mechanical_check_only",
        "support_points": support,
        "iid_target": target,
        "sample_size_checks": rows,
        "conclusion": (
            "half mean pairwise squared distance is an unbiased sample-variance "
            "U-statistic whose expectation is invariant to sample size under an "
            "unchanged iid centre distribution; denominator-n variance is not"
        ),
        "biological_effect_values_opened": False,
    }


def main() -> int:
    receipt = mechanical_receipt()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
