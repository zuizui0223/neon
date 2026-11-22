"""Source-only Figshare raw file header/row count tests, no animal records."""
from __future__ import annotations
import unittest
from analysis.neon_prairie_vole_verified_raw_schema_v1 import PIN,header_and_shape
class OriginalVoleSensorCSVTests(unittest.TestCase):
    def test_exact_raw_sources_present(self):
        for name in ("prox_full_noduplicates.csv","full_voles_trap.csv",
                     "collar_ids.csv","global_ids.csv"):
            self.assertIn(name,PIN)
            self.assertEqual(len(PIN[name][2]),32)
    def test_no_animal_content_exported(self):
        s=header_and_shape(b"animal,time,event\nz,12:10,1\nx,12:20,0\n")
        self.assertEqual(s["column_names"],["animal","time","event"])
        self.assertEqual(s["source_data_rows"],2)
        self.assertEqual(s["ragged_rows"],0)
    def test_nonunique_headers_fail(self):
        with self.assertRaises(ValueError):
            header_and_shape(b"tag,time,tag\n1,2,3\n")
    def test_ragged_row_exposed(self):
        self.assertEqual(header_and_shape(b"a,b\n1,2,3\n")["ragged_rows"],1)
if __name__=="__main__":unittest.main()
