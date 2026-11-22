"""Only mock Figshare CSV headers; never inspect original animal response."""
from __future__ import annotations
import unittest
from analysis.run_neon_prairie_vole_figshare_file_headers_v1 import csv_headers_and_nrows,PIN,check_filename_file
class PublishedProximityLoggerSourceTests(unittest.TestCase):
    def test_csv_header_and_row_count(self):
        hdr,n,d=csv_headers_and_nrows(b"animal,contact,count\nx,y,2\na,b,3\n")
        self.assertEqual((hdr,n,d),(["animal","contact","count"],2,","))
    def test_tab_and_semicolon_original_formats(self):
        a,n,d=csv_headers_and_nrows(b"animal;id;date\na;b;2021\n")
        self.assertEqual((n,d),(1,";"))
        a,n,d=csv_headers_and_nrows(b"animal\tid\tdate\na\tb\t2021\n")
        self.assertEqual((n,d),(1,"\t"))
    def test_duplicate_headers_and_ragged_rows_fail_closed(self):
        for src in (b"animal,animal\nx,y\n",b"a,b,c\nx,y\n",b"a\nx\n"):
            with self.assertRaises(ValueError):
                csv_headers_and_nrows(src)
    def test_provider_ids_and_sizes_fixed_before_open(self):
        self.assertEqual(len(PIN),9)
        self.assertEqual(PIN["prox_full_noduplicates.csv"],(27855393,50636655,1973533))
        self.assertEqual(PIN["full_voles_trap.csv"],(27855354,50636346,185698))
    def test_external_host_rejected(self):
        with self.assertRaises(ValueError):
            check_filename_file("https://example.com/files/50636655",50636655,2000000)
if __name__=="__main__":
    unittest.main()
