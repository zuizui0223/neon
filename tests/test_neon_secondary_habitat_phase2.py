from pathlib import Path
import importlib.util
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"fit_neon_secondary_habitat_phase2_v1.py"
spec=importlib.util.spec_from_file_location("neon_secondary",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class NeonSecondaryHabitatPhase2Tests(unittest.TestCase):
    def test_frozen_contrasts_are_exact(self):
        self.assertEqual(
            m.frozen_contrasts(),
            [
                {
                    "species":"Chaetodipus hispidus",
                    "site":"OAES",
                    "habitats":["grassland_herbaceous","shrub_scrub"],
                },
                {
                    "species":"Perognathus parvus",
                    "site":"ONAQ",
                    "habitats":["forest","shrub_scrub"],
                },
                {
                    "species":"Peromyscus boylii",
                    "site":"SJER",
                    "habitats":["forest","grassland_herbaceous"],
                },
            ],
        )

    def test_prepare_contrast_does_not_discover_other_species(self):
        rows=[
            {"species":"Chaetodipus hispidus","site":"OAES","nlcd_class":"grasslandHerbaceous","n_unique_individuals":"5","primary_n5_eligible":"True","packing_z":"0"},
            {"species":"Chaetodipus hispidus","site":"OAES","nlcd_class":"shrubScrub","n_unique_individuals":"6","primary_n5_eligible":"True","packing_z":"0.1"},
            {"species":"Dipodomys ordii","site":"OAES","nlcd_class":"grasslandHerbaceous","n_unique_individuals":"10","primary_n5_eligible":"True","packing_z":"1"},
        ]
        df=m.prepare_contrast(rows,m.frozen_contrasts()[0])
        self.assertEqual(len(df),2)
        self.assertEqual(set(df["species"]),{"Chaetodipus hispidus"})

    def test_prepare_requires_both_frozen_habitats(self):
        rows=[
            {"species":"Perognathus parvus","site":"ONAQ","nlcd_class":"evergreenForest","n_unique_individuals":"5","primary_n5_eligible":"True","packing_z":"0"},
            {"species":"Perognathus parvus","site":"ONAQ","nlcd_class":"mixedForest","n_unique_individuals":"6","primary_n5_eligible":"True","packing_z":"0.1"},
        ]
        with self.assertRaises(ValueError):
            m.prepare_contrast(rows,m.frozen_contrasts()[1])

    def test_habitat_term_uses_first_habitat_as_reference(self):
        self.assertEqual(
            m.habitat_term_name(["forest","shrub_scrub"]),
            "C(habitat_group, Treatment(reference='forest'))[T.shrub_scrub]",
        )
        self.assertEqual(
            m.habitat_term_name(["grassland_herbaceous","shrub_scrub"]),
            "C(habitat_group, Treatment(reference='grassland_herbaceous'))[T.shrub_scrub]",
        )


if __name__=="__main__":
    unittest.main()
