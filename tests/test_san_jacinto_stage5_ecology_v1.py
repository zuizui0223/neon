import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestSanJacintoStage5Ecology(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.persistence = json.loads(
            (ROOT / "results/san_jacinto_stage5_temporal_persistence_v1.json").read_text()
        )
        cls.individual = json.loads(
            (ROOT / "results/san_jacinto_individual_footprint_assortativity_v1.json").read_text()
        )
        cls.design = (ROOT / "docs/SAN_JACINTO_TRANSITION_NICHE_EXPLORATION_V1.md").read_text()
        cls.interpretation = (
            ROOT / "docs/SAN_JACINTO_TEMPORAL_SCALE_ECOLOGY_INTERPRETATION_V1.md"
        ).read_text()

    def test_stage5a_temporal_persistence_is_frozen_and_supported(self):
        p = self.persistence["primary"]
        self.assertEqual(p["reference_units"], 8)
        self.assertEqual(p["informative_nonzero_null_sd"], 8)
        self.assertEqual(p["positive_z_units"], 8)
        self.assertAlmostEqual(p["global_mean_standardized_persistence"], 4.0908870811)
        self.assertAlmostEqual(p["one_sided_monte_carlo_p_upper"], 0.000199960008)
        self.assertEqual(
            p["decision"], "support_persistent_species_specific_multi_night_footprints"
        )

    def test_stage5b_individual_footprint_assortativity_is_supported(self):
        x = self.individual
        self.assertEqual(x["support"]["multi_night_individuals_before_unit_filter"], 928)
        self.assertEqual(x["support"]["eligible_grid_seasons"], 22)
        self.assertEqual(x["support"]["informative_grid_seasons_nonzero_null_sd"], 22)
        p = x["primary"]
        self.assertAlmostEqual(
            p["global_mean_standardized_footprint_assortativity"], 2.314861833224311
        )
        self.assertAlmostEqual(p["one_sided_monte_carlo_p_upper"], 0.00009999000099990002)
        self.assertEqual(p["decision"], "support_species_specific_multinight_footprints")
        self.assertEqual(x["secondary"]["positive_raw_difference_units"], 20)
        self.assertAlmostEqual(
            x["secondary"]["correlation_unit_z_with_stage4_night_first_ses"],
            0.69425481417086,
        )

    def test_stage5a_and_stage5b_are_not_conflated_in_docs(self):
        self.assertIn("# Stage 5A — frozen temporal persistence test", self.design)
        self.assertIn("# Stage 5A result — seasonal persistence supported", self.design)
        self.assertIn("# Stage 5B — individual multi-night footprint assortativity", self.design)
        self.assertIn("# Stage 5B result — individual species-specific footprints supported", self.design)
        self.assertIn("928", self.interpretation)
        self.assertIn("0.6943", self.interpretation)
        self.assertIn("footprint size", self.interpretation.lower())


if __name__ == "__main__":
    unittest.main()
