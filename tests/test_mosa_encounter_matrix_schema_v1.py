"""Checksum-locked author encounter-matrix structure, no ecology."""
import hashlib
import unittest
from analysis.audit_mosa_encounter_matrix_schema_v1 import parse_encounter_headers

class EncounterSchemaTests(unittest.TestCase):
    def test_comma_index_plus_binary_columns(self):
        raw=b'"","1","2","3"\n"animal1",1,0,1\n"animal2",0,1,0\n'
        r=parse_encounter_headers(raw)
        self.assertEqual(r["rows"],2)
        self.assertEqual(r["columns"],4)
        self.assertTrue(r["first_column_unique"])
        self.assertFalse(r["contains_spatial_coordinates"])

    def test_semicolon_variant(self):
        raw=b'tag;N1;N2\na;1;0\nb;0;1\n'
        r=parse_encounter_headers(raw)
        self.assertEqual(r["delimiter"],"SEMICOLON")
        self.assertEqual(r["rows"],2)
        self.assertTrue(r["first_column_unique"])

    def test_duplicate_primary_identity_warning(self):
        raw=b'tag,N1,N2\na,1,0\na,0,1\n'
        r=parse_encounter_headers(raw)
        self.assertFalse(r["first_column_unique"])
        self.assertEqual(r["first_column_duplicate_rows"],1)

if __name__=="__main__":
    unittest.main()
