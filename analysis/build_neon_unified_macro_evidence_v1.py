#!/usr/bin/env python3
"""One-source-graded NEON macro evidence ledger.

Assemble the *existing*, dated, immutable result receipts into one
macroecological inference hierarchy. Never multiply/pool incompatible p-values,
promote failed density generality, invent site overlap, or fit new effects.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FILES = {
    "recurrence": "neon_uniform_null_correction_receipt_20261020.json",
    "density": "multiscale_density_development_result_v1.json",
    "density_modes": "multiscale_density_heterogeneity_result_v1.json",
    "recurrence_support": "neon_crossseason_genus_template_support_receipt_20261019.json",
    "habitat": "neon_five_anchor_chm_source_receipt_20261020.json",
    "san_jacinto": "san_jacinto_crossseason_ecological_comparator_receipt_20261019.json",
    "crosswalk": "neon_unified_macro_source_crosswalk_receipt_20261025.json",
    "macro_selection": "neon_macro_biogeographic_selection_receipt_20261025.json",
}
OUTPUT = RESULTS / "neon_unified_macro_evidence_20261025.json"

def require(value: bool, reason: str) -> None:
    if not value:
        raise ValueError("MACRO_EVIDENCE_SOURCE_DRIFT: " + reason)

def _read(root: Path) -> dict[str, dict]:
    return {name: json.loads((root / filename).read_text(encoding="utf-8"))
            for name, filename in FILES.items()}

def build(root: Path = RESULTS) -> dict:
    src = _read(root)
    rec, dev, het = src["recurrence"], src["density"], src["density_modes"]
    sup, habitat, sj = src["recurrence_support"], src["habitat"], src["san_jacinto"]
    cw = src["crosswalk"]
    macro = src["macro_selection"]
    require(rec["status"] == "CORRECTED_UNIFORM_NULL_SUPPORTS_RECURRENCE_CONDITIONALLY",
            "corrected recurrence no longer supports the frozen observational result")
    all14, clear12 = rec["full_14site"], rec["source_disjoint_12site"]
    require((all14["physical_sites"], all14["seasonal_pairs"], all14["positive_site_means"]) == (14, 58, 11),
            "full corrected recurrence cohort changed")
    require((clear12["physical_sites"], clear12["seasonal_pairs"], clear12["positive_site_means"]) == (12, 46, 10),
            "source disjoint recurrence cohort changed")
    require(all14["corrected_site_mean_Z"] > 0 and clear12["corrected_site_mean_Z"] > 0,
            "corrected recurrence effect direction changed")
    require(all14["within_site_comonotone_stress"]["plus_one_p"] < .05
            and clear12["within_site_comonotone_stress"]["plus_one_p"] < .05,
            "correction rank-coupled conditional null threshold changed")
    require(rec["correction"]["post_result_correctness_reanalysis_not_new_independent_confirmation"],
            "corrected sampler erroneously called new confirmation")
    require((sup["eligible_primary_pairs"], sup["eligible_primary_sites"],
             sup["candidate_adjacent_season_pairs_after_effort"],
             sup["eligible_2genus_diagnostic_pairs"],
             sup["selected_bouts_with_trap_effort_ge90_per_night"]) == (58,14,803,216,1838),
            "original source population/selection denominators changed")
    require(dev["support"]["analysis_sessions"]==1326
            and dev["support"]["sites"]==40 and dev["support"]["genera"]==8,
            "old density development cohort changed")
    guard=dev["preregistered_guard"]
    require(guard["passed"] is False
            and guard["required_positive_genus_count"]==6
            and guard["observed_positive_genus_count"]==5,
            "the original failed density generality was modified")
    require(het["primary_guard_remains_failed"] and het["primary_guard_may_not_be_relaxed"],
            "heterogeneity audit reopened failed primary")
    dx=dev["genus_specific_delta"]
    require(len(dx)==8
            and sum(x["beta"]>0 for x in dx)==5,
            "original eight genus effects drifted")
    modes=het["robust_multisite_descriptive_modes"]
    require(len(modes["packing_like"])==3
            and len(modes["footprint_compression_like"])==2
            and len(modes["unresolved_or_context_dependent"])==3,
            "post hoc spatial modes changed")
    require(habitat["original_plots"]==30 and habitat["valid_anchors"]==150
            and habitat["plots_with_nonzero_five_anchor_canopy_range"]==14
            and habitat["ecological_genus_habitat_effect_computed"] is False,
            "independent habitat source coverage or effect scope drifted")
    require(sj["source_test"]["seasonal_units"]==10
            and sj["source_test"]["physical_grids"]==6
            and sj["source_test"]["positive_unit_Z_count"]==9
            and sj["boundaries"]["p_values_must_not_be_pooled"],
            "San Jacinto previous, different-rank evidence changed")

    require(cw["status"] == "STOP_MATCHED_RESPONSES_NOT_STRUCTURALLY_GENERAL",
            "original source-only joint macro crosswalk decision changed")
    match = cw["exact_pair_crosswalk"]
    require(cw["original_source"]["frozen_season_pairs"] == 58
            and cw["original_source"]["sites"] == 14
            and match["pairs_with_same_original_recurrence_genus_repeat_supported_in_both_events"] == 12
            and match["distinct_physical_sites_with_matched_pairs"] == 8
            and match["genera_with_matched_pairs_across_at_least_two_sites"] == 1,
            "independently source-reproduced crosswalk changed")
    require(not cw["new_post_result_source_feasibility_gates"]["pass"]
            and not cw["limitations"]["actual_W_B_m2_calculated"]
            and not cw["limitations"]["joint_spatial_recurrence_density_effect_computed"],
            "crosswalk improperly promoted into ecological response")

    macro_d = macro["original_source_denominators"]
    macro_cov = macro["sampling_coverage_summary"]
    require(macro["status"]=="SOURCE_ONLY_MACRO_SELECTION_RECONSTRUCTED"
            and (macro_d["effort_valid_three_night_bouts"],
                 macro_d["original_adjacent_season_pairs"],
                 macro_d["original_primary_three_genus_eligible_pairs"])==(1838,803,58)
            and (macro_d["physical_sites_with_one_or_more_candidate_pairs"],
                 macro_d["primary_independent_physical_sites"])==(42,14)
            and (macro_cov["distinct_candidate_domains"],
                 macro_cov["distinct_primary_domains"])==(18,10)
            and macro["effect_boundary"]["macro_habitat_or_latitude_effect_fit"] is False,
            "original geographic sampling support or effect scope changed")

    def recurrence(group: dict) -> dict:
        return {
            "sites":group["physical_sites"], "pairs":group["seasonal_pairs"],
            "positive_site_means":group["positive_site_means"],
            "corrected_site_mean_z":group["corrected_site_mean_Z"],
            "post_result_product_null_plus_one_p":group["independent_product_null"]["plus_one_p"],
            "post_result_product_null_tail_at_simulation_floor":group["independent_product_null"]["p_is_finite_simulation_resolution_floor"],
            "post_result_rank_coupled_null_plus_one_p":group["within_site_comonotone_stress"]["plus_one_p"],
            "rank_coupled_null_not_any_joint_model_bound":group["within_site_comonotone_stress"]["not_a_proven_bound_for_all_joint_nulls"],
        }

    return {
        "schema":"neon.unified_mammal_spatial_macro_evidence.v1",
        "date":"2026-10-25",
        "status":"INTEGRATED_EXISTING_EVIDENCE_NO_NEW_ECOLOGICAL_TEST",
        "source_receipts":{k:"results/"+v for k,v in sorted(FILES.items())},
        "scientific_centre":"Persistence of taxon-associated spatial organization across observed identity and population-state changes",
        "macro_sampling_frame":{
            "original_source_release":sup["original_NEON_source_provenance"]["release"],
            "effort_qualified_three_night_selected_bouts":sup["selected_bouts_with_trap_effort_ge90_per_night"],
            "adjacent_season_candidates":sup["candidate_adjacent_season_pairs_after_effort"],
            "primary_at_least_3_genus_pairs":sup["eligible_primary_pairs"],
            "primary_sites":sup["eligible_primary_sites"],
            "diagnostic_at_least_2_genus_pairs_not_confirmed":sup["eligible_2genus_diagnostic_pairs"],
            "unqualified_or_absent_biomes_not_as_negative_spatial_effect":True,
            "original_2026_release_already_used_for_hypothesis_generation":True,
        },
        "geographic_macro_selection_source_only":{
            "status":"ORIGINAL_RELEASE_INCLUSION_SUPPORT_ONLY",
            "effort_valid_three_night_bouts":macro_d["effort_valid_three_night_bouts"],
            "physical_sites_with_qualifying_effort_bouts":macro_d["physical_sites_with_one_or_more_effort_valid_bouts"],
            "candidate_adjacent_season_pairs":macro_d["original_adjacent_season_pairs"],
            "candidate_physical_sites":macro_d["physical_sites_with_one_or_more_candidate_pairs"],
            "primary_strict_three_genus_pairs":macro_d["original_primary_three_genus_eligible_pairs"],
            "primary_strict_sites":macro_d["primary_independent_physical_sites"],
            "strict_fraction_of_candidate_pairs":macro_d["primary_eligibility_fraction_of_candidates"],
            "candidate_ecological_domains":macro_cov["distinct_candidate_domains"],
            "primary_ecological_domains":macro_cov["distinct_primary_domains"],
            "core_candidate_pairs":macro["field_site_core_gradient_grouped_source_only"]["CORE"]["source_adjacent_season_candidate_pairs"],
            "core_strict_pairs":macro["field_site_core_gradient_grouped_source_only"]["CORE"]["primary_eligible_pairs"],
            "gradient_candidate_pairs":macro["field_site_core_gradient_grouped_source_only"]["GRADIENT"]["source_adjacent_season_candidate_pairs"],
            "gradient_strict_pairs":macro["field_site_core_gradient_grouped_source_only"]["GRADIENT"]["primary_eligible_pairs"],
            "ecological_recurrence_by_domain_estimated":False,
            "geographic_ineligibility_not_zero_recurrence":True,
        },
        "spatial_recurrence":{
            "status":"POSITIVE_CORRECTED_CONDITIONAL_PATTERN",
            "all_original_sites":recurrence(all14),
            "exclude_source_reused_seasons":recurrence(clear12),
            "taxonomic_rank":"genus",
            "sampling_unit":"site x plot x consecutive season, independent geographic unit site",
            "all_original_shared_tags_excluded_from_both_seasons":True,
            "biological_death_birth_or_emigration_proven":False,
            "old_accepted_swap_null_not_validated":True,
            "no_competition_or_habitat_cause_identified":True,
        },
        "density_accommodation":{
            "status":"DEVELOPMENT_HETEROGENEITY_WITH_FROZEN_GENERALITY_FAILURE",
            "sessions":dev["support"]["analysis_sessions"],
            "sites":dev["support"]["sites"],"genera":dev["support"]["genera"],
            "genus_balanced_beta_w_m2_per_mnka":dev["primary"]["beta_W_m2_per_mnka"],
            "genus_balanced_beta_b_m2_per_mnka":dev["primary"]["beta_B_debiased_m2_per_mnka"],
            "genus_balanced_delta_beta_m2_per_mnka":dev["primary"]["delta_beta_m2_per_mnka"],
            "old_required_positive_genera":guard["required_positive_genus_count"],
            "old_observed_positive_genera":guard["observed_positive_genus_count"],
            "old_general_cross_genus_rule_passed":False,
            "all_eight_genera_including_negative": [
                {"genus":r["genus"],"beta_delta_m2_per_mnka":r["beta"],
                 "sessions":r["sessions"],"sites":r["sites"]} for r in dx],
            "post_result_spatial_response_modes":{
                "packing_like":[v["genus"] for v in modes["packing_like"]],
                "footprint_compression_like":[v["genus"] for v in modes["footprint_compression_like"]],
                "unresolved":list(modes["unresolved_or_context_dependent"]),
            },
            "future_confirmatory_response_opened":False,
            "spatial_accommodation_causally_due_to_competition":False,
        },
        "habitat_source_only":{
            "tested_original_plots":habitat["original_plots"],
            "valid_five_anchor_chm_values":habitat["valid_anchors"],
            "plots_with_nonzero_five_anchor_chm_range":habitat["plots_with_nonzero_five_anchor_canopy_range"],
            "plots_with_all_five_anchors_chm_zero":habitat["plots_with_all_five_valid_and_zero_canopy"],
            "non_e5_coordinate_uncertainty_missing":habitat["anchors_with_unknown_coordinate_uncertainty"],
            "all_stations_capture_dated_and_raster_matched":False,
            "genus_habitat_or_detection_effect_estimated":False,
        },
        "independent_system_prior":{
            "status":"SINGLE_STUDY_AREA_DIFFERENT_SPECIES_RANK_ORIGINAL_NOT_RECALIBRATED",
            "seasonal_units":sj["source_test"]["seasonal_units"],
            "physical_grids_in_one_study_area":sj["source_test"]["physical_grids"],
            "positive_unit_z":sj["source_test"]["positive_unit_Z_count"],
            "historical_grid_signflip_p_not_pooled":sj["source_test"]["one_sided_exact_grid_signflip_p"],
        },
        "joint_macro_inference":{
            "matched_same_population_site_plot_event_support_audited":True,
            "source_only_exact_matched_season_pairs":match["pairs_with_same_original_recurrence_genus_repeat_supported_in_both_events"],
            "source_only_matched_physical_sites":match["distinct_physical_sites_with_matched_pairs"],
            "source_only_multi_site_genera":match["genera_with_matched_pairs_across_at_least_two_sites"],
            "original_release_same_population_source_feasibility_passed":False,
            "direct_joint_model_status":"STOP_TOO_FEW_MATCHED_PAIRS_AND_REPLICATED_GENERA",
            "same_population_coupling_effect_estimated":False,
            "cross_cohort_site_overlap_known":False,
            "R_and_density_beta_different_estimands_not_pooled":True,
            "new_confirmatory_data_required":True,
            "mechanism_status":"HABITAT_VS_DETECTION_VS_INTERACTIONS_UNRESOLVED",
        },
        "plan":"docs/NEON_UNIFIED_MACROECOLOGY_20261025.md",
    }

def main() -> int:
    OUTPUT.write_text(json.dumps(build(),ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":"INTEGRATED_EXISTING_EVIDENCE_NO_NEW_ECOLOGICAL_TEST",
        "output":str(OUTPUT.relative_to(ROOT)),"preserved_density_failure":True,
        "no_combined_p_value":True},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
