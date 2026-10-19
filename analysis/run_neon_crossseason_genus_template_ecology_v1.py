#!/usr/bin/env python3
"""NEON independent cross-season genus-template ecology validation.

Outcome is ONLY same-genus trap-location recurrence between DIFFERENT
tagged individuals across consecutive meteorological seasons, under the
precommitted fixed-fixed season-B null and physical SITE-BLOCK inference.

This does not calculate W/B, individual home ranges, density allocation
or the original rejected eight-genus hypothesis. No identifiers exported.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import json
import os
from pathlib import Path
from statistics import mean

from analysis.run_multiscale_density_estimability_release2026_v3 import (
    PRODUCT, RELEASE, START, END, PRODUCT_URL, QUERY_URL, TOKEN_ENV,
    MAX_DOWNLOAD_WORKERS, _request_json, _site_codes, _inventory,
    _download_many, _read_plot_rows, _read_trap_rows, _candidate_nights,
)
from analysis.audit_multiscale_density_mnka_variation_v1 import _taxonomy
from analysis.audit_neon_crossseason_genus_support_v1 import source_event_support
from analysis.neon_crossseason_template_null_v1 import (
    fixed_fixed_null_for_unit, crossseason_template_inference
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_crossseason_genus_template_ecology_v1.json"
FROZEN=ROOT/"results/neon_crossseason_genus_template_support_receipt_20261019.json"
N_DRAWS=2000
N_BURN=1000
SWAPS=40
MIN_ESS=200
SEED=2026101901


def require(condition,msg):
    if not condition:
        raise RuntimeError("SOURCE-LOCK STOP: "+msg)


def verified_support_gate(source_summary:dict, original:dict):
    fields=(
        "approved_original_three_night_sessions",
        "eligible_distinct_selected_events",
        "selected_one_bout_per_season_sessions",
        "selected_bouts_with_trap_effort_ge90_per_night",
        "candidate_adjacent_season_pairs_after_effort",
        "eligible_primary_pairs","eligible_primary_sites",
        "eligible_primary_site_plot_units",
        "eligible_primary_season_year_combinations",
        "eligible_2genus_diagnostic_pairs",
        "primary_shared_genus_count_distribution",
        "bridge_tag_histories_excluded",
        "cross_genus_identity_conflicts",
        "ambiguous_same_night_tag_event_combinations",
        "event_source_exclusion_categories",
        "capture_source_exclusion_categories",
    )
    for field in fields:
        require(source_summary[field]==original[field],
                "original preregistered support changed: "+field)
    require(
        original["status"]=="SOURCE_STRUCTURAL_GO_OUTCOME_SEALED"
        and original["eligible_primary_pairs"]==58
        and original["eligible_primary_sites"]==14
        and source_summary["crossseason_spatial_overlap_opened"] is False,
        "pre-effect 58-unit 14-site GO receipt changed"
    )


def run() -> dict:
    frozen=json.loads(FROZEN.read_text(encoding="utf-8"))
    if RELEASE!="RELEASE-2026" or START!="2015-04" or END!="2026-09":
        raise RuntimeError("Original release or window changed")
    token=os.environ.get(TOKEN_ENV,"").strip()
    if not token:
        raise RuntimeError("Original NEON source credential unavailable")
    all_target,genus_by_taxon,_=_taxonomy()
    sites=_site_codes(_request_json(PRODUCT_URL))
    manifest=_inventory(_request_json(
        QUERY_URL,token=token,body={
            "productCode":PRODUCT,"siteCodes":sites,
            "startDateMonth":START,"endDateMonth":END,
            "release":RELEASE,"package":"basic","includeProvisional":False,
        }
    ))
    require(len(manifest)==3547,
            "release manifest differs from archived source eligibility")
    plots=[]
    plot_files=[x for x in manifest if "mam_perplotnight" in x["name"]]
    require(len(plot_files)==1773,
            "released perplotnight count changed")
    for meta,raw in zip(
        plot_files,_download_many(plot_files,token,max_workers=MAX_DOWNLOAD_WORKERS)
    ):
        plots.extend(_read_plot_rows(raw,meta["site"],meta["month"]))
    nights,site_months=_candidate_nights(plots)
    trap_files=[x for x in manifest if "mam_pertrapnight" in x["name"]
                and (x["site"],x["month"]) in site_months]
    require(len(trap_files)==1707,
            "released pertrapnight sample pool changed")
    traps=[]
    for meta,raw in zip(
        trap_files,_download_many(trap_files,token,max_workers=MAX_DOWNLOAD_WORKERS)
    ):
        for row in _read_trap_rows(raw,nights):
            row["_site"]=meta["site"]
            traps.append(row)
    require(len(plots)==21363 and len(traps)==1505827,
            "NEON source row universe drifted")

    internal=[]
    summary=source_event_support(
        plots,traps,genus_by_taxon,internal_units=internal
    )
    verified_support_gate(summary,frozen)
    require(len(internal)==58,
            "Private spatial units do not match prior support count")

    by_site=defaultdict(list)
    null_states=Counter()
    unit_diagnostics=[]
    # Deterministic unit order based ONLY on approved source identifiers.
    # The identifiers and exact genus/trap labels remain ephemeral in RAM.
    units=sorted(internal,key=lambda x:(
        x["site"],x["site_plot"],x["season_ordinal"]
    ))
    for idx,item in enumerate(units):
        effect=fixed_fixed_null_for_unit(
            item["A"],item["B"],seed=SEED+idx,
            n_draws=N_DRAWS,burn_in=N_BURN,
            swaps_per_draw=SWAPS,min_effective_draws=MIN_ESS,
        )
        null_states[effect["status"]]+=1
        unit_diagnostics.append({
            "source_genera":effect["source_genera"],
            "observed_genus_trap_cells_season_A":effect["season_A_observed_genus_trap_cells"],
            "observed_genus_trap_cells_season_B":effect["season_B_observed_genus_trap_cells"],
            "status":effect["status"],
            "z":effect.get("z"),
            "lag1_overlap_autocorrelation":effect.get("lag1_overlap_autocorrelation"),
            "approx_effective_null_draws_lag1":effect.get("approx_effective_null_draws_lag1"),
            "swap_acceptance_rate":effect.get("swap_acceptance_rate"),
        })
        if effect["status"]=="INFORMATIVE_FIXED_FIXED_NULL":
            by_site[item["site"]].append(effect["z"])

    site_result=crossseason_template_inference(by_site,seed=SEED)
    informative=sum(len(v) for v in by_site.values())
    require(informative==null_states["INFORMATIVE_FIXED_FIXED_NULL"],
            "Informative unit count did not reconcile site groups")
    require(informative+sum(n for key,n in null_states.items() if key!="INFORMATIVE_FIXED_FIXED_NULL")
            ==summary["eligible_primary_pairs"],
            "Original eligible 58 unit denominator not conserved")

    # Original preregistered positive direction, physical sites, and
    # fixed null are not rewritten after seeing this outcome.
    overall=site_result["status"]
    return {
        "schema":"neon.independent_crossseason_genus_template_ecology.v1",
        "status":overall,
        "source":{
            "release":RELEASE,"product":PRODUCT,
            "source_files_MD5_verified":len(manifest),
            "source_plot_rows":len(plots),"source_trap_rows":len(traps),
            "original_study":"NEON RELEASE-2026 2015-04 through 2026-09",
            "structural_receipt":"results/neon_crossseason_genus_template_support_receipt_20261019.json",
            "original_pre_effect_source_gate_reproduced":True,
            "San_Jacinto_study_area_prior_seen_before_freeze":True,
        },
        "frozen_design":{
            "document":"docs/NEON_CROSS_SEASON_GENUS_SPATIAL_TEMPLATE_DESIGN_20261019.md",
            "taxon_rank":"genus; species-group and uncertain species retained at genus level",
            "shared_marked_individuals_excluded_from_both_seasons":True,
            "target_source_site_plot_adjacent_meteorological_seasons":True,
            "minimum_genera_per_unit":3,
            "minimum_replaced_tagged_individuals_per_genus_per_season":2,
            "minimum_canonical_traps_per_night":90,
            "original_eligible_pairs":summary["eligible_primary_pairs"],
            "original_eligible_physical_sites":summary["eligible_primary_sites"],
            "null_randomization":"binary season-B 2x2 fixed-fixed swaps; each genus occupancy and each station season-B richness preserved",
            "season_A_matrix_fixed":True,
            "null_replicates_per_unit":N_DRAWS,
            "accepted_swap_burnin":N_BURN,
            "accepted_swaps_between_draws":SWAPS,
            "minimum_approx_effective_null_draws":MIN_ESS,
            "random_seed":SEED,
            "global_primary_inference":"physical NEON site means of unit Z; exact 2^site sign flips if <=18 sites",
            "alpha_one_sided":0.05,
            "minimum_informative_physical_sites":8,
            "no_additional_environmental_moderators_examined":True,
        },
        "unit_result_counts":dict(null_states),
        "informative_unit_source_geometry_summary":{
            "informative_unit_count":informative,
            "informative_site_count":len(by_site),
            "unlabelled_unit_diagnostics":unit_diagnostics,
        },
        "independent_site_ecology":site_result,
        "claim_boundary":{
            "ecological_main_endpoint_opened":True,
            "site_test_criterion_supported":site_result["ecological_site_level_criterion_passed"],
            "negative_or_stop_result_retained_unchanged":True,
            "taxon_resolution_genus_not_species":True,
            "causal_competition_or_habitat_filtering_proven":False,
            "capture_detectability_standardized_across_genera":False,
            "activity_centres_telemetry_or_movement_estimated":False,
            "individual_identity_linkage_beyond_source_tag_proven":False,
            "original_eight_genus_density_generality":"FAILED_5_OF_8",
            "F_C_fixed_total_identification":"HISTORICAL_NO_CONSERVATIVE_DIRECT_PAIRS",
            "MOSA_W_B_effects":"SEALED",
            "no_raw_animal_ids_or_site_codes_exported":True,
        },
    }


def main()->int:
    try:
        output=run()
    except Exception as exc:
        output={
            "schema":"neon.independent_crossseason_genus_template_ecology.v1",
            "status":"STOP_ORIGINAL_SOURCE_OR_SPATIAL_NULL_RUN",
            "diagnostic":str(exc)[:600],
            "ecological_main_endpoint_opened":False,
            "original_eight_genus_density_generality":"FAILED_5_OF_8",
            "MOSA_W_B_effects":"SEALED",
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(output,indent=2,sort_keys=True))
    return 3 if output["status"]=="STOP_ORIGINAL_SOURCE_OR_SPATIAL_NULL_RUN" else 0


if __name__=="__main__":
    raise SystemExit(main())
