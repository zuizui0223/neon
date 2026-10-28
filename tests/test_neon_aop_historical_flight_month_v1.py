"""Synthetic-only monthly flight acquisition availability tests."""
import unittest
from datetime import date
from analysis.run_neon_aop_historical_flight_month_v1 import (
    nearest_flight_month,audit_flight_month_availability
)

def unit(a,b):
    return {"site":"SYNTH","site_plot":("SYNTH","P"),
            "capture_dates_A":tuple(date(*d) for d in a),
            "capture_dates_B":tuple(date(*d) for d in b)}

class FlightMonthAvailabilityTests(unittest.TestCase):
    def test_nearest_year_selection_no_canopy_and_prefer_earlier_tie(self):
        self.assertEqual(nearest_flight_month(date(2024,6,4),["2024-05","2024-07"]),
                         ("2024-05",-1))
        self.assertEqual(nearest_flight_month(date(2024,6,4),["2024-06"]),("2024-06",0))
        self.assertEqual(nearest_flight_month(date(2024,2,4),[]),(None,None))
        with self.assertRaises(ValueError):
            nearest_flight_month(date(2024,5,4),["2024-00"])

    def test_original_pair_dates_and_support_not_independent_sites(self):
        a=[(2024,4,1),(2024,4,2),(2024,4,3)]
        b=[(2024,8,1),(2024,8,2),(2024,8,3)]
        c=[(2024,9,1),(2024,9,2),(2024,9,3)]
        result=audit_flight_month_availability(
            [unit(a,b),unit(b,c)],
            {"SYNTH":["2024-04","2024-09"]},
            expected_pairs=2,expected_sites=1,expected_plots=1)
        self.assertEqual(result["original_repeated_capture_day_attempts"],12)
        self.assertEqual(result["original_distinct_plot_day_keys"],9)
        self.assertEqual(result["pairs_all_six_days_within_3_months"],2)
        self.assertEqual(result["sites_with_one_or_more_flight_month"],1)
        self.assertEqual(result["total_unique_site_flight_month_pairs"],2)
        self.assertTrue(result["AOP_month_metadata_does_not_prove_tile_coverage_at_mammal_trap"])
        self.assertFalse(result["private_site_plot_day_month_pairs_exported"])

    def test_missing_site_acquisition_does_not_impute(self):
        a=[(2024,4,1),(2024,4,2),(2024,4,3)]
        b=[(2024,6,1),(2024,6,2),(2024,6,3)]
        r=audit_flight_month_availability([unit(a,b)],{"SYNTH":[]},
                                          expected_pairs=1,expected_sites=1,expected_plots=1)
        self.assertEqual(r["original_day_attempts_with_any_published_month"],0)
        self.assertEqual(r["pairs_all_six_days_within_24_months"],0)

if __name__=="__main__":
    unittest.main()
