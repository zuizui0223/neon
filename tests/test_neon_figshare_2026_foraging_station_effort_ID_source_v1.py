"""Synthetic event/site/timestamp source-key integrity without biological data."""
import unittest
from datetime import date

from analysis.audit_neon_figshare_2026_foraging_station_effort_ID_source_v1 import (
    original_day,original_key,original_tag,numerical,REQUIRED_STATION,
)

class Test2026FigshareIndependentDetectorSourceKeys(unittest.TestCase):
    def test_literal_tag_preserves_leading_zero_and_na_missing(self):
        self.assertEqual(original_tag(" 000345 "), "000345")
        for value in ("", "NA", "nan", "N/A", "unknown", "No PIT"):
            self.assertIsNone(original_tag(value))

    def test_source_date_parser_does_not_shift_day(self):
        for value in ("2022-05-07","05/07/2022","2022/05/07","05-07-2022"):
            self.assertEqual(original_day(value),date(2022,5,7))
        self.assertIsNone(original_day("missing"))
        self.assertIsNone(original_day("2022-02-30"))

    def test_exact_source_station_night_no_fuzzy_relabel(self):
        row={"Grid":"G1","Site":"S2","Session":"2","Night":"03"}
        self.assertEqual(original_key(row,("Grid","Site","Session","Night")),
                         ("G1","S2","2","03"))
        self.assertIsNone(original_key({"Grid":"G1","Site":"","Session":"2","Night":"03"},
                                        ("Grid","Site","Session","Night")))
        self.assertNotEqual(original_key(row,("Grid","Site","Session","Night")),
                            ("G1","S2","2","3"))

    def test_seed_availability_source_only_validity(self):
        for field in ("0","1","5.25","0.004"):
            self.assertTrue(numerical(field))
        for field in ("NA","nan","inf","-1",""):
            self.assertFalse(numerical(field))
        self.assertEqual(REQUIRED_STATION,100)

if __name__=="__main__":
    unittest.main()
