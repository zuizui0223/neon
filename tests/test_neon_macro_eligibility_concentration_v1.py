"""Regression check on descriptive NEON site/domain representativeness.

Source-only, not a test of mammal ecological persistence or habitat effects.
"""
import json
import unittest
from pathlib import Path
from analysis.neon_macro_eligibility_concentration_v1 import run

ROOT=Path(__file__).resolve().parents[1]


class MacroDomainConcentrationTests(unittest.TestCase):
    def test_exact_803_candidate_to_58_strict_domain_composition(self):
        source=json.loads((ROOT/"results/neon_macro_biogeographic_selection_receipt_20261025.json").read_text())
        saved=json.loads((ROOT/"results/neon_macro_eligibility_concentration_20261025.json").read_text())
        self.assertEqual(saved,run(source))
        self.assertEqual((saved["all_candidate_pairs"]["sample_pairs"],
                          saved["strict_eligible_pairs"]["sample_pairs"]),(803,58))
        self.assertEqual((saved["all_candidate_pairs"]["domains_with_positive_pairs"],
                          saved["strict_eligible_pairs"]["domains_with_positive_pairs"]),(18,10))
        self.assertAlmostEqual(saved["all_candidate_pairs"]["effective_shannon_domains"],15.076389565919214,places=9)
        self.assertAlmostEqual(saved["strict_eligible_pairs"]["effective_shannon_domains"],7.55530803035287,places=9)
        self.assertAlmostEqual(saved["strict_to_candidate_effective_shannon_domain_ratio"],0.501135102493766,places=9)
        self.assertTrue(saved["scientific_scope"]["descriptive_no_clustered_p_value"])
        self.assertTrue(saved["scientific_scope"]["no_ecological_recurrence_effect_for_nonqualified_sites"])


if __name__=="__main__":
    unittest.main()
