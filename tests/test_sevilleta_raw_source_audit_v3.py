from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from analysis import audit_sevilleta_raw_source_v3 as m


class SevilletaRawSourceAuditTests(unittest.TestCase):
    def test_expected_raw_schema_can_advance(self):
        text=(
            "year,season,location,web,trap,night,species,sex,tag,recap\n"
            "2010,1,grass,1,15,1,pefl,M,123,n\n"
        )
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x.csv"
            p.write_text(text,encoding="utf-8")
            out=m.audit(p)
        self.assertTrue(out["source_adequacy_for_estimability_design"])
        self.assertFalse(out["species_specific_counts_inspected"])

    def test_missing_identity_blocks_advance(self):
        text="year,season,location,web,trap,night,species,sex\n2010,1,g,1,2,1,pefl,F\n"
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x.csv"
            p.write_text(text,encoding="utf-8")
            out=m.audit(p)
        self.assertFalse(out["source_adequacy_for_estimability_design"])


if __name__=="__main__":
    unittest.main()
