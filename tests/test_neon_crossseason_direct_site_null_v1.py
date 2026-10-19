"""Source-free tests for direct site-level fixed-fixed meta-null calibration.

The primary original 14-site signflip remains frozen. This new post-result
review samples original within-unit fixed-fixed null draws, without replacing
or relabelling the primary ecological significance test.
"""
import unittest

from analysis.neon_crossseason_direct_site_null_v1 import (
    direct_site_null_calibration,
)


def make_unit(site, observed_z=1.0, seq=None):
    vals=list(seq if seq is not None else [-2,-1,0,1,2]*40)
    return {
        "site":site,
        "observed_unit_z":float(observed_z),
        "null_unit_z_draws":vals,
    }


class DirectSiteNullCalibrationTests(unittest.TestCase):
    def test_strong_same_direction_is_detected_under_both_couplings(self):
        units=[make_unit(f"S{i}") for i in range(8)]
        r=direct_site_null_calibration(
            units, seed=2026101929, n_replicates=4000
        )
        self.assertEqual(r["independent_unit_marginal_null"]["sites"],8)
        self.assertEqual(r["comonotone_within_site_marginal_null"]["sites"],8)
        self.assertLess(r["independent_unit_marginal_null"]["one_sided_p"],0.05)
        self.assertLess(r["comonotone_within_site_marginal_null"]["one_sided_p"],0.05)
        self.assertTrue(r["original_signflip_not_assumed_for_new_tests"])
        self.assertFalse(r["raw_Neon_unit_samples_exported"])

    def test_explicit_site_coupling_can_increase_p_with_shared_units(self):
        units=[make_unit(f"S{i}",observed_z=1.1) for i in range(8)]
        # Same-site correlated unit nulls; B marginal preserved exactly
        # but comonotone rank shared within the physical site.
        units+=[make_unit(f"S{i}",observed_z=1.1) for i in range(8)]
        r=direct_site_null_calibration(
            units, seed=2026101929, n_replicates=5000
        )
        p_ind=r["independent_unit_marginal_null"]["one_sided_p"]
        p_dep=r["comonotone_within_site_marginal_null"]["one_sided_p"]
        self.assertGreaterEqual(p_dep,p_ind)
        self.assertLess(p_dep,0.05)

    def test_null_zero_observed_effect_not_called_recurrence(self):
        units=[make_unit(f"S{i}",observed_z=0.0) for i in range(8)]
        r=direct_site_null_calibration(units,seed=100,n_replicates=2000)
        self.assertGreater(r["independent_unit_marginal_null"]["one_sided_p"],0.4)
        self.assertGreater(r["comonotone_within_site_marginal_null"]["one_sided_p"],0.4)
        self.assertFalse(r["calibration_robust_at_0_05_under_both_couplings"])

    def test_duplicate_site_units_do_not_invent_new_independent_sites(self):
        units=[make_unit("SITE_X") for _ in range(25)]
        r=direct_site_null_calibration(units,seed=6,n_replicates=200)
        self.assertEqual(r["independent_unit_marginal_null"]["sites"],1)
        self.assertEqual(r["independent_unit_marginal_null"]["units"],25)

    def test_equal_draw_count_and_finite_inputs_fail_closed(self):
        units=[make_unit("SITE_A"), make_unit("SITE_B",seq=[-1,0,1])]
        with self.assertRaisesRegex(ValueError,"equal null draw"):
            direct_site_null_calibration(units,seed=100,n_replicates=100)
        units=[make_unit("SITE_A")]
        units[0]["null_unit_z_draws"][0]=float("nan")
        with self.assertRaisesRegex(ValueError,"finite"):
            direct_site_null_calibration(units,seed=100,n_replicates=100)

    def test_seed_reproducibility_and_order_invariance(self):
        units=[make_unit(f"S{i}",observed_z=0.5+(i%3)/4) for i in range(8)]
        units+= [make_unit(f"S{i}",observed_z=0.5+(i%3)/4) for i in range(8)]
        a=direct_site_null_calibration(units,seed=2026101929,n_replicates=1000)
        b=direct_site_null_calibration(units,seed=2026101929,n_replicates=1000)
        self.assertEqual(a,b)

    def test_no_full_raw_null_vectors_and_site_names_in_output(self):
        units=[make_unit(f"PRIVATE_SITE_{i}") for i in range(8)]
        r=direct_site_null_calibration(units,seed=123,n_replicates=500)
        self.assertNotIn("PRIVATE_SITE",str(r))
        self.assertNotIn("null_unit_z_draws",str(r))
        self.assertFalse(r["original_density_W_B_reestimated"])
        self.assertTrue(r["post_result_statistical_validation_not_a_second_independent_ecological_dataset"])


if __name__=="__main__":
    unittest.main()
