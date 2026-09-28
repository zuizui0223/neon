from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def ci_excludes_zero(record: dict[str, Any]) -> bool:
    lo=float(record["ci95_low"])
    hi=float(record["ci95_high"])
    return lo>0.0 or hi<0.0


def evaluate_result_gate(
    *,
    portal_primary: dict[str, Any],
    portal_sensitivity: dict[str, Any],
    neon_primary: dict[str, Any],
    neon_secondary: dict[str, Any],
    recapture_validation: dict[str, Any],
    packing_n_audit: dict[str, Any],
) -> dict[str, Any]:
    packing_pass=bool(packing_n_audit.get("passes"))

    portal_coeff=portal_primary["coefficients"]
    portal_treatment=ci_excludes_zero(portal_coeff["treatment"])
    portal_interaction=ci_excludes_zero(portal_coeff["interaction"])
    portal_primary_supported=portal_treatment or portal_interaction

    reversals=portal_sensitivity.get("direction_reversal_summary",{})
    treatment_reversals=list(reversals.get("treatment_reversal_labels",[]))
    interaction_reversals=list(reversals.get("interaction_reversal_labels",[]))
    portal_robust=not treatment_reversals and not interaction_reversals

    neon_habitat=neon_primary["coefficients"]["habitat_shrub_scrub_vs_forest"]
    neon_supported=ci_excludes_zero(neon_habitat)

    secondary_supported=[]
    for row in neon_secondary.get("contrasts",[]):
        effect=row["habitat_effect"]
        q=effect.get("q_value_bh3")
        if q is not None and float(q)<=0.05 and ci_excludes_zero(effect):
            secondary_supported.append({
                "species":row.get("species"),
                "site":row.get("site"),
                "estimate":float(effect["estimate"]),
                "q_value_bh3":float(q),
            })

    move=recapture_validation["coefficients"]["packing_z"]
    movement_supported=ci_excludes_zero(move)

    portal_evidence=portal_primary_supported and portal_robust
    neon_evidence=neon_supported or bool(secondary_supported)

    if not packing_pass:
        decision="stop_metric_mechanical_dependence"
    elif portal_evidence and neon_evidence:
        decision="advance_to_manuscript"
    elif portal_evidence:
        decision="advance_portal_system_specific_boundary"
    elif neon_supported:
        decision="advance_neon_boundary_with_portal_null"
    else:
        decision="stop_no_replicated_ecological_signal"

    return {
        "decision":decision,
        "packing_metric_mechanical_audit_passed":packing_pass,
        "portal_primary_supported":portal_primary_supported,
        "portal_treatment_ci_excludes_zero":portal_treatment,
        "portal_interaction_ci_excludes_zero":portal_interaction,
        "portal_robust":portal_robust,
        "portal_treatment_reversal_labels":treatment_reversals,
        "portal_interaction_reversal_labels":interaction_reversals,
        "neon_myodes_primary_supported":neon_supported,
        "secondary_neon_supported_count":len(secondary_supported),
        "secondary_neon_supported":secondary_supported,
        "movement_validation_supported":movement_supported,
        "cross_system_primary_support":portal_evidence and neon_evidence,
    }


def _load(path: Path) -> dict:
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _coefficient_summary(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "estimate":float(record["estimate"]),
        "standard_error":float(record["standard_error"]),
        "ci95_low":float(record["ci95_low"]),
        "ci95_high":float(record["ci95_high"]),
        "p_value":float(record["p_value"]),
    }


def build_phase2_summary(
    *,
    portal_primary: dict[str, Any],
    portal_sensitivity: dict[str, Any],
    neon_primary: dict[str, Any],
    neon_secondary: dict[str, Any],
    neon_context: dict[str, Any],
    recapture_validation: dict[str, Any],
    packing_n_audit: dict[str, Any],
    source_artifacts: dict[str, Any],
) -> dict[str, Any]:
    gate=evaluate_result_gate(
        portal_primary=portal_primary,
        portal_sensitivity=portal_sensitivity,
        neon_primary=neon_primary,
        neon_secondary=neon_secondary,
        recapture_validation=recapture_validation,
        packing_n_audit=packing_n_audit,
    )

    secondary=[
        {
            "species":row["species"],
            "site":row["site"],
            "habitats":row["habitats"],
            "session_count":int(row["session_count"]),
            "habitat_effect":{
                **_coefficient_summary(row["habitat_effect"]),
                "q_value_bh3":float(row["habitat_effect"]["q_value_bh3"]),
            },
        }
        for row in neon_secondary.get("contrasts",[])
    ]

    context={
        species:{
            "session_count":int(row["session_count"]),
            "site_count":int(row["site_count"]),
            "site_adjusted_range":float(row["site_adjusted_range"]),
            "site_adjusted_sd":float(row["site_adjusted_sd"]),
            "adjusted_site_means":{
                str(k):float(v) for k,v in row["adjusted_site_means"].items()
            },
        }
        for species,row in neon_context.get("site_context_family_n5",{}).items()
    }

    payload={
        "schema":"neon.public_mammal_space_use.phase2_summary.v1",
        "inferential_status":"retrospective_public_data_phase2",
        "decision":gate["decision"],
        "gate":gate,
        "portal":{
            "species":portal_primary.get("species"),
            "session_count":int(portal_primary["session_count"]),
            "plot_count":int(portal_primary["plot_count"]),
            "treatment":_coefficient_summary(portal_primary["coefficients"]["treatment"]),
            "interaction":_coefficient_summary(portal_primary["coefficients"]["interaction"]),
            "z_logN":_coefficient_summary(portal_primary["coefficients"]["z_logN"]),
            "model":portal_primary["model"],
            "direction_reversal_summary":portal_sensitivity.get("direction_reversal_summary",{}),
        },
        "neon_myodes":{
            "species":neon_primary.get("species"),
            "session_count":int(neon_primary["session_count"]),
            "n_range":neon_primary.get("n_range"),
            "habitat_effect":_coefficient_summary(
                neon_primary["coefficients"]["habitat_shrub_scrub_vs_forest"]
            ),
            "z_logN":_coefficient_summary(neon_primary["coefficients"]["z_logN"]),
            "site_effect":_coefficient_summary(neon_primary["coefficients"]["site_DEJU_vs_BONA"]),
            "model":neon_primary["model"],
            "robustness":neon_context.get("myodes_robustness",{}),
        },
        "neon_secondary_habitat":secondary,
        "neon_site_context_descriptive":context,
        "movement_validation":{
            "status":recapture_validation.get("status"),
            "nobs":int(recapture_validation["model"]["nobs"]),
            "stratum_count":int(recapture_validation["model"]["stratum_count"]),
            "packing_z":_coefficient_summary(
                recapture_validation["coefficients"]["packing_z"]
            ),
            "z_logN":_coefficient_summary(
                recapture_validation["coefficients"]["z_logN"]
            ),
        },
        "packing_n_independence":packing_n_audit,
        "peromyscus_cryptic_complex_sensitivity":{
            "required_by_amendment":True,
            "executed":False,
            "decision_relevance":"not required to establish current stop decision because no primary or supported secondary ecological signal depends on Peromyscus",
            "future_use":"must be completed before any future manuscript promotes a Peromyscus ecological result",
        },
        "source_artifacts":source_artifacts,
        "ecological_interpretation":{
            "supported":[
                "Packing_z passes the prespecified mechanical N-independence audit"
            ] if gate["packing_metric_mechanical_audit_passed"] else [],
            "not_supported":[
                "kangaroo-rat exclosure changes Chaetodipus penicillatus population spatial packing at matched captured abundance",
                "Myodes rutilus population packing differs detectably between shrub/scrub and forest after N and site are controlled",
                "the three frozen secondary within-site habitat contrasts provide replicated generalization",
                "population Packing_z predicts independent recapture displacement after N and species-site context are controlled",
            ],
            "descriptive_only":[
                "several species show large adjusted site-to-site ranges in Packing_z; these site effects were not frozen as a causal mechanism test"
            ],
        },
        "manuscript_authorized":gate["decision"]!="stop_no_replicated_ecological_signal"
            and gate["decision"]!="stop_metric_mechanical_dependence",
    }
    return payload


def _markdown(summary: dict[str, Any]) -> str:
    portal=summary["portal"]
    neon=summary["neon_myodes"]
    move=summary["movement_validation"]
    gate=summary["gate"]
    lines=[
        "# Public mammal Phase-2 result — V1",
        "",
        f"**Decision: {summary['decision']}**",
        "",
        "## Mechanical validity",
        "",
        f"- Packing_z mechanical N-independence audit passed: **{gate['packing_metric_mechanical_audit_passed']}**",
        "",
        "## Portal — Chaetodipus penicillatus",
        "",
        f"- sessions: {portal['session_count']}; plots: {portal['plot_count']}",
        f"- treatment effect: {portal['treatment']['estimate']:.4f} "
        f"(95% CI {portal['treatment']['ci95_low']:.4f} to {portal['treatment']['ci95_high']:.4f})",
        f"- treatment × z_logN: {portal['interaction']['estimate']:.4f} "
        f"(95% CI {portal['interaction']['ci95_low']:.4f} to {portal['interaction']['ci95_high']:.4f})",
        f"- robustness direction reversals: treatment={gate['portal_treatment_reversal_labels']}; "
        f"interaction={gate['portal_interaction_reversal_labels']}",
        "",
        "## NEON — Myodes rutilus",
        "",
        f"- sessions: {neon['session_count']}",
        f"- shrub/scrub vs forest: {neon['habitat_effect']['estimate']:.4f} "
        f"(95% CI {neon['habitat_effect']['ci95_low']:.4f} to {neon['habitat_effect']['ci95_high']:.4f})",
        "",
        "## Frozen secondary habitat family",
        "",
        f"- supported after BH FDR: **{gate['secondary_neon_supported_count']} / 3**",
        "",
        "## Recapture movement validation",
        "",
        f"- events: {move['nobs']}; species-site strata: {move['stratum_count']}",
        f"- Packing_z coefficient: {move['packing_z']['estimate']:.6f} "
        f"(95% CI {move['packing_z']['ci95_low']:.6f} to {move['packing_z']['ci95_high']:.6f})",
        "",
        "## Interpretation",
        "",
        "The abundance-conditioned Packing_z response is mechanically well behaved under the prespecified null audit, "
        "but the frozen ecological hypotheses did not produce replicated evidence strong enough to advance a manuscript.",
        "",
        "Site-to-site Packing_z variation remains descriptive and hypothesis-generating. It is not used to rescue the stopped primary programme.",
        "",
        "The Peromyscus cryptic-complex rebuild was not executed because it cannot alter this stop decision; it remains mandatory before any future Peromyscus result is promoted.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--portal-primary",type=Path,required=True)
    parser.add_argument("--portal-sensitivity",type=Path,required=True)
    parser.add_argument("--neon-primary",type=Path,required=True)
    parser.add_argument("--neon-secondary",type=Path,required=True)
    parser.add_argument("--neon-context",type=Path,required=True)
    parser.add_argument("--recapture-validation",type=Path,required=True)
    parser.add_argument("--packing-n-audit",type=Path,required=True)
    parser.add_argument("--source-artifacts",type=Path,required=True)
    parser.add_argument("--output-json",type=Path,required=True)
    parser.add_argument("--output-gate",type=Path,required=True)
    parser.add_argument("--output-md",type=Path,required=True)
    args=parser.parse_args()

    summary=build_phase2_summary(
        portal_primary=_load(args.portal_primary),
        portal_sensitivity=_load(args.portal_sensitivity),
        neon_primary=_load(args.neon_primary),
        neon_secondary=_load(args.neon_secondary),
        neon_context=_load(args.neon_context),
        recapture_validation=_load(args.recapture_validation),
        packing_n_audit=_load(args.packing_n_audit),
        source_artifacts=_load(args.source_artifacts),
    )
    gate={
        "schema":"neon.public_mammal_space_use.phase2_result_gate.v1",
        "decision":summary["decision"],
        "manuscript_authorized":summary["manuscript_authorized"],
        "gate":summary["gate"],
        "source_artifacts":summary["source_artifacts"],
        "peromyscus_cryptic_complex_sensitivity":summary["peromyscus_cryptic_complex_sensitivity"],
    }

    for path in (args.output_json,args.output_gate,args.output_md):
        path.parent.mkdir(parents=True,exist_ok=True)
    args.output_json.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    args.output_gate.write_text(json.dumps(gate,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    args.output_md.write_text(_markdown(summary),encoding="utf-8")
    print(json.dumps({
        "decision":summary["decision"],
        "manuscript_authorized":summary["manuscript_authorized"],
        "packing_metric_mechanical_audit_passed":summary["gate"]["packing_metric_mechanical_audit_passed"],
        "portal_primary_supported":summary["gate"]["portal_primary_supported"],
        "neon_myodes_primary_supported":summary["gate"]["neon_myodes_primary_supported"],
        "secondary_neon_supported_count":summary["gate"]["secondary_neon_supported_count"],
        "movement_validation_supported":summary["gate"]["movement_validation_supported"],
    },sort_keys=True))


if __name__=="__main__":
    main()
