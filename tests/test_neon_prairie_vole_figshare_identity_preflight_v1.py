"""Pure source-format checks for different animal-ID namespaces."""
from __future__ import annotations
import unittest
from datetime import date
from analysis.run_neon_prairie_vole_figshare_identity_preflight_v1 import (
    FROZEN_ORIGINAL_MD5,FIELDS,ORIGINAL_ROWS,ident,time_date
)
class OriginalPrairieVoleJoinSourceTests(unittest.TestCase):
    def test_pinned_original_files_have_frozen_sizes_and_headers(self):
        self.assertEqual(len(FROZEN_ORIGINAL_MD5),6)
        self.assertEqual(ORIGINAL_ROWS["prox_full_noduplicates.csv"],50741)
        self.assertEqual(ORIGINAL_ROWS["full_voles_trap.csv"],4454)
        self.assertIn("c1",FIELDS["prox_full_noduplicates.csv"])
        self.assertIn("tag",FIELDS["collar_ids.csv"])
        for name,md5 in FROZEN_ORIGINAL_MD5.items():
            self.assertEqual(len(md5),32)
    def test_exact_id_namespace_is_not_numeric_relabelled(self):
        self.assertEqual(ident("  001  "),"001")
        self.assertEqual(ident("1"),"1")
        self.assertNotEqual(ident("001"),ident("1"))
        self.assertEqual(ident(None),"")
    def test_only_explicit_date_formats(self):
        self.assertEqual(time_date("2021-12-20 15:12:01"),date(2021,12,20))
        self.assertEqual(time_date("2022-01-05T12:32:33Z"),date(2022,1,5))
        self.assertEqual(time_date("12/20/2021"),date(2021,12,20))
        self.assertEqual(time_date("12/20/21 02:15"),date(2021,12,20))
    def test_missing_unrecognized_dates_are_not_silent_zero(self):
        self.assertIsNone(time_date(""))
        self.assertIsNone(time_date("NA"))
        self.assertIsNone(time_date("2021/35/12"))
if __name__=="__main__":
    unittest.main()
