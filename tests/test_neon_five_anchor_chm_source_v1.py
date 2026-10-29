"""Synthetic five-point NEON canopy-grid descriptive SOURCE gate tests.

Only fixture plot keys, anchor labels and synthetic canopy heights are used.
No animal records, genus outcome, trap spatial recurrence or W/B fit.
"""
import unittest

from analysis.neon_five_anchor_chm_source_v1 import (
    ANCHORS, aggregate_five_anchor_height_support,
)


def point(plot,anchor,value,*,status="VALID_REFERENCE_PIXEL",
          known_uncertainty=True,flagged=False):
    return {
        "plot_key":plot,"anchor":anchor,"status":status,
        "height_m":value,"uncertainty_known":known_uncertainty,
        "historically_flagged_grid":flagged,
    }


class FiveAnchorSourceSupportTests(unittest.TestCase):
    def test_known_canopy_heterogeneity_vs_zero_reference(self):
        a=[point("SECRET_PLOT_A",name,val) for name,val in zip(
            ANCHORS,[0.,0.,4.,8.,0.]
        )]
        b=[point("SECRET_PLOT_B",name,0.) for name in ANCHORS]
        out=aggregate_five_anchor_height_support(a+b,expected_plots=2)
        self.assertEqual(out["original_plots"],2)
        self.assertEqual(out["original_anchor_attempts"],10)
        self.assertEqual(out["valid_anchors"],10)
        self.assertEqual(out["plots_with_all_five_valid_anchors"],2)
        self.assertEqual(out["plots_with_nonzero_five_anchor_canopy_range"],1)
        self.assertEqual(out["plots_E5_zero_other_anchor_positive"],1)
        self.assertEqual(out["valid_E5_reference_anchors"],2)
        self.assertEqual(out["zero_E5_reference_heights"],2)
        self.assertAlmostEqual(out["five_anchor_range_m_summary"]["median"],4.)
        self.assertFalse(out["all_100_trap_station_habitat_verified"])

    def test_masked_nodata_never_becomes_zero_canopy(self):
        a=[point("SECRET_PLOT_A",name,0.) for name in ANCHORS]
        a[0]["status"]="REFERENCE_PIXEL_NODATA"
        a[0]["height_m"]=None
        out=aggregate_five_anchor_height_support(a,expected_plots=1)
        self.assertEqual(out["valid_anchors"],4)
        self.assertEqual(out["masked_or_unavailable_anchors"],1)
        self.assertEqual(out["valid_zero_canopy_anchors"],4)
        self.assertEqual(out["plots_with_all_five_valid_anchors"],0)

    def test_E5_nodata_is_not_called_zero(self):
        a=[point("SECRET_PLOT_A",name,0.) for name in ANCHORS]
        a[-1]["status"]="OUTSIDE_RASTER"
        a[-1]["height_m"]=None
        out=aggregate_five_anchor_height_support(a,expected_plots=1)
        self.assertEqual(out["valid_E5_reference_anchors"],0)
        self.assertEqual(out["zero_E5_reference_heights"],0)
        self.assertEqual(out["plots_E5_zero_other_anchor_positive"],0)

    def test_single_valid_anchor_does_not_estimate_within_plot_range(self):
        a=[point("SECRET_PLOT_A",name,0.) for name in ANCHORS]
        for p in a[:-1]:p["status"]="NO_RELEASED_TILE";p["height_m"]=None
        out=aggregate_five_anchor_height_support(a,expected_plots=1)
        self.assertEqual(out["plots_with_two_or_more_valid_anchors"],0)
        self.assertIsNone(out["five_anchor_range_m_summary"]["median"])

    def test_unknown_uncertainty_not_assumed_zero(self):
        rows=[point("SECRET_PLOT_A",name,1.,known_uncertainty=False) for name in ANCHORS]
        out=aggregate_five_anchor_height_support(rows,expected_plots=1)
        self.assertEqual(out["anchors_with_unknown_coordinate_uncertainty"],5)
        self.assertEqual(out["anchors_with_known_coordinate_uncertainty"],0)
        self.assertFalse(out["unknown_coordinate_uncertainty_was_treated_as_zero"])

    def test_duplicate_or_missing_anchor_fails_closed(self):
        rows=[point("SECRET_PLOT_A",name,1.) for name in ANCHORS]
        with self.assertRaisesRegex(ValueError,"duplicate"):
            aggregate_five_anchor_height_support(rows+[rows[0]],expected_plots=1)
        with self.assertRaisesRegex(ValueError,"five original anchors"):
            aggregate_five_anchor_height_support(rows[:-1],expected_plots=1)

    def test_nonfinite_or_invalid_source_height_rejected(self):
        rows=[point("SECRET_PLOT_A",name,1.) for name in ANCHORS]
        rows[0]["height_m"]=float("nan")
        with self.assertRaisesRegex(ValueError,"finite"):
            aggregate_five_anchor_height_support(rows,expected_plots=1)
        rows[0]["height_m"]=0.
        rows[1]["status"]="REFERENCE_PIXEL_NODATA"
        with self.assertRaisesRegex(ValueError,"missing"):
            aggregate_five_anchor_height_support(rows,expected_plots=1)

    def test_aggregate_never_discloses_source_plot_ids_or_trap_positions(self):
        rows=[point("SECRET_PLOT_A",name,2.,flagged=True) for name in ANCHORS]
        out=aggregate_five_anchor_height_support(rows,expected_plots=1)
        self.assertNotIn("SECRET_PLOT_A",str(out))
        self.assertNotIn("A10",str(out))
        self.assertEqual(out["plots_with_published_geolocation_issue"],1)
        self.assertFalse(out["ecological_genus_habitat_effect_computed"])
        self.assertFalse(out["historical_capture_date_alignment_proven"])

if __name__=="__main__":
    unittest.main()
