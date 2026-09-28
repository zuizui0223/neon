from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Callable

from scipy.stats import t as student_t


def _float(value) -> float:
    return float(str(value).strip())


def _int(value) -> int:
    return int(float(str(value).strip()))


def _truthy(value) -> bool:
    return str(value).strip().lower() in {"1","true","t","yes","y"}


def _mean_ci_t(values: list[float]) -> dict:
    clean=[float(x) for x in values]
    n=len(clean)
    if n==0:
        return {
            "n":0,
            "mean":None,
            "sd":None,
            "standard_error":None,
            "df":None,
            "ci95_low":None,
            "ci95_high":None,
            "estimable":False,
        }
    mean=statistics.mean(clean)
    if n<2:
        return {
            "n":n,
            "mean":mean,
            "sd":None,
            "standard_error":None,
            "df":0,
            "ci95_low":None,
            "ci95_high":None,
            "estimable":False,
        }
    sd=statistics.stdev(clean)
    se=sd/math.sqrt(n)
    df=n-1
    critical=float(student_t.ppf(0.975,df))
    return {
        "n":n,
        "mean":mean,
        "sd":sd,
        "standard_error":se,
        "df":df,
        "ci95_low":mean-critical*se,
        "ci95_high":mean+critical*se,
        "estimable":True,
    }


def _eligible(
    row: dict,
    *,
    n_min: int,
    pit_complete: bool=False,
    known_sex_min: float | None=None,
) -> bool:
    if _int(row.get("n_male",0))<n_min:
        return False
    if _int(row.get("n_female",0))<n_min:
        return False
    if pit_complete:
        value=row.get("pit_reliable_fraction")
        if value in (None,"") or abs(_float(value)-1.0)>1e-12:
            return False
    if known_sex_min is not None:
        value=row.get("known_sex_fraction")
        if value in (None,"") or _float(value)<known_sex_min:
            return False
    return True


def _species_effect(
    rows: list[dict],
    *,
    species: str,
    unit_field: str,
) -> dict:
    selected=[row for row in rows if str(row.get("species",""))==species]
    by_unit=defaultdict(list)
    for row in selected:
        unit=str(row.get(unit_field,"")).strip()
        if not unit:
            continue
        by_unit[unit].append(_float(row["delta_sex_packing"]))

    unit_means={
        unit:statistics.mean(values)
        for unit,values in sorted(by_unit.items())
    }
    summary=_mean_ci_t(list(unit_means.values()))
    return {
        "species":species,
        "session_count":len(selected),
        "spatial_unit_count":len(unit_means),
        "unit_means":unit_means,
        "effect":summary["mean"],
        "sd_across_units":summary["sd"],
        "standard_error":summary["standard_error"],
        "df":summary["df"],
        "ci95_low":summary["ci95_low"],
        "ci95_high":summary["ci95_high"],
        "estimable":summary["estimable"],
    }


def source_effect(
    rows: list[dict],
    *,
    source: str,
    species_set: list[str],
    unit_field: str,
    n_min: int,
    pit_complete: bool=False,
    known_sex_min: float | None=None,
) -> dict:
    eligible=[
        dict(row) for row in rows
        if str(row.get("source",""))==source
        and str(row.get("species","")) in species_set
        and _eligible(
            row,
            n_min=n_min,
            pit_complete=pit_complete,
            known_sex_min=known_sex_min,
        )
    ]
    species_results=[
        _species_effect(
            eligible,
            species=species,
            unit_field=unit_field,
        )
        for species in species_set
    ]
    all_estimable=all(row["estimable"] for row in species_results)
    if all_estimable:
        family=_mean_ci_t([row["effect"] for row in species_results])
        status="estimable"
    else:
        family=_mean_ci_t([])
        status="non_estimable_full_frozen_species_set"

    return {
        "source":source,
        "n_min_per_sex":n_min,
        "pit_complete":pit_complete,
        "known_sex_min":known_sex_min,
        "session_count":len(eligible),
        "frozen_species_count":len(species_set),
        "species":species_results,
        "family":{
            "status":status,
            "effect":family["mean"],
            "species_count":family["n"],
            "sd_across_species":family["sd"],
            "standard_error":family["standard_error"],
            "df":family["df"],
            "ci95_low":family["ci95_low"],
            "ci95_high":family["ci95_high"],
            "estimable":family["estimable"] and all_estimable,
        },
    }


def leave_one_species_out(primary: dict) -> list[dict]:
    species=primary["species"]
    out=[]
    for excluded in species:
        kept=[
            row["effect"] for row in species
            if row["species"]!=excluded["species"]
            and row["effect"] is not None
        ]
        summary=_mean_ci_t(kept)
        out.append({
            "excluded_species":excluded["species"],
            "effect":summary["mean"],
            "species_count":summary["n"],
            "ci95_low":summary["ci95_low"],
            "ci95_high":summary["ci95_high"],
            "estimable":summary["estimable"],
        })
    return out


def leave_one_unit_out(primary: dict) -> dict[str,list[dict]]:
    result={}
    for species in primary["species"]:
        unit_means=species["unit_means"]
        rows=[]
        for excluded in sorted(unit_means):
            kept=[
                value for unit,value in unit_means.items()
                if unit!=excluded
            ]
            rows.append({
                "excluded_unit":excluded,
                "effect":statistics.mean(kept) if kept else None,
                "remaining_unit_count":len(kept),
            })
        result[species["species"]]=rows
    return result


def replicated_decision(
    portal: dict,
    neon: dict,
    *,
    shared_species: list[str],
) -> dict:
    p_family=portal["family"]
    n_family=neon["family"]
    p_species={row["species"]:row for row in portal["species"]}
    n_species={row["species"]:row for row in neon["species"]}

    concordant=[]
    for species in shared_species:
        p=p_species.get(species)
        n=n_species.get(species)
        if (
            p and n
            and p.get("effect") is not None
            and n.get("effect") is not None
            and p["effect"]>0
            and n["effect"]>0
        ):
            concordant.append(species)

    conditions={
        "portal_family_effect_positive":(
            p_family.get("effect") is not None
            and p_family["effect"]>0
        ),
        "neon_family_effect_positive":(
            n_family.get("effect") is not None
            and n_family["effect"]>0
        ),
        "portal_family_ci95_low_above_zero":(
            p_family.get("ci95_low") is not None
            and p_family["ci95_low"]>0
        ),
        "neon_family_ci95_low_above_zero":(
            n_family.get("ci95_low") is not None
            and n_family["ci95_low"]>0
        ),
        "at_least_2_of_3_shared_species_positive_in_both":(
            len(concordant)>=2
        ),
    }
    passed=all(conditions.values())
    return {
        "decision":(
            "replicated_positive_support"
            if passed else
            "no_replicated_positive_support"
        ),
        "conditions":conditions,
        "shared_species_positive_in_both":concordant,
        "shared_species_positive_in_both_count":len(concordant),
        "shared_species_denominator":len(shared_species),
    }


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="",encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def analyze(
    portal_rows: list[dict],
    neon_rows: list[dict],
    lock: dict,
    support_gate: dict,
) -> dict:
    portal_expected=int(
        support_gate["portal_summary"]["support_paired_n3_sessions"]
    )
    neon_expected=int(
        support_gate["neon_summary"]["support_paired_n3_sessions"]
    )
    portal_actual=sum(
        _int(row.get("n_male",0))>=3 and _int(row.get("n_female",0))>=3
        for row in portal_rows
    )
    neon_actual=sum(
        _int(row.get("n_male",0))>=3 and _int(row.get("n_female",0))>=3
        for row in neon_rows
    )
    if portal_actual!=portal_expected:
        raise RuntimeError(
            f"Portal Phase-3 N>=3 count {portal_actual} != support gate {portal_expected}"
        )
    if neon_actual!=neon_expected:
        raise RuntimeError(
            f"NEON Phase-3 N>=3 count {neon_actual} != support gate {neon_expected}"
        )

    portal_species=lock["source_estimators"]["Portal"]["qualifying_species"]
    neon_species=lock["source_estimators"]["NEON"]["qualifying_species"]
    shared=lock["shared_species"]

    portal_primary=source_effect(
        portal_rows,
        source="Portal",
        species_set=portal_species,
        unit_field="plot_id",
        n_min=3,
    )
    neon_primary=source_effect(
        neon_rows,
        source="NEON",
        species_set=neon_species,
        unit_field="site",
        n_min=3,
    )

    decision=replicated_decision(
        portal_primary,
        neon_primary,
        shared_species=shared,
    )

    sensitivities={
        "n_min_2_per_sex":{
            "Portal":source_effect(
                portal_rows,source="Portal",
                species_set=portal_species,unit_field="plot_id",n_min=2,
            ),
            "NEON":source_effect(
                neon_rows,source="NEON",
                species_set=neon_species,unit_field="site",n_min=2,
            ),
        },
        "n_min_5_per_sex":{
            "Portal":source_effect(
                portal_rows,source="Portal",
                species_set=portal_species,unit_field="plot_id",n_min=5,
            ),
            "NEON":source_effect(
                neon_rows,source="NEON",
                species_set=neon_species,unit_field="site",n_min=5,
            ),
        },
        "portal_pit_reliable_fraction_1":{
            "Portal":source_effect(
                portal_rows,source="Portal",
                species_set=portal_species,unit_field="plot_id",n_min=3,
                pit_complete=True,
            ),
        },
        "known_sex_fraction_ge_0_8":{
            "Portal":source_effect(
                portal_rows,source="Portal",
                species_set=portal_species,unit_field="plot_id",n_min=3,
                known_sex_min=0.8,
            ),
            "NEON":source_effect(
                neon_rows,source="NEON",
                species_set=neon_species,unit_field="site",n_min=3,
                known_sex_min=0.8,
            ),
        },
        "leave_one_species_out":{
            "Portal":leave_one_species_out(portal_primary),
            "NEON":leave_one_species_out(neon_primary),
        },
        "leave_one_spatial_unit_out":{
            "Portal":leave_one_unit_out(portal_primary),
            "NEON":leave_one_unit_out(neon_primary),
        },
    }

    return {
        "schema":"neon.public_mammal_sex_packing.phase3_summary.v1",
        "frozen_date":"2026-09-29",
        "inferential_status":"retrospective_public_data_phase3",
        "primary":{
            "Portal":portal_primary,
            "NEON":neon_primary,
            "decision":decision,
        },
        "sensitivities":sensitivities,
        "provenance_checks":{
            "portal_support_gate_n3_sessions":portal_expected,
            "portal_effect_table_n3_sessions":portal_actual,
            "neon_support_gate_n3_sessions":neon_expected,
            "neon_effect_table_n3_sessions":neon_actual,
            "phase3_lock_state":lock["state"],
            "support_gate_decision":support_gate["decision"],
        },
        "claim_boundary":lock["claim_boundary"],
        "season_primary_role":lock["season"]["primary_role"],
        "ecological_effects_inspected":True,
        "ecological_model_fits":2,
    }


def render_markdown(summary: dict) -> str:
    primary=summary["primary"]
    lines=[
        "# Heteromyid sex-specific spatial packing — Phase 3 result",
        "",
        f"**Decision: {primary['decision']['decision']}**",
        "",
    ]
    for source in ("Portal","NEON"):
        row=primary[source]
        fam=row["family"]
        lines += [
            f"## {source}",
            "",
            f"- primary sessions in frozen species: {row['session_count']}",
            f"- family effect: {fam['effect']:.6f}" if fam["effect"] is not None else "- family effect: non-estimable",
            (
                f"- 95% t CI: {fam['ci95_low']:.6f} to {fam['ci95_high']:.6f}"
                if fam["ci95_low"] is not None else
                "- 95% t CI: non-estimable"
            ),
            "",
            "Species effects:",
        ]
        for sp in row["species"]:
            ci=(
                f"{sp['ci95_low']:.6f} to {sp['ci95_high']:.6f}"
                if sp["ci95_low"] is not None else
                "non-estimable"
            )
            lines.append(
                f"- {sp['species']}: {sp['effect']:.6f} "
                f"(units={sp['spatial_unit_count']}, 95% CI {ci})"
            )
        lines.append("")
    d=primary["decision"]
    lines += [
        "## Replication rule",
        "",
        f"- shared species positive in both sources: {d['shared_species_positive_in_both_count']} / {d['shared_species_denominator']}",
        f"- species: {', '.join(d['shared_species_positive_in_both']) if d['shared_species_positive_in_both'] else 'none'}",
        "",
        "The frozen primary decision is not changed by sensitivity analyses.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--portal",type=Path,required=True)
    parser.add_argument("--neon",type=Path,required=True)
    parser.add_argument("--lock",type=Path,required=True)
    parser.add_argument("--support-gate",type=Path,required=True)
    parser.add_argument("--output-json",type=Path,required=True)
    parser.add_argument("--output-md",type=Path,required=True)
    args=parser.parse_args()

    summary=analyze(
        _read_csv(args.portal),
        _read_csv(args.neon),
        json.loads(args.lock.read_text()),
        json.loads(args.support_gate.read_text()),
    )
    args.output_json.parent.mkdir(parents=True,exist_ok=True)
    args.output_md.parent.mkdir(parents=True,exist_ok=True)
    args.output_json.write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    args.output_md.write_text(render_markdown(summary),encoding="utf-8")
    print(json.dumps(summary["primary"],indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
