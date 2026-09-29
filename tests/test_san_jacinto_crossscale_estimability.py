from __future__ import annotations

import unittest

from analysis import san_jacinto_crossscale_estimability_v1 as m


class SanJacintoEstimabilityTests(unittest.TestCase):
    def test_nocturnal_time_order(self):
        self.assertLess(m.parse_nocturnal_time("10:30"),m.parse_nocturnal_time("12:30"))
        self.assertLess(m.parse_nocturnal_time("12:30"),m.parse_nocturnal_time("2:00"))
        self.assertLess(m.parse_nocturnal_time("2:00"),m.parse_nocturnal_time("5:00"))

    def test_global_bouts_split_on_large_gap(self):
        rows=[
            {"date":"8/1/15"},{"date":"8/2/15"},{"date":"8/3/15"},
            {"date":"9/1/15"},{"date":"9/2/15"},
        ]
        mapping,summary=m.build_bouts(rows)
        self.assertEqual(len(summary),2)
        self.assertEqual(mapping["2015-08-01"],1)
        self.assertEqual(mapping["2015-09-01"],2)

    def test_first_nightly_location_uses_earliest_time(self):
        rows=[]
        # Create 10 monthly bouts to satisfy the frozen structural bout range.
        for month in range(1,11):
            rows.append({
                "date":f"{month}/1/16","time_bin":"early","time":"10:00",
                "grid":"1","flag":"A2","species":"CHFA","unique_ID":f"x{month}",
                "history":"NID","sex":"M",
            })
        # Add same individual with later capture on the first night.
        rows.append({
            "date":"1/1/16","time_bin":"middle","time":"1:00",
            "grid":"1","flag":"B2","species":"CHFA","unique_ID":"x1",
            "history":"R","sex":"",
        })
        states,qc=m.nightly_states(rows)
        state=next(x for x in states if x["unique_ID"]=="x1")
        self.assertEqual(state["flag"],"A2")


if __name__=="__main__":
    unittest.main()
