from __future__ import annotations

import importlib.util
import statistics
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def _load_exact():
    path=ROOT/"analysis"/"mammal_spatial_packing_exact_v2.py"
    spec=importlib.util.spec_from_file_location("packing_exact_v2",path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PACKING=_load_exact()


def _rank_average(values: list[float]) -> list[float]:
    order=sorted(range(len(values)),key=lambda i:values[i])
    ranks=[0.0]*len(values)
    i=0
    while i<len(order):
        j=i+1
        while j<len(order) and values[order[j]]==values[order[i]]:
            j+=1
        rank=(i+1+j)/2.0
        for k in range(i,j):
            ranks[order[k]]=rank
        i=j
    return ranks


def _pearson(x: list[float], y: list[float]) -> float:
    if len(x)<2 or len(x)!=len(y):
        return 0.0
    mx=statistics.mean(x)
    my=statistics.mean(y)
    dx=sum((v-mx)**2 for v in x) ** 0.5
    dy=sum((v-my)**2 for v in y) ** 0.5
    if dx==0 or dy==0:
        return 0.0
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/(dx*dy)


def _spearman(x: list[float], y: list[float]) -> float:
    return _pearson(_rank_average(x),_rank_average(y))


def _regular_grid(rows: int, cols: int, spacing_m: float) -> np.ndarray:
    return np.asarray(
        [(x*spacing_m,y*spacing_m) for y in range(rows) for x in range(cols)],
        dtype=float,
    )


def audit_standard_geometries() -> dict:
    designs=[
        ("portal_7x7_6.25m",_regular_grid(7,7,6.25)),
        ("neon_10x10_10m",_regular_grid(10,10,10.0)),
        ("neon_7x7_10m",_regular_grid(7,7,10.0)),
    ]
    sex_counts=[
        (3,3),(3,5),(3,8),(3,12),
        (5,3),(5,5),(5,8),
        (8,3),(8,5),(8,8),
        (12,3),
    ]
    threshold=0.2
    geometries=[]
    for label,traps in designs:
        rows=[]
        for n_male,n_female in sex_counts:
            male=PACKING.exact_null_moments(traps,n_male)
            female=PACKING.exact_null_moments(traps,n_female)
            rows.append({
                "n_male":n_male,
                "n_female":n_female,
                "sex_ratio":n_male/(n_male+n_female),
                "male_null_mean":male["mean"],
                "male_null_sd":male["sd"],
                "female_null_mean":female["mean"],
                "female_null_sd":female["sd"],
                # Each sex-specific z-score has exact null expectation zero.
                "expected_delta":0.0,
            })
        ratios=[float(row["sex_ratio"]) for row in rows]
        expected=[float(row["expected_delta"]) for row in rows]
        rho=_spearman(ratios,expected)
        geometries.append({
            "label":label,
            "trap_count":len(traps),
            "design_points":rows,
            "mean_expected_delta":statistics.mean(expected),
            "spearman_sex_ratio_vs_expected_delta":rho,
            "warning_threshold_abs_rho":threshold,
            "passes":abs(rho)<=threshold,
        })

    return {
        "schema":"neon.public_mammal_sex_packing.mechanical_null.v2",
        "status":"pre_effect_exact_mechanical_null_audit",
        "method":"exact_finite_population_pairwise_distance_moments",
        "legacy_warning_threshold_abs_rho":threshold,
        "geometries":geometries,
        "passes":all(row["passes"] for row in geometries),
        "ecological_effects_inspected":False,
        "ecological_model_fits":0,
    }
