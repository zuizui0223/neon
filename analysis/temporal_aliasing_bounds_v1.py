from __future__ import annotations

import math
from typing import Iterable, Sequence

import numpy as np


def _point(x: Sequence[float]) -> np.ndarray:
    p=np.asarray(x,dtype=float)
    if p.ndim!=1 or len(p)==0 or not np.isfinite(p).all():
        raise ValueError("point must be a finite one-dimensional coordinate")
    return p


def euclidean(a: Sequence[float], b: Sequence[float]) -> float:
    x=_point(a)
    y=_point(b)
    if x.shape!=y.shape:
        raise ValueError("points must have matching dimensions")
    return float(np.linalg.norm(x-y))


def movement_representative_sensitivity(
    first_t: Sequence[float],
    first_u: Sequence[float],
    last_t: Sequence[float],
    last_u: Sequence[float],
) -> dict[str,float]:
    d_first=euclidean(first_t,first_u)
    d_last=euclidean(last_t,last_u)
    delta_t=euclidean(first_t,last_t)
    delta_u=euclidean(first_u,last_u)
    observed=abs(d_first-d_last)
    bound=delta_t+delta_u
    return {
        "movement_first":d_first,
        "movement_last":d_last,
        "absolute_difference":observed,
        "within_t":delta_t,
        "within_u":delta_u,
        "bound":bound,
        "slack":bound-observed,
    }


def mean_pairwise_distance(points: Iterable[Sequence[float]]) -> float:
    xy=np.asarray(list(points),dtype=float)
    if xy.ndim!=2 or len(xy)<2 or not np.isfinite(xy).all():
        raise ValueError("points must be a finite n x d array with n>=2")
    diff=xy[:,None,:]-xy[None,:,:]
    distances=np.sqrt(np.sum(diff*diff,axis=2))
    return float(np.mean(distances[np.triu_indices(len(xy),1)]))


def mpd_representative_sensitivity(
    first_points: Iterable[Sequence[float]],
    last_points: Iterable[Sequence[float]],
) -> dict[str,float]:
    first=np.asarray(list(first_points),dtype=float)
    last=np.asarray(list(last_points),dtype=float)
    if (
        first.ndim!=2
        or last.ndim!=2
        or first.shape!=last.shape
        or len(first)<2
        or not np.isfinite(first).all()
        or not np.isfinite(last).all()
    ):
        raise ValueError("first and last must be matching finite n x d arrays with n>=2")

    mpd_first=mean_pairwise_distance(first)
    mpd_last=mean_pairwise_distance(last)
    delta=np.sqrt(np.sum((first-last)**2,axis=1))
    observed=abs(mpd_first-mpd_last)
    bound=2.0*float(np.mean(delta))
    return {
        "n":int(len(first)),
        "mpd_first":mpd_first,
        "mpd_last":mpd_last,
        "absolute_difference":observed,
        "mean_within_span":float(np.mean(delta)),
        "bound":bound,
        "slack":bound-observed,
    }


def standardized_packing_sensitivity_bound(
    mean_within_span: float,
    null_sd: float,
) -> float:
    a=float(mean_within_span)
    s=float(null_sd)
    if not math.isfinite(a) or a<0:
        raise ValueError("mean_within_span must be finite and nonnegative")
    if not math.isfinite(s) or s<=0:
        raise ValueError("null_sd must be finite and positive")
    return 2.0*a/s
