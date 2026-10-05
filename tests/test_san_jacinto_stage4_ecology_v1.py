import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestSanJacintoStage4Ecology(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.primary = json.loads(
            (ROOT / "results/san_jacinto_public_data_scale_decomposition_v1.json").read_text()
        )
        cls.cross = json.loads(
            (ROOT / "results/san_jacinto_public30_scale_decomposition_v1.json").read_text()
        )

    def test_primary_stage4_is_closed_on_between_night_footprint(self):
        x = self.primary
        self.assertTrue(x["all_reference"]["passed"])
        self.assertEqual(x["all_reference"]["observed"], {
            "analyzable": 30, "segregated": 8, "aggregated": 0
        })
        p = x["primary"]
        self.assertEqual(p["night_first_retained_n"], 7)
        self.assertAlmostEqual(p["night_first_retention_fraction"], 0.875)
        self.assertEqual(p["anchor_retained_n"], 0)
        self.assertEqual(p["anchor_retention_fraction"], 0)
        self.assertEqual(p["classification"], "between_night_footprint")
        self.assertEqual(p["night_first_lost_ids"], "1|summer")
        self.assertEqual(p["anchor_retained_ids"], [])

    def test_independent_implementation_agrees_exactly_on_decision(self):
        a = self.primary["primary"]
        b = self.cross["scale_decomposition"]
        self.assertTrue(self.cross["reference_gate"]["passed"])
        self.assertEqual(
            self.cross["reference_gate"]["observed"],
            {"analyzable": 30, "segregated": 8, "aggregated": 0},
        )
        self.assertEqual(a["all_reference_segregated_ids"], b["all_segregated_ids"])
        self.assertEqual(a["night_first_retained_n"], b["night_first_retained_all_significant_n"])
        self.assertEqual(a["night_first_retention_fraction"], b["night_first_retention_fraction"])
        self.assertEqual(a["anchor_retained_n"], b["anchor_retained_all_significant_n"])
        self.assertEqual(a["anchor_retention_fraction"], b["anchor_retention_fraction"])
        self.assertEqual(a["classification"], b["classification"])

    def test_reduced_representations_create_no_new_significant_units(self):
        sec = self.primary["secondary"]
        self.assertEqual(sec["newly_significant_outside_all"]["night_first"], [])
        self.assertEqual(sec["newly_significant_outside_all"]["anchor"], [])
        self.assertAlmostEqual(sec["ses_correlation"]["all_vs_night_first"], 0.94740750876)
        self.assertAlmostEqual(sec["ses_correlation"]["all_vs_anchor"], 0.10876851419)

    def test_exact_32_unit_reproduction_is_not_reclassified(self):
        self.assertEqual(
            set(self.primary["fixed_universe"]["excluded_grid_seasons"]),
            {"3|winter", "7|winter"},
        )
        self.assertFalse(self.primary["claim_boundary"]["stage3_32_unit_reproduction_reclassified"])


if __name__ == "__main__":
    unittest.main()
