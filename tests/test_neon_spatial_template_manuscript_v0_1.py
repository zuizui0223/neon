"""Check ecology paper's numerical claims, independent-programme boundaries, SVG.

Original success criterion is never rewritten to match a paper's narrative.
No raw animals, trap locations, outcomes, or private source data accessed.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
NS={"svg":"http://www.w3.org/2000/svg"}


def receipt(path):
    return json.loads((ROOT/"results"/path).read_text(encoding="utf-8"))


class SeasonalMammalEcologyManuscriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paper=(ROOT/"manuscript/NEON_SPATIAL_TEMPLATE_REASSEMBLY_ECOLOGY_V0_1.md").read_text(encoding="utf-8")
        cls.neon=receipt("neon_crossseason_genus_template_ecology_receipt_20261019.json")
        cls.source=receipt("neon_crossseason_genus_template_support_receipt_20261019.json")
        cls.san=receipt("san_jacinto_crossseason_ecological_comparator_receipt_20261019.json")
        cls.old=receipt("multiscale_density_development_result_v1.json")
        cls.svg=ET.fromstring((ROOT/"manuscript/figures/neon_crossseason_genus_site_means_v1.svg").read_text())

    def test_original_neon_site_result_is_source_confirmed(self):
        a=self.neon["independent_site_ecology"]
        self.assertEqual(a["physical_sites"],14)
        self.assertEqual(a["informative_seasonal_units"],58)
        self.assertEqual(a["positive_site_means"],11)
        self.assertEqual(a["signflip_samples"],16384)
        self.assertAlmostEqual(a["site_mean_Z_mean"],0.8007420166137748,places=12)
        self.assertAlmostEqual(a["one_sided_site_signflip_p"],0.00115966796875,places=12)
        self.assertTrue(a["ecological_site_level_criterion_passed"])
        self.assertEqual(self.source["eligible_primary_pairs"],58)
        self.assertEqual(self.source["eligible_primary_sites"],14)
        self.assertEqual(self.neon["unit_result_counts"],{"INFORMATIVE_FIXED_FIXED_NULL":58})
        for phrase in ("+0.800742","0.001159668","11 of 14","58 of 58"):
            self.assertIn(phrase,self.paper)

    def test_san_jacinto_comparator_not_pooled_or_mistaken_as_neon_species_result(self):
        a=self.san["source_test"]
        self.assertEqual(a["taxon_rank"],"species")
        self.assertEqual(a["physical_grids"],6)
        self.assertEqual(a["seasonal_units"],10)
        self.assertEqual(a["positive_physical_grid_means"],5)
        self.assertAlmostEqual(a["one_sided_exact_grid_signflip_p"],0.046875,places=12)
        self.assertEqual(self.neon["frozen_design"]["taxon_rank"].split(";")[0],"genus")
        self.assertTrue(self.san["boundaries"]["p_values_must_not_be_pooled"])
        self.assertIn("p=0.046875",self.paper)
        self.assertIn("species-level",self.paper)
        self.assertIn("genus-level",self.paper)
        self.assertIn("do not",self.paper.lower())

    def test_svg_bars_match_sign_counts_and_public_metrics(self):
        self.assertEqual(self.svg.tag,"{http://www.w3.org/2000/svg}svg")
        self.assertTrue(self.svg.findall("svg:title",NS))
        all_rect=self.svg.findall(".//svg:rect",NS)
        self.assertEqual(sum(r.get("fill")=="#366f8b" for r in all_rect),11)
        self.assertEqual(sum(r.get("fill")=="#c77e59" for r in all_rect),3)
        texts=[e.text or "" for e in self.svg.findall(".//svg:text",NS)]
        self.assertTrue(any("11/14 positive" in t for t in texts))
        self.assertTrue(any("0.00116" in t for t in texts))
        self.assertTrue(any("Mean across sites +0.801" in t for t in texts))
        self.assertIn("figures/neon_crossseason_genus_site_means_v1.svg",self.paper)

    def test_novelty_is_bounded_by_prior_stable_rodent_spatial_studies(self):
        self.assertIn("Goldingay and Price (1997)",self.paper)
        self.assertNotIn("Thinsp",self.paper)
        self.assertIn("Chock et al. (2022)",self.paper)
        self.assertIn("10.1046/j.1523-1739.1997.95480.x",self.paper)
        self.assertIn("10.1007/s00442-021-05104-5",self.paper)
        self.assertIn("not the first",self.paper.lower())
        self.assertIn("**Status: RESEARCH DRAFT, not submitted.**",self.paper)

    def test_original_density_failure_and_mechanism_uncertainty_unchanged(self):
        self.assertFalse(self.old["preregistered_guard"]["passed"])
        self.assertEqual(self.old["preregistered_guard"]["observed_positive_genus_count"],5)
        self.assertEqual(self.old["preregistered_guard"]["required_positive_genus_count"],6)
        self.assertEqual(self.neon["claim_boundary"]["original_eight_genus_density_generality"],"FAILED_5_OF_8")
        self.assertFalse(self.neon["claim_boundary"]["causal_competition_or_habitat_filtering_proven"])
        self.assertFalse(self.neon["claim_boundary"]["capture_detectability_standardized_across_genera"])
        self.assertIn("does not directly measure mortality",self.paper)
        self.assertIn("taxonomic units",self.paper)
        self.assertIn("biotic interactions",self.paper)


if __name__=="__main__":
    unittest.main()
