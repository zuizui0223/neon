#!/usr/bin/env python3
"""Source-gated NEON within-bout genus re-encounter comparison.

The 26 October SOURCE-only first-night cohort fixed Microtus vs Peromyscus
across seven original physical sites BEFORE any day2/3 matched outcomes.
This observation is NOT true genus- or station-specific capture p,
independent confirmation of exact-station recurrence, or a survival test.
"""
from __future__ import annotations
from pathlib import Path
import json,os

from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.audit_multiscale_density_mnka_variation_v1 import _taxonomy
from analysis.neon_macro_firstnight_reencounter_source_v1 import source_first_night_cohort
from analysis.neon_macro_genus_reencounter_effect_v1 import firstnight_reencounter
from analysis.run_multiscale_density_estimability_release2026_v3 import TOKEN_ENV

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"results/neon_genus_firstnight_reencounter_source_20261026.json"
OUT=ROOT/"build/neon_genus_firstnight_reencounter_outcome_20261026.json"
DESIGN="docs/NEON_GENUS_FIRST_NIGHT_REENCOUNTER_SOURCE_GATE_20261026.md"
EXPECTED_GENUS_PAIR=("Microtus","Peromyscus")


def need(condition:bool,reason:str):
    if not condition:
        raise RuntimeError("GENUS_FIRSTNIGHT_REENCOUNTER_LOCK_STOP: "+reason)


def run()->dict:
    frozen=json.loads(SOURCE.read_text(encoding="utf-8"))
    need(frozen["status"]=="SOURCE_MATCHED_GENUS_REENCOUNTER_COMPARISON_GO"
         and frozen["predeclared_source_gate"]["passed"],
         "previous firstnight exposure cohort not source qualified")
    fixed=frozen["preselected_genus_pair_if_pass"]
    chosen=tuple(fixed["genera"])
    need(chosen==EXPECTED_GENUS_PAIR
         and fixed["shared_qualified_physical_sites"]==7,
         "pre-response genus comparison changed after source gate")
    token=os.environ.get(TOKEN_ENV,"").strip()
    need(bool(token),"NEON original release token unavailable")

    old,two,source,plots,traps=original_sources_for_two_genus(
        include_private_source_rows=True
    )
    need(len(old)==58 and len(two)==158,"NEON original frozen season cohorts changed")
    _,bytaxon,_=_taxonomy()
    newsource,private=source_first_night_cohort(
        two,plots,traps,bytaxon
    )
    for field in ("status","source_firstnight_marked_animals",
                  "unique_source_three_night_bouts",
                  "independent_sites_with_firstnight_tagged_captures",
                  "number_of_genera_with_one_plus_firstnight_captures",
                  "preselected_genus_pair_if_pass"):
        need(newsource[field]==frozen[field],
             "prior original firstnight source denominator cannot be reproduced")
    pre=private["source_selected_genus_pair"]
    need(pre is not None and (pre[0],pre[1])==chosen and len(pre[2])==7,
         "original private source genus pair/site support changed")
    # Only NOW access whether already selected first-night individuals
    # reappeared in day2/3 captures of the SAME original trapping bout.
    obs=firstnight_reencounter(
        private,traps,bytaxon,
        selected_genera=chosen,
        selected_sites=set(pre[2]),
        minimum_marked_animals_per_genus_site=5,
        minimum_sites=6,
        bootstrap_seed=2026102601,
        bootstrap_draws=2000,
    )
    return {
        "schema":"neon.macro.genus_source_paired_three_night_reencounter.v1",
        "status":obs["status"],
        "research_status":"POST_RESULT_SAME_HISTORICAL_RELEASE_OBSERVATION_PROCESS",
        "source_gate_receipt":"results/neon_genus_firstnight_reencounter_source_20261026.json",
        "original_NEON_release":"RELEASE-2026",
        "original_158_two_genus_pairs_unchanged":True,
        "original_58_threeplus_pairs_unchanged":True,
        "original_firstnight_source_reconstructed_and_selected_pair_unchanged":True,
        "fixed_design":DESIGN,
        "source":source,
        "reencounter":{
            **obs,
            "no_alternative_genus_or_site_selected_from_late_outcomes":True,
            "day2_or3_event_recorded_reencounter_not_true_detection_p":True,
        },
        "scientific_boundaries":{
            "original_historical_genus_exact_trap_recurrence_results_unchanged":True,
            "six_night_456_code_operability_source_18of158_STOP_unchanged":True,
            "original_density_universal_5of8_FAIL_unchanged":True,
            "tower_temperature_79of80_QC_STOP_unchanged":True,
            "original_10m_neighbor_site_reuse_exclusion_nonsupport_unchanged":True,
            "cause_of_genus_to_exact_trap_recurrence_not_identified":True,
            "reencounter_neither_true_genus_p_nor_animal_survival":True,
            "original_source_animal_site_plot_trap_date_IDs_not_exported":True,
        },
    }


def main()->int:
    try:
        report=run()
        exitcode=0
    except Exception as e:
        report={
            "schema":"neon.macro.genus_source_paired_three_night_reencounter.v1",
            "status":"STOP_SOURCE_OR_LATER_NIGHT_RECORD_INVARIANT",
            "error_class":type(e).__name__,
            "no_private_original_source_names_or_exception_message_exported":True,
            "original_Neon_ecology_unchanged":True,
        }
        exitcode=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
    return exitcode

if __name__=="__main__":
    raise SystemExit(main())
