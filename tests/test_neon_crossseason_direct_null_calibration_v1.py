"""Synthetic verification of site-weighted direct conditional null calibration.

No NEON animal, genus, trap station, W/B or source geographic identifier is read.
The ORIGINAL sign-flip decision is not altered or reclassified.
"""
import math
import unittest
from analysis.neon_crossseason_direct_null_calibration_v1 import (
    direct_site_weighted_product_null, season_sharing_diagnostic
)


def units_two_sites():
    return [
        {"unit_index":0,"site":"SECRET_A","observed_z":2.5,
         "null_z_draws":[-1.,0.,1.]},
        {"unit_index":1,"site":"SECRET_A","observed_z":2.5,
         "null_z_draws":[-1.,0.,1.]},
        {"unit_index":2,"site":"SECRET_B","observed_z":2.5,
         "null_z_draws":[-1.,0.,1.]},
    ]


class DirectSiteNullTests(unittest.TestCase):
    def test_strong_signal_outside_all_null_support_yields_mc_floor(self):
        a=direct_site_weighted_product_null(units_two_sites(),seed=2026101902,n_replicates=1000)
        self.assertEqual(a["physical_sites"],2)
        self.assertEqual(a["seasonal_units"],3)
        self.assertAlmostEqual(a["observed_equal_site_weighted_mean_z"],2.5)
        self.assertEqual(a["upper_tail_exceedances"],0)
        self.assertEqual(a["one_sided_p_with_plus_one"],1/1001)
        self.assertTrue(a["product_null_disallows_signflip_symmetry_assumption"])
        self.assertTrue(a["post_result_calibration_not_new_confirmatory_test"])
        self.assertFalse(a["genus_specific_detection_bias_excluded"])

    def test_null_signal_around_zero_does_not_become_false_positive(self):
        z=[
            {"unit_index":0,"site":"S1","observed_z":0.,
             "null_z_draws":[-1.,1.]},
            {"unit_index":1,"site":"S2","observed_z":0.,
             "null_z_draws":[-1.,1.]},
        ]
        a=direct_site_weighted_product_null(z,seed=20,n_replicates=3000)
        self.assertGreater(a["one_sided_p_with_plus_one"],0.4)
        self.assertLess(a["one_sided_p_with_plus_one"],0.9)

    def test_equal_site_weighting_not_unequal_unit_weighting(self):
        z=[
            *[{"unit_index":i,"site":"MULTI_SITE","observed_z":1.,
               "null_z_draws":[0.,1.]} for i in range(9)],
            {"unit_index":9,"site":"SINGLE_SITE","observed_z":-1.,
             "null_z_draws":[-1.,0.]},
        ]
        a=direct_site_weighted_product_null(z,seed=5,n_replicates=1000)
        self.assertAlmostEqual(a["observed_equal_site_weighted_mean_z"],0.)
        self.assertEqual(a["physical_sites"],2)
        self.assertEqual(a["seasonal_units"],10)

    def test_order_invariant_given_stable_original_unit_index(self):
        x=units_two_sites()
        a=direct_site_weighted_product_null(x,seed=98,n_replicates=2000)
        b=direct_site_weighted_product_null(x[::-1],seed=98,n_replicates=2000)
        self.assertEqual(a,b)

    def test_reject_nonfinite_null_values_and_duplicate_indices(self):
        z=units_two_sites()
        z[0]["null_z_draws"][1]=float("nan")
        with self.assertRaisesRegex(ValueError,"finite"):
            direct_site_weighted_product_null(z,seed=3,n_replicates=100)
        x=units_two_sites()
        x[1]["unit_index"]=x[0]["unit_index"]
        with self.assertRaisesRegex(ValueError,"duplicate"):
            direct_site_weighted_product_null(x,seed=3,n_replicates=100)

    def test_no_source_site_names_or_draws_exported(self):
        a=direct_site_weighted_product_null(units_two_sites(),seed=9,n_replicates=400)
        self.assertNotIn("SECRET_",str(a))
        self.assertNotIn("null_z_draws",str(a))
        self.assertNotIn("unit_index",str(a))
        self.assertFalse(a["raw_source_labels_or_null_draw_arrays_exported"])

    def test_shared_adjacent_seasons_are_counted_as_dependence(self):
        units=[
            {"site":"A","site_plot":("A","P"),"season_ordinal":100},
            {"site":"A","site_plot":("A","P"),"season_ordinal":101},
            {"site":"A","site_plot":("A","Q"),"season_ordinal":100},
            {"site":"B","site_plot":("B","P"),"season_ordinal":100},
        ]
        a=season_sharing_diagnostic(units)
        self.assertEqual(a["season_keys_used_in_multiple_pair_roles"],1)
        self.assertEqual(a["physical_sites_with_any_adjacent_pair_season_reuse"],1)
        self.assertEqual(a["number_seasonal_units"],4)
        self.assertTrue(a["joint_shared_season_covariance_not_preserved"])
        self.assertNotIn("'A'",str(a))
        self.assertNotIn("'B'",str(a))

    def test_source_receipt_matches_original_frozen_statistic(self):
        import json
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]
        z=json.loads((root/"results/neon_crossseason_genus_template_ecology_receipt_20261019.json").read_text())
        stat=z["independent_site_ecology"]
        self.assertEqual(stat["physical_sites"],14)
        self.assertEqual(stat["informative_seasonal_units"],58)
        self.assertEqual(stat["positive_site_means"],11)
        self.assertAlmostEqual(stat["site_mean_Z_mean"],0.8007420166137748,places=10)
        self.assertAlmostEqual(stat["one_sided_site_signflip_p"],0.00115966796875,places=14)

if __name__=="__main__":
    unittest.main()
