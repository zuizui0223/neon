from __future__ import annotations

# AI assistance disclosure: This file was drafted or refactored with OpenAI ChatGPT (GPT-5.6 Sol, October 2026); it remains under author responsibility and is verified against the frozen positional-aliasing artifact.

import argparse
import json
import math
from pathlib import Path

import numpy as np

from analysis import san_jacinto_positional_aliasing_v1 as source


def flag_xy(flag: str) -> tuple[int,int]:
    flag=str(flag).strip().upper()
    return int(flag[1:])-1, ord(flag[0])-ord("A")


def canonical_vector(dx: int,dy: int) -> tuple[tuple[int,int],int]:
    if dx>0 or (dx==0 and dy>0):
        return (dx,dy),1
    return (-dx,-dy),-1


def audit_species(rows: list[dict], species: str, *, permutations: int, seed: int) -> dict:
    changed=[]
    for row in rows:
        if row["species"]!=species or not bool(row["any_flag_change"]):
            continue
        x1,y1=flag_xy(row["first_flag"])
        x2,y2=flag_xy(row["last_flag"])
        dx=x2-x1; dy=y2-y1
        key,sign=canonical_vector(dx,dy)
        changed.append({
            "cluster":f'{row["grid"]}|{row["unique_ID"]}',
            "stratum":(str(row["grid"]),key[0],key[1]),
            "sign":sign,
            "dx":dx,
            "dy":dy,
            "distance_m":float(row["first_last_distance_m"]),
        })
    if not changed:
        raise RuntimeError(f"no changed nights for {species}")

    clusters=sorted({r["cluster"] for r in changed})
    strata=sorted({r["stratum"] for r in changed},key=str)
    ci={x:i for i,x in enumerate(clusters)}
    si={x:i for i,x in enumerate(strata)}

    A=np.zeros((len(clusters),len(strata)),dtype=np.int16)
    m=np.zeros(len(strata),dtype=np.int16)
    for r in changed:
        A[ci[r["cluster"]],si[r["stratum"]]]+=int(r["sign"])
        m[si[r["stratum"]]]+=1

    d=A.sum(axis=0).astype(float)
    observed=float(np.sum(d*d/m))

    rng=np.random.default_rng(seed)
    ge=0
    done=0
    chunk=5000
    while done<permutations:
        n=min(chunk,permutations-done)
        flips=rng.choice(np.array([-1,1],dtype=np.int8),size=(n,len(clusters)))
        D=flips@A
        stat=np.sum((D.astype(float)**2)/m,axis=1)
        ge+=int(np.sum(stat>=observed-1e-12))
        done+=n
    p=(ge+1)/(permutations+1)

    mean_dx=6.25*sum(r["dx"] for r in changed)/len(changed)
    mean_dy=6.25*sum(r["dy"] for r in changed)/len(changed)
    mean_mag=math.hypot(mean_dx,mean_dy)
    rms=math.sqrt(sum(r["distance_m"]**2 for r in changed)/len(changed))

    return {
        "repeat_capture_nights":sum(r["species"]==species for r in rows),
        "changed_nights":len(changed),
        "changed_grid_individual_clusters":len(clusters),
        "grid_vector_strata":len(strata),
        "mean_directed_dx_m":mean_dx,
        "mean_directed_dy_m":mean_dy,
        "mean_directed_vector_magnitude_m":mean_mag,
        "changed_night_rms_distance_m":rms,
        "mean_vector_to_rms_ratio":mean_mag/rms,
        "grid_stratified_directional_chi_statistic":observed,
        "cluster_signflip_permutations":permutations,
        "cluster_signflip_seed":seed,
        "cluster_signflip_p_upper":p,
        "interpretation":(
            "no_evidence_against_grid_stratified_time_reversal_symmetry"
            if p>=0.05 else
            "evidence_against_grid_stratified_time_reversal_symmetry"
        ),
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--cache",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--permutations",type=int,default=500000)
    parser.add_argument("--seed",type=int,default=20261005)
    args=parser.parse_args()

    rows=source.download_rows(args.cache)
    repeat=source.prepare_repeat_nights(rows)

    result={
        "schema":"neon.live_trap_time_reversal_symmetry_audit.v1",
        "status":"post_result_exploratory_non_rescuing",
        "spatial_unit":"trap-grid coordinates; 6.25 m spacing",
        "test":{
            "null":"within each species, grid, and unordered relative displacement vector, first-to-last direction is symmetric under time reversal",
            "statistic":"sum over grid x unsigned-vector strata of (n_forward-n_reverse)^2/(n_forward+n_reverse)",
            "randomization":"one independent sign flip per grid x individual cluster, applied jointly to all changed repeat nights from that cluster",
            "p_value":"upper-tail Monte Carlo randomization p-value",
        },
        "species":{
            "PEMA":audit_species(repeat,"PEMA",permutations=args.permutations,seed=args.seed),
            "PEER":audit_species(repeat,"PEER",permutations=args.permutations,seed=args.seed+1),
        },
        "claim_boundary":{
            "proves_time_reversal_symmetry":False,
            "confirmatory":False,
            "can_rescue_or_replace_frozen_gates":False,
            "interpretation":"Failure to reject is consistency evidence only; sparse vector strata, finite sample size, and grid-coordinate conventions limit power.",
        },
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
