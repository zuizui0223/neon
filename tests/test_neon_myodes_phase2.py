from pathlib import Path
import importlib.util
import unittest
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"fit_neon_myodes_phase2_v1.py"
spec=importlib.util.spec_from_file_location("neon_myodes",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class NeonMyodesPhase2Tests(unittest.TestCase):
    def test_prepare_primary_filters_species_sites_habitats_and_maps_nlcd(self):
        rows=[
            {"species":"Myodes rutilus","site":"BONA","nlcd_class":"evergreenForest","n_unique_individuals":"5","primary_n5_eligible":"True","packing_z":"-0.2"},
            {"species":"Myodes rutilus","site":"BONA","nlcd_class":"shrubScrub","n_unique_individuals":"8","primary_n5_eligible":"True","packing_z":"0.1"},
            {"species":"Myodes rutilus","site":"DEJU","nlcd_class":"mixedForest","n_unique_individuals":"10","primary_n5_eligible":"True","packing_z":"0.2"},
            {"species":"Myodes rutilus","site":"DEJU","nlcd_class":"shrubScrub","n_unique_individuals":"6","primary_n5_eligible":"True","packing_z":"0.3"},
            {"species":"Myodes rutilus","site":"HEAL","nlcd_class":"shrubScrub","n_unique_individuals":"9","primary_n5_eligible":"True","packing_z":"1.0"},
            {"species":"Peromyscus maniculatus","site":"BONA","nlcd_class":"evergreenForest","n_unique_individuals":"9","primary_n5_eligible":"True","packing_z":"1.0"},
        ]
        df=m.prepare_neon_myodes_primary(rows)
        self.assertEqual(len(df),4)
        self.assertEqual(set(df["site"]),{"BONA","DEJU"})
        self.assertEqual(set(df["habitat_group"]),{"forest","shrub_scrub"})
        self.assertAlmostEqual(float(df["z_logN"].mean()),0.0,places=12)
        self.assertAlmostEqual(float(df["z_logN"].std(ddof=0)),1.0,places=12)

    def test_prepare_primary_requires_both_habitats_at_both_sites(self):
        rows=[
            {"species":"Myodes rutilus","site":"BONA","nlcd_class":"evergreenForest","n_unique_individuals":"5","primary_n5_eligible":"True","packing_z":"0"},
            {"species":"Myodes rutilus","site":"BONA","nlcd_class":"shrubScrub","n_unique_individuals":"6","primary_n5_eligible":"True","packing_z":"0"},
            {"species":"Myodes rutilus","site":"DEJU","nlcd_class":"evergreenForest","n_unique_individuals":"7","primary_n5_eligible":"True","packing_z":"0"},
        ]
        with self.assertRaises(ValueError):
            m.prepare_neon_myodes_primary(rows)

    def test_build_primary_model_is_full_rank_and_contains_frozen_terms(self):
        rows=[]
        for site in ("BONA","DEJU"):
            for habitat,nlcd in (("forest","evergreenForest"),("shrub_scrub","shrubScrub")):
                for i in range(6):
                    rows.append({
                        "species":"Myodes rutilus",
                        "site":site,
                        "nlcd_class":nlcd,
                        "n_unique_individuals":str(5+i),
                        "primary_n5_eligible":"True",
                        "packing_z":str(0.1*i + (0.2 if habitat=="shrub_scrub" else 0.0)),
                    })
        df=m.prepare_neon_myodes_primary(rows)
        model=m.build_neon_myodes_model(df)
        self.assertEqual(
            model.formula,
            "packing_z ~ C(habitat_group, Treatment(reference='forest')) + z_logN + C(site)",
        )
        self.assertEqual(np.linalg.matrix_rank(model.exog),model.exog.shape[1])
        self.assertIn(m.primary_habitat_term_name(),model.exog_names)

    def test_rank_audit_rejects_habitat_aliased_with_site(self):
        # Forest only at BONA and shrub only at DEJU -> exact alias.
        df=pd.DataFrame({
            "packing_z":[0.,0.1,0.2,0.3,0.4,0.5],
            "habitat_group":["forest"]*3+["shrub_scrub"]*3,
            "z_logN":[-1.,0.,1.,-1.,0.,1.],
            "site":["BONA"]*3+["DEJU"]*3,
        })
        with self.assertRaises(ValueError):
            m.build_neon_myodes_model(df)

    def test_primary_habitat_term_is_frozen(self):
        self.assertEqual(
            m.primary_habitat_term_name(),
            "C(habitat_group, Treatment(reference='forest'))[T.shrub_scrub]",
        )


if __name__=="__main__":
    unittest.main()
