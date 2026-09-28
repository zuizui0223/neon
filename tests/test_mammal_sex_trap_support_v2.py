from __future__ import annotations

import unittest

from analysis import mammal_sex_trap_support_v2 as m


class TrapSupportTests(unittest.TestCase):
    def test_unique_three_per_sex_is_primary_eligible(self):
        rows=[
            {"id":f"M{i}","sex":"M","loc":f"M{i}"}
            for i in range(3)
        ]+[
            {"id":f"F{i}","sex":"F","loc":f"F{i}"}
            for i in range(3)
        ]
        out=m.trap_support_record(
            rows,id_field="id",location_field="loc"
        )
        self.assertTrue(out["trap_support_valid"])
        self.assertTrue(out["support_paired_n3_eligible"])
        self.assertEqual(out["duplicate_location_excess_count"],0)

    def test_duplicate_location_across_sexes_fails_closed(self):
        rows=[
            {"id":"M1","sex":"M","loc":"A1"},
            {"id":"M2","sex":"M","loc":"A2"},
            {"id":"M3","sex":"M","loc":"A3"},
            {"id":"F1","sex":"F","loc":"A1"},
            {"id":"F2","sex":"F","loc":"B2"},
            {"id":"F3","sex":"F","loc":"B3"},
        ]
        out=m.trap_support_record(
            rows,id_field="id",location_field="loc"
        )
        self.assertTrue(out["count_only_paired_n3_eligible"])
        self.assertFalse(out["support_paired_n3_eligible"])
        self.assertEqual(
            out["trap_support_non_estimable_reason"],
            "duplicate_retained_trap_location",
        )

    def test_first_record_per_individual_is_deterministic(self):
        rows=[
            {"id":"x","sex":"M","loc":"A1"},
            {"id":"x","sex":"F","loc":"B1"},
            {"id":"y","sex":"F","loc":"C1"},
        ]
        out=m.trap_support_record(
            rows,id_field="id",location_field="loc"
        )
        self.assertEqual(out["n_total"],2)
        self.assertEqual(out["n_male"],1)
        self.assertEqual(out["n_female"],1)


if __name__=="__main__":
    unittest.main()
