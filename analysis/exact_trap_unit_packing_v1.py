from __future__ import annotations

import math
from typing import Any, Iterable

import numpy as np


def _xy(values: np.ndarray, label: str) -> np.ndarray:
    arr=np.asarray(values,dtype=float)
    if arr.ndim!=2 or arr.shape[1]!=2:
        raise ValueError(f"{label} must have shape (n,2)")
    if not np.isfinite(arr).all():
        raise ValueError(f"{label} must be finite")
    return arr


def mean_pairwise_distance(points_xy: np.ndarray) -> float:
    points=_xy(points_xy,"points_xy")
    n=len(points)
    if n<2:
        raise ValueError("at least two points are required")
    diff=points[:,None,:]-points[None,:,:]
    dist=np.sqrt(np.sum(diff*diff,axis=2))
    return float(np.mean(dist[np.triu_indices(n,1)]))


def _p_inclusion(n: int, m: int, k: int) -> float:
    if n<k or m<k:
        return 0.0
    return math.comb(n,k)/math.comb(m,k)


def exact_mpd_null_moments(active_trap_xy: np.ndarray, n: int) -> dict[str,Any]:
    """Exact MPD moments for sampling n distinct trap units without replacement.

    Distinct trap units may share identical XY coordinates. This is intentional
    for colocated detector designs such as multiple trap types at one grid point.
    """
    traps=_xy(active_trap_xy,"active_trap_xy")
    m=len(traps)
    if isinstance(n,bool) or not isinstance(n,(int,np.integer)):
        raise ValueError("n must be an integer")
    n=int(n)
    if n<2:
        raise ValueError("n must be at least 2")
    if n>m:
        raise ValueError("n cannot exceed active trap-unit count")

    diff=traps[:,None,:]-traps[None,:,:]
    d=np.sqrt(np.sum(diff*diff,axis=2))
    upper=np.triu_indices(m,1)
    edge=d[upper]

    s1=float(np.sum(edge))
    s2=float(np.sum(edge*edge))
    k_pairs=math.comb(m,2)
    q=math.comb(n,2)

    incident_sum=np.sum(d,axis=1)
    incident_sq=np.sum(d*d,axis=1)
    adjacent_products=0.5*float(
        np.sum(incident_sum*incident_sum-incident_sq)
    )
    all_edge_pair_products=0.5*(s1*s1-s2)
    disjoint_products=all_edge_pair_products-adjacent_products

    p2=_p_inclusion(n,m,2)
    p3=_p_inclusion(n,m,3)
    p4=_p_inclusion(n,m,4)

    mean=s1/k_pairs
    second=(
        p2*s2
        + 2.0*p3*adjacent_products
        + 2.0*p4*disjoint_products
    )/(q*q)
    variance=second-mean*mean
    tol=1e-10*max(1.0,abs(second),mean*mean)
    if variance < -tol:
        raise ArithmeticError(f"negative variance beyond tolerance: {variance}")
    variance=max(0.0,variance)

    return {
        "mode":"exact_distinct_trap_units_finite_population",
        "trap_unit_count":m,
        "n_individuals":n,
        "null_mean_mpd":float(mean),
        "null_sd_mpd":float(math.sqrt(variance)),
        "null_variance_mpd":float(variance),
    }


def packing_from_trap_units(
    *,
    active_unit_ids: Iterable[str],
    active_unit_xy: np.ndarray,
    observed_unit_ids: Iterable[str],
) -> dict[str,Any]:
    ids=[str(x) for x in active_unit_ids]
    xy=_xy(active_unit_xy,"active_unit_xy")
    if len(ids)!=len(xy):
        raise ValueError("active_unit_ids and active_unit_xy length mismatch")
    if len(set(ids))!=len(ids):
        raise ValueError("active trap-unit IDs must be unique")

    observed=[str(x) for x in observed_unit_ids]
    n=len(observed)
    if n<2:
        return {
            "estimable":False,
            "non_estimable_reason":"fewer_than_two_individuals",
            "n_individuals":n,
        }
    if len(set(observed))!=n:
        return {
            "estimable":False,
            "non_estimable_reason":"duplicate_observed_trap_unit_id",
            "n_individuals":n,
        }

    index={unit:i for i,unit in enumerate(ids)}
    missing=sorted(set(observed)-set(index))
    if missing:
        return {
            "estimable":False,
            "non_estimable_reason":"observed_trap_unit_not_active",
            "missing_unit_ids":missing,
            "n_individuals":n,
        }

    # Duplicate XY is allowed here because multiple distinct trap units may be
    # colocated at a grid point.
    observed_xy=np.asarray([xy[index[unit]] for unit in observed],dtype=float)
    observed_mpd=mean_pairwise_distance(observed_xy)
    null=exact_mpd_null_moments(xy,n)

    if null["null_sd_mpd"]<=0.0:
        return {
            "estimable":False,
            "non_estimable_reason":"zero_null_variance",
            "n_individuals":n,
            "mpd_observed":observed_mpd,
            **null,
        }

    return {
        "estimable":True,
        "non_estimable_reason":None,
        "n_individuals":n,
        "mpd_observed":observed_mpd,
        "packing_z":(
            observed_mpd-null["null_mean_mpd"]
        )/null["null_sd_mpd"],
        **null,
    }
