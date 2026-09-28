from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results"/"generated"/"packing_n_independence_v1.json"


def _load_packing():
    path=ROOT/"analysis"/"mammal_spatial_packing_v1.py"
    spec=importlib.util.spec_from_file_location("mammal_spatial_packing_v1",path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PACKING=_load_packing()


def regular_grid_xy(*,rows:int,cols:int,spacing_m:float) -> np.ndarray:
    if rows<1 or cols<1 or spacing_m<=0:
        raise ValueError("rows, cols and spacing_m must be positive")
    return np.asarray(
        [(float(c)*spacing_m,float(r)*spacing_m) for r in range(rows) for c in range(cols)],
        dtype=float,
    )


def _rank_average(values:list[float]) -> np.ndarray:
    arr=np.asarray(values,dtype=float)
    order=np.argsort(arr,kind="mergesort")
    ranks=np.empty(len(arr),dtype=float)
    i=0
    while i<len(order):
        j=i+1
        while j<len(order) and arr[order[j]]==arr[order[i]]:
            j+=1
        rank=(i+1+j)/2.0
        ranks[order[i:j]]=rank
        i=j
    return ranks


def spearman(x:list[float],y:list[float]) -> float:
    if len(x)!=len(y) or len(x)<3:
        raise ValueError("Spearman requires equal vectors of length >=3")
    rx=_rank_average(x)
    ry=_rank_average(y)
    sx=float(np.std(rx,ddof=0))
    sy=float(np.std(ry,ddof=0))
    if sx==0 or sy==0:
        raise ValueError("Spearman undefined for constant input")
    return float(np.corrcoef(rx,ry)[0,1])


def audit_geometry(
    *,
    label:str,
    xy:np.ndarray,
    n_values:list[int],
    sessions_per_n:int,
    null_replicates:int,
    seed:int,
) -> dict:
    traps=np.asarray(xy,dtype=float)
    if traps.ndim!=2 or traps.shape[1]!=2:
        raise ValueError("xy must have shape (n,2)")
    if sessions_per_n<1 or null_replicates<1:
        raise ValueError("simulation counts must be positive")
    if not n_values:
        raise ValueError("n_values must be non-empty")

    rng=np.random.default_rng(int(seed))
    ns:list[float]=[]
    zs:list[float]=[]
    by_n=[]

    for n in n_values:
        if n<2 or n>len(traps):
            raise ValueError(f"invalid n={n} for {len(traps)} traps")
        null=PACKING.packing_null(
            traps,
            int(n),
            replicates=int(null_replicates),
            seed=int(seed)+100003*int(n),
        )
        if float(null["sd"])<=0:
            raise RuntimeError(f"{label}: zero null variance at n={n}")

        n_z=[]
        for _ in range(int(sessions_per_n)):
            idx=rng.choice(len(traps),size=int(n),replace=False)
            score=PACKING.packing_score_from_null(traps[idx],null)
            if not score["estimable"]:
                raise RuntimeError(f"{label}: simulated score non-estimable at n={n}")
            z=float(score["packing_z"])
            ns.append(float(n))
            zs.append(z)
            n_z.append(z)

        by_n.append({
            "n":int(n),
            "simulated_sessions":len(n_z),
            "mean_packing_z":float(np.mean(n_z)),
            "sd_packing_z":float(np.std(n_z,ddof=0)),
            "null_mode":str(null["mode"]),
            "null_draw_count":int(null["draw_count"]),
        })

    rho=spearman(ns,zs)
    mean_z=float(np.mean(zs))
    return {
        "label":label,
        "trap_count":len(traps),
        "n_values":[int(x) for x in n_values],
        "simulated_session_count":len(zs),
        "sessions_per_n":int(sessions_per_n),
        "null_replicates":int(null_replicates),
        "seed":int(seed),
        "mean_packing_z":mean_z,
        "spearman_n_vs_packing_z":rho,
        "passes_abs_rho_le_0_2":abs(rho)<=0.2,
        "by_n":by_n,
    }


def main() -> None:
    n_values=list(range(3,26))
    configs=[
        ("portal_7x7_6.25m",regular_grid_xy(rows=7,cols=7,spacing_m=6.25),2026092801),
        ("neon_standard_10x10_10m",regular_grid_xy(rows=10,cols=10,spacing_m=10.0),2026092802),
        ("neon_reduced_7x7_10m",regular_grid_xy(rows=7,cols=7,spacing_m=10.0),2026092803),
    ]
    audits=[
        audit_geometry(
            label=label,
            xy=xy,
            n_values=n_values,
            sessions_per_n=100,
            null_replicates=999,
            seed=seed,
        )
        for label,xy,seed in configs
    ]
    payload={
        "schema":"neon.public_mammal_space_use.packing_n_independence.v1",
        "status":"mechanical_null_audit",
        "response":"Packing_z",
        "failure_rule":"absolute Spearman rho between N and Packing_z > 0.2 in any representative geometry",
        "representative_geometries":[
            {
                "label":"portal_7x7_6.25m",
                "rationale":"Portal primary 49-stake regular grid",
            },
            {
                "label":"neon_standard_10x10_10m",
                "rationale":"standard NEON mammal diversity-grid geometry",
            },
            {
                "label":"neon_reduced_7x7_10m",
                "rationale":"reduced-grid geometry sensitivity",
            },
        ],
        "audits":audits,
        "passes":all(row["passes_abs_rho_le_0_2"] for row in audits),
        "ecological_model_fits":0,
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "passes":payload["passes"],
        "rho_by_geometry":{x["label"]:x["spearman_n_vs_packing_z"] for x in audits},
        "mean_z_by_geometry":{x["label"]:x["mean_packing_z"] for x in audits},
    },sort_keys=True))


if __name__=="__main__":
    main()
