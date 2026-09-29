from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from analysis import audit_jornada_smes_source_v1 as m


class JornadaSourceAuditTests(unittest.TestCase):
    def test_capture_table_detected(self):
        text=(
            "year,month,session,site,web,station,species,sex,tag_id\n"
            "2001,10,1,G,2,10,PF,M,A1\n"
        )
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"capture.csv").write_text(text,encoding="utf-8")
            out=m.audit_directory(root)
        self.assertTrue(out["source_adequacy_for_estimability_design"])
        self.assertEqual(out["structurally_adequate_capture_tables"],["capture.csv"])

    def test_aggregated_table_is_not_adequate(self):
        text="year,site,species,abundance\n2001,G,PF,4\n"
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"agg.csv").write_text(text,encoding="utf-8")
            out=m.audit_directory(root)
        self.assertFalse(out["source_adequacy_for_estimability_design"])


if __name__=="__main__":
    unittest.main()
