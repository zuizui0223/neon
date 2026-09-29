from __future__ import annotations

import unittest

from analysis import audit_auburn_dordii_estimability_v1 as m


class AuburnParserTests(unittest.TestCase):
    def test_infer_sex_ignores_nonreproductive(self):
        self.assertEqual(m.infer_sex(age="adult",condition="scrotal"),"M")
        self.assertEqual(m.infer_sex(age="adult",condition="non-scrotal"),"M")
        self.assertEqual(m.infer_sex(age="adult",condition="lactating"),"F")
        self.assertEqual(
            m.infer_sex(age="adult",condition="post-lactating, estrus"),
            "F",
        )
        self.assertIsNone(
            m.infer_sex(age="adult",condition="non-reproductive")
        )
        self.assertIsNone(
            m.infer_sex(age="subadult",condition="scrotal")
        )

    def test_trap_grid_coordinates(self):
        self.assertEqual(m.trap_xy("A1"),(0.0,0.0))
        self.assertEqual(m.trap_xy("A10"),(90.0,0.0))
        self.assertEqual(m.trap_xy("J1"),(0.0,90.0))
        self.assertEqual(m.trap_xy("J10"),(90.0,90.0))

    def test_parse_minimal_appendix2_record(self):
        text=(
            "Appendix 2.  Captures of small mammals\n"
            "Summer 2006\n"
            "A1 D. ordii ? adult scrotal 74 910 X X -\n"
            "A5 D. ordii\n"
            "?\n"
            "adult lactating 61 911 X - X\n"
            "Appendix 3.  Number of burrows used\n"
        )
        rows=m.parse_appendix2(text)
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]["sex_inferred"],"M")
        self.assertEqual(rows[1]["sex_inferred"],"F")
        self.assertEqual(rows[1]["tag_id"],"911")

    def test_parse_minimal_appendix4_record(self):
        text=(
            "Appendix 4.  Distances between burrows\n"
            "Summer 2006\n"
            "911 ad\n?\nlactating 61 3 4 bur 1-2 21.1 y\n"
            "103 ad ? scrotal 66 2 2 bur 1-2 18.0 y\n"
            "Appendix 5.  Captures and observations\n"
        )
        rows=m.parse_appendix4(text)
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]["id"],"911")
        self.assertEqual(rows[0]["sex_inferred"],"F")
        self.assertEqual(rows[0]["burrows_4n"],3)
        self.assertEqual(rows[1]["sex_inferred"],"M")


if __name__=="__main__":
    unittest.main()
