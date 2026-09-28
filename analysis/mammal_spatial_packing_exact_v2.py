from __future__ import annotations

import math
from typing import Any

import numpy as np


def _validated_xy(values: np.ndarray, label: str) -> np.ndarray:
    xy=np.asarray(values,dtype=float)
    if xy.ndim != 2 or xy.shape[1] != 2:
        raise ValueError(f"{label} must have shape (n, 2)")
    if not np.isfinite(xy).all():
        raise ValueError(f"{label} must be finite")
    return xy


def mean_pairwise_distance(points_xy: np.ndarray) -> float:
    xy=_validated_xy(points_xy,"points_xy")
    n=len(xy)
    if n < 2:
        raise ValueError("at least two points are required")
    diff=xy[:,None,:]-xy[None,:,:]
    dist=np.sqrt(np.sum(diff*diff,axis=2))
    return float(np.mean(dist[np.triu_indices(n,1)]))


def _inclusion_probability(n: int, m: int, k: int) -> float:
    if n < k or m < k:
        return 0.0
    return math.comb(n,k)/math.comb(m,k)


def exact_null_moments(
    active_traps_xy: np.ndarray,
    n_individuals: int,
) -> dict[str, Any]:
    """Exact moments of MPD for a simple random subset of active traps.

    If S is a uniformly sampled n-subset of M trap locations and U is the
    mean pairwise distance among traps in S, E[U] and Var(U) can be computed
    from the finite trap-distance population. No Monte Carlo approximation is
    needed.
    """
    traps=_validated_xy(active_traps_xy,"active_traps_xy")
    if isinstance(n_individuals,bool) or not isinstance(
        n_individuals,(int,np.integer)
    ):
        raise ValueError("n_individuals must be an integer")
    n=int(n_individuals)
    m=len(traps)
    if n < 2:
        raise ValueError("n_individuals must be at least 2")
    if n > m:
        raise ValueError("n_individuals cannot exceed active trap count")

    diff=traps[:,None,:]-traps[None,:,:]
    distances=np.sqrt(np.sum(diff*diff,axis=2))
    upper=np.triu_indices(m,1)
    edge_values=distances[upper]

    s1=float(np.sum(edge_values))
    s2=float(np.sum(edge_values*edge_values))
    pair_population=math.comb(m,2)
    sampled_pairs=math.comb(n,2)

    # For unordered pairs of trap-pair edges:
    # A = products for two edges sharing exactly one trap.
    # D = products for two disjoint edges.
    incident_sum=np.sum(distances,axis=1)
    incident_sq_sum=np.sum(distances*distances,axis=1)
    adjacent_product_sum=0.5*float(
        np.sum(incident_sum*incident_sum-incident_sq_sum)
    )
    all_distinct_edge_product_sum=0.5*(s1*s1-s2)
    disjoint_product_sum=(
        all_distinct_edge_product_sum-adjacent_product_sum
    )

    p2=_inclusion_probability(n,m,2)
    p3=_inclusion_probability(n,m,3)
    p4=_inclusion_probability(n,m,4)

    mean=s1/pair_population
    second_moment=(
        p2*s2
        + 2.0*p3*adjacent_product_sum
        + 2.0*p4*disjoint_product_sum
    )/(sampled_pairs*sampled_pairs)
    variance=second_moment-mean*mean

    tolerance=1e-10*max(1.0,abs(second_moment),mean*mean)
    if variance < -tolerance:
        raise ArithmeticError(
            f"negative exact variance beyond tolerance: {variance}"
        )
    variance=max(0.0,variance)

    return {
        "mode":"exact_finite_population_moments",
        "draw_count":0,
        "trap_count":m,
        "n_individuals":n,
        "pair_population":pair_population,
        "sampled_pair_count":sampled_pairs,
        "mean":float(mean),
        "sd":float(math.sqrt(variance)),
        "variance":float(variance),
    }


def packing_score_exact(
    observed_xy: np.ndarray,
    active_traps_xy: np.ndarray,
) -> dict[str, Any]:
    observed=_validated_xy(observed_xy,"observed_xy")
    traps=_validated_xy(active_traps_xy,"active_traps_xy")
    n=len(observed)

    if n < 2:
        return {
            "n_individuals":n,
            "mpd_observed":None,
            "mpd_null_mean":None,
            "mpd_null_sd":None,
            "packing_z":None,
            "null_mode":"exact_finite_population_moments",
            "null_draw_count":0,
            "estimable":False,
            "non_estimable_reason":"fewer_than_two_individuals",
        }
    if n > len(traps):
        raise ValueError("observed individual count cannot exceed active trap count")

    # The exact finite-population null is a simple random subset of trap
    # locations. Duplicate observed trap locations violate that support.
    if len(np.unique(observed,axis=0)) != n:
        return {
            "n_individuals":n,
            "mpd_observed":mean_pairwise_distance(observed),
            "mpd_null_mean":None,
            "mpd_null_sd":None,
            "packing_z":None,
            "null_mode":"exact_finite_population_moments",
            "null_draw_count":0,
            "estimable":False,
            "non_estimable_reason":"duplicate_observed_trap_locations",
        }

    null=exact_null_moments(traps,n)
    observed_mpd=mean_pairwise_distance(observed)
    if null["sd"] <= 0.0:
        return {
            "n_individuals":n,
            "mpd_observed":observed_mpd,
            "mpd_null_mean":null["mean"],
            "mpd_null_sd":null["sd"],
            "packing_z":None,
            "null_mode":null["mode"],
            "null_draw_count":0,
            "estimable":False,
            "non_estimable_reason":"zero_null_variance",
        }

    return {
        "n_individuals":n,
        "mpd_observed":observed_mpd,
        "mpd_null_mean":null["mean"],
        "mpd_null_sd":null["sd"],
        "packing_z":(observed_mpd-null["mean"])/null["sd"],
        "null_mode":null["mode"],
        "null_draw_count":0,
        "estimable":True,
        "non_estimable_reason":None,
    }
