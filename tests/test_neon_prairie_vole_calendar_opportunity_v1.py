"""Date parser and active interval gates; no original identity or dyad values."""
from __future__ import annotations
import unittest
from datetime import date
from analysis.neon_prairie_vole_calendar_opportunity_v1 import parse_iso,parse_us,MIN_ADJACENT_DAY_WINDOWS
class TimeSupportTest(unittest.TestCase):
    def test_US_capture_dates_distinct_from_iso_collar_dates(self):
        self.assertEqual(parse_iso("2021-12-14"),date(2021,12,14))
        self.assertEqual(parse_us("12/14/21"),date(2021,12,14))
        with self.assertRaises(ValueError):parse_us("14/12/21")
    def test_source_gate_is_fixed_before_look_at_contacts(self):
        self.assertEqual(MIN_ADJACENT_DAY_WINDOWS,3)
    def test_missing_date_is_a_stop_not_absence(self):
        with self.assertRaises(ValueError):parse_iso("")
if __name__=="__main__":unittest.main()
