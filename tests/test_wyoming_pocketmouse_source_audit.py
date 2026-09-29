from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from analysis import audit_wyoming_pocketmouse_source_v1 as m


class WyomingPocketMouseSourceAuditTests(unittest.TestCase):
    def test_full_capture_table_is_adequate(self):
        text=(
            "Date,Site,Grid Point,Species,Sex,PIT Tag,Night\n"
            "2016-06-01,A,A01,PF,M,123,1\n"
        ).encode()
        row=m.audit_table("captures.csv",text)
        self.assertTrue(row["structurally_adequate_capture_table"])

    def test_aggregated_table_is_not_adequate(self):
        text=(
            "Date,Site,Species,Count\n"
            "2016-06-01,A,PF,10\n"
        ).encode()
        row=m.audit_table("summary.csv",text)
        self.assertFalse(row["structurally_adequate_capture_table"])

    def test_zip_audit_does_not_compute_outcomes(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"x.zip"
            with zipfile.ZipFile(path,"w") as zf:
                zf.writestr(
                    "captures.csv",
                    "Date,Site,Grid Point,Species,Sex,PIT Tag,Night\n"
                    "2016-06-01,A,A01,PF,M,123,1\n",
                )
            out=m.audit_zip(path)
        self.assertTrue(out["source_adequacy_for_estimability_design"])
        self.assertFalse(out["species_specific_counts_inspected"])
        self.assertFalse(out["movement_distances_computed"])
        self.assertFalse(out["packing_effects_computed"])


if __name__=="__main__":
    unittest.main()
