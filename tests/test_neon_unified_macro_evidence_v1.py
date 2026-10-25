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
