#!/usr/bin/env python3
"""Frozen coordinate metrics for multiscale density accommodation.

Pure functions only. This module does not download or read NEON response data.
It defines the primary nominal 10x10 trap-lattice geometry and the W/B
estimators to be used if the remaining pre-effect gates pass.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

COORD_RE = re.compile(r"^([A-Ja-j])0?([1-9]|10)$")
SPACING_M = 10.0
MIN_REPEAT_SUPPORTED_INDIVIDUALS = 5

Point = tuple[float, float]


@dataclass(frozen=True)
class IndividualSpatialMetric:
    tag_id: str
    k_nights: int
    within_variance_m2: float
    centroid_m: Point


def squared_distance(a: Point, b: Point) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def half_mean_pairwise_squared(points: Sequence[Point]) -> float:
    if len(points) < 2:
        raise ValueError("at least two points are required")
    total = 0.0
    n_pairs = 0
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            total += squared_distance(points[i], points[j])
            n_pairs += 1
    return 0.5 * total / n_pairs


def parse_standard_trap_coordinate(value: str) -> Point | None:
    """Map A1..J10 to a nominal 10 m square lattice.

    Axis orientation is arbitrary for Euclidean squared distances. X/unknown,
    off-grid, and malformed coordinates return None rather than being repaired.
    """
    text = str(value or "").strip()
    match = COORD_RE.fullmatch(text)
    if not match:
        return None
    row = ord(match.group(1).upper()) - ord("A")
    col = int(match.group(2)) - 1
    return row * SPACING_M, col * SPACING_M


def _centroid(points: Sequence[Point]) -> Point:
    if not points:
        raise ValueError("cannot calculate centroid of empty point set")
    return (
        sum(x for x, _ in points) / len(points),
        sum(y for _, y in points) / len(points),
    )


def individual_metric(
    tag_id: str,
    night_coordinate_records: Iterable[tuple[str, str]],
) -> IndividualSpatialMetric | None:
    """Calculate one individual's metric from distinct trapping nights.

    Duplicate rows with the same night and same coordinate are collapsed.
    If one individual has >1 distinct valid coordinate on the same night, the
    individual-session is structurally inconsistent and returns None.
    Invalid/unknown coordinates are ignored. At least two coordinate-bearing
    distinct nights are required.
    """
    by_night: dict[str, set[Point]] = {}
    for night, coord in night_coordinate_records:
        night = str(night or "").strip()
        point = parse_standard_trap_coordinate(coord)
        if not night or point is None:
            continue
        by_night.setdefault(night, set()).add(point)

    points: list[Point] = []
    for night in sorted(by_night):
        coords = by_night[night]
        if len(coords) > 1:
            return None
        points.append(next(iter(coords)))

    if len(points) < 2:
        return None

    return IndividualSpatialMetric(
        tag_id=str(tag_id),
        k_nights=len(points),
        within_variance_m2=half_mean_pairwise_squared(points),
        centroid_m=_centroid(points),
    )


def session_metrics(
    individual_records: Mapping[str, Iterable[tuple[str, str]]],
    *,
    minimum_individuals: int = MIN_REPEAT_SUPPORTED_INDIVIDUALS,
) -> dict:
    """Calculate matched-cohort W, B_observed, and B_debiased.

    W is the equal-individual mean of unbiased within-individual covariance
    traces. B_observed is the unbiased covariance trace of the same individuals'
    session centroids. The predeclared centroid-noise correction is
    mean_i(W_i / k_i).
    """
    metrics = []
    excluded = []
    for tag_id in sorted(individual_records):
        metric = individual_metric(tag_id, individual_records[tag_id])
        if metric is None:
            excluded.append(tag_id)
        else:
            metrics.append(metric)

    if len(metrics) < minimum_individuals:
        raise ValueError(
            f"need at least {minimum_individuals} repeat-supported individuals; "
            f"got {len(metrics)}"
        )

    W = sum(x.within_variance_m2 for x in metrics) / len(metrics)
    B_observed = half_mean_pairwise_squared([x.centroid_m for x in metrics])
    correction = sum(
        x.within_variance_m2 / x.k_nights for x in metrics
    ) / len(metrics)
    B_debiased = B_observed - correction

    return {
        "n_individuals": len(metrics),
        "individuals": [
            {
                "tag_id": x.tag_id,
                "k_nights": x.k_nights,
                "within_variance_m2": x.within_variance_m2,
                "centroid_m": list(x.centroid_m),
            }
            for x in metrics
        ],
        "excluded_or_inconsistent_tag_ids": excluded,
        "W_m2": W,
        "B_observed_m2": B_observed,
        "centroid_noise_correction_m2": correction,
        "B_debiased_m2": B_debiased,
    }
