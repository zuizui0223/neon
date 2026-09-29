from __future__ import annotations

import unittest

from analysis import audit_san_jacinto_figshare_source_v1 as m


class SanJacintoSourceAuditTests(unittest.TestCase):
    def test_expected_capture_schema_is_adequate(self):
        cols=["Individual ID","Sex","Species","Grid","Trap Location","Date","Night"]
        s=m.classify(cols)
        self.assertTrue(m.adequate(s))

    def test_missing_sex_blocks_adequacy(self):
        cols=["Individual ID","Species","Grid","Trap Location","Date"]
        s=m.classify(cols)
        self.assertFalse(m.adequate(s))

    def test_trap_location_classifies_as_trap(self):
        self.assertIn("Trap Location",m.classify(["Trap Location"])["trap"])


if __name__=="__main__":
    unittest.main()
