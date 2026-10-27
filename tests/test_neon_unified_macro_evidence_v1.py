"""Regression checks for the unified NEON macroecology result hierarchy.

These checks reject a false universal packing conclusion, using 58 nested
seasonal comparisons as 58 independent sites, invented habitat mechanisms,
or retroactive pooling of historical accepted-clock p-values.
"""
import json
import unittest
from pathlib import Path

from analysis.build_neon_unified_macro_evidence_v1 import build

ROOT=Path(__file__).resolve().parents[1]
RECEIPT=ROOT/"results/neon_unified_macro_evidence_20261025.json"
DESIGN=ROOT/"docs/NEON_UNIFIED_MACROECOLOGY_20261025.md"


class UnifiedMacroEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger=json.loads(RECEIPT.read_text(encoding="utf-8"))
        cls.design=DESIGN.read_text(encoding="utf-8")

    def test_ledger_exactly_reproduced_from_original_receipts(self):
        self.assertEqual(self.ledger,build())

    def test_corrected_ecological_pattern_preserved(self):
        r=self.ledger["spatial_recurrence"]
        self.assertEqual((r["all_original_sites"]["sites"],r["all_original_sites"]["pairs"]), (14,58))
        self.assertEqual((r["exclude_source_reused_seasons"]["sites"],r["exclude_source_reused_seasons"]["pairs"]), (12,46))
        self.assertEqual((r["all_original_sites"]["positive_site_means"],r["exclude_source_reused_seasons"]["positive_site_means"]), (11,10))
        self.assertAlmostEqual(r["all_original_sites"]["corrected_site_mean_z"], .7946637727454396,places=12)
        self.assertAlmostEqual(r["exclude_source_reused_seasons"]["corrected_site_mean_z"], .8431617303483938,places=12)
        self.assertTrue(r["old_accepted_swap_null_not_validated"])

    def test_old_density_falsification_is_immutable(self):
        d=self.ledger["density_accommodation"]
        self.assertEqual((d["sessions"],d["sites"],d["genera"]), (1326,40,8))
        self.assertEqual((d["old_observed_positive_genera"],d["old_required_positive_genera"]), (5,6))
        self.assertFalse(d["old_general_cross_genus_rule_passed"])
        self.assertEqual(len(d["all_eight_genera_including_negative"]),8)
        self.assertEqual(sum(g["beta_delta_m2_per_mnka"]>0 for g in d["all_eight_genera_including_negative"]),5)
        self.assertEqual(len(d["post_result_spatial_response_modes"]["footprint_compression_like"]),2)

    def test_no_false_joint_macro_inference_or_causal_habitat(self):
        j=self.ledger["joint_macro_inference"]
        self.assertFalse(j["same_population_coupling_effect_estimated"])
        self.assertFalse(j["cross_cohort_site_overlap_known"])
        self.assertTrue(j["matched_same_population_site_plot_event_support_audited"])
        self.assertEqual((j["source_only_exact_matched_season_pairs"],
                          j["source_only_matched_physical_sites"],
                          j["source_only_multi_site_genera"]), (12,8,1))
        self.assertEqual(j["direct_joint_model_status"],
                         "STOP_TOO_FEW_MATCHED_PAIRS_AND_REPLICATED_GENERA")
        self.assertFalse(j["original_release_same_population_source_feasibility_passed"])
        self.assertTrue(j["R_and_density_beta_different_estimands_not_pooled"])
        self.assertFalse(self.ledger["habitat_source_only"]["genus_habitat_or_detection_effect_estimated"])
        self.assertEqual(self.ledger["status"],"INTEGRATED_CORRECTED_PRIMARY_AND_POST_RESULT_TWO_GENUS_EXPLORATORY_EFFECT")
        self.assertIn("same-site crosswalk",self.design)
        self.assertIn("source-only",self.design)
        c=json.loads((ROOT/"results/neon_unified_macro_source_crosswalk_receipt_20261025.json").read_text(encoding="utf-8"))
        self.assertFalse(c["new_post_result_source_feasibility_gates"]["pass"])
        self.assertEqual(c["original_source"]["frozen_season_pairs"],58)
        self.assertFalse(c["limitations"]["actual_W_B_m2_calculated"])

    def test_exact_two_exploratory_positive_same_release_not_new_replication(self):
        e=self.ledger["exploratory_exact_two_genus_spatial_recurrence"]
        self.assertEqual((e["source_exact_two_pairs"],e["source_sites"],e["source_domains"]),
                         (158,30,15))
        self.assertEqual((e["informative_exact_uniform_two_row_pairs"],
                          e["noninformative_zero_variance_pairs"],
                          e["positive_physical_sites"]), (150,8,25))
        self.assertAlmostEqual(e["site_mean_z"],0.6147113767599713,places=12)
        self.assertEqual((e["source_reuse_disjoint_pairs"],e["source_reuse_disjoint_sites"]),(48,17))
        self.assertAlmostEqual(e["source_reuse_disjoint_mean_z"],0.6983519175917221,places=12)
        self.assertEqual((e["all_two_plus_source_union_pairs"],
                          e["all_two_plus_source_union_unique_sites"],
                          e["all_two_plus_source_union_ecological_domains"]),(216,31,15))
        self.assertTrue(e["genus_richness_specific_estimands_not_pooled"])
        self.assertTrue(e["source_release_same_as_original_primary_not_independent_replication"])
        self.assertTrue(e["genus_specific_capture_propensity_not_calibrated"])
        self.assertTrue(e["within_site_rank_coupling_not_universal_dependence_bound"])
        self.assertFalse(e["environmental_mechanism_not_fitted"] is False)

    def test_seventeen_new_physical_sites_positive_but_strict_reuse_stop(self):
        x=self.ledger["exact_two_new_geographic_site_sensitivity"]
        self.assertEqual((x["new_original14_nonoverlap_physical_sites"],
                          x["new_original14_nonoverlap_ecological_domains"],
                          x["new_domains_absent_from_original_strict14"]),(17,11,5))
        self.assertEqual((x["source_exact_two_pairs"],x["informative_exact_null_pairs"],
                          x["positive_site_means"]),(74,71,15))
        self.assertAlmostEqual(x["equal_site_mean_z"],0.7600592308705587,places=12)
        self.assertAlmostEqual(x["rank_coupled_within_site_stress_p"],0.000599970001499925,places=12)
        self.assertEqual((x["source_reuse_full_site_survivor_sites"],
                          x["source_reuse_full_site_survivor_pairs"]),(9,16))
        self.assertEqual(x["source_reuse_full_site_sensitivity_status"],
                         "STOP_WHOLE_SITE_SOURCE_DISJOINT_SUBCOHORT_UNDERPOWERED")
        self.assertTrue(x["same_historical_release_not_new_temporal_sampling"])
        self.assertTrue(x["post_result_no_independent_preregistration"])
        self.assertTrue(x["genus_specific_detection_not_calibrated"])

    def test_common_six_night_recorded_trap_control_does_not_exclude_catchability(self):
        o=self.ledger["recorded_six_night_station_opportunity_control"]
        self.assertEqual((o["common_all_six_station_min"],o["common_all_six_station_median"]),
                         (93,100))
        self.assertEqual((o["source_pairs_retaining_full_genus_station_support"],
                          o["source_sites_retained"]),(158,30))
        self.assertEqual((o["effect_informative_original_pairs"],
                          o["effect_independent_physical_sites"],
                          o["effect_positive_site_means"]),(150,30,25))
        self.assertAlmostEqual(o["effect_site_equal_mean_Z"],0.6109014700960878,places=12)
        self.assertAlmostEqual(o["original_unrestricted_exact_two_mean_Z"],0.6147113767599713,places=12)
        self.assertEqual((o["whole_site_season_source_reuse_removed_pairs"],
                          o["whole_site_season_source_reuse_removed_sites"]),(48,17))
        self.assertTrue(o["recorded_station_presence_does_not_verify_operability"])
        self.assertTrue(o["genus_dependent_capture_probability_not_calibrated"])

    def test_temperature_provider_source_qc_stop_is_not_ecological_null(self):
        w=self.ledger["independent_original_tower_temperature_source_QC"]
        self.assertEqual((w["provider_MD5_size_verified_parsed_months"],
                          w["source_months_QC_good"],
                          w["source_months_QC_failed"]),(205,143,62))
        self.assertEqual((w["source_pairs_with_two_qualified_months"],
                          w["sites_with_two_qualified_months"],
                          w["domains_with_two_qualified_months"]),(79,27,15))
        self.assertEqual(w["minimum_predeclared_source_pairs_for_model"],80)
        self.assertEqual(w["status"],"STOP_BEFORE_ABIOTIC_ECOLOGICAL_ASSOCIATION")
        self.assertFalse(w["temperature_slope_or_confidence_interval_estimated"])
        self.assertTrue(w["not_evidence_of_zero_climate_ecological_effect"])
        self.assertTrue(w["no_threshold_relaxation_or_different_weather_variable"])

    def test_10m_patch_beyond_exact_trap_is_mixed_not_general(self):
        x=self.ledger["exact_trap_conditional_10m_local_patch_ecology"]
        self.assertEqual(x["original_source_exact_two_pairs"],158)
        self.assertEqual((x["conditional_patch_variance_informative_pairs"],
                          x["conditional_patch_zero_variance_pairs"]),(153,5))
        self.assertEqual((x["physical_sites"],x["positive_site_mean_count"]),(30,22))
        self.assertAlmostEqual(x["original_full_mean_Z"],0.31030688542725354,places=12)
        self.assertAlmostEqual(x["full_rank_coupled_conditional_p"],0.03914804259787011,places=12)
        self.assertEqual((x["whole_site_season_reuse_exclusion_pairs"],
                          x["whole_site_season_reuse_exclusion_sites"]),(50,17))
        self.assertAlmostEqual(x["whole_site_season_reuse_exclusion_mean_Z"],0.1825892504019166,places=12)
        self.assertAlmostEqual(x["whole_site_season_reuse_exclusion_rank_coupled_p"],0.22053897305134743,places=12)
        self.assertFalse(x["strong_general_patch_recurrence_after_source_disjointness_established"])
        self.assertTrue(x["taxon_specific_spatially_correlated_catchability_unresolved"])
        self.assertTrue(x["new_outcome_historical_post_result_not_independent_replication"])
        self.assertIn("ORIGINAL_SAME_TRAP_OVERLAP_FIXED",x["null_conditions"])

    def test_operability_status_456_source_stop_protects_catchability_uncertainty(self):
        o=self.ledger["official_neon_six_night_operability_source_limit"]
        self.assertEqual((o["original_two_genus_pairs"],
                          o["original_physical_sites"]),(158,30))
        self.assertEqual((o["status_rows"],
                          o["median_all_six_night_recorded_stations"],
                          o["median_all_six_night_official_status456_stations"]),
                         (87916,100,60))
        self.assertEqual((o["retained_strict_source_pairs"],
                          o["retained_strict_physical_sites"],
                          o["retained_strict_NEON_domains"]),(18,8,7))
        self.assertEqual((o["predeclared_minimum_source_pairs"],
                          o["predeclared_minimum_physical_sites"],
                          o["predeclared_minimum_NEON_domains"]),(80,18,10))
        self.assertEqual(sum((
                          o["trapStatus_one_not_set_or_unprocessed_rows"],
                          o["trapStatus_two_disturbed_closed_rows"],
                          o["trapStatus_three_door_open_spoor_rows"],
                          o["trapStatus_four_multiple_capture_rows"],
                          o["trapStatus_five_capture_rows"],
                          o["trapStatus_six_trap_set_empty_rows"]
                          )),87916)
        self.assertFalse(o["new_operability_coded_genus_recurrence_Z_or_p_calculated"])
        self.assertTrue(o["source_QC_not_species_specific_capture_detection_estimator"])
        self.assertTrue(o["failure_of_estimation_not_negative_ecological_effect"])
        self.assertTrue(o["codes_four_five_select_capture_related_outcomes"])
        self.assertEqual(o["status"],"STRICT_STATUS_456_COHORT_SOURCE_STOP_NO_ECOLOGICAL_EFFECT")

    def test_firstnight_reencounter_difference_is_not_true_capture_p(self):
        x=self.ledger["firstnight_genus_reencounter_observation_process"]
        self.assertEqual((x["original_source_firstnight_animals"],
                          x["unique_original_three_night_bouts"],
                          x["firstnight_capture_physical_sites"]),(3255,293,30))
        self.assertEqual(x["source_ranked_and_selected_genus_pair"],
                         ["Microtus","Peromyscus"])
        self.assertEqual(x["matched_original_physical_sites"],7)
        self.assertEqual((x["microtus_firstnight_animals"],
                          x["microtus_recaptured_on_later_original_night"],
                          x["peromyscus_firstnight_animals"],
                          x["peromyscus_recaptured_on_later_original_night"]),
                         (179,97,435,330))
        self.assertAlmostEqual(x["site_equal_microtus_minus_peromyscus_fraction"],
                               -0.23509421168579211,places=12)
        self.assertAlmostEqual(x["site_block_bootstrap_95_interval"][0],
                               -0.45695823864059304,places=12)
        self.assertAlmostEqual(x["site_block_bootstrap_95_interval"][1],
                               -0.023687163564519265,places=12)
        self.assertTrue(x["bootstrap_interval_excludes_zero"])
        self.assertFalse(x["genus_specific_trap_level_capture_detection_probability_known"])
        self.assertFalse(x["cause_of_between_season_genus_at_exact_station_recurrence_identified"])
        self.assertTrue(x["unknown_later_availability_release_fate_and_movement"])

    def test_original_fate_source_uncertainty_not_release_or_detection_p(self):
        x=self.ledger["original_firstnight_disposition_source_constraint"]
        self.assertEqual((x["original_firstnight_marked_records"],
                          x["original_comparison_physical_sites"]),(615,7))
        self.assertEqual((x["firstnight_microtus_source_tags"],
                          x["firstnight_peromyscus_source_tags"]),(179,436))
        self.assertEqual((x["unmapped_post2017_microtus_fate_codes"],
                          x["unmapped_post2017_peromyscus_fate_codes"]),(111,280))
        self.assertEqual((x["explicit_released_microtus_source_tags"],
                          x["explicit_released_peromyscus_source_tags"]),(30,72))
        self.assertAlmostEqual(
            x["known_fate_classifier_fraction_not_original_metadata_completeness"],
            0.21138211382113822,places=12)
        self.assertEqual((x["physical_sites_reaching_five_explicit_release_per_genus"],
                          x["minimum_original_physical_sites_required"]),(1,6))
        self.assertFalse(x["new_released_conditioned_reencounter_outcome_estimated"])
        self.assertTrue(x["original_2017plus_unmapped_codes_not_assumed_absent_or_unreleased"])
        self.assertEqual(x["original_2017plus_raw_fate_label"],"processed")
        self.assertEqual(x["original_2017plus_raw_processed_fate_count"],391)
        self.assertTrue(x["raw_processed_individual_release_not_confirmed"])
        self.assertTrue(x["all_391_original_2017plus_other_unmapped_values_same_processed_token"])
        self.assertTrue(x["no_fate_code_reclassification_before_new_source_design"])
        self.assertTrue(x["static_codebook_unavailable_via_this_API_does_not_mean_its_absent_elsewhere"])
        self.assertTrue(x["original_7site_minus_23_5pp_reencounter_not_true_capture_p"])

    def test_geographic_macro_selection_denominator_and_causal_scope(self):
        q=self.ledger["geographic_macro_selection_source_only"]
        self.assertEqual((q["effort_valid_three_night_bouts"],
                          q["physical_sites_with_qualifying_effort_bouts"]), (1838,45))
        self.assertEqual((q["candidate_adjacent_season_pairs"],
                          q["candidate_physical_sites"]), (803,42))
        self.assertEqual((q["primary_strict_three_genus_pairs"],
                          q["primary_strict_sites"]), (58,14))
        self.assertEqual((q["candidate_ecological_domains"],
                          q["primary_ecological_domains"]), (18,10))
        self.assertAlmostEqual(q["strict_fraction_of_candidate_pairs"],58/803)
        self.assertEqual((q["core_candidate_pairs"],q["core_strict_pairs"],
                          q["gradient_candidate_pairs"],q["gradient_strict_pairs"]),
                          (373,27,430,31))
        self.assertFalse(q["ecological_recurrence_by_domain_estimated"])
        self.assertTrue(q["geographic_ineligibility_not_zero_recurrence"])

    def test_macro_population_denominator_not_inflated(self):
        z=self.ledger["macro_sampling_frame"]
        self.assertEqual((z["effort_qualified_three_night_selected_bouts"],
                          z["adjacent_season_candidates"],
                          z["primary_at_least_3_genus_pairs"],
                          z["diagnostic_at_least_2_genus_pairs_not_confirmed"]), (1838,803,58,216))
        self.assertTrue(z["unqualified_or_absent_biomes_not_as_negative_spatial_effect"])

if __name__ == "__main__":
    unittest.main()
