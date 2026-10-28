"""NEON full 100-station canopy QA: synthetic-only ecological-effect-blind tests."""
from __future__ import annotations
from datetime import date
import unittest

from analysis.neon_3000_chm_source_qa_v1 import (
    VALID,month_gap,original_month_source_alignment,
    aggregate_full_station_chm,protected_five_anchor_replay
)


def unit(start,other):
    return {
        "site":"EXAMPLE","site_plot":("EXAMPLE","PLOT"),
        "capture_dates_A":tuple(date(*d) for d in start),
        "capture_dates_B":tuple(date(*d) for d in other),
    }


class FullStationCanopySourceTests(unittest.TestCase):
    def test_month_direction_and_calendar_only(self):
        self.assertEqual(month_gap(date(2022,6,1),"2024-06"),24)
        self.assertEqual(month_gap(date(2024,7,30),"2024-06"),-1)
        self.assertEqual(month_gap(date(2024,6,1),"2024-06"),0)
        with self.assertRaises(ValueError):
            month_gap(date(2024,6,1),"2024-13")

    def test_original_time_alignment_separates_duplicated_pair_days(self):
        a=[(2024,4,1),(2024,4,2),(2024,4,3)]
        b=[(2024,5,1),(2024,5,2),(2024,5,3)]
        c=[(2024,6,1),(2024,6,2),(2024,6,3)]
        v=original_month_source_alignment(
            [unit(a,b),unit(b,c)],{"EXAMPLE":"2024-05"},
            expected_pairs=2,expected_sites=1,expected_plots=1
        )
        self.assertEqual(v["paired_source_day_attempts"],12)
        self.assertEqual(v["unique_source_plot_day_keys"],9)
        self.assertEqual(v["pairs_all_six_days_within_3_calendar_months"],2)
        self.assertEqual(v["pairs_all_six_days_same_acquisition_year"],2)
        self.assertTrue(v["acquisition_not_assumed_contemporaneous_with_capture"])
        self.assertFalse(v["original_capture_tags_or_spatial_response_read"])

    def test_full_station_plot_heterogeneity_and_zero_E5(self):
        rows=[
          {"plot_key":("EXAMPLE","P1"),"station":"A1",
           "status":VALID,"height_m":0.0,"historically_flagged_plot":False},
          {"plot_key":("EXAMPLE","P1"),"station":"A2",
           "status":VALID,"height_m":12.0,"historically_flagged_plot":False},
          {"plot_key":("EXAMPLE","P1"),"station":"E5",
           "status":VALID,"height_m":0.0,"historically_flagged_plot":False},
          {"plot_key":("EXAMPLE","P2"),"station":"A1",
           "status":VALID,"height_m":0.0,"historically_flagged_plot":True},
          {"plot_key":("EXAMPLE","P2"),"station":"A2",
           "status":VALID,"height_m":0.0,"historically_flagged_plot":True},
          {"plot_key":("EXAMPLE","P2"),"station":"E5",
           "status":VALID,"height_m":0.0,"historically_flagged_plot":True},
        ]
        out=aggregate_full_station_chm(rows,expected_plots=2,stations=("A1","A2","E5"))
        self.assertEqual(out["valid_station_pixels"],6)
        self.assertEqual(out["plots_with_nonzero_full_station_height_range"],1)
        self.assertEqual(out["plots_all_stations_zero_canopy"],1)
        self.assertEqual(out["plots_E5_zero_but_another_station_positive"],1)
        self.assertEqual(out["historically_flagged_original_plots_retained"],1)
        self.assertFalse(out["full_historical_habitat_or_detection_effect_estimated"])
        self.assertNotIn("EXAMPLE",str(out))
        self.assertNotIn("12.0",str(out))

    def test_missing_pixel_not_substituted_by_zero(self):
        rows=[
          {"plot_key":("TEST","P"),"station":"A1","status":VALID,"height_m":0.0,
           "historically_flagged_plot":False},
          {"plot_key":("TEST","P"),"station":"A2","status":"CHM_PIXEL_MASKED","height_m":None,
           "historically_flagged_plot":False},
        ]
        out=aggregate_full_station_chm(rows,expected_plots=1,stations=("A1","A2"))
        self.assertEqual(out["valid_station_pixels"],1)
        self.assertEqual(out["valid_zero_pixels"],1)
        self.assertEqual(out["plots_all_station_pixels_valid"],0)
        with self.assertRaises(ValueError):
            rows[1]["height_m"]=0.0
            aggregate_full_station_chm(rows,expected_plots=1,stations=("A1","A2"))

    def test_protected_original_five_anchor_identity_check(self):
        five=("A1","A10","J1","J10","E5")
        rows=[
            {"plot_key":("EXAMPLE","P"),"station":name,"status":VALID,
             "height_m":(5.0 if name=="A10" else 0.0),
             "historically_flagged_plot":False}
            for name in five
        ]
        out=protected_five_anchor_replay(rows,expected_plots=1)
        self.assertEqual(out["five_named_anchor_pixels_valid"],5)
        self.assertEqual(out["five_anchor_zero_pixels"],4)
        self.assertEqual(out["E5_zero_pixels"],1)
        self.assertEqual(out["plots_five_anchor_positive_canopy_range"],1)
        self.assertTrue(out["all_original_five_anchor_pixels_valid"])

    def test_month_source_requires_original_site_set(self):
        u=unit([(2024,1,1),(2024,1,2),(2024,1,3)],
               [(2024,6,1),(2024,6,2),(2024,6,3)])
        with self.assertRaises(ValueError):
            original_month_source_alignment([u],{"OTHER":"2024-01"},
                                            expected_pairs=1,expected_sites=1,expected_plots=1)


if __name__=="__main__":
    unittest.main()
