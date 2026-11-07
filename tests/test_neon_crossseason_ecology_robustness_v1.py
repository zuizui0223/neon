"""Synthetic source-free and frozen-receipt tests of exploratory site influence.

Primary precommitted ecological test is NEVER revised by this script.
No species/site names, animals, trap coordinates or private data are read.
"""
from __future__ import annotations
import json
import unittest
from pathlib import Path

from analysis.review_neon_crossseason_site_influence_v1 import (
    exact_site_signflip, sensitivity_from_site_means, review_receipt
)

ROOT=Path(__file__).resolve().parents[1]


class SiteInfluenceAuditTests(unittest.TestCase):
    def test_exact_six_equal_positive_sites_has_p_one_sixtyfourth(self):
        r=exact_site_signflip([2.0]*6)
        self.assertEqual(r["number_site_sign_combinations"],64)
        self.assertEqual(r["one_sided_p"],1/64)

    def test_sign_and_all_site_removal_are_deterministic(self):
        arr=[-1,0.5,1.0,2.0,2.5]
        a=sensitivity_from_site_means(arr)
        b=sensitivity_from_site_means(list(reversed(arr)))
        self.assertEqual(a,b)
        self.assertEqual(a["all_single_site_omission_count"],5)
        self.assertEqual(a["strongest_three_positive_sites_removed"]["sites_remaining"],2)

    def test_frozen_14_site_p_and_stability_arithmetic(self):
        doc=json.loads((ROOT/"results/neon_crossseason_genus_template_ecology_receipt_20261019.json").read_text())
        result=review_receipt(doc)
        self.assertEqual(result["status"],"EXPLORATORY_SITE_INFLUENCE_NOT_NEW_CONFIRMATORY_TEST")
        self.assertEqual(result["original_frozen_primary_sites"],14)
        self.assertEqual(result["original_frozen_primary_positive_sites"],11)
        self.assertAlmostEqual(result["original_frozen_primary_mean_Z"],0.8007420166137748,places=12)
        self.assertAlmostEqual(result["original_frozen_primary_p"],0.00115966796875,places=12)
        diag=result["influence_diagnostics"]
        self.assertEqual(diag["all_single_site_omission_count"],14)
        self.assertLessEqual(diag["largest_leave_one_site_out_p"],0.00232)
        self.assertGreater(diag["largest_leave_one_site_out_p"],0)
        self.assertLess(diag["strongest_three_positive_sites_removed"]["one_sided_p"],0.01)

    def test_report_does_not_claim_causation_or_invent_site_ensembles(self):
        doc=json.loads((ROOT/"results/neon_crossseason_genus_template_ecology_receipt_20261019.json").read_text())
        r=review_receipt(doc)
        self.assertTrue(r["exploratory_not_preregistered"])
        self.assertFalse(r["new_original_spatial_effects_opened"])
        self.assertFalse(r["habitat_filtering_mechanism_identified"])
        self.assertFalse(r["causal_interactions_identified"])
        self.assertFalse(r["source_geographic_or_individual_IDs_exported"])
        self.assertEqual(r["original_density_paper_status"],"FAILED_5_OF_8")
        self.assertEqual(r["MOSA_WB_status"],"SEALED")

    def test_source_receipt_cannot_be_relabelled_success_when_primary_not_passed(self):
        doc=json.loads((ROOT/"results/neon_crossseason_genus_template_ecology_receipt_20261019.json").read_text())
        doc["independent_site_ecology"]["one_sided_site_signflip_p"]=0.2
        with self.assertRaisesRegex(ValueError,"precommitted"):
            review_receipt(doc)


if __name__=="__main__":
    unittest.main()
