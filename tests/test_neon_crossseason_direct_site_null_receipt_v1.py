"""Cross-validate the source-exact NEON direct site-null calibration receipt.

All input data are public aggregate ecological summaries, never raw animal
tracks or source-level trap identifiers. A pass does not prove a causal
mechanism or transform a post-result check into prospective replication.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


def receipt(filename: str):
    return json.loads((ROOT/"results"/filename).read_text(encoding="utf-8"))


class FixedFixedDirectSiteNullReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cal=receipt("neon_crossseason_direct_site_null_calibration_receipt_20261019.json")
        cls.primary=receipt("neon_crossseason_genus_template_ecology_receipt_20261019.json")
        cls.doc=(ROOT/"docs/NEON_CROSSSEASON_DIRECT_NULL_SITE_CALIBRATION_20261019.md").read_text(encoding="utf-8")
        cls.paper=(ROOT/"manuscript/NEON_SPATIAL_TEMPLATE_REASSEMBLY_ECOLOGY_V0_2.md").read_text(encoding="utf-8")
        cls.old=receipt("multiscale_density_development_result_v1.json")

    def test_all_prior_source_nulls_and_primary_site_p_reproduce(self):
        c=self.cal
        z=c["exact_original_primary_reproduction"]
        old=self.primary["independent_site_ecology"]
        self.assertTrue(z["all_58_unit_Z_and_MCMC_diagnostics_match_archived"])
        self.assertTrue(z["original_14_sorted_site_means_match_archived"])
        self.assertEqual(c["source_original_seasonal_units"],58)
        self.assertEqual(c["source_independent_physical_sites"],14)
        self.assertAlmostEqual(z["original_14_sorted_site_means_match_archived"],1)
        self.assertAlmostEqual(z["original_exact_signflip_p_unchanged"],old["one_sided_site_signflip_p"],places=12)
        self.assertAlmostEqual(z["original_physical_site_mean_Z_unchanged"],old["site_mean_Z_mean"],places=12)
        self.assertTrue(self.primary["claim_boundary"]["site_test_criterion_supported"])

    def test_direct_marginal_p_is_monte_carlo_floor_not_exact_zero(self):
        d=self.cal["independent_unit_marginal_null"]
        self.assertEqual(d["null_meta_replicates"],20000)
        self.assertEqual(d["extreme_null_meta_replicates"],0)
        self.assertEqual(d["one_sided_p"],1/20001)
        self.assertLess(d["one_sided_p"],0.05)
        self.assertTrue(d["no_sign_symmetry_assumption_invoked"])
        self.assertTrue(self.cal["scientific_boundary"]["two_direct_null_couplings_are_post_result_checks"])

    def test_same_site_comonotone_stress_still_positive_but_not_universal_bound(self):
        c=self.cal
        d=c["comonotone_within_site_marginal_null"]
        self.assertEqual(d["null_meta_replicates"],20000)
        self.assertEqual(d["extreme_null_meta_replicates"],28)
        self.assertEqual(d["one_sided_p"],29/20001)
        self.assertGreater(d["null_quantiles"]["q975"],0)
        self.assertLess(d["null_quantiles"]["q975"],c["observed_equal_site_weighted_mean_Z"])
        self.assertTrue(c["calibration_robust_at_0_05_under_both_couplings"])
        self.assertTrue(c["comonotone_is_not_a_proven_upper_bound_on_all_joint_ecological_nulls"])
        self.assertTrue(c["scientific_boundary"]["same_site_reused_season_dependence_not_known"])

    def test_paper_records_all_p_values_without_treating_calibration_as_preregistered(self):
        for snippet in (
            "0.001159668","0.00144993","0.000049998",
            "58 original unit Zs","comonotone","post-result",
            "not an empirically identified joint capture process",
            "figures/neon_crossseason_genus_site_means_v1.svg"
        ):
            self.assertIn(snippet,self.paper)
        self.assertIn("AFTER the positive primary result",self.doc)
        self.assertIn("20,000",self.doc)
        self.assertIn("2026101929",self.doc)

    def test_no_spurious_ecological_causality_or_density_result(self):
        b=self.cal["scientific_boundary"]
        self.assertFalse(self.cal["original_density_W_B_reestimated"])
        self.assertTrue(self.cal["post_result_statistical_validation_not_a_second_independent_ecological_dataset"])
        self.assertTrue(b["no_competition_habitat_filtering_or_detection_causation_proven"])
        self.assertTrue(b["all_original_unit_null_vectors_dropped_after_computation"])
        self.assertTrue(b["raw_tags_sites_or_trap_positions_exported"] is False)
        self.assertEqual(b["density_W_B_original_generalization"],"FAILED_5_OF_8")
        self.assertEqual(b["MOSA_W_B"],"SEALED")
        self.assertFalse(self.old["preregistered_guard"]["passed"])


if __name__=="__main__":
    unittest.main()
