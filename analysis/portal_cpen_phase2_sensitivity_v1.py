from __future__ import annotations

import itertools
import math
from typing import Callable, Iterable

import numpy as np


LONG_TERM_PORTAL_PLOTS={
    "3","4","10","11","14","15","16","17","19","21","23",
}


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1","true","t","yes","y"}


def long_term_portal_plots() -> set[str]:
    return set(LONG_TERM_PORTAL_PLOTS)


def select_portal_sensitivity_rows(
    rows: Iterable[dict],
    *,
    n_min: int,
    long_term_only: bool=False,
) -> list[dict]:
    flag_by_n={
        3:"sensitivity_n3_eligible",
        5:"primary_n5_eligible",
        8:"sensitivity_n8_eligible",
    }
    if n_min not in flag_by_n:
        raise ValueError("n_min must be one of 3, 5, 8")
    flag=flag_by_n[n_min]
    out=[]
    for raw in rows:
        row=dict(raw)
        if str(row.get("species","")).strip()!="Chaetodipus penicillatus":
            continue
        if not _truthy(row.get(flag)):
            continue
        try:
            n=int(row.get("n_unique_individuals"))
            packing=float(row.get("packing_z"))
        except (TypeError,ValueError):
            continue
        if n < n_min or not np.isfinite(packing):
            continue
        plot=str(row.get("plot_id","")).strip()
        if not plot:
            continue
        if long_term_only and plot not in LONG_TERM_PORTAL_PLOTS:
            continue
        treatment=str(row.get("treatment","")).strip()
        if treatment not in {"control","exclosure","kangaroo_rat_exclosure"}:
            continue
        row["n_unique_individuals"]=n
        row["packing_z"]=packing
        row["plot_id"]=plot
        out.append(row)
    return out


def filter_pit_reliable_captures(rows: Iterable[dict]) -> list[dict]:
    return [dict(row) for row in rows if _truthy(row.get("pit_tag",""))]


def _validated_xy(values: np.ndarray, label: str) -> np.ndarray:
    xy=np.asarray(values,dtype=float)
    if xy.ndim!=2 or xy.shape[1]!=2:
        raise ValueError(f"{label} must have shape (n, 2)")
    if not np.isfinite(xy).all():
        raise ValueError(f"{label} must be finite")
    return xy


def radius_of_gyration(points_xy: np.ndarray) -> float:
    xy=_validated_xy(points_xy,"points_xy")
    if len(xy)<2:
        raise ValueError("at least two points are required")
    centroid=np.mean(xy,axis=0)
    sq=np.sum((xy-centroid)**2,axis=1)
    return float(np.sqrt(np.mean(sq)))


def mean_nearest_neighbour_distance(points_xy: np.ndarray) -> float:
    xy=_validated_xy(points_xy,"points_xy")
    if len(xy)<2:
        raise ValueError("at least two points are required")
    diff=xy[:,None,:]-xy[None,:,:]
    dist=np.sqrt(np.sum(diff*diff,axis=2))
    np.fill_diagonal(dist,np.inf)
    return float(np.mean(np.min(dist,axis=1)))


def standardized_geometry_metric(
    observed_xy: np.ndarray,
    active_traps_xy: np.ndarray,
    *,
    metric: Callable[[np.ndarray],float],
    replicates: int,
    seed: int,
) -> dict:
    observed=_validated_xy(observed_xy,"observed_xy")
    traps=_validated_xy(active_traps_xy,"active_traps_xy")
    n=len(observed)
    if n<2:
        return {
            "estimable":False,
            "non_estimable_reason":"fewer_than_two_individuals",
            "observed":None,
            "null_mean":None,
            "null_sd":None,
            "z":None,
            "null_mode":None,
            "null_draw_count":0,
        }
    if n>len(traps):
        raise ValueError("observed individual count cannot exceed active trap count")
    if replicates<1:
        raise ValueError("replicates must be positive")

    observed_value=float(metric(observed))
    combinations=math.comb(len(traps),n)
    values=[]
    if combinations<=replicates:
        mode="exact"
        for indices in itertools.combinations(range(len(traps)),n):
            values.append(float(metric(traps[list(indices)])))
    else:
        mode="monte_carlo"
        rng=np.random.default_rng(int(seed))
        for _ in range(int(replicates)):
            indices=rng.choice(len(traps),size=n,replace=False)
            values.append(float(metric(traps[indices])))

    arr=np.asarray(values,dtype=float)
    mean=float(np.mean(arr))
    sd=float(np.std(arr,ddof=0))
    if sd<=0:
        return {
            "estimable":False,
            "non_estimable_reason":"zero_null_variance",
            "observed":observed_value,
            "null_mean":mean,
            "null_sd":sd,
            "z":None,
            "null_mode":mode,
            "null_draw_count":len(values),
        }
    return {
        "estimable":True,
        "non_estimable_reason":None,
        "observed":observed_value,
        "null_mean":mean,
        "null_sd":sd,
        "z":(observed_value-mean)/sd,
        "null_mode":mode,
        "null_draw_count":len(values),
    }


def _opposite_sign(a: float, b: float) -> bool:
    return (a>0 and b<0) or (a<0 and b>0)


def direction_reversal_summary(
    primary: dict[str,float],
    checks: Iterable[dict],
) -> dict:
    rows=[dict(row) for row in checks]
    return {
        "treatment_reversal_labels":[
            str(row["label"])
            for row in rows
            if _opposite_sign(float(primary["treatment"]),float(row["treatment"]))
        ],
        "interaction_reversal_labels":[
            str(row["label"])
            for row in rows
            if _opposite_sign(float(primary["interaction"]),float(row["interaction"]))
        ],
    }
