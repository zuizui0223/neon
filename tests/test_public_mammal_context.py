import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"public_mammal_context_v1.py"
spec=importlib.util.spec_from_file_location("context",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PublicMammalContextTests(unittest.TestCase):
    def test_neon_nlcd_groups_are_frozen(self):
        cases={
            "Deciduous Forest":"forest",
            "Evergreen Forest":"forest",
            "Mixed Forest":"forest",
            "Shrub/Scrub":"shrub_scrub",
            "Grassland/Herbaceous":"grassland_herbaceous",
            "Pasture/Hay":"cropland_pasture",
            "Cultivated Crops":"cropland_pasture",
            "Woody Wetlands":"wetland",
            "Emergent Herbaceous Wetlands":"wetland",
            "Open Water":"other_rare",
            "Developed, Open Space":"other_rare",
            "Developed, Low Intensity":"other_rare",
            "Developed, Medium Intensity":"other_rare",
            "Developed, High Intensity":"other_rare",
            "Barren Land":"other_rare",
        }
        for raw,expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(m.map_neon_nlcd(raw),expected)

    def test_unknown_or_blank_nlcd_is_other_rare(self):
        self.assertEqual(m.map_neon_nlcd(""),"other_rare")
        self.assertEqual(m.map_neon_nlcd("Unknown legacy class"),"other_rare")

    def test_portal_competition_context(self):
        self.assertEqual(m.portal_competition_context("control"),"control")
        self.assertEqual(m.portal_competition_context("exclosure"),"kangaroo_rat_exclosure")
        self.assertIsNone(m.portal_competition_context("removal"))
        self.assertIsNone(m.portal_competition_context("setup"))


if __name__=="__main__":
    unittest.main()
