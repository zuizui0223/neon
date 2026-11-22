"""Synthetic fixed-site and season-adjusted temporal-lag estimator tests."""
import json
import unittest
from analysis.neon_macro_site_fixed_lag_model_v1 import site_fixed_lag_model

def records(beta=-.2,sites=20):
    out=[]
    for i in range(sites):
        for j in range(9):
            q=j%4
            gap=35+((j*17+i*11)%95)+i%3
            z=2.2+i*.1+(.12*q)+beta*(gap/30)
            out.append({"site":f"FAKE_SITE_{i}",
                        "gap_days":gap,"transition":q,"z":z})
    return out

class MacroSiteLagModels(unittest.TestCase):
    def test_known_synthetic_within_site_negative_time_decay_recovers_slope(self):
        s=site_fixed_lag_model(records(),seed=101,n_bootstrap=200)
        self.assertEqual(s["status"],"EXPLORATORY_SITE_AND_TRANSITION_ADJUSTED_LAG_ESTIMATED")
        self.assertAlmostEqual(s["slope_standardized_recurrence_Z_per_30_capture_gap_days"],-.2,places=10)
        self.assertEqual(s["physical_sites"],20)
        self.assertEqual(s["number_original_informative_units"],180)
        self.assertEqual(s["transition_types_with_original_data"],[0,1,2,3])
        self.assertGreaterEqual(s["whole_site_bootstrap_draws_valid"],190)
        self.assertAlmostEqual(s["bootstrap_two_sided_percentile_95_interval"][0],-.2,places=8)
        self.assertAlmostEqual(s["bootstrap_two_sided_percentile_95_interval"][1],-.2,places=8)
        self.assertNotIn("FAKE_SITE",json.dumps(s))
        self.assertTrue(s["historical_observed_ecological_Zs_not_independent_new_release_data"])

    def test_zero_negative_time_association_not_relabelled_positive(self):
        z=site_fixed_lag_model(records(beta=0),seed=55,n_bootstrap=200)
        self.assertAlmostEqual(z["slope_standardized_recurrence_Z_per_30_capture_gap_days"],0,places=9)
        self.assertLessEqual(abs(z["bootstrap_two_sided_percentile_95_interval"][0]),1e-9)

    def test_rank_deficient_time_lag_collinear_with_season_stops(self):
        sample=records()
        for r in sample:
            r["gap_days"]=70+r["transition"]*10
        z=site_fixed_lag_model(sample,seed=55,n_bootstrap=200)
        self.assertEqual(z["status"],"STOP_SITE_TRANSITION_FIXED_EFFECTS_RANK_DEFICIENT")
        self.assertFalse(z["outcome_slope_estimated"])

    def test_invalid_source_days_or_missing_site_must_stop(self):
        src=records()
        src[0]["gap_days"]=-1
        with self.assertRaisesRegex(ValueError,"Invalid source"):
            site_fixed_lag_model(src,seed=55,n_bootstrap=200)
        src=records()
        src[0]["site"]=""
        with self.assertRaisesRegex(ValueError,"Invalid source"):
            site_fixed_lag_model(src,seed=55,n_bootstrap=200)

if __name__=="__main__":
    unittest.main()
