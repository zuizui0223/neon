from __future__ import annotations

import itertools
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


def packing_null(
    active_traps_xy: np.ndarray,
    n_individuals: int,
    *,
    replicates: int,
    seed: int,
) -> dict[str, Any]:
    traps=_validated_xy(active_traps_xy,"active_traps_xy")
    if isinstance(n_individuals,bool) or not isinstance(n_individuals,(int,np.integer)):
        raise ValueError("n_individuals must be an integer")
    n=int(n_individuals)
    if n < 2:
        raise ValueError("n_individuals must be at least 2")
    if n > len(traps):
        raise ValueError("n_individuals cannot exceed active trap count")
    if isinstance(replicates,bool) or not isinstance(replicates,(int,np.integer)) or replicates < 1:
        raise ValueError("replicates must be a positive integer")

    combinations=math.comb(len(traps),n)
    values: list[float]=[]
    if combinations <= int(replicates):
        mode="exact"
        for indices in itertools.combinations(range(len(traps)),n):
            values.append(mean_pairwise_distance(traps[list(indices)]))
    else:
        mode="monte_carlo"
        rng=np.random.default_rng(int(seed))
        for _ in range(int(replicates)):
            indices=rng.choice(len(traps),size=n,replace=False)
            values.append(mean_pairwise_distance(traps[indices]))

    arr=np.asarray(values,dtype=float)
    return {
        "mode":mode,
        "draw_count":len(values),
        "mean":float(np.mean(arr)),
        "sd":float(np.std(arr,ddof=0)),
        "min":float(np.min(arr)),
        "max":float(np.max(arr)),
    }


def packing_score(
    observed_xy: np.ndarray,
    active_traps_xy: np.ndarray,
    *,
    replicates: int,
    seed: int,
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
            "null_mode":None,
            "null_draw_count":0,
            "estimable":False,
            "non_estimable_reason":"fewer_than_two_individuals",
        }
    if n > len(traps):
        raise ValueError("observed individual count cannot exceed active trap count")

    observed_mpd=mean_pairwise_distance(observed)
    null=packing_null(traps,n,replicates=replicates,seed=seed)
    if null["sd"] <= 0.0:
        return {
            "n_individuals":n,
            "mpd_observed":observed_mpd,
            "mpd_null_mean":null["mean"],
            "mpd_null_sd":null["sd"],
            "packing_z":None,
            "null_mode":null["mode"],
            "null_draw_count":null["draw_count"],
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
        "null_draw_count":null["draw_count"],
        "estimable":True,
        "non_estimable_reason":None,
    }
