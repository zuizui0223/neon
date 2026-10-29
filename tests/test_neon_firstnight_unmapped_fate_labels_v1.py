"""Test original fate token audit privacy, thresholds, and no semantic inference."""
import unittest,json
from analysis.run_neon_firstnight_unmapped_fate_labels_v1 import (
    safe_label,tally_unmapped,
)

class FateUnknownLabelAuditTests(unittest.TestCase):
    def test_repeated_safe_source_labels_visible_as_unmapped_not_released(self):
        arr=["New - released"]*8+["Recapture"]*7+["rare free text"]*2+["EMAIL@HOST"]*5
        r=tally_unmapped(arr,expected=22)
        self.assertEqual(r["n_original_unmapped_source_values"],22)
        self.assertEqual(r["n_original_unmapped_records_in_displayed_token_forms"],15)
        self.assertEqual(r["n_original_unmapped_records_with_literal_suppressed"],7)
        self.assertTrue(all(x["no_release_interpretation_assigned"]
                            for x in r["frequent_safe_original_raw_token_forms"]))
        self.assertNotIn("EMAIL@HOST",json.dumps(r))
        self.assertNotIn("rare free text",json.dumps(r))

    def test_source_like_identifiers_are_never_displayed(self):
        for value in ("SITE_NAME", "FirstnightUID", "tag 876100", "2022-03",
                      "Microtus recapture", "person abc", "email@example.com",
                      "private url http://server"):
            self.assertIsNone(safe_label(value))
        self.assertEqual(safe_label("New - released"),"New - released")
        self.assertEqual(safe_label("Recapture"),"Recapture")

    def test_source_count_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"source-count drift"):
            tally_unmapped(["Unknown"],expected=391)

if __name__=="__main__":
    unittest.main()
