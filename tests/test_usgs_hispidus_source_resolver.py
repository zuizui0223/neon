from __future__ import annotations

import unittest

from analysis import resolve_usgs_hispidus_source_v1 as m


class UsgsHispidusSourceResolverTests(unittest.TestCase):
    def test_spatial_capture_schema_is_adequate(self):
        cols=["Species","Sex","PIT","Capture Date","Trap Station"]
        out=m._classify_columns(cols)
        self.assertTrue(out["species"])
        self.assertTrue(out["sex"])
        self.assertTrue(out["identity"])
        self.assertTrue(out["capture_time"])
        self.assertTrue(out["trap_or_station"])

    def test_demographic_only_schema_is_inadequate(self):
        raw=(
            b"Species,Sex,PIT,Capture Date,Weight\n"
            b"Chaetodipus hispidus,M,123,2020-01-01,20\n"
        )
        out=m.audit_text_file("x.csv",raw,"text/csv")
        self.assertFalse(out["has_spatial_capture_field"])
        self.assertFalse(out["structurally_adequate_for_estimability_design"])


if __name__=="__main__":
    unittest.main()
