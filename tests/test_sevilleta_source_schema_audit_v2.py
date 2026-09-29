from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from analysis import audit_sevilleta_source_schema_v2 as m


class SevilletaSourceAuditV2Tests(unittest.TestCase):
    def test_valid_name_is_species_not_identity(self):
        self.assertIn("species",m.classify_column("valid_name"))
        self.assertNotIn("identity",m.classify_column("valid_name"))

    def test_exact_id_is_identity(self):
        self.assertIn("identity",m.classify_column("ID"))
        self.assertIn("identity",m.classify_column("tag_id"))

    def test_biotime_like_schema_is_inadequate(self):
        text=(
            "ABUNDANCE,BIOMAS,valid_name,SAMPLE_DESC,LATITUDE,LONGITUDE,DAY,MONTH,YEAR\n"
            "2,40,Dipodomys merriami,x,34,-106,16,5,1999\n"
        )
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"x.csv"
            path.write_text(text,encoding="utf-8")
            out=m.audit_file(path)
        self.assertEqual(out["structural_columns"]["species"],["valid_name"])
        self.assertEqual(out["structural_columns"]["identity"],[])
        self.assertFalse(out["source_adequacy_for_next_estimability_design"])
        self.assertIn("identity",out["missing_required_structural_fields"])
        self.assertIn("sex",out["missing_required_structural_fields"])
        self.assertIn("trap",out["missing_required_structural_fields"])

    def test_full_capture_schema_can_advance(self):
        text=(
            "date,site,web,stake,night,species,sex,tag_id\n"
            "2015-01-01,A,1,12,1,DM,M,T1\n"
        )
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"x.csv"
            path.write_text(text,encoding="utf-8")
            out=m.audit_file(path)
        self.assertTrue(out["source_adequacy_for_next_estimability_design"])


if __name__=="__main__":
    unittest.main()
