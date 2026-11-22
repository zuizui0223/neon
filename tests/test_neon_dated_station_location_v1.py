"""Source-only tests of NEON geoNEON mammal uncertainty and date history.

Synthetic examples only: no capture positions, genus recurrence effect or
current animal identities. The official R implementation assumes
max monumented U+3m for nonmonumented positions and measured U+1m for
direct uncertainty, which are source CONVENTIONS not empirical bounds.
"""
from __future__ import annotations
from datetime import date
import unittest
from analysis.neon_dated_station_location_v1 import (
    station_labels_10x10,adjust_grid_uncertainty,choose_location_at_capture,
)


class DatedMammalGeolocationTests(unittest.TestCase):
    def test_all_100_named_station_labels_without_imputed_positions(self):
        stations=station_labels_10x10()
        self.assertEqual(len(stations),100)
        self.assertEqual(stations[0],"A1")
        self.assertEqual(stations[-1],"J10")
        self.assertEqual(len(set(stations)),100)
        self.assertNotIn("X1",stations)

    def test_monumented_U_plus_1_and_nonmonumented_max_U_plus_3(self):
        source={"E5":1.5,"A1":None,"J10":None,"A10":2.0}
        d=adjust_grid_uncertainty(source)
        self.assertEqual(d["E5"]["adjusted_uncertainty_m"],2.5)
        self.assertEqual(d["A10"]["adjusted_uncertainty_m"],3.0)
        self.assertEqual(d["A1"]["adjusted_uncertainty_m"],5.0)
        self.assertEqual(d["J10"]["adjusted_uncertainty_m"],5.0)
        self.assertEqual(d["A1"]["source"],"ASSUMED_GRID_MAX_MONUMENT_PLUS_3M")
        self.assertEqual(d["E5"]["source"],"DIRECT_REPORTED_PLUS_1M")
        self.assertFalse(d["A1"]["raw_uncertainty_was_measured"])

    def test_unknown_without_any_monument_stops_instead_of_assuming_zero(self):
        with self.assertRaisesRegex(ValueError,"monument"):
            adjust_grid_uncertainty({"A1":None,"A2":None})

    def test_nonfinite_negative_and_noncanonical_inputs_rejected(self):
        for x in (-1.,float("nan"),float("inf")):
            with self.subTest(value=x):
                with self.assertRaisesRegex(ValueError,"finite"):
                    adjust_grid_uncertainty({"E5":x})
        with self.assertRaisesRegex(ValueError,"standard"):
            adjust_grid_uncertainty({"X1":1.})

    def test_history_record_matches_original_day_in_half_open_interval(self):
        old={"locationStartDate":"2016-01-01",
             "locationEndDate":"2020-01-01","locationCurrent":False,
             "locationUtmEasting":111.0}
        newer={"locationStartDate":"2020-01-01",
               "locationEndDate":None,"locationCurrent":True,
               "locationUtmEasting":222.0}
        self.assertIs(choose_location_at_capture([old,newer],date(2019,12,31)),old)
        self.assertIs(choose_location_at_capture([old,newer],"2020-01-01"),newer)
        self.assertIs(choose_location_at_capture([old,newer],"2026-04-02"),newer)

    def test_history_outside_recorded_coverage_never_uses_newest_by_default(self):
        original={"locationStartDate":"2020-01-01",
                  "locationEndDate":None,"locationCurrent":True}
        with self.assertRaisesRegex(ValueError,"No.*date-valid"):
            choose_location_at_capture([original],"2019-04-01")

    def test_history_overlaps_or_missing_start_fail_closed(self):
        a={"locationStartDate":"2018-01-01","locationEndDate":None}
        b={"locationStartDate":"2019-01-01","locationEndDate":None}
        with self.assertRaisesRegex(ValueError,"Ambiguous"):
            choose_location_at_capture([a,b],"2019-03-02")
        with self.assertRaisesRegex(ValueError,"start"):
            choose_location_at_capture([{"locationEndDate":None}],"2019-03-02")
        with self.assertRaisesRegex(ValueError,"range"):
            choose_location_at_capture([
                {"locationStartDate":"2022-01-01",
                 "locationEndDate":"2020-01-01"}],"2021-01-01")


if __name__=="__main__":
    unittest.main()
