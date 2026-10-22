"""Reproducibility guard for already-opened *predictor-only* NEON qualifier audit.

Does not open any W/B, home-range, centroid, detection or ecological outcome.
"""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(file):
    return json.loads((ROOT/"results"/file).read_text(encoding="utf-8"))


class SourceQualifierSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q=load("conspecific_congeneric_qualifier_sensitivity_receipt_20261018.json")
        cls.base=load("conspecific_congeneric_predictor_feasibility_receipt_20261018.json")
        cls.dev=load("multiscale_density_development_result_v1.json")
        cls.fut=load("future_neon_provisional_holdout_decision_v1.json")

    def test_original_neon_history_and_session_universe_unchanged(self):
        q=self.q
        s=q["source"]
        old=self.base["invariants"]
        self.assertEqual(s["original_known_alive_invariants"],old)
        self.assertEqual(old["original_source_target_sessions"],1536)
        self.assertEqual(old["original_target_histories"],47360)
        self.assertEqual(old["original_target_capture_rows"],104322)
        self.assertEqual(s["qualifier_source_columns_verified"],1707)
        self.assertTrue(q["qualifier_sensitivity"]["original_genus_N_invariant_every_event"])
        self.assertTrue(q["qualifier_sensitivity"]["strict_structural_response_session_universe_unchanged"])

    def test_qualifier_rule_can_only_increase_unresolved_histories(self):
        q=self.q["qualifier_sensitivity"]
        self.assertEqual(q["warning_capture_rows"],29101)
        self.assertEqual(q["warning_tag_histories"],13868)
        self.assertEqual(q["newly_unresolved_formerly_resolved_histories"],11832)
        original=self.base["invariants"]["taxonomy_histories"]
        sensitive=q["qualifier_sensitive_taxonomy_histories"]
        self.assertEqual(original["RESOLVED_SPECIES"],43162)
        self.assertEqual(original["UNRESOLVED_IN_GENUS"],4095)
        self.assertEqual(original["CROSS_GENUS"],103)
        self.assertEqual(sensitive["RESOLVED_SPECIES"],31330)
        self.assertEqual(sensitive["UNRESOLVED_IN_GENUS"],15927)
        self.assertEqual(sensitive["CROSS_GENUS"],103)
        self.assertEqual(sum(sensitive.values()),47360)

    def test_peromyscus_predictor_feasibility_survives_conservative_taxonomy(self):
        baseline=self.base["per_genus"]["Peromyscus"]
        qual=self.q["qualifier_sensitivity"]["per_genus"]["Peromyscus"]
        self.assertEqual(baseline["series_joint_F_C_variation"],74)
        self.assertEqual(qual["series_joint_F_C_variation"],62)
        self.assertEqual(qual["sites_in_3plus_series"],33)
        self.assertEqual(qual["species_sessions_in_3plus_series"],948)
        self.assertEqual(qual["event_sessions_with_resolved_other_congener_C"],255)
        self.assertEqual(qual["event_sessions_with_unresolved_genus_U"],757)
        self.assertEqual(qual["fixed_effects_predictor_geometry"]["predictor_rank_after_FE"],2)
        self.assertLess(qual["fixed_effects_predictor_geometry"]["predictor_condition_number"],30)
        self.assertEqual(qual["state"],"PREDICTOR_ONLY_POTENTIALLY_IDENTIFIABLE")

    def test_U_is_qualifier_conservative_index_not_misidentification_rate(self):
        p=self.q["qualifier_sensitivity"]["per_genus"]["Peromyscus"]
        self.assertAlmostEqual(p["fraction_of_genus_N_unresolved"],
                               p["unresolved_abundance_sum"]/p["genus_abundance_sum"],places=10)
        self.assertGreater(p["fraction_of_genus_N_unresolved"],0.5)
        self.assertAlmostEqual(self.base["per_genus"]["Peromyscus"]["fraction_of_genus_N_unresolved"],
                               0.09592861126603458,places=10)
        self.assertTrue(self.q["field_meaning"]["qualifier_warning_does_not_prove_error"])
        self.assertTrue(self.q["field_meaning"]["unqualified_stable_species_does_not_prove_genetic_identity"])
        self.assertFalse(self.q["scientific_interpretation"]["actual_species_misidentification_rate_estimated"])

    def test_new_hypothesis_does_not_override_neon_or_mosa_failures(self):
        self.assertFalse(self.q["W_B_or_density_spatial_effects_computed"])
        self.assertFalse(self.q["hypothesis_confirmed"])
        self.assertFalse(self.dev["preregistered_guard"]["passed"])
        self.assertEqual(self.dev["preregistered_guard"]["observed_positive_genus_count"],5)
        self.assertEqual(self.dev["preregistered_guard"]["required_positive_genus_count"],6)
        self.assertFalse(self.fut["scientific_decision"]["peromyscus_WB_positive_D_direction_replicated"])
        self.assertEqual(self.fut["mode_replicability"]["full_five_genus_result"],
                         "NOT_ESTIMABLE_ALL_FIVE_FROZEN_GENERA")
        self.assertEqual(self.q["scientific_interpretation"]["MOSA_density_spatial_effects"],"SEALED")


if __name__=="__main__":
    unittest.main()
