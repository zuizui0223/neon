from __future__ import annotations

from typing import Iterable

import numpy as np


def z_log_n(values: Iterable[float]) -> np.ndarray:
    x=np.asarray(list(values),dtype=float)
    if x.ndim != 1 or x.size < 2:
        raise ValueError("values must contain at least two observations")
    if not np.isfinite(x).all() or np.any(x <= 0):
        raise ValueError("N values must be finite and positive")
    logx=np.log(x)
    sd=float(np.std(logx,ddof=0))
    if sd <= 0:
        raise ValueError("log(N) has zero population standard deviation")
    return (logx-float(np.mean(logx)))/sd


def assert_full_rank(X: np.ndarray, columns: Iterable[str]) -> None:
    matrix=np.asarray(X,dtype=float)
    names=list(columns)
    if matrix.ndim != 2:
        raise ValueError("design matrix must be two-dimensional")
    if matrix.shape[1] != len(names):
        raise ValueError("column names do not match design matrix width")
    if not np.isfinite(matrix).all():
        raise ValueError("design matrix must be finite")
    rank=int(np.linalg.matrix_rank(matrix))
    if rank != matrix.shape[1]:
        raise ValueError(
            f"design matrix rank deficient: rank={rank}, columns={matrix.shape[1]}, names={names}"
        )


def bh_adjust(p_values: Iterable[float]) -> list[float]:
    values=np.asarray(list(p_values),dtype=float)
    if values.ndim != 1:
        raise ValueError("p_values must be one-dimensional")
    if values.size == 0:
        return []
    if not np.isfinite(values).all() or np.any(values < 0) or np.any(values > 1):
        raise ValueError("p-values must be finite and lie in [0, 1]")
    order=np.argsort(values)
    ordered=values[order]
    m=len(ordered)
    adjusted=np.empty(m,dtype=float)
    running=1.0
    for i in range(m-1,-1,-1):
        rank=i+1
        running=min(running,float(ordered[i])*m/rank)
        adjusted[i]=min(1.0,running)
    result=np.empty(m,dtype=float)
    result[order]=adjusted
    return [float(x) for x in result]


def _lookup(values, term: str) -> float:
    try:
        return float(values[term])
    except Exception as error:
        raise KeyError(f"term {term!r} not found") from error


def coefficient_record(result, term: str) -> dict:
    ci=result.conf_int()
    try:
        bounds=ci.loc[term]
        low=float(bounds.iloc[0])
        high=float(bounds.iloc[1])
    except AttributeError:
        bounds=ci[term]
        low=float(bounds[0])
        high=float(bounds[1])
    return {
        "term":term,
        "estimate":_lookup(result.params,term),
        "standard_error":_lookup(result.bse,term),
        "ci95_low":low,
        "ci95_high":high,
        "p_value":_lookup(result.pvalues,term),
    }


def verify_phase2_artifact_metadata(lock: dict, label: str, metadata: dict) -> None:
    expected={
        "artifact_id":int(lock["artifact_id"]),
        "name":str(lock["name"]),
        "digest":str(lock["digest"]),
        "workflow_run_id":int(lock["workflow_run_id"]),
        "workflow_head_sha":str(lock["workflow_head_sha"]),
    }
    run=metadata.get("workflow_run") or {}
    actual={
        "artifact_id":int(metadata.get("id",-1)),
        "name":str(metadata.get("name","")),
        "digest":str(metadata.get("digest","")),
        "workflow_run_id":int(run.get("id",-1)),
        "workflow_head_sha":str(run.get("head_sha","")),
    }
    if actual != expected:
        raise ValueError(
            f"{label} Phase-2 artifact metadata drift: expected={expected}, actual={actual}"
        )
