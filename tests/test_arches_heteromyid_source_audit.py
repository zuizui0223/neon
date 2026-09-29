from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from analysis import audit_arches_heteromyid_source_v1 as m


class ArchesSourceAuditTests(unittest.TestCase):
    def test_capture_schema_detected_without_counts(self):
        text=(
            "Date,Session,Night,Species,Sex,Tag,Station\n"
            "1999-01-01,1,1,DO,M,T1,10\n"
        )
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x.csv"
            p.write_text(text,encoding="utf-8")
            out=m.audit_one(p,"X")
        self.assertTrue(out["adequate_for_estimability_design"])
        self.assertEqual(out["structural_columns"]["identity"],["Tag"])
        self.assertEqual(out["structural_columns"]["trap"],["Station"])

    def test_missing_identity_blocks_next_stage(self):
        text="Date,Species,Sex,Station\n1999-01-01,DO,F,10\n"
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x.csv"
            p.write_text(text,encoding="utf-8")
            out=m.audit_one(p,"X")
        self.assertFalse(out["adequate_for_estimability_design"])
        self.assertFalse(out["required_presence"]["identity"])


if __name__=="__main__":
    unittest.main()
