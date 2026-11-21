"""Tests for date FORMAT only, never individual animal timestamps."""
import unittest
from analysis.neon_prairie_vole_date_format_source_v1 import date_pattern,DATES
class DateFormatTests(unittest.TestCase):
    def test_source_patterns_hide_original_dates(self):
        self.assertEqual(date_pattern("2021-12-17"),"####-##-##")
        self.assertEqual(date_pattern("12/14/2021 16:02"),"##/##/#### ##:##")
        self.assertEqual(date_pattern(""),"MISSING")
        self.assertNotIn("2021",date_pattern("2021-12-17"))
    def test_mapped_columns_originate_from_verified_headers(self):
        self.assertIn("datetime",DATES["prox_full_noduplicates.csv"])
        self.assertIn("TimeStart",DATES["rfid_trap_network_data_method.csv"])
        self.assertIn("date_on",DATES["collar_ids.csv"])
if __name__=="__main__":unittest.main()
