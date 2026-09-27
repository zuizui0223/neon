import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"neon_phase2_context_sensitivity_v1.py"
spec=importlib.util.spec_from_file_location("neon_sens",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class NeonPhase2ContextSensitivityTests(unittest.TestCase):
    def test_frozen_site_context_species_are_exact(self):
        self.assertEqual(
            m.frozen_site_context_species(),
            {
                "Chaetodipus hispidus",
                "Chaetodipus penicillatus",
                "Dipodomys merriami",
                "Dipodomys ordii",
                "Myodes rutilus",
                "Onychomys leucogaster",
                "Peromyscus gossypinus",
                "Peromyscus leucopus",
                "Peromyscus maniculatus",
                "Sigmodon hispidus",
            },
        )

    def test_prepare_context_dataframe_keeps_one_species_and_multiple_sites(self):
        rows=[
            {"species":"Dipodomys ordii","site":"JORN","year":"2022","n_unique_individuals":"5","packing_z":"0.1","primary_n5_eligible":"True"},
            {"species":"Dipodomys ordii","site":"JORN","year":"2023","n_unique_individuals":"8","packing_z":"0.2","primary_n5_eligible":"True"},
            {"species":"Dipodomys ordii","site":"MOAB","year":"2022","n_unique_individuals":"6","packing_z":"0.4","primary_n5_eligible":"True"},
            {"species":"Dipodomys merriami","site":"JORN","year":"2022","n_unique_individuals":"7","packing_z":"0.9","primary_n5_eligible":"True"},
        ]
        df=m.prepare_context_dataframe(rows,"Dipodomys ordii",n_min=5)
        self.assertEqual(set(df["site"]),{"JORN","MOAB"})
        self.assertEqual(len(df),3)
        self.assertAlmostEqual(float(df["z_logN"].mean()),0.0,places=12)

    def test_context_summary_returns_adjusted_site_means(self):
        rows=[]
        for year in range(2020,2025):
            for site,offset in [("A",0.0),("B",0.5)]:
                rows.append({
                    "species":"Dipodomys ordii",
                    "site":site,
                    "year":str(year),
                    "n_unique_individuals":str(5+(year%3)),
                    "packing_z":str(offset+0.02*(year-2020)),
                    "primary_n5_eligible":"True",
                })
        out=m.fit_context_summary(rows,"Dipodomys ordii",n_min=5)
        self.assertEqual(set(out["adjusted_site_means"]),{"A","B"})
        self.assertGreater(out["adjusted_site_means"]["B"],out["adjusted_site_means"]["A"])
        self.assertGreater(out["site_adjusted_range"],0)

    def test_prepare_myodes_threshold_uses_frozen_sites_and_habitats(self):
        rows=[
            {"species":"Myodes rutilus","site":"BONA","year":"2022","n_unique_individuals":"3","packing_z":"0.1","sensitivity_n3_eligible":"True","primary_n5_eligible":"False","sensitivity_n8_eligible":"False","nlcd_class":"evergreenForest"},
            {"species":"Myodes rutilus","site":"BONA","year":"2022","n_unique_individuals":"8","packing_z":"0.2","sensitivity_n3_eligible":"True","primary_n5_eligible":"True","sensitivity_n8_eligible":"True","nlcd_class":"shrubScrub"},
            {"species":"Myodes rutilus","site":"DEJU","year":"2022","n_unique_individuals":"9","packing_z":"0.3","sensitivity_n3_eligible":"True","primary_n5_eligible":"True","sensitivity_n8_eligible":"True","nlcd_class":"evergreenForest"},
            {"species":"Myodes rutilus","site":"HEAL","year":"2022","n_unique_individuals":"9","packing_z":"0.4","sensitivity_n3_eligible":"True","primary_n5_eligible":"True","sensitivity_n8_eligible":"True","nlcd_class":"shrubScrub"},
        ]
        n3=m.prepare_myodes_threshold(rows,n_min=3)
        n8=m.prepare_myodes_threshold(rows,n_min=8)
        self.assertEqual(set(n3["site"]),{"BONA","DEJU"})
        self.assertEqual(set(n3["habitat_group"]),{"forest","shrub_scrub"})
        self.assertEqual(len(n8),2)


    def test_myodes_threshold_summary_uses_same_habitat_term(self):
        rows=[]
        for year in range(2020,2025):
            for site in ("BONA","DEJU"):
                for raw_nlcd,offset in (("evergreenForest",0.0),("shrubScrub",0.4)):
                    n=5+((year+(0 if site=="BONA" else 1))%4)
                    rows.append({
                        "species":"Myodes rutilus",
                        "site":site,
                        "year":str(year),
                        "n_unique_individuals":str(n),
                        "packing_z":str(offset+0.01*(year-2020)),
                        "primary_n5_eligible":"True",
                        "sensitivity_n3_eligible":"True",
                        "sensitivity_n8_eligible":"True" if n>=8 else "False",
                        "nlcd_class":raw_nlcd,
                    })
        out=m.fit_myodes_threshold_summary(rows,n_min=5,label="synthetic")
        self.assertEqual(out["label"],"synthetic")
        self.assertEqual(out["site_count"],2)
        self.assertEqual(out["habitat_session_counts"],{"forest":10,"shrub_scrub":10})
        self.assertIn("habitat_effect",out["coefficients"])
        self.assertGreater(out["coefficients"]["habitat_effect"]["estimate"],0)

    def test_myodes_leave_one_site_out_returns_both_sites(self):
        rows=[]
        for year in range(2020,2025):
            for site in ("BONA","DEJU"):
                for raw_nlcd in ("evergreenForest","shrubScrub"):
                    rows.append({
                        "species":"Myodes rutilus",
                        "site":site,
                        "year":str(year),
                        "n_unique_individuals":str(5+((year-2020)%3)),
                        "packing_z":str((0.3 if raw_nlcd=="shrubScrub" else 0.0)+(0.1 if site=="DEJU" else 0.0)+0.01*(year-2020)),
                        "primary_n5_eligible":"True",
                        "sensitivity_n3_eligible":"True",
                        "sensitivity_n8_eligible":"False",
                        "nlcd_class":raw_nlcd,
                    })
        out=m.fit_myodes_leave_one_out(rows,unit_field="site",n_min=5)
        self.assertEqual({x["left_out"] for x in out},{"BONA","DEJU"})
        self.assertTrue(all(x["estimable"] for x in out))

    def test_context_family_is_fixed_to_ten_species(self):
        rows=[]
        for species in m.frozen_site_context_species():
            for site,offset in (("A",0.0),("B",0.2)):
                for year in (2022,2023,2024):
                    rows.append({
                        "species":species,
                        "site":site,
                        "year":str(year),
                        "n_unique_individuals":str(5+(year%2)),
                        "packing_z":str(offset+0.01*(year-2022)),
                        "primary_n5_eligible":"True",
                    })
        out=m.fit_frozen_context_family(rows,n_min=5)
        self.assertEqual(set(out),m.frozen_site_context_species())
        self.assertTrue(all(v["site_count"]==2 for v in out.values()))

    def test_aggregate_peromyscus_complex_rows(self):
        rows=[
            {"taxonID":"PM","scientificName":"Peromyscus maniculatus","tagID":"a"},
            {"taxonID":"PL","scientificName":"Peromyscus leucopus","tagID":"b"},
            {"taxonID":"PB","scientificName":"Peromyscus boylii","tagID":"c"},
        ]
        out=m.aggregate_peromyscus_complex_rows(rows)
        self.assertEqual(out[0]["scientificName"],"Peromyscus_maniculatus_leucopus_complex")
        self.assertEqual(out[1]["scientificName"],"Peromyscus_maniculatus_leucopus_complex")
        self.assertEqual(out[0]["taxonID"],"PEROMYSCUS_ML_COMPLEX")
        self.assertEqual(out[2]["scientificName"],"Peromyscus boylii")


if __name__=="__main__":
    unittest.main()
