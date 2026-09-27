from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]
GATE=ROOT/"validation"/"public_mammal_space_use_v1"/"estimability_gate_v1.json"


class PublicMammalEstimabilityGateTests(unittest.TestCase):
    def test_gate_blocks_modeling_until_design_amendment(self):
        gate=json.loads(GATE.read_text(encoding="utf-8"))
        self.assertEqual(gate["decision"],"amend_design_before_modeling")
        self.assertFalse(gate["phase2_modeling_authorized"])
        self.assertEqual(
            gate["required_next_spec"],
            "docs/superpowers/specs/2026-09-27-public-mammal-space-use-phase2-amendment.md",
        )

    def test_portal_gate_is_chaetodipus_penicillatus_only(self):
        gate=json.loads(GATE.read_text(encoding="utf-8"))
        portal=gate["portal"]
        self.assertEqual(portal["primary_species"],["Chaetodipus penicillatus"])
        self.assertEqual(portal["n5_session_counts"],{"control":194,"kangaroo_rat_exclosure":196})
        self.assertEqual(portal["n5_plot_counts"],{"control":10,"kangaroo_rat_exclosure":8})

    def test_neon_gate_freezes_identifiable_species_structure(self):
        gate=json.loads(GATE.read_text(encoding="utf-8"))
        neon=gate["neon"]
        self.assertEqual(
            neon["within_site_habitat_species"],
            ["Chaetodipus hispidus","Myodes rutilus","Perognathus parvus","Peromyscus boylii"],
        )
        self.assertEqual(
            neon["cross_site_habitat_species"],
            ["Myodes rutilus","Peromyscus maniculatus","Sigmodon hispidus"],
        )
        self.assertEqual(
            neon["primary_habitat_identifiable_species"],
            [
                "Chaetodipus hispidus","Myodes rutilus","Perognathus parvus",
                "Peromyscus boylii","Peromyscus maniculatus","Sigmodon hispidus",
            ],
        )

    def test_cross_dataset_same_species_synthesis_is_not_estimable(self):
        gate=json.loads(GATE.read_text(encoding="utf-8"))
        self.assertEqual(gate["cross_dataset"]["shared_species_meeting_original_gate"],[])
        self.assertEqual(
            gate["cross_dataset"]["decision"],
            "drop_same_species_cross_dataset_synthesis_from_primary_design",
        )

    def test_gate_records_zero_ecological_model_fits(self):
        gate=json.loads(GATE.read_text(encoding="utf-8"))
        self.assertEqual(gate["ecological_model_fits_before_gate"],0)


if __name__=="__main__":
    unittest.main()
