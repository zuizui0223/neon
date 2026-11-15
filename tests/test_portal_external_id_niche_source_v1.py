"""Source-only Portal rodent eligibility tests; no ecological effects."""
from __future__ import annotations
import unittest
from analysis.portal_external_id_niche_source_v1 import i,stake,csv_rows
class PortalIdentitySourceTest(unittest.TestCase):
    def test_49_original_stakes_only(self):
        self.assertEqual(stake("11"),11)
        self.assertEqual(stake("77"),77)
        self.assertEqual(stake("54"),54)
        for value in ("08","80","99","0","NA","11.1","71.5",""):
            self.assertIsNone(stake(value))
    def test_missing_values_distinct_from_zero(self):
        self.assertIsNone(i("NA"));self.assertIsNone(i(""))
        self.assertEqual(i("0"),0)
    def test_source_schema_fail_closed(self):
        with self.assertRaises(ValueError):
            csv_rows(b"plot,species,stake\n1,PP,11\n",
                ("year","month","period","plot","stake","species","id"))
    def test_rodent_header(self):
        rows,fields=csv_rows(b"year,month,period,plot,stake,species,id\n2002,4,23,1,11,PP,42\n",
              ("year","month","period","plot","stake","species","id"))
        self.assertEqual(next(rows)["id"],"42")
    def test_duplicate_header_rejected(self):
        with self.assertRaises(ValueError):
            csv_rows(b"year,month,month,plot\n1,1,1,1\n",
                     ("year","month","plot"))
if __name__=="__main__":unittest.main()
