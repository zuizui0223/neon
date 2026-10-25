"""Verify ecology manuscript v0.3 reflects corrected, source-locked numbers.

This is a documentation/provenance consistency check, not a new ecological
test, independent confirmation, or habitat regression.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript/NEON_SPATIAL_TEMPLATE_REASSEMBLY_ECOLOGY_V0_3.md"
RECEIPT = ROOT / "results/neon_uniform_null_correction_receipt_20261020.json"


class CorrectedEcologyManuscriptV03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paper = MANUSCRIPT.read_text(encoding="utf-8")
        cls.receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))

    def test_new_manuscript_uses_exact_corrected_site_statistics(self):
        x = self.receipt
        for key, nsite, npairs, npositive, value in (
            ("full_14site", 14, 58, 11, "+0.794663773"),
            ("source_disjoint_12site", 12, 46, 10, "+0.843161730"),
        ):
            d = x[key]
            self.assertEqual((d["physical_sites"], d["seasonal_pairs"], d["positive_site_means"]),
                             (nsite, npairs, npositive))
            self.assertIn(value, self.paper)
            self.assertAlmostEqual(float(value), d["corrected_site_mean_Z"], places=8)
            self.assertEqual(d["independent_product_null"]["draws"], 100000)
            self.assertEqual(d["within_site_comonotone_stress"]["draws"], 20000)

    def test_calibration_values_and_corrected_old_null_disclosed(self):
        self.assertIn("**0.001250**", self.paper)
        self.assertIn("**0.002100**", self.paper)
        self.assertIn("0.000010", self.paper)
        self.assertIn("accepted-swap", self.paper.lower())
        self.assertIn("historical", self.paper.lower())
        self.assertIn("not a guaranteed upper", self.paper.lower())
        self.assertIn("SUBMISSION HOLD", self.paper)
        self.assertIn("not a new preregistration", self.paper.lower())

    def test_no_habitat_detection_or_competition_effect_claim(self):
        for claim in (
            "No statistical association between genus recurrence and CHM was calculated",
            "capture-space pattern",
            "taxon-specific detection",
            "MOSA W/B effects remain sealed",
            "must not",
        ):
            self.assertIn(claim.lower(), self.paper.lower())
        self.assertIn("Figure 2", self.paper)
        self.assertIn("obsolete accepted-only sampler", self.paper)

    def test_original_results_immutable_and_ref_is_only_corrected_source(self):
        x = self.receipt
        self.assertEqual(x["full_14site"]["physical_sites"], 14)
        self.assertEqual(x["source_disjoint_12site"]["physical_sites"], 12)
        self.assertTrue(x["correction"]["post_result_correctness_reanalysis_not_new_independent_confirmation"])
        self.assertTrue(x["scientific_boundaries"]["San_Jacinto_species_level_source_not_recalibrated_in_this_run"])


if __name__ == "__main__":
    unittest.main()
