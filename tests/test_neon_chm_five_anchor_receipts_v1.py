"""Frozen E5 vs five-anchor source raster receipts and biological limits.

No raw animal/plot identity, trapping position, canopy tile or genus
spatial ecology response is read by this test. Do not promote source
availability to causal habitat selection.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def record(filename: str) -> dict:
    return json.loads((ROOT/"results"/filename).read_text(encoding="utf-8"))


class CHMSourceReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e5=record("neon_e5_chm_reference_pixels_receipt_20261020.json")
        cls.five=record("neon_five_anchor_chm_source_receipt_20261020.json")

    def test_same_fixed_14_site_30_plot_original_cohort(self):
        e,f=self.e5,self.five
        self.assertEqual(e["fixed_original_sites"],14)
        self.assertEqual(e["fixed_original_plots"],30)
        self.assertEqual(f["original_plots"],30)
        self.assertEqual(f["original_anchor_attempts"],150)
        self.assertTrue(f["frozen_58_unit_30_plot_14_site_cohort_reproduced"])
        self.assertTrue(f["original_source"]["same_58_pairs_30_plots_14_sites_reproduced"])
        self.assertEqual(f["original_source"]["manifest_files"],3547)
        self.assertEqual(f["original_source"]["downloaded_source_files_MD5_size_verified"],3480)
        self.assertEqual(f["original_source"]["source_trap_rows"],1505827)

    def test_all_real_pixels_have_provider_integrity_not_synthetic_grid(self):
        self.assertEqual(self.e5["valid_reference_pixels"],30)
        self.assertEqual(self.e5["unique_selected_tiles"],29)
        self.assertEqual(self.e5["tiles_downloaded_and_provider_checksum_size_verified"],29)
        self.assertEqual(self.five["valid_anchors"],150)
        self.assertEqual(self.five["masked_or_unavailable_anchors"],0)
        self.assertEqual(self.five["unique_provider_size_and_checksum_verified_CHM_tiles"],34)
        self.assertEqual(self.five["provider_checksum_types"],{"crc32c":34})
        self.assertTrue(self.five["source_effect_scope"]["only_five_literal_station_anchors_evaluated"])
        self.assertFalse(self.five["source_effect_scope"]["all_100_station_locations_verified"])

    def test_reference_only_measurement_misses_within_grid_variation(self):
        self.assertEqual(self.e5["valid_reference_height_m_summary"]["zero_values"],19)
        self.assertTrue(self.five["earlier_E5_30_valid_19_zero_reproduced"])
        self.assertEqual(self.five["zero_E5_reference_heights"],19)
        self.assertEqual(self.five["plots_with_nonzero_five_anchor_canopy_range"],14)
        self.assertEqual(self.five["plots_E5_zero_other_anchor_positive"],3)
        self.assertEqual(self.five["plots_with_all_five_valid_and_zero_canopy"],16)
        self.assertAlmostEqual(self.five["five_anchor_range_m_summary"]["maximum"],36.904,places=3)
        self.assertEqual(self.five["five_anchor_range_m_summary"]["median"],0)

    def test_120_of_150_uncertainties_unknown_not_fabricated(self):
        self.assertEqual(self.five["anchors_with_known_coordinate_uncertainty"],30)
        self.assertEqual(self.five["anchors_with_unknown_coordinate_uncertainty"],120)
        self.assertEqual(self.five["plots_with_published_geolocation_issue"],4)
        self.assertFalse(self.five["unknown_coordinate_uncertainty_was_treated_as_zero"])
        self.assertFalse(self.five["historical_capture_date_alignment_proven"])
        self.assertFalse(self.five["CHM_zero_means_no_understory"])

    def test_five_anchor_chm_never_promoted_to_mammal_ecological_mechanism(self):
        self.assertEqual(self.five["status"],"FIVE_NAMED_CHM_REFERENCE_ANCHORS_AUDITED_NOT_HABITAT_EFFECT")
        self.assertFalse(self.five["ecological_genus_habitat_effect_computed"])
        self.assertFalse(self.five["source_effect_scope"]["no_genus_trap_recurrence_or_habitat_regression_computed"] is False)
        self.assertFalse(self.e5["scientific_boundary"]["habitat_or_detection_effect_estimated"])
        self.assertFalse(self.five["original_density_W_B_claim_reclassified"])
        self.assertEqual(self.five["MOSA_W_B_effects"],"SEALED")


if __name__=="__main__":
    unittest.main()
