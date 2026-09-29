from __future__ import annotations

import math
from collections import Counter
from typing import Any

import numpy as np


def _xy(values: np.ndarray, label: str) -> np.ndarray:
    out=np.asarray(values,dtype=float)
    if out.ndim!=2 or out.shape[1]!=2:
        raise ValueError(f"{label} must have shape (n, 2)")
    if not np.isfinite(out).all():
        raise ValueError(f"{label} must be finite")
    return out


def mean_pairwise_distance(points_xy: np.ndarray) -> float:
    xy=_xy(points_xy,"points_xy")
    n=len(xy)
    if n<2:
        raise ValueError("at least two points are required")
    diff=xy[:,None,:]-xy[None,:,:]
    dist=np.sqrt(np.sum(diff*diff,axis=2))
    return float(np.mean(dist[np.triu_indices(n,1)]))


def _p_inclusion(n: int, m: int, k: int) -> float:
    if n<k or m<k:
        return 0.0
    return math.comb(n,k)/math.comb(m,k)


def exact_slot_null_moments(
    active_slot_xy: np.ndarray,
    n_individuals: int,
) -> dict[str,Any]:
    """Exact MPD moments under uniform sampling of finite trap slots.

    Rows of active_slot_xy are trap slots, not necessarily unique
    coordinates. If two traps occupy one station, include that station
    coordinate twice. Sampling is without replacement over slots, while
    zero distance between co-located slots is retained in the null.
    """
    slots=_xy(active_slot_xy,"active_slot_xy")
    if isinstance(n_individuals,bool) or not isinstance(
        n_individuals,(int,np.integer)
    ):
        raise ValueError("n_individuals must be an integer")
    n=int(n_individuals)
    m=len(slots)
    if n<2:
        raise ValueError("n_individuals must be at least 2")
    if n>m:
        raise ValueError("n_individuals cannot exceed active slot count")

    diff=slots[:,None,:]-slots[None,:,:]
    distances=np.sqrt(np.sum(diff*diff,axis=2))
    upper=np.triu_indices(m,1)
    edge=distances[upper]

    s1=float(np.sum(edge))
    s2=float(np.sum(edge*edge))
    pair_population=math.comb(m,2)
    sampled_pairs=math.comb(n,2)

    incident_sum=np.sum(distances,axis=1)
    incident_sq=np.sum(distances*distances,axis=1)
    adjacent=0.5*float(np.sum(incident_sum*incident_sum-incident_sq))
    all_edge_pairs=0.5*(s1*s1-s2)
    disjoint=all_edge_pairs-adjacent

    p2=_p_inclusion(n,m,2)
    p3=_p_inclusion(n,m,3)
    p4=_p_inclusion(n,m,4)

    mean=s1/pair_population
    second=(
        p2*s2
        + 2.0*p3*adjacent
        + 2.0*p4*disjoint
    )/(sampled_pairs*sampled_pairs)
    variance=second-mean*mean
    tolerance=1e-10*max(1.0,abs(second),mean*mean)
    if variance < -tolerance:
        raise ArithmeticError(
            f"negative exact variance beyond tolerance: {variance}"
        )
    variance=max(0.0,variance)

    return {
        "mode":"exact_finite_trap_slot_moments",
        "slot_count":m,
        "unique_coordinate_count":len({
            (float(x),float(y)) for x,y in slots
        }),
        "n_individuals":n,
        "pair_population":pair_population,
        "sampled_pair_count":sampled_pairs,
        "mean":float(mean),
        "variance":float(variance),
        "sd":float(math.sqrt(variance)),
    }


def _multiplicity(xy: np.ndarray) -> Counter[tuple[float,float]]:
    return Counter((float(x),float(y)) for x,y in xy)


def support_check(
    observed_xy: np.ndarray,
    active_slot_xy: np.ndarray,
) -> dict[str,Any]:
    observed=_xy(observed_xy,"observed_xy")
    slots=_xy(active_slot_xy,"active_slot_xy")

    observed_counts=_multiplicity(observed)
    slot_counts=_multiplicity(slots)
    unsupported={
        f"{coord[0]},{coord[1]}":{
            "observed":count,
            "capacity":slot_counts.get(coord,0),
        }
        for coord,count in observed_counts.items()
        if count>slot_counts.get(coord,0)
    }
    return {
        "supported":not unsupported and len(observed)<=len(slots),
        "observed_count":len(observed),
        "slot_count":len(slots),
        "unsupported_coordinates":unsupported,
        "maximum_observed_coordinate_multiplicity":(
            max(observed_counts.values()) if observed_counts else 0
        ),
        "maximum_slot_coordinate_capacity":(
            max(slot_counts.values()) if slot_counts else 0
        ),
    }


def packing_score_exact_slots(
    observed_xy: np.ndarray,
    active_slot_xy: np.ndarray,
) -> dict[str,Any]:
    observed=_xy(observed_xy,"observed_xy")
    slots=_xy(active_slot_xy,"active_slot_xy")
    n=len(observed)

    if n<2:
        return {
            "estimable":False,
            "non_estimable_reason":"fewer_than_two_individuals",
            "n_individuals":n,
            "null_mode":"exact_finite_trap_slot_moments",
        }

    support=support_check(observed,slots)
    if not support["supported"]:
        return {
            "estimable":False,
            "non_estimable_reason":"observed_coordinate_multiplicity_exceeds_trap_slot_capacity",
            "n_individuals":n,
            "support":support,
            "null_mode":"exact_finite_trap_slot_moments",
        }

    null=exact_slot_null_moments(slots,n)
    observed_mpd=mean_pairwise_distance(observed)
    if null["sd"]<=0:
        return {
            "estimable":False,
            "non_estimable_reason":"zero_null_variance",
            "n_individuals":n,
            "mpd_observed":observed_mpd,
            "mpd_null_mean":null["mean"],
            "mpd_null_sd":null["sd"],
            "support":support,
            "null_mode":null["mode"],
        }

    return {
        "estimable":True,
        "non_estimable_reason":None,
        "n_individuals":n,
        "mpd_observed":observed_mpd,
        "mpd_null_mean":null["mean"],
        "mpd_null_sd":null["sd"],
        "packing_z":(observed_mpd-null["mean"])/null["sd"],
        "support":support,
        "null_mode":null["mode"],
    }
