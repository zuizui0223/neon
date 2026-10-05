import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "MANUSCRIPT_JAE_SPATIAL_TEMPLATE_V0_1.md"


class TestSpatialTemplateManuscriptV01(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = MANUSCRIPT.read_text(encoding="utf-8")
        cls.stage1 = json.loads((ROOT / "results/san_jacinto_movement_direction_partitioning_v1.json").read_text())
        cls.stage4 = json.loads((ROOT / "results/san_jacinto_public30_scale_decomposition_v1.json").read_text())
        cls.stage5a = json.loads((ROOT / "results/san_jacinto_stage5_temporal_persistence_v1.json").read_text())
        cls.stage5b = json.loads((ROOT / "results/san_jacinto_individual_footprint_assortativity_v1.json").read_text())
        cls.stage7 = json.loads((ROOT / "results/san_jacinto_turnover_persistence_v1.json").read_text())
        cls.stage8 = json.loads((ROOT / "results/san_jacinto_turnover_generalization_v1.json").read_text())
        cls.stage9 = json.loads((ROOT / "results/san_jacinto_cross_season_turnover_v1.json").read_text())

    def test_core_stage_decisions(self):
        self.assertEqual(
            self.stage1["primary"]["decision"],
            "stop_no_directional_maintenance_support",
        )
        self.assertEqual(
            self.stage4["scale_decomposition"]["classification"],
            "between_night_footprint",
        )
        self.assertEqual(
            self.stage5a["primary"]["decision"],
            "support_persistent_species_specific_multi_night_footprints",
        )
        self.assertEqual(
            self.stage5b["primary"]["decision"],
            "support_species_specific_multinight_footprints",
        )
        self.assertEqual(
            self.stage7["primary"]["decision"],
            "support_species_level_spatial_template_beyond_individual_identity",
        )
        self.assertEqual(
            self.stage8["primary"]["decision"],
            "broader_turnover_generalization_not_supported",
        )
        self.assertEqual(
            self.stage9["primary"]["decision"],
            "support_cross_season_species_template_reassembly",
        )

    def test_manuscript_contains_frozen_numbers(self):
        required = [
            "-0.1966",
            "0.8000",
            "7 of 8",
            "0 of 8",
            "0.9474",
            "2.3149",
            "4.0909",
            "188",
            "1.0374",
            "0.00160",
            "290",
            "1.7747",
            "0.046875",
            "0.125",
        ]
        for token in required:
            self.assertIn(token, self.text)

    def test_identity_turnover_is_central_question(self):
        self.assertIn(
            "Does spatial niche partitioning recur when the same marked individuals are excluded from successive time windows?",
            self.text,
        )
        self.assertIn("persist above individual identity", self.text.lower())
        self.assertIn("disjoint individual sets", self.text.lower())

    def test_identity_turnover_boundary_is_explicit(self):
        low = self.text.lower()
        self.assertIn("identity turnover", low)
        self.assertIn("disjoint sets of observed identities", low)
        self.assertIn("does **not** establish literal demographic replacement", low)

    def test_public_source_boundary_is_explicit(self):
        low = self.text.lower()
        self.assertIn("grid 3 winter", low)
        self.assertIn("grid 7 winter", low)
        self.assertIn("public-data-supported universe of 30", low)

    def test_no_causal_mechanism_overclaim(self):
        low = self.text.lower()
        forbidden = [
            "competition causes the spatial template",
            "habitat filtering is proven",
            "collective memory causes",
            "proves coexistence",
        ]
        for phrase in forbidden:
            self.assertNotIn(phrase, low)

    def test_stage8_scope_limit_retained(self):
        self.assertIn("broader turnover generalization was suggestive but not established", self.text.lower())
        self.assertIn("p=0.125", re.sub(r"\\", "", self.text.replace(" ", "")))

    def test_abstract_is_numbered_and_under_350_words(self):
        start = self.text.index("## Abstract") + len("## Abstract")
        end = self.text.index("## Keywords")
        abstract = self.text[start:end]
        for n in range(1, 6):
            self.assertRegex(abstract, rf"(?m)^\s*{n}\.")
        words = re.findall(r"\b[\w’'-]+\b", abstract)
        self.assertLessEqual(len(words), 350)


if __name__ == "__main__":
    unittest.main()
