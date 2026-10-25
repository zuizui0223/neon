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
    "exact_two_source":"neon_exact_two_genus_source_receipt_20261025.json",
    "exact_two_ecology":"neon_exact_two_genus_ecological_receipt_20261025.json",
    "expanded_2plus_geo":"neon_macro_two_plus_genus_coverage_20261025.json",
    "new_site_sensitivity":"neon_exact_two_new_sites_sensitivity_receipt_20261025.json",
    "recorded_stations_source":"neon_macro_six_night_recorded_station_support_20261025.json",
    "recorded_stations_recurrence":"neon_macro_six_night_common_station_recurrence_receipt_20261025.json",
    "original_tower_temperature_qc":"neon_macro_original_tower_month_thermal_QC_STOP_20261025.json",
    "exact_station_conditioned_10m_patch":"neon_macro_10m_patch_conditional_20261025.json",
    "official_trap_status_456_stop":"neon_macro_six_night_trapStatus456_SOURCE_STOP_20261026.json",
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
    two_source = src["exact_two_source"]
    two_effect = src["exact_two_ecology"]
    expanded = src["expanded_2plus_geo"]
    new_site = src["new_site_sensitivity"]
    station_source=src["recorded_stations_source"]
    station_effect=src["recorded_stations_recurrence"]
    climate_source=src["original_tower_temperature_qc"]
    patch=src["exact_station_conditioned_10m_patch"]
    trap_qc=src["official_trap_status_456_stop"]
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

    require(two_source["status"]=="EXACT_TWO_GENUS_SOURCE_GO_NO_EFFECT_OPENED"
            and two_source["precommitted_source_gate"]["passed"]
            and (two_source["exact_two_source"]["pairs"],
                 two_source["exact_two_source"]["physical_sites"],
                 two_source["exact_two_source"]["domains"])==(158,30,15),
            "source-only exactly-two population drifted")
    require(two_effect["status"]=="EXPLORATORY_CONDITIONAL_TWO_GENUS_RECURRENCE_POSITIVE"
            and two_effect["variance_source_support"]["passed"]
            and two_effect["observed"]["informative_exact_two_genus_pairs"]==150
            and two_effect["observed"]["positive_physical_site_mean_count"]==25
            and two_effect["observed"]["physical_sites"]==30,
            "exact two-genus ecological outcome, support or status changed")
    require(abs(two_effect["observed"]["corrected_equal_site_mean_Z"]-0.6147113767599713)<1e-10
            and abs(two_effect["source_disjoint_exact_two_genus_conditional_meta_null"]["observed_equal_site_mean_z"]-0.6983519175917221)<1e-10
            and (two_effect["source_disjoint_exact_two_genus_conditional_meta_null"]["sites"],
                 two_effect["source_disjoint_exact_two_genus_conditional_meta_null"]["seasonal_pairs"])==(17,48),
            "new site-block corrected Z or disjoint sensitivity drifted")
    require(two_effect["claim_boundary"]["post_result_historical_exploratory_not_confirmatory"]
            and two_effect["claim_boundary"]["no_density_W_B_or_climate_biogeographic_effect_fitted"],
            "exploratory new source effects falsely labelled independent or causal")
    require(expanded["status"]=="EFFECT_BLIND_EXPANDED_SAMPLE_COVERAGE_ONLY"
            and (expanded["all_two_plus"]["pairs"],
                 expanded["all_two_plus"]["physical_sites"],
                 expanded["all_two_plus"]["ecological_domains"])==(216,31,15),
            "2+ original macro geographical union changed")
    require(two_effect["full_exact_two_genus_conditional_meta_null"]["rank_comonotone_within_site_exact_marginal_stress"]["one_sided_plus_one_p"]<0.05,
            "exact two-genus constrained exploratory site-null no longer supported")

    require(new_site["status"]=="NEW_PHYSICAL_SITES_POSITIVE_CONDITIONAL_EXPLORATORY_SENSITIVITY"
            and new_site["feasibility"]["passed"]
            and (new_site["source"]["geographically_new_exact_two_physical_sites"],
                 new_site["source"]["new_site_exact_two_pairs"],
                 new_site["observed_geographically_nonoverlap_sites"]["informative_exact_two_pairs"],
                 new_site["observed_geographically_nonoverlap_sites"]["positive_site_mean_count"])==(17,74,71,15),
            "geographically nonoverlap exploratory sensitivity source cohort changed")
    require(abs(new_site["observed_geographically_nonoverlap_sites"]["equal_site_mean_z"]-0.7600592308705587)<1e-10
            and new_site["source"]["new_ecological_domains_not_in_original_strict14"]==5
            and new_site["scientific_inference"]["post_result_geographic_sensitivity_not_predeclared_independent_replication"],
            "new physical-site conditional ecology sign or pre-effect caveat changed")
    require(new_site["whole_site_source_reuse_exclusion"]["status"]==
            "STOP_WHOLE_SITE_SOURCE_DISJOINT_SUBCOHORT_UNDERPOWERED"
            and (new_site["whole_site_source_reuse_exclusion"]["remaining_physical_sites"],
                 new_site["whole_site_source_reuse_exclusion"]["remaining_informative_pairs"])==(9,16),
            "strict entire season-reuse site exclusion was improperly opened")

    require(station_source["status"]=="SOURCE_COMMON_SIX_NIGHT_RECORDED_STATION_GO"
            and station_source["retained_pairs"]==158
            and station_source["retained_independent_physical_sites"]==30
            and station_source["retained_NEON_ecological_domains"]==15
            and station_source["all_six_recorded_station_count_distribution"]["min"]==93,
            "original all-six recorded station support changed")
    require(station_effect["status"]=="OBSERVATION_MATCHED_STATION_EXPLORATORY_RECURRENCE_POSITIVE"
            and station_effect["variance_pre_effect"]["passed"]
            and (station_effect["observed"]["informative_seasonal_pairs"],
                 station_effect["observed"]["independent_physical_sites"],
                 station_effect["observed"]["positive_site_mean_count"])==(150,30,25)
            and abs(station_effect["observed"]["site_weighted_mean_Z"]-0.6109014700960878)<1e-10,
            "six-night original two-row observational-geometry sensitivity changed")
    require(station_effect["whole_site_reused_season_sensitivity_status"]==
            "SOURCE_WHOLE_SITE_SEASON_REUSE_SENSITIVITY_FIT"
            and (station_effect["whole_site_reused_season_sensitivity"]["seasonal_pairs"],
                 station_effect["whole_site_reused_season_sensitivity"]["sites"])==(48,17),
            "source whole-site reused-season observational effect changed")
    require(station_effect["claim_boundary"]["recorded_station_roster_not_proof_of_operable_traps"]
            and station_effect["claim_boundary"]["genus_specific_catchability_or_stable_microhabitat_not_excluded"],
            "ecological observation process control overclaimed")
    require(climate_source["status"]=="STOP_ORIGINAL_TOWER_TEMPERATURE_QC_OR_DOMAIN_SUPPORT"
            and climate_source["climate_effect_opened"] is False
            and (climate_source["weather_source_QA"]["verified_and_parsed_months"],
                 climate_source["weather_source_QA"]["QC_good_months"],
                 climate_source["weather_source_QA"]["QC_bad_months"])==(205,143,62)
            and (climate_source["weather_pair_pre_effect_feasibility"]["source_pair_with_both_months_station_quality_verified"],
                 climate_source["weather_pair_pre_effect_feasibility"]["quality_verified_original_physical_sites"],
                 climate_source["weather_pair_pre_effect_feasibility"]["quality_verified_ecological_domains"])==(79,27,15)
            and climate_source["source_metadata_and_selection"]["source_structural_thresholds"]["minimum_original_QC_paired_pairs"]==80,
            "the environmental site-month source quality gate was not preserved")


    require(patch["status"]=="POSITIVE_EXPLORATORY_10M_PATCH_RECURRENCE_BEYOND_SAME_TRAP_OVERLAP"
            and patch["source_conditional_null_variance_gate"]["passed"]
            and (patch["source_conditional_null_variance_gate"]["original_source_pairs"],
                 patch["source_conditional_null_variance_gate"]["exact_conditional_variance_positive_pairs"],
                 patch["source_conditional_null_variance_gate"]["exact_conditional_variance_zero_pairs"])==(158,153,5),
            "new exploratory exact-overlap-conditioned 10m patch source/gate changed")
    require((patch["observed"]["physical_sites"],
             patch["observed"]["positive_site_mean_count"],
             patch["observed"]["informative_source_pairs"])==(30,22,153)
            and abs(patch["observed"]["equal_physical_site_mean_Z_neighbor_given_same_station_overlap"]-0.31030688542725354)<1e-10,
            "source-stabilized exact-overlap-conditioned patch score drifted")
    require(patch["conditional_site_meta_null"]["comonotone_within_site_marginal_null"]["one_sided_p"]<.05
            and patch["site_reused_season_exclusion"]["conditional_site_meta_null"]["comonotone_within_site_marginal_null"]["one_sided_p"]>.05,
            "main/strict season-source patch robustness distinction changed")
    require((patch["site_reused_season_exclusion"]["remaining_informative_pairs"],
             patch["site_reused_season_exclusion"]["remaining_physical_sites"])==(50,17)
            and abs(patch["site_reused_season_exclusion"]["conditional_site_meta_null"]["observed_equal_site_weighted_mean_Z"]-0.1825892504019166)<1e-10,
            "new patch source reuse exclusion cohort/effect drifted")
    require(patch["inference"]["correlated_genus_catchability_at_neighbor_traps_not_excluded"]
            and patch["inference"]["no_independent_new_release_or_confirmation"],
            "new ecological patch mechanism falsely claimed as causally established")

    require(trap_qc["status"]=="STOP_OPERABLE_456_SIX_NIGHT_SOURCE_SUPPORT"
            and (trap_qc["source_two_genus_original_pairs"],
                 trap_qc["source_original_physical_sites"],
                 trap_qc["retained_pairs"],
                 trap_qc["retained_physical_sites"],
                 trap_qc["retained_NEON_domains"])==(158,30,18,8,7)
            and trap_qc["original_source_rule"]["passed"] is False
            and (trap_qc["original_source_rule"]["minimum_retained_pairs"],
                 trap_qc["original_source_rule"]["minimum_physical_sites"],
                 trap_qc["original_source_rule"]["minimum_domains"])==(80,18,10),
            "original NEON operational-status source STOP overridden or source counts changed")
    require((trap_qc["all_six_verified_status_456_stations"]["minimum"],
             trap_qc["all_six_verified_status_456_stations"]["median"],
             trap_qc["all_six_verified_status_456_stations"]["maximum"])==(1,60,97)
            and sum(trap_qc["source_status_code_row_counts"].values())==87916,
            "original source official NEON trap status count/topology drifted")
    require(trap_qc["effects_sealed"]["no_new_observed_genus_A_cross_B_trap_overlap"]
            and trap_qc["inference_limits"]["source_station_operability_is_not_capture_detection_probability"],
            "unsupported operational-source subcohort incorrectly promoted to biological causal effect")

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
        "date":"2026-10-26",
        "status":"INTEGRATED_CORRECTED_PRIMARY_AND_POST_RESULT_TWO_GENUS_EXPLORATORY_EFFECT",
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
        "exploratory_exact_two_genus_spatial_recurrence":{
            "status":"CONDITIONAL_POSITIVE_POST_RESULT_SAME_RELEASE_EXPLORATION",
            "separate_original_strict_three_plus_pairs":two_source["original_strict_primary"]["pairs"],
            "source_exact_two_pairs":two_source["exact_two_source"]["pairs"],
            "source_sites":two_source["exact_two_source"]["physical_sites"],
            "source_domains":two_source["exact_two_source"]["domains"],
            "informative_exact_uniform_two_row_pairs":two_effect["observed"]["informative_exact_two_genus_pairs"],
            "noninformative_zero_variance_pairs":two_effect["variance_source_support"]["null_zero_variance_pairs"],
            "positive_physical_sites":two_effect["observed"]["positive_physical_site_mean_count"],
            "site_mean_z":two_effect["observed"]["corrected_equal_site_mean_Z"],
            "rank_coupled_20000_conditional_p":two_effect["full_exact_two_genus_conditional_meta_null"]["rank_comonotone_within_site_exact_marginal_stress"]["one_sided_plus_one_p"],
            "source_reuse_disjoint_pairs":two_effect["source_disjoint_exact_two_genus_conditional_meta_null"]["seasonal_pairs"],
            "source_reuse_disjoint_sites":two_effect["source_disjoint_exact_two_genus_conditional_meta_null"]["sites"],
            "source_reuse_disjoint_mean_z":two_effect["source_disjoint_exact_two_genus_conditional_meta_null"]["observed_equal_site_mean_z"],
            "source_reuse_disjoint_rank_coupled_p":two_effect["source_disjoint_exact_two_genus_conditional_meta_null"]["rank_comonotone_within_site_exact_marginal_stress"]["one_sided_plus_one_p"],
            "all_two_plus_source_union_pairs":expanded["all_two_plus"]["pairs"],
            "all_two_plus_source_union_unique_sites":expanded["all_two_plus"]["physical_sites"],
            "all_two_plus_source_union_ecological_domains":expanded["all_two_plus"]["ecological_domains"],
            "genus_richness_specific_estimands_not_pooled":True,
            "source_release_same_as_original_primary_not_independent_replication":True,
            "within_site_rank_coupling_not_universal_dependence_bound":True,
            "genus_specific_capture_propensity_not_calibrated":True,
            "environmental_mechanism_not_fitted":True,
        },
        "exact_two_new_geographic_site_sensitivity":{
            "status":"POST_RESULT_PHYSICAL_SITE_NONOVERLAP_POSITIVE_CONDITIONAL",
            "new_original14_nonoverlap_physical_sites":new_site["source"]["geographically_new_exact_two_physical_sites"],
            "new_original14_nonoverlap_ecological_domains":new_site["source"]["new_site_ecological_domains"],
            "new_domains_absent_from_original_strict14":new_site["source"]["new_ecological_domains_not_in_original_strict14"],
            "source_exact_two_pairs":new_site["source"]["new_site_exact_two_pairs"],
            "informative_exact_null_pairs":new_site["observed_geographically_nonoverlap_sites"]["informative_exact_two_pairs"],
            "positive_site_means":new_site["observed_geographically_nonoverlap_sites"]["positive_site_mean_count"],
            "equal_site_mean_z":new_site["observed_geographically_nonoverlap_sites"]["equal_site_mean_z"],
            "rank_coupled_within_site_stress_p":new_site["conditional_new_site_meta_null"]["rank_comonotone_within_site_exact_marginal_stress"]["one_sided_plus_one_p"],
            "source_reuse_full_site_sensitivity_status":new_site["whole_site_source_reuse_exclusion"]["status"],
            "source_reuse_full_site_survivor_pairs":new_site["whole_site_source_reuse_exclusion"]["remaining_informative_pairs"],
            "source_reuse_full_site_survivor_sites":new_site["whole_site_source_reuse_exclusion"]["remaining_physical_sites"],
            "same_historical_release_not_new_temporal_sampling":True,
            "post_result_no_independent_preregistration":True,
            "genus_specific_detection_not_calibrated":True,
        },
        "recorded_six_night_station_opportunity_control":{
            "status":"EXPLORATORY_POSITIVE_UNDER_COMMON_RECORDED_STATIONS",
            "original_two_genus_source_pairs":station_source["original_exact_two_genus_pairs"],
            "common_all_six_station_min":station_source["all_six_recorded_station_count_distribution"]["min"],
            "common_all_six_station_median":station_source["all_six_recorded_station_count_distribution"]["median"],
            "source_pairs_retaining_full_genus_station_support":station_source["retained_pairs"],
            "source_sites_retained":station_source["retained_independent_physical_sites"],
            "effect_informative_original_pairs":station_effect["observed"]["informative_seasonal_pairs"],
            "effect_independent_physical_sites":station_effect["observed"]["independent_physical_sites"],
            "effect_positive_site_means":station_effect["observed"]["positive_site_mean_count"],
            "effect_site_equal_mean_Z":station_effect["observed"]["site_weighted_mean_Z"],
            "original_unrestricted_exact_two_mean_Z":station_effect["original_same_release_30_site_mean_Z_reference"],
            "within_site_rank_coupled_conditional_p":station_effect["conditional_meta_exact_two_row_marginal"]["rank_comonotone_within_site_exact_marginal_stress"]["one_sided_plus_one_p"],
            "whole_site_season_source_reuse_removed_pairs":station_effect["whole_site_reused_season_sensitivity"]["seasonal_pairs"],
            "whole_site_season_source_reuse_removed_sites":station_effect["whole_site_reused_season_sensitivity"]["sites"],
            "whole_site_season_source_reuse_removed_site_Z":station_effect["whole_site_reused_season_sensitivity"]["observed_equal_site_mean_z"],
            "recorded_station_presence_does_not_verify_operability":True,
            "genus_dependent_capture_probability_not_calibrated":True,
            "same_historical_neon_release_not_new_replication":True,
        },
        "independent_original_tower_temperature_source_QC":{
            "status":"STOP_BEFORE_ABIOTIC_ECOLOGICAL_ASSOCIATION",
            "requested_original_site_months":climate_source["weather_source_QA"]["requested_source_site_months"],
            "provider_MD5_size_verified_parsed_months":climate_source["weather_source_QA"]["verified_and_parsed_months"],
            "source_months_QC_good":climate_source["weather_source_QA"]["QC_good_months"],
            "source_months_QC_failed":climate_source["weather_source_QA"]["QC_bad_months"],
            "source_pairs_with_two_qualified_months":climate_source["weather_pair_pre_effect_feasibility"]["source_pair_with_both_months_station_quality_verified"],
            "sites_with_two_qualified_months":climate_source["weather_pair_pre_effect_feasibility"]["quality_verified_original_physical_sites"],
            "domains_with_two_qualified_months":climate_source["weather_pair_pre_effect_feasibility"]["quality_verified_ecological_domains"],
            "minimum_predeclared_source_pairs_for_model":climate_source["source_metadata_and_selection"]["source_structural_thresholds"]["minimum_original_QC_paired_pairs"],
            "temperature_slope_or_confidence_interval_estimated":False,
            "not_evidence_of_zero_climate_ecological_effect":True,
            "no_threshold_relaxation_or_different_weather_variable":True,
        },
        "exact_trap_conditional_10m_local_patch_ecology":{
            "status":"MIXED_EXPLORATORY_FULL_COHORT_POSITIVE_SOURCE_REUSED_SITE_EXCLUSION_NOT_SUPPORTED",
            "null_conditions":"genus_station_margins_AND_ORIGINAL_SAME_TRAP_OVERLAP_FIXED",
            "original_source_exact_two_pairs":patch["source_conditional_null_variance_gate"]["original_source_pairs"],
            "conditional_patch_variance_informative_pairs":patch["source_conditional_null_variance_gate"]["exact_conditional_variance_positive_pairs"],
            "conditional_patch_zero_variance_pairs":patch["source_conditional_null_variance_gate"]["exact_conditional_variance_zero_pairs"],
            "physical_sites":patch["observed"]["physical_sites"],
            "positive_site_mean_count":patch["observed"]["positive_site_mean_count"],
            "original_full_mean_Z":patch["observed"]["equal_physical_site_mean_Z_neighbor_given_same_station_overlap"],
            "full_product_null_conditional_p":patch["conditional_site_meta_null"]["independent_unit_marginal_null"]["one_sided_p"],
            "full_rank_coupled_conditional_p":patch["conditional_site_meta_null"]["comonotone_within_site_marginal_null"]["one_sided_p"],
            "whole_site_season_reuse_exclusion_pairs":patch["site_reused_season_exclusion"]["remaining_informative_pairs"],
            "whole_site_season_reuse_exclusion_sites":patch["site_reused_season_exclusion"]["remaining_physical_sites"],
            "whole_site_season_reuse_exclusion_mean_Z":patch["site_reused_season_exclusion"]["conditional_site_meta_null"]["observed_equal_site_weighted_mean_Z"],
            "whole_site_season_reuse_exclusion_product_p":patch["site_reused_season_exclusion"]["conditional_site_meta_null"]["independent_unit_marginal_null"]["one_sided_p"],
            "whole_site_season_reuse_exclusion_rank_coupled_p":patch["site_reused_season_exclusion"]["conditional_site_meta_null"]["comonotone_within_site_marginal_null"]["one_sided_p"],
            "strong_general_patch_recurrence_after_source_disjointness_established":False,
            "unit_conditional_marginal_moments_exact_no_MCMC":True,
            "new_outcome_historical_post_result_not_independent_replication":True,
            "taxon_specific_spatially_correlated_catchability_unresolved":True,
        },
        "official_neon_six_night_operability_source_limit":{
            "status":"STRICT_STATUS_456_COHORT_SOURCE_STOP_NO_ECOLOGICAL_EFFECT",
            "original_two_genus_pairs":trap_qc["source_two_genus_original_pairs"],
            "original_physical_sites":trap_qc["source_original_physical_sites"],
            "status_rows":trap_qc["original_canonical_trap_status_rows"],
            "trapStatus_one_not_set_or_unprocessed_rows":trap_qc["source_status_code_row_counts"]["1"],
            "trapStatus_two_disturbed_closed_rows":trap_qc["source_status_code_row_counts"]["2"],
            "trapStatus_three_door_open_spoor_rows":trap_qc["source_status_code_row_counts"]["3"],
            "trapStatus_four_multiple_capture_rows":trap_qc["source_status_code_row_counts"]["4"],
            "trapStatus_five_capture_rows":trap_qc["source_status_code_row_counts"]["5"],
            "trapStatus_six_trap_set_empty_rows":trap_qc["source_status_code_row_counts"]["6"],
            "median_all_six_night_recorded_stations":station_source["all_six_recorded_station_count_distribution"]["median"],
            "median_all_six_night_official_status456_stations":trap_qc["all_six_verified_status_456_stations"]["median"],
            "minimum_all_six_night_status456_stations":trap_qc["all_six_verified_status_456_stations"]["minimum"],
            "maximum_all_six_night_status456_stations":trap_qc["all_six_verified_status_456_stations"]["maximum"],
            "retained_strict_source_pairs":trap_qc["retained_pairs"],
            "retained_strict_physical_sites":trap_qc["retained_physical_sites"],
            "retained_strict_NEON_domains":trap_qc["retained_NEON_domains"],
            "predeclared_minimum_source_pairs":trap_qc["original_source_rule"]["minimum_retained_pairs"],
            "predeclared_minimum_physical_sites":trap_qc["original_source_rule"]["minimum_physical_sites"],
            "predeclared_minimum_NEON_domains":trap_qc["original_source_rule"]["minimum_domains"],
            "new_operability_coded_genus_recurrence_Z_or_p_calculated":False,
            "source_QC_not_species_specific_capture_detection_estimator":True,
            "failure_of_estimation_not_negative_ecological_effect":True,
            "codes_four_five_select_capture_related_outcomes":True,
            "strict_six_night_status_intersection_does_not_mean_82percent_traps_nonoperable":True,
            "original_conditional_positive_30site_result_unchanged":True,
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
        "status":"INTEGRATED_CORRECTED_PRIMARY_AND_POST_RESULT_TWO_GENUS_EXPLORATORY_EFFECT",
        "output":str(OUTPUT.relative_to(ROOT)),"preserved_density_failure":True,
        "no_combined_p_value":True},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
