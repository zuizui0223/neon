"""Immutable NEON fixed-total overlap result and scientific HOLD claims.

Only archive aggregates are inspected: NO raw source individuals or W/B fits.
"""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def result(path):
    return json.loads((ROOT/"results"/path).read_text(encoding="utf-8"))


class FixedTotalLiteralDataEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=result("neon_u_adjusted_fixed_total_predictor_receipt_20261019.json")
        cls.pair=result("neon_fixed_total_literal_composition_support_receipt_20261019.json")
        cls.old=result("multiscale_density_development_result_v1.json")
        cls.hold=result("future_neon_provisional_holdout_decision_v1.json")
        cls.doc=(ROOT/"docs/NEON_FIXED_TOTAL_COMPOSITION_TEST_20261019.md").read_text(encoding="utf-8")

    def test_fixed_source_cohort_originality(self):
        for obj in (self.source,self.pair):
            z=(obj.get("source_invariants") or obj.get("frozen_source_invariants"))
            self.assertEqual(z["original_source_target_sessions"],1536)
            self.assertEqual(z["original_target_histories"],47360)
            self.assertEqual(z["original_target_capture_rows"],104322)
        self.assertEqual(self.source["model"]["baseline"]["strictly_species_labelled_source_sessions"],948)
        self.assertEqual(self.source["model"]["qualifier_conservative"]["original_physical_sites"],33)

    def test_source_math_identifiable_but_no_WB(self):
        for x in ("baseline","qualifier_conservative"):
            a=self.source["model"][x]
            self.assertEqual(a["rank_FCU_after_nuisance"],3)
            self.assertEqual(a["rank_FC_after_nuisance_and_U"],2)
            self.assertTrue(a["fixed_total_replacement_contrast_estimable"])
            self.assertTrue(a["U_adjusted_predictor_only_candidate"])
            self.assertFalse(a["W_B_or_ecological_effects_opened"])
            self.assertGreater(a["fixed_total_replacement_residual_SS"],100)
            self.assertLess(a["condition_FC_after_nuisance_and_U"],30)

    def test_literal_primary_pairs_collapse_from_four_to_zero(self):
        v=self.pair["direct_composition_overlap"]
        b=v["baseline"]["primary_same_calendar_month"]
        q=v["qualifier_conservative"]["primary_same_calendar_month"]
        self.assertEqual(b["distinct_event_pairs"],4)
        self.assertEqual(b["physical_sites_with_pairs"],2)
        self.assertEqual(b["sessions_in_matched_contexts"],8)
        self.assertEqual(q["distinct_event_pairs"],0)
        self.assertEqual(q["physical_sites_with_pairs"],0)
        self.assertEqual(q["sessions_in_matched_contexts"],0)
        self.assertTrue(v["qualifier_conservative"]["no_literal_same_season_fixed_total_pair"])

    def test_broad_cross_season_is_separate_not_primary(self):
        v=self.pair["direct_composition_overlap"]
        self.assertEqual(v["baseline"]["broader_within_series_any_season"]["distinct_event_pairs"],18)
        self.assertEqual(v["qualifier_conservative"]["broader_within_series_any_season"]["distinct_event_pairs"],1)
        self.assertEqual(v["qualifier_conservative"]["additional_cross_season_pairs"],1)
        self.assertTrue(v["qualifier_conservative"]["broader_within_series_any_season"]["seasonally_not_equivalent_to_primary"])

    def test_never_promote_source_overlap_to_ecological_effect(self):
        self.assertEqual(self.pair["status"],"U_CONSERVATIVE_NO_LITERAL_SAME_SEASON_FIXED_TOTAL_PAIR_MODEL_ONLY_HOLD")
        self.assertTrue(self.pair["interpretation"]["does_not_prove_mammal_ecological_null"])
        self.assertFalse(self.pair["interpretation"]["historical_data_adequate_for_literal_fixed_total_biological_confirmation"])
        self.assertFalse(self.pair["direct_composition_overlap"]["qualifier_conservative"]["ecological_W_B_effects_opened"])
        self.assertFalse(self.old["preregistered_guard"]["passed"])
        self.assertEqual(self.old["preregistered_guard"]["observed_positive_genus_count"],5)
        self.assertEqual(self.old["preregistered_guard"]["required_positive_genus_count"],6)
        self.assertFalse(self.hold["scientific_decision"]["peromyscus_WB_positive_D_direction_replicated"])
        self.assertIn("NO literal same-season",self.doc)

    def test_scientific_study_remains_sealed(self):
        self.assertEqual(self.pair["interpretation"]["primary_Theta_spatial_effect"],"NOT_FITTED_IN_THIS_SOURCE_AUDIT")
        self.assertEqual(self.pair["interpretation"]["MOSA_WB"],"SEALED")
        self.assertIn("model-based",self.doc)


if __name__=="__main__":
    unittest.main()
