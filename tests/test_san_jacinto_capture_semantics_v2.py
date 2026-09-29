from __future__ import annotations

import unittest

from analysis import audit_san_jacinto_capture_semantics_v2 as m


class SanJacintoSemanticAuditV2Tests(unittest.TestCase):
    def row(self,**overrides):
        base={
            "date":"8/1/15","time_bin":"early","time":"20:00","grid":"1",
            "flag":"A1","species":"CHFA","unique_ID":"x1","history":"NID","sex":"M",
        }
        base.update(overrides)
        return base

    def test_two_digit_year_is_2015(self):
        self.assertEqual(m.parse_date("8/10/15").isoformat(),"2015-08-10")

    def test_lowercase_flag_normalizes(self):
        rows=[self.row(flag="f6")]
        out=m.audit_rows(rows)
        self.assertEqual(out["noncanonical_flag_row_count"],0)

    def test_multi_individual_slot_is_distinguished(self):
        rows=[
            self.row(unique_ID="a"),
            self.row(unique_ID="b",sex="F"),
        ]
        out=m.audit_rows(rows)
        self.assertEqual(out["duplicate_capture_slot_count"],1)
        self.assertEqual(out["multi_individual_capture_slot_count"],1)
        self.assertEqual(out["same_individual_repeat_slot_count"],0)

    def test_grid_species_identity_sex_conflict(self):
        rows=[
            self.row(unique_ID="a",sex="M"),
            self.row(unique_ID="a",sex="F",date="8/2/15",flag="A2"),
        ]
        out=m.audit_rows(rows)
        self.assertEqual(out["grid_species_identity_sex_conflict_count"],1)


if __name__=="__main__":
    unittest.main()
