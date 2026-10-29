"""Verify public controlled fate codes can be shown without raw source identifiers."""
import unittest
from analysis.run_neon_original_fate_codes_v1 import safe_controlled

class SourceDictionaryFateSafetyTests(unittest.TestCase):
    def test_public_controlled_fate_labels(self):
        self.assertEqual(safe_controlled("released"),"released")
        self.assertEqual(safe_controlled("dead"),"dead")
        self.assertEqual(safe_controlled("New / release"),"New / release")
    def test_do_not_serialize_raw_site_or_tag_identity(self):
        self.assertEqual(safe_controlled("A1/SITE0129"),"WITHHELD_NONCONTROLLED_CODE")
        self.assertEqual(safe_controlled("nightuid secret"),"WITHHELD_NONCONTROLLED_CODE")
        self.assertEqual(safe_controlled("2020-12"),"WITHHELD_NONCONTROLLED_CODE")
    def test_free_text_metadata_not_serialized(self):
        self.assertEqual(safe_controlled("User@site.org"),"WITHHELD_NONCONTROLLED_CODE")

if __name__=="__main__":
    unittest.main()
