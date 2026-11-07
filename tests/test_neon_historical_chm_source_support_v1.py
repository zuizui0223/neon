"""Synthetic checks for nearest original CHM actual pixel availability."""
from datetime import date
import unittest

from analysis.neon_historical_chm_source_support_v1 import (
    frozen_selected_month_days,source_month_manifest_support,
    summarize_actual_historical_pixels
)

def u(a,b):
    return {"site":"SYNTH","site_plot":("SYNTH","P"),
            "capture_dates_A":tuple(date(2022,mo,day) for mo,day in a),
            "capture_dates_B":tuple(date(2022,mo,day) for mo,day in b)}
D=[u([(4,1),(4,2),(4,3)],[(7,1),(7,2),(7,3)]),
   u([(7,1),(7,2),(7,3)],[(9,1),(9,2),(9,3)])]
MONTHS={"SYNTH":["2022-04","2022-09"]}

class OriginalHistoricalCHMTests(unittest.TestCase):
    def test_day_selection_deduplicates_overlapping_seasonal_pairs(self):
        days,pairs=frozen_selected_month_days(D,MONTHS,
            expected_pairs=2,expected_sites=1,expected_plots=1)
        self.assertEqual(len(days),9)
        self.assertTrue(all(p["within12"] for p in pairs))
        self.assertEqual(days[(("SYNTH","P"),date(2022,7,1))],("2022-09",2))
        self.assertEqual(sum(p["prior3"] for p in pairs),0)
    def test_released_month_without_tile_is_not_assumed_habitat(self):
        out=source_month_manifest_support(D,MONTHS,
            {("SYNTH","2022-04"):[{"name":"TEST"}],
             ("SYNTH","2022-09"):[]},
            expected_pairs=2,expected_sites=1,expected_plots=1)
        self.assertEqual(out["selected_original_site_flight_months"],2)
        self.assertEqual(out["selected_within12_site_flight_months"],2)
        self.assertEqual(out["within12_selected_months_with_CHM_tiles"],1)
        self.assertEqual(out["original_pairs_with_closest_AOP_month_abs_lag12"],2)
    def test_independent_exact_pixel_coverage_requires_all_six_dates(self):
        days,_=frozen_selected_month_days(D,MONTHS,
            expected_pairs=2,expected_sites=1,expected_plots=1)
        valid={key:100 for key in days}
        good=summarize_actual_historical_pixels(D,MONTHS,valid,
            expected_pairs=2,expected_sites=1,expected_plots=1)
        self.assertEqual(good["within12_actually_qualified_pairs"],2)
        valid[(("SYNTH","P"),date(2022,7,2))]=94
        fail=summarize_actual_historical_pixels(D,MONTHS,valid,
            expected_pairs=2,expected_sites=1,expected_plots=1)
        self.assertEqual(fail["within12_actually_qualified_pairs"],0)
        self.assertEqual(fail["qualified_physical_sites_by_class"]["within12"],0)
    def test_missing_day_cannot_be_imputed_from_adjacent_dates(self):
        days,_=frozen_selected_month_days(D,MONTHS,
            expected_pairs=2,expected_sites=1,expected_plots=1)
        valid={key:100 for key in days}
        valid.pop((("SYNTH","P"),date(2022,4,2)))
        with self.assertRaises(ValueError):
            summarize_actual_historical_pixels(D,MONTHS,valid,
                expected_pairs=2,expected_sites=1,expected_plots=1)
    def test_missing_manifest_month_is_rejected(self):
        with self.assertRaises(ValueError):
            source_month_manifest_support(D,MONTHS,{("SYNTH","2022-04"):[]},
                expected_pairs=2,expected_sites=1,expected_plots=1)
    def test_no_optimistic_zero_when_missing_historical_flight(self):
        first=u([(4,1),(4,2),(4,3)],[(7,1),(7,2),(7,3)])
        days,pairs=frozen_selected_month_days([first],{"SYNTH":[]},
            expected_pairs=1,expected_sites=1,expected_plots=1)
        self.assertEqual(sum(month is None for month,lag in days.values()),6)
        report=summarize_actual_historical_pixels([first],{"SYNTH":[]},{},
            expected_pairs=1,expected_sites=1,expected_plots=1)
        self.assertEqual(report["selected_plot_day_keys_within12"],0)
        self.assertEqual(report.get("within12_actually_qualified_pairs",0),0)

if __name__=="__main__":
    unittest.main()
