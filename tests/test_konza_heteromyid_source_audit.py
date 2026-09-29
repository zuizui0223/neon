from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from analysis import audit_konza_heteromyid_source_v1 as m


class KonzaSourceAuditTests(unittest.TestCase):
    def test_required_schema_passes(self):
        cols=m.REQUIRED_COLUMNS
        text=",".join(cols)+"\n"
        row={c:"" for c in cols}
        row.update({
            "Recyear":"2010","Season":"SP","RecMonth":"3","Recday":"15",
            "TrapDay":"2","Watershed":"004B","Line":"E","Sta":"5",
            "Species":"Ch","Sex":"M","Status":"a","REarTag":"123",
        })
        text+=",".join(str(row[c]) for c in cols)+"\n"
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"CSM012.csv"
            p.write_text(text,encoding="utf-8")
            out=m.audit_file(p)
        self.assertTrue(out["source_adequacy_for_estimability_design"])
        self.assertFalse(out["species_specific_counts_inspected"])
        self.assertFalse(out["sex_specific_counts_inspected"])

    def test_missing_mark_column_fails(self):
        cols=[c for c in m.REQUIRED_COLUMNS if c!="REarTag"]
        text=",".join(cols)+"\n"+",".join("" for _ in cols)+"\n"
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"CSM012.csv"
            p.write_text(text,encoding="utf-8")
            out=m.audit_file(p)
        self.assertFalse(out["source_adequacy_for_estimability_design"])
        self.assertIn("REarTag",out["missing_required_columns"])


if __name__=="__main__":
    unittest.main()
