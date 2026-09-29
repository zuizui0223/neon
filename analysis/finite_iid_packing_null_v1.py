from __future__ import annotations

import math
from typing import Any

import numpy as np


def validate_xy(values: np.ndarray, label: str) -> np.ndarray:
    xy=np.asarray(values,dtype=float)
    if xy.ndim != 2 or xy.shape[1] != 2:
        raise ValueError(f"{label} must have shape (n, 2)")
    if not np.isfinite(xy).all():
        raise ValueError(f"{label} must be finite")
    return xy


def mean_pairwise_distance(points_xy: np.ndarray) -> float:
    xy=validate_xy(points_xy,"points_xy")
    n=len(xy)
    if n<2:
        raise ValueError("at least two points are required")
    diff=xy[:,None,:]-xy[None,:,:]
    d=np.sqrt(np.sum(diff*diff,axis=2))
    return float(np.mean(d[np.triu_indices(n,1)]))


def exact_iid_mpd_null_moments(
    support_xy: np.ndarray,
    n_individuals: int,
) -> dict[str,Any]:
    """Exact MPD moments for iid draws with replacement from finite support.

    U_N = mean_{i<j} h(X_i,X_j), where X_i are iid uniform over the
    support points and h is Euclidean distance.

    Disjoint pair kernels are independent. Pair kernels sharing one
    individual have covariance E[h(X1,X2)h(X1,X3)] - E[h]^2.
    """
    support=validate_xy(support_xy,"support_xy")
    if isinstance(n_individuals,bool) or not isinstance(
        n_individuals,(int,np.integer)
    ):
        raise ValueError("n_individuals must be an integer")
    n=int(n_individuals)
    if n<2:
        raise ValueError("n_individuals must be at least 2")
    m=len(support)
    if m<2:
        raise ValueError("support must contain at least two points")

    diff=support[:,None,:]-support[None,:,:]
    distances=np.sqrt(np.sum(diff*diff,axis=2))

    mu=float(np.mean(distances))
    second=float(np.mean(distances*distances))
    var_h=max(0.0,second-mu*mu)

    row_sums=np.sum(distances,axis=1)
    shared_second=float(np.sum(row_sums*row_sums)/(m**3))
    cov_shared=shared_second-mu*mu

    pair_count=math.comb(n,2)
    triple_count=math.comb(n,3) if n>=3 else 0
    variance=(
        pair_count*var_h
        + 6.0*triple_count*cov_shared
    )/(pair_count*pair_count)

    tolerance=1e-12*max(1.0,abs(second),mu*mu)
    if variance < -tolerance:
        raise ArithmeticError(
            f"negative iid MPD variance beyond tolerance: {variance}"
        )
    variance=max(0.0,variance)

    return {
        "mode":"exact_iid_uniform_finite_support_with_replacement",
        "support_count":m,
        "n_individuals":n,
        "pair_count":pair_count,
        "mean":mu,
        "variance":float(variance),
        "sd":float(math.sqrt(variance)),
        "kernel_variance":var_h,
        "shared_pair_covariance":float(cov_shared),
    }


def packing_score_iid_exact(
    observed_xy: np.ndarray,
    support_xy: np.ndarray,
) -> dict[str,Any]:
    observed=validate_xy(observed_xy,"observed_xy")
    n=len(observed)
    if n<2:
        return {
            "estimable":False,
            "non_estimable_reason":"fewer_than_two_individuals",
            "n_individuals":n,
            "packing_z":None,
        }

    null=exact_iid_mpd_null_moments(support_xy,n)
    observed_mpd=mean_pairwise_distance(observed)
    if null["sd"]<=0:
        return {
            "estimable":False,
            "non_estimable_reason":"zero_null_variance",
            "n_individuals":n,
            "mpd_observed":observed_mpd,
            "mpd_null_mean":null["mean"],
            "mpd_null_sd":null["sd"],
            "packing_z":None,
        }

    return {
        "estimable":True,
        "non_estimable_reason":None,
        "n_individuals":n,
        "mpd_observed":observed_mpd,
        "mpd_null_mean":null["mean"],
        "mpd_null_sd":null["sd"],
        "packing_z":float((observed_mpd-null["mean"])/null["sd"]),
        "null_mode":null["mode"],
    }


def canonical_grid_7x7(spacing_m: float=6.25) -> dict[str,tuple[float,float]]:
    if not math.isfinite(spacing_m) or spacing_m<=0:
        raise ValueError("spacing_m must be finite and positive")
    return {
        f"{row}{col}":((col-1)*spacing_m,row_index*spacing_m)
        for row_index,row in enumerate("ABCDEFG")
        for col in range(1,8)
    }
