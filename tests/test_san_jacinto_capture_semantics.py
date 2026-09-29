from __future__ import annotations

import unittest

from analysis import audit_san_jacinto_capture_semantics_v1 as m


class SanJacintoSemanticAuditTests(unittest.TestCase):
    def test_unique_slots_and_49_flags_support_geometry(self):
        rows=[]
        for flag in range(1,50):
            rows.append({
                "date":"8/1/2015","time_bin":"early","time":"20:00",
                "grid":"1","flag":str(flag),"species":"CHFA",
                "unique_ID":f"x{flag}","history":"NID","sex":"M",
            })
        # ensure all three time-bin labels exist without duplicating slots
        for i,label in enumerate(("middle","late"),start=50):
            rows.append({
                "date":"8/1/2015","time_bin":label,"time":"22:00",
                "grid":"1","flag":"1","species":"CHFA",
                "unique_ID":f"x{i}","history":"NID","sex":"F",
            })
        out=m.audit_rows(rows)
        self.assertEqual(out["grid_flag_counts"]["1"],49)
        self.assertEqual(out["capture_slot_duplicate_count"],0)
        self.assertTrue(out["geometry_support_compatible"])
        self.assertTrue(out["trap_interval_slot_uniqueness_passed"])

    def test_duplicate_same_interval_flag_is_detected(self):
        base={
            "date":"8/1/2015","time_bin":"early","time":"20:00",
            "grid":"1","flag":"1","species":"CHFA","history":"NID",
        }
        rows=[
            {**base,"unique_ID":"a","sex":"M"},
            {**base,"unique_ID":"b","sex":"F"},
        ]
        out=m.audit_rows(rows)
        self.assertEqual(out["capture_slot_duplicate_count"],1)
        self.assertFalse(out["trap_interval_slot_uniqueness_passed"])

    def test_id_sex_conflict_is_detected(self):
        rows=[
            {"date":"8/1/2015","time_bin":"early","time":"20:00","grid":"1",
             "flag":"1","species":"CHFA","unique_ID":"a","history":"NID","sex":"M"},
            {"date":"8/2/2015","time_bin":"early","time":"20:00","grid":"1",
             "flag":"2","species":"CHFA","unique_ID":"a","history":"R","sex":"F"},
        ]
        out=m.audit_rows(rows)
        self.assertEqual(out["individual_id_sex_conflict_count"],1)


if __name__=="__main__":
    unittest.main()
