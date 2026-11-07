"""Cross-check separately authored direct fixed-fixed source null calibrations.

This test reads only redacted, aggregate result JSON and a manuscript.
It never consumes raw animals, trapping grids, genotype sequences, or
unpublished environmental / W-B ecological outcomes.
"""
from __future__ import annotations

import json
from math import isclose
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

def read(name: str):
    return json.loads((ROOT/"results"/name).read_text(encoding="utf-8"))


class CrossSeasonDirectNullReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.primary=read("neon_crossseason_genus_template_ecology_receipt_20261019.json")
        cls.two=read("neon_crossseason_direct_site_null_calibration_receipt_20261019.json")
        cls.independent=read("neon_crossseason_conditional_product_100k_replication_receipt_20261019.json")
        cls.old=read("multiscale_density_development_result_v1.json")
        cls.manuscript=(ROOT/"manuscript/NEON_SPATIAL_TEMPLATE_REASSEMBLY_ECOLOGY_V0_2.md").read_text(encoding="utf-8")

    def test_two_independent_codepaths_replay_same_frozen_14_site_statistic(self):
        primary=self.primary["independent_site_ecology"]
        one=self.two["exact_original_primary_reproduction"]
        repeat=self.independent["original_primary_result_unmodified"]
        self.assertEqual(primary["physical_sites"],14)
        self.assertEqual(primary["informative_seasonal_units"],58)
        self.assertEqual(primary["positive_site_means"],11)
        self.assertTrue(one["all_58_unit_Z_and_MCMC_diagnostics_match_archived"])
        self.assertTrue(repeat["all_original_58_null_chain_Zs_and_14_site_means_reproduced"])
        for x in (one["original_physical_site_mean_Z_unchanged"],repeat["site_mean_Z"]):
            self.assertTrue(isclose(x,primary["site_mean_Z_mean"],abs_tol=1e-12))
        for x in (one["original_exact_signflip_p_unchanged"],repeat["site_signflip_one_sided_p"]):
            self.assertTrue(isclose(x,0.00115966796875,abs_tol=1e-15))

    def test_20k_and_100k_independent_null_tails_are_resolution_floors(self):
        a=self.two["independent_unit_marginal_null"]
        b=self.independent["direct_null_calibration"]
        self.assertEqual((a["extreme_null_meta_replicates"],a["null_meta_replicates"]),(0,20000))
        self.assertEqual((b["upper_tail_exceedances"],b["monte_carlo_replicates"]),(0,100000))
        self.assertAlmostEqual(a["one_sided_p"],1/20001,places=14)
        self.assertAlmostEqual(b["one_sided_p_with_plus_one"],1/100001,places=14)
        self.assertAlmostEqual(b["observed_equal_site_weighted_mean_z"],self.primary["independent_site_ecology"]["site_mean_Z_mean"],places=12)
        self.assertFalse(b["genus_specific_detection_bias_excluded"])

    def test_coupled_within_site_is_second_post_result_assumption_stress(self):
        coupled=self.two["comonotone_within_site_marginal_null"]
        self.assertEqual(coupled["null_meta_replicates"],20000)
        self.assertEqual(coupled["extreme_null_meta_replicates"],28)
        self.assertAlmostEqual(coupled["one_sided_p"],29/20001,places=12)
        self.assertLess(coupled["one_sided_p"],0.05)
        self.assertTrue(self.two["comonotone_is_not_a_proven_upper_bound_on_all_joint_ecological_nulls"])
        self.assertTrue(self.two["scientific_boundary"]["two_direct_null_couplings_are_post_result_checks"])

    def test_shared_season_event_overlap_is_reported_not_concealed(self):
        d=self.independent["reused_season_dependence_diagnostic"]
        self.assertEqual(d["season_keys_used_in_multiple_pair_roles"],3)
        self.assertEqual(d["source_pair_roles_at_reused_seasons"],6)
        self.assertEqual(d["physical_sites_with_any_adjacent_pair_season_reuse"],2)
        self.assertTrue(d["joint_shared_season_covariance_not_preserved"])
        self.assertFalse(d["raw_site_plot_and_season_identifiers_exported"])
        self.assertTrue(self.independent["interpretation"]["shared_season_dependence_not_jointly_preserved"])

    def test_paper_states_inference_scope_and_original_failed_density_study(self):
        self.assertIn("100,000",self.manuscript)
        self.assertIn("three site×plot×season keys",self.manuscript)
        self.assertIn("two of the fourteen sites",self.manuscript)
        self.assertIn("within-site",self.manuscript)
        self.assertIn("not an empirically identified joint capture process",self.manuscript)
        self.assertIn("NOT",self.manuscript.upper())
        self.assertFalse(self.old["preregistered_guard"]["passed"])
        self.assertEqual(self.old["preregistered_guard"]["observed_positive_genus_count"],5)
        self.assertEqual(self.old["preregistered_guard"]["required_positive_genus_count"],6)
        self.assertFalse(self.independent["old_density_W_B_responses_reanalysed"])

if __name__=="__main__":
    unittest.main()
