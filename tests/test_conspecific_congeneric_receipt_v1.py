"""Protect effect-blind species-versus-congener result and failed old claims.

This test NEVER computes W/B, never opens any raw positions, and may not be
used as retrospective confirmation of the earlier 8-genus hypothesis.
"""
from __future__ import annotations
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def load(filename: str):
    return json.loads((ROOT/"results"/filename).read_text(encoding="utf-8"))


class FrozenConspecificCongenericReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load("conspecific_congeneric_predictor_feasibility_receipt_20261018.json")
        cls.prior=load("multiscale_density_mnka_variation_decision_v1.json")
        cls.dev=load("multiscale_density_development_result_v1.json")
        cls.future=load("future_neon_provisional_holdout_decision_v1.json")
        cls.contract=(ROOT/"docs/CONSPECIFIC_VS_CONGENERIC_CROWDING_NEXT_GENERATION_20261018.md").read_text(encoding="utf-8")

    def test_source_invariants_match_exact_original_target_universe(self):
        a=self.data["invariants"]
        b=self.prior
        self.assertEqual(a["original_source_target_sessions"],1536)
        self.assertEqual(a["original_target_histories"],47360)
        self.assertEqual(a["original_target_capture_rows"],104322)
        self.assertEqual(a["original_response_series"],273)
        self.assertEqual(a["original_genus_mnka_varying_series"],176)
        self.assertEqual(a["original_genus_mnka_varying_sessions"],1408)
        self.assertEqual(a["original_target_histories"],b["taxonomy_history"]["target_tag_histories"])
        self.assertEqual(a["original_genus_mnka_varying_series"],
                         b["mnka_variation"]["series_with_at_least_3_sessions_and_2_mnka_values"])
        self.assertEqual(a["original_target_capture_rows"],
                         b["taxonomy_history"]["target_capture_rows_used_for_history"])
        self.assertEqual(a["strict_species_response_sessions"]+a["species_group_response_sessions"],1536)
        self.assertEqual(a["target_species_ids_in_original_roster"],31)
        self.assertEqual(a["target_species_group_ids_in_original_roster"],4)
        self.assertEqual(a["taxonomy_histories"]["CROSS_GENUS"],103)
        self.assertEqual(sum(a["taxonomy_histories"].values()),47360)

    def test_peromyscus_only_passes_predeclared_predictor_gates(self):
        d=self.data
        self.assertEqual(d["candidate_genera_predictor_only"],["Peromyscus"])
        th=d["fixed_feasibility_thresholds"]
        self.assertEqual(th,{
            "minimum_species_sessions":60,
            "minimum_sites":6,
            "minimum_threeplus_series":8,
            "minimum_jointly_varying_series":5,
            "residual_rank":2,
            "maximum_condition_number":30.0,
        })
        p=d["per_genus"]["Peromyscus"]
        self.assertEqual(p["state"],"PREDICTOR_ONLY_POTENTIALLY_IDENTIFIABLE")
        self.assertEqual(p["species_sessions_in_3plus_series"],948)
        self.assertEqual(p["sites_in_3plus_series"],33)
        self.assertEqual(p["species_series_with_3plus_sessions"],109)
        self.assertEqual(p["series_joint_F_C_variation"],74)
        self.assertGreaterEqual(p["series_joint_F_C_variation"],th["minimum_jointly_varying_series"])
        self.assertEqual(p["fixed_effects_predictor_geometry"]["predictor_rank_after_FE"],2)
        self.assertLess(p["fixed_effects_predictor_geometry"]["predictor_condition_number"],30)

    def test_strict_frozen_other_genera_remain_stop(self):
        for genus,vals in self.data["per_genus"].items():
            if genus=="Peromyscus":
                continue
            self.assertEqual(vals["state"],"PREDICTOR_ONLY_STRUCTURAL_LIMIT",genus)
            self.assertTrue(vals["no_spatial_effect_or_W_B_opened"])
        d=self.data["per_genus"]["Dipodomys"]
        self.assertEqual(d["series_joint_F_C_variation"],7)
        self.assertEqual(d["sites_in_3plus_series"],4)

    def test_species_uncertainty_is_retained_and_reported(self):
        d=self.data
        p=d["per_genus"]["Peromyscus"]
        self.assertEqual(p["event_sessions_with_resolved_other_congener_C"],378)
        self.assertEqual(p["event_sessions_with_unresolved_genus_U"],432)
        self.assertEqual(p["unresolved_abundance_sum"],1892)
        self.assertAlmostEqual(p["fraction_of_genus_N_unresolved"],1892/19723,places=9)
        self.assertEqual(d["invariants"]["taxonomy_histories"]["UNRESOLVED_IN_GENUS"],4095)
        self.assertFalse(d["biological_caution"]["species_groups_never_assigned_to_species"] is False)
        self.assertTrue(d["biological_caution"]["same_genus_multitaxon_histories_not_assigned_to_a_specific_species"])

    def test_original_ecology_falsification_unchanged(self):
        self.assertFalse(self.dev["preregistered_guard"]["passed"])
        self.assertEqual(self.dev["preregistered_guard"]["observed_positive_genus_count"],5)
        self.assertEqual(self.dev["preregistered_guard"]["required_positive_genus_count"],6)
        self.assertFalse(self.future["scientific_decision"]["new_five_genus_mode_confirmed"])
        self.assertFalse(self.future["scientific_decision"]["peromyscus_WB_positive_D_direction_replicated"])
        self.assertEqual(self.data["hypothesis_scope"],
                         "NEW post-development species-vs-congener question, not retrospective original hypothesis confirmation")

    def test_never_promote_capture_index_to_ecological_effect(self):
        b=self.data["biological_caution"]
        self.assertFalse(b["W_B_or_density_spatial_effects_computed"])
        self.assertFalse(b["MOSA_spatial_effects_opened"])
        self.assertFalse(b["new_mammal_spatial_ecological_claim"])
        self.assertTrue(b["this_is_predictor_only_historical_response_consumed_data"])
        self.assertEqual(b["original_8_genus_guard"],"FAILED_5_OF_8")
        self.assertIn("Casula",self.contract)
        self.assertIn("NOT the first",self.contract)
        self.assertIn("never",self.contract.lower())


if __name__=="__main__":
    unittest.main()
