import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"run_carrier_prevalence_response_once_v1.py"
spec=importlib.util.spec_from_file_location("response_runner",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class CarrierPrevalenceResponseRunnerTests(unittest.TestCase):
    def test_exact_sign_test(self):
        self.assertEqual(m.exact_sign_test_greater(0, 6), 1.0)
        self.assertAlmostEqual(m.exact_sign_test_greater(6, 6), 1/64)
        self.assertAlmostEqual(m.exact_sign_test_greater(5, 6), 7/64)

    def test_spearman_rank_direction(self):
        self.assertAlmostEqual(m.spearman([1,2,3],[2,4,6]),1.0)
        self.assertAlmostEqual(m.spearman([1,2,3],[6,4,2]),-1.0)

    def test_secondary_trait_summary_is_within_site(self):
        site_results=[
            {
                "site_code":"A",
                "species_results":[
                    {"scientific_name":"s1","carrier_excess":0.1},
                    {"scientific_name":"s2","carrier_excess":0.2},
                    {"scientific_name":"s3","carrier_excess":0.3},
                ],
            },
            {
                "site_code":"B",
                "species_results":[
                    {"scientific_name":"s1","carrier_excess":0.3},
                    {"scientific_name":"s2","carrier_excess":0.2},
                    {"scientific_name":"s3","carrier_excess":0.1},
                ],
            },
        ]
        traits={
            "s1":{"adult_mass_g":1.0},
            "s2":{"adult_mass_g":2.0},
            "s3":{"adult_mass_g":3.0},
        }
        # Fill all declared trait keys with missing values except adult mass.
        for row in traits.values():
            for key in (
                "dispersal_km","habitat_breadth_n","det_diet_breadth_n",
                "home_range_km2","density_n_km2","trophic_level"
            ):
                row[key]=None
        out=m.secondary_trait_summary(site_results,traits)
        self.assertEqual(out["adult_mass_g"]["estimable_site_count"],2)
        self.assertEqual(out["adult_mass_g"]["positive_site_rho_count"],1)
        self.assertEqual(out["adult_mass_g"]["negative_site_rho_count"],1)
        self.assertEqual(out["adult_mass_g"]["median_within_site_spearman_rho"],0.0)

    def test_response_inventory_rejects_undeclared_site(self):
        payload={
            "data":{
                "productCode":"DP1.10072.001",
                "releases":[{
                    "release":"RELEASE-2026",
                    "packages":[{
                        "siteCode":"XXXX",
                        "packageType":"basic",
                        "month":"2026-01",
                        "files":[],
                    }],
                }],
            }
        }
        with self.assertRaises(RuntimeError):
            m.response_inventory(payload,("TEST",))

if __name__=="__main__":
    unittest.main()
