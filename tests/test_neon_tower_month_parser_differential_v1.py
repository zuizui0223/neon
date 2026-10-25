"""Synthetic parser-differential diagnostics never reveal source filenames."""
import unittest,json
from analysis.run_neon_tower_month_parser_differential_v1 import safe_parser_profile
from analysis.neon_macro_tower_thermal_contrast_v1 import select_fixed_temperature_file

class TowerParserDifferentialTests(unittest.TestCase):
    def rec(self,suffix:str):
        return {"name":"NEON.D01.PRIVATE_SOURCE.DP1.00002.001.00000.000."+suffix,
                "size":149163,"url":"https://example.test/PRIVATE_SOURCE_FILE",
                "md5":"a"*32}

    def test_expected_numeric_height_suffix_matches(self):
        rec=self.rec("010.030.SAAT_30min.csv")
        selected=select_fixed_temperature_file([rec])
        result=safe_parser_profile(rec,selected)
        self.assertTrue(result["current_exact_three_digit_position_regex_matches"])
        self.assertTrue(result["full_new_parser_selects_a_record"])
        self.assertTrue(result["full_new_parser_same_provider_name_as_pilot"])
        self.assertNotIn("PRIVATE_SOURCE",json.dumps(result))

    def test_strict_regex_rejection_detected_but_not_silently_lost(self):
        rec=self.rec("030.SAAT_30min.csv")
        selected=select_fixed_temperature_file([rec])
        result=safe_parser_profile(rec,selected)
        self.assertFalse(result["current_exact_three_digit_position_regex_matches"])
        self.assertFalse(result["full_new_parser_selects_a_record"])
        self.assertTrue(result["file_contains_explicit_SAAT_30min_table"])
        self.assertTrue(result["no_source_identifier_name_url_or_date_returned"])
        self.assertNotIn("PRIVATE_SOURCE",json.dumps(result))

if __name__=="__main__":
    unittest.main()
