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
        self.assertFalse(j["matched_same_population_site_plot_event_support_audited"])
        self.assertTrue(j["R_and_density_beta_different_estimands_not_pooled"])
        self.assertFalse(self.ledger["habitat_source_only"]["genus_habitat_or_detection_effect_estimated"])
        self.assertEqual(self.ledger["status"],"INTEGRATED_EXISTING_EVIDENCE_NO_NEW_ECOLOGICAL_TEST")
        self.assertIn("same-site crosswalk",self.design)
        self.assertIn("source-only",self.design)

    def test_macro_population_denominator_not_inflated(self):
        z=self.ledger["macro_sampling_frame"]
        self.assertEqual((z["effort_qualified_three_night_selected_bouts"],
                          z["adjacent_season_candidates"],
                          z["primary_at_least_3_genus_pairs"],
                          z["diagnostic_at_least_2_genus_pairs_not_confirmed"]), (1838,803,58,216))
        self.assertTrue(z["unqualified_or_absent_biomes_not_as_negative_spatial_effect"])

if __name__ == "__main__":
    unittest.main()
