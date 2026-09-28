from __future__ import annotations

import importlib.util
import statistics
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def _load_packing():
    path=ROOT/"analysis"/"mammal_spatial_packing_v1.py"
    spec=importlib.util.spec_from_file_location("mammal_spatial_packing_v1",path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PACKING=_load_packing()


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


def simulate_random_sex_delta(
    active_traps_xy: np.ndarray,
    *,
    n_male: int,
    n_female: int,
    sessions: int,
    packing_replicates: int,
    seed: int,
) -> dict:
    traps=np.asarray(active_traps_xy,dtype=float)
    if n_male<2 or n_female<2:
        raise ValueError("both sex counts must be at least 2")
    if n_male+n_female>len(traps):
        raise ValueError("combined sex count cannot exceed active trap count")
    if sessions<1:
        raise ValueError("sessions must be positive")

    male_null=PACKING.packing_null(
        traps,n_male,replicates=packing_replicates,seed=seed+101,
    )
    female_null=PACKING.packing_null(
        traps,n_female,replicates=packing_replicates,seed=seed+202,
    )
    if male_null["sd"]<=0 or female_null["sd"]<=0:
        raise ValueError("sex-specific packing null has zero variance")

    rng=np.random.default_rng(int(seed))
    deltas=[]
    for _ in range(int(sessions)):
        selected=rng.choice(
            len(traps),
            size=n_male+n_female,
            replace=False,
        )
        rng.shuffle(selected)
        male_xy=traps[selected[:n_male]]
        female_xy=traps[selected[n_male:]]
        male=PACKING.packing_score_from_null(male_xy,male_null)
        female=PACKING.packing_score_from_null(female_xy,female_null)
        deltas.append(float(male["packing_z"])-float(female["packing_z"]))

    return {
        "n_male":int(n_male),
        "n_female":int(n_female),
        "sex_ratio":n_male/(n_male+n_female),
        "simulated_sessions":len(deltas),
        "mean_delta":float(np.mean(deltas)),
        "sd_delta":float(np.std(deltas,ddof=0)),
        "male_null_mode":male_null["mode"],
        "female_null_mode":female_null["mode"],
    }


def summarize_mechanical_null(rows: list[dict]) -> dict:
    ratios=[float(row["sex_ratio"]) for row in rows]
    deltas=[float(row["mean_delta"]) for row in rows]
    rho=_spearman(ratios,deltas)
    threshold=0.2
    return {
        "row_count":len(rows),
        "mean_delta_across_design_points":(
            statistics.mean(deltas) if deltas else None
        ),
        "spearman_sex_ratio_vs_delta":rho,
        "warning_threshold_abs_rho":threshold,
        "passes":abs(rho)<=threshold,
    }


def _regular_grid(rows: int, cols: int, spacing_m: float) -> np.ndarray:
    return np.asarray(
        [(x*spacing_m,y*spacing_m) for y in range(rows) for x in range(cols)],
        dtype=float,
    )


def audit_standard_geometries(
    *,
    sessions_per_design: int=1000,
    packing_replicates: int=999,
) -> dict:
    designs=[
        ("portal_7x7_6.25m",_regular_grid(7,7,6.25),2026092801),
        ("neon_10x10_10m",_regular_grid(10,10,10.0),2026092802),
        ("neon_7x7_10m",_regular_grid(7,7,10.0),2026092803),
    ]
    sex_counts=[
        (3,3),(3,5),(3,8),(3,12),
        (5,3),(5,5),(5,8),
        (8,3),(8,5),(8,8),
        (12,3),
    ]
    geometries=[]
    for label,traps,base_seed in designs:
        rows=[]
        for index,(n_male,n_female) in enumerate(sex_counts):
            row=simulate_random_sex_delta(
                traps,
                n_male=n_male,
                n_female=n_female,
                sessions=sessions_per_design,
                packing_replicates=packing_replicates,
                seed=base_seed+index*1000,
            )
            rows.append(row)
        summary=summarize_mechanical_null(rows)
        geometries.append({
            "label":label,
            "trap_count":len(traps),
            "design_points":rows,
            **summary,
        })
    return {
        "schema":"neon.public_mammal_sex_packing.mechanical_null.v1",
        "status":"pre_effect_mechanical_null_audit",
        "warning_threshold_abs_rho":0.2,
        "sessions_per_design":sessions_per_design,
        "packing_replicates":packing_replicates,
        "geometries":geometries,
        "passes":all(row["passes"] for row in geometries),
        "ecological_effects_inspected":False,
        "ecological_model_fits":0,
    }
