from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path

from scipy.stats import spearmanr
from scipy.stats import t as student_t


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1","true","t","yes","y"}


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="",encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def mean_grid_effects(
    rows: list[dict],
    *,
    response: str,
    species: str,
    grids: list[str],
    eligibility: str,
) -> dict:
    selected=[
        row for row in rows
        if row["species"]==species
        and str(row["grid"]) in grids
        and truthy(row[eligibility])
    ]
    by_grid={}
    for grid in grids:
        values=[
            float(row[response]) for row in selected
            if str(row["grid"])==str(grid)
        ]
        if not values:
            raise RuntimeError(
                f"{species} {response}: frozen matched grid {grid} has no eligible rows"
            )
        by_grid[str(grid)]=float(statistics.mean(values))

    effects=list(by_grid.values())
    effect=float(statistics.mean(effects))
    if len(effects)<2:
        raise RuntimeError(f"{species}: fewer than two frozen matched grids")
    sd=float(statistics.stdev(effects))
    se=sd/math.sqrt(len(effects))
    return {
        "species":species,
        "row_count":len(selected),
        "grid_count":len(effects),
        "grid_effects":by_grid,
        "effect":effect,
        "sd_across_grids":sd,
        "standard_error":se,
    }


def family_summary(species_rows: list[dict]) -> dict:
    if len(species_rows)<2:
        raise ValueError("family summary requires at least two species")
    effects=[float(x["effect"]) for x in species_rows]
    ses=[float(x["standard_error"]) for x in species_rows]
    s=len(effects)

    observed_var=float(statistics.variance(effects))
    sampling_var=[x*x for x in ses]
    mean_sampling=float(statistics.mean(sampling_var))
    tau2=max(0.0,observed_var-mean_sampling)
    variance=tau2/s + sum(sampling_var)/(s*s)
    se=math.sqrt(variance)
    mean=float(statistics.mean(effects))
    df=s-1

    t95=float(student_t.ppf(0.975,df))
    t90=float(student_t.ppf(0.95,df))
    return {
        "species_count":s,
        "effect":mean,
        "standard_error":se,
        "df":df,
        "ci95_low":mean-t95*se,
        "ci95_high":mean+t95*se,
        "ci90_low":mean-t90*se,
        "ci90_high":mean+t90*se,
        "observed_species_variance":observed_var,
        "mean_species_sampling_variance":mean_sampling,
        "tau2_method_of_moments":tau2,
        "method":"equal_species_random_effects_moments_with_grid_uncertainty",
    }


def endpoint_summary(
    rows: list[dict],
    *,
    response: str,
    matched_grids: dict[str,list[str]],
    eligibility: str,
) -> dict:
    species_rows=[
        mean_grid_effects(
            rows,
            response=response,
            species=species,
            grids=grids,
            eligibility=eligibility,
        )
        for species,grids in matched_grids.items()
    ]
    family=family_summary(species_rows)
    positive=[x["species"] for x in species_rows if x["effect"]>0]
    directional={
        "family_effect_positive":family["effect"]>0,
        "family_ci95_low_above_zero":family["ci95_low"]>0,
        "positive_species":positive,
        "positive_species_count":len(positive),
        "species_denominator":len(species_rows),
    }
    directional["passed"]=(
        directional["family_effect_positive"]
        and directional["family_ci95_low_above_zero"]
        and len(positive)>=3
    )
    return {
        "species":species_rows,
        "family":family,
        "directional_gate":directional,
    }


def packing_equivalence(packing: dict, margin: float=0.5) -> dict:
    family=packing["family"]
    inside=[
        x["species"] for x in packing["species"]
        if abs(float(x["effect"]))<margin
    ]
    family_inside=(
        family["ci90_low"]>-margin
        and family["ci90_high"]<margin
    )
    return {
        "margin":margin,
        "family_ci90_inside_margin":family_inside,
        "species_inside_margin":inside,
        "species_inside_margin_count":len(inside),
        "species_denominator":len(packing["species"]),
        "passed":family_inside and len(inside)>=3,
    }


def leave_one_species_out(species_rows: list[dict]) -> list[dict]:
    out=[]
    for excluded in species_rows:
        kept=[x for x in species_rows if x["species"]!=excluded["species"]]
        fam=family_summary(kept)
        out.append({
            "excluded_species":excluded["species"],
            "family":fam,
        })
    return out


def leave_one_grid_out(species_rows: list[dict]) -> dict[str,list[dict]]:
    out={}
    for row in species_rows:
        effects=row["grid_effects"]
        rows=[]
        for excluded in sorted(effects):
            kept=[v for g,v in effects.items() if g!=excluded]
            rows.append({
                "excluded_grid":excluded,
                "remaining_grid_count":len(kept),
                "effect":float(statistics.mean(kept)) if kept else None,
            })
        out[row["species"]]=rows
    return out


def matched_grid_spearman(packing: dict, movement: dict) -> dict:
    p={
        (row["species"],grid):value
        for row in packing["species"]
        for grid,value in row["grid_effects"].items()
    }
    m={
        (row["species"],grid):value
        for row in movement["species"]
        for grid,value in row["grid_effects"].items()
    }
    keys=sorted(set(p)&set(m))
    if len(keys)<3:
        return {"n":len(keys),"rho":None,"p_value":None}
    result=spearmanr(
        [p[k] for k in keys],
        [m[k] for k in keys],
    )
    return {
        "n":len(keys),
        "rho":float(result.statistic),
        "p_value":float(result.pvalue),
        "pairs":[
            {
                "species":k[0],
                "grid":k[1],
                "packing_effect":p[k],
                "movement_effect":m[k],
            }
            for k in keys
        ],
        "inferential_role":"descriptive_only",
    }


def final_decision(
    packing: dict,
    movement: dict,
    equivalence: dict,
) -> dict:
    movement_positive=bool(movement["directional_gate"]["passed"])
    packing_positive=bool(packing["directional_gate"]["passed"])
    packing_equiv=bool(equivalence["passed"])

    if movement_positive and packing_positive:
        decision="authorize_crossscale_propagation_manuscript"
    elif movement_positive and (not packing_positive) and packing_equiv:
        decision="authorize_crossscale_decoupling_manuscript"
    else:
        decision="stop_no_confirmatory_crossscale_result"

    return {
        "movement_positive_gate_passed":movement_positive,
        "packing_positive_gate_passed":packing_positive,
        "packing_equivalence_gate_passed":packing_equiv,
        "decision":decision,
    }


def analyze(
    packing_first: list[dict],
    movement_first: list[dict],
    packing_last: list[dict],
    movement_last: list[dict],
    lock: dict,
) -> dict:
    matched={
        str(species):[str(x) for x in grids]
        for species,grids in lock["matched_grids"].items()
    }

    packing_primary=endpoint_summary(
        packing_first,
        response="delta_packing",
        matched_grids=matched,
        eligibility="paired_n3_eligible",
    )
    movement_primary=endpoint_summary(
        movement_first,
        response="delta_movement",
        matched_grids=matched,
        eligibility="paired_n3_eligible",
    )
    equivalence=packing_equivalence(
        packing_primary,
        margin=float(lock["packing"]["equivalence_margin"]),
    )
    decision=final_decision(
        packing_primary,movement_primary,equivalence
    )

    sensitivities={
        "n_min_2_per_sex":{
            "packing":endpoint_summary(
                packing_first,response="delta_packing",
                matched_grids=matched,eligibility="paired_n2_eligible",
            ),
            "movement":endpoint_summary(
                movement_first,response="delta_movement",
                matched_grids=matched,eligibility="paired_n2_eligible",
            ),
        },
        "last_nightly_capture":{
            "packing":endpoint_summary(
                packing_last,response="delta_packing",
                matched_grids=matched,eligibility="paired_n3_eligible",
            ),
            "movement":endpoint_summary(
                movement_last,response="delta_movement",
                matched_grids=matched,eligibility="paired_n3_eligible",
            ),
        },
        "leave_one_species_out":{
            "packing":leave_one_species_out(packing_primary["species"]),
            "movement":leave_one_species_out(movement_primary["species"]),
        },
        "leave_one_matched_grid_out":{
            "packing":leave_one_grid_out(packing_primary["species"]),
            "movement":leave_one_grid_out(movement_primary["species"]),
        },
        "matched_grid_spearman_descriptive":matched_grid_spearman(
            packing_primary,movement_primary
        ),
    }

    return {
        "schema":"neon.san_jacinto_crossscale.effect_result.v1",
        "frozen_date":"2026-09-29",
        "primary":{
            "packing":packing_primary,
            "movement":movement_primary,
            "packing_equivalence":equivalence,
            "decision":decision,
        },
        "sensitivities":sensitivities,
        "claim_boundary":{
            "natal_or_breeding_dispersal":False,
            "home_range_size":False,
            "reproductive_causation":False,
            "universal_heteromyidae":False,
        },
        "packing_effects_computed":True,
        "movement_distances_computed":True,
        "ecological_effect_models_fit":2,
        "sensitivities_can_rescue_primary":False,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--packing-first",type=Path,required=True)
    parser.add_argument("--movement-first",type=Path,required=True)
    parser.add_argument("--packing-last",type=Path,required=True)
    parser.add_argument("--movement-last",type=Path,required=True)
    parser.add_argument("--lock",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()

    out=analyze(
        read_csv(args.packing_first),
        read_csv(args.movement_first),
        read_csv(args.packing_last),
        read_csv(args.movement_last),
        json.loads(args.lock.read_text()),
    )
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out["primary"],indent=2,sort_keys=True))


if __name__=="__main__":
    raise SystemExit(main())
