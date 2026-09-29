from __future__ import annotations

import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from analysis import audit_usgs_hispidus_raw_zip_v2 as m


class UsgsHispidusZipAuditTests(unittest.TestCase):
    def test_spatial_capture_table_can_advance(self):
        csv_text=(
            "Species,Sex,PIT,Capture Date,Trap Station\n"
            "Chaetodipus hispidus,M,123,2020-01-01,A12\n"
        )
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"raw.zip"
            with zipfile.ZipFile(path,"w") as zf:
                zf.writestr("captures.csv",csv_text)
            out=m.audit_zip(path)
        self.assertEqual(out["structurally_adequate_members"],["captures.csv"])
        self.assertTrue(out["source_adequacy_for_estimability_design"])

    def test_tagloss_table_without_location_cannot_advance(self):
        csv_text=(
            "Species,Sex,PIT,Capture Date,Tag Status\n"
            "Chaetodipus hispidus,M,123,2020-01-01,both\n"
        )
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"raw.zip"
            with zipfile.ZipFile(path,"w") as zf:
                zf.writestr("tagloss.csv",csv_text)
            out=m.audit_zip(path)
        self.assertFalse(out["source_adequacy_for_estimability_design"])


if __name__=="__main__":
    unittest.main()
