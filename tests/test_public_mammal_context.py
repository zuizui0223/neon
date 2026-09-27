import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"public_mammal_context_v1.py"
LOOKUP=ROOT/"data"/"external"/"neon_nlcd_group_lookup_v1.csv"
spec=importlib.util.spec_from_file_location("context",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PublicMammalContextTests(unittest.TestCase):
    def test_forest_classes(self):
        for value in ("Deciduous Forest","Evergreen Forest","Mixed Forest"):
            self.assertEqual(m.map_neon_nlcd(value),"forest")

    def test_shrub_and_herbaceous_classes(self):
        self.assertEqual(m.map_neon_nlcd("Shrub/Scrub"),"shrub_scrub")
        self.assertEqual(m.map_neon_nlcd("Dwarf Scrub"),"shrub_scrub")
        self.assertEqual(m.map_neon_nlcd("Grassland/Herbaceous"),"grassland_herbaceous")
        self.assertEqual(m.map_neon_nlcd("Sedge/Herbaceous"),"grassland_herbaceous")

    def test_agriculture_and_wetland_classes(self):
        self.assertEqual(m.map_neon_nlcd("Pasture/Hay"),"cropland_pasture")
        self.assertEqual(m.map_neon_nlcd("Cultivated Crops"),"cropland_pasture")
        self.assertEqual(m.map_neon_nlcd("Woody Wetlands"),"wetland")
        self.assertEqual(m.map_neon_nlcd("Emergent Herbaceous Wetlands"),"wetland")

    def test_other_classes_and_unknown(self):
        for value in (
            "Open Water","Perennial Ice/Snow","Developed, Open Space",
            "Developed, Low Intensity","Developed, Medium Intensity",
            "Developed, High Intensity","Barren Land (Rock/Sand/Clay)",
            "Lichens","Moss",
        ):
            self.assertEqual(m.map_neon_nlcd(value),"other_rare")
        with self.assertRaises(KeyError):
            m.map_neon_nlcd("Totally New Class")

    def test_neon_session_camelcase_classes(self):
        aliases={
            "deciduousForest":"forest",
            "evergreenForest":"forest",
            "mixedForest":"forest",
            "dwarfScrub":"shrub_scrub",
            "shrubScrub":"shrub_scrub",
            "grasslandHerbaceous":"grassland_herbaceous",
            "sedgeHerbaceous":"grassland_herbaceous",
            "pastureHay":"cropland_pasture",
            "cultivatedCrops":"cropland_pasture",
            "woodyWetlands":"wetland",
            "emergentHerbaceousWetlands":"wetland",
        }
        for raw,expected in aliases.items():
            self.assertEqual(m.map_neon_nlcd(raw),expected)

    def test_portal_competition_context(self):
        self.assertEqual(m.portal_competition_context("control"),"control")
        self.assertEqual(m.portal_competition_context("exclosure"),"kangaroo_rat_exclosure")
        self.assertIsNone(m.portal_competition_context("removal"))
        self.assertIsNone(m.portal_competition_context("setup"))

    def test_lookup_file_has_only_declared_groups(self):
        rows=m.load_nlcd_lookup(LOOKUP)
        self.assertEqual(
            set(rows.values()),
            {"forest","shrub_scrub","grassland_herbaceous","cropland_pasture","wetland","other_rare"},
        )


if __name__=="__main__":
    unittest.main()
