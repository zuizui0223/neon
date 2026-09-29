from __future__ import annotations

import unittest

from analysis import san_jacinto_temporal_aliasing_estimability_v1 as m


class TemporalAliasingEstimabilityTests(unittest.TestCase):
    def test_two_digit_year(self):
        self.assertEqual(m.parse_date("8/10/15").isoformat(),"2015-08-10")

    def test_nocturnal_order(self):
        self.assertLess(m.parse_nocturnal_time("10:00"),m.parse_nocturnal_time("1:00"))

    def test_repeat_capture_requires_two_rows_same_night(self):
        # Pure structural logic: two rows with same identity-date survive prepare.
        rows=[]
        for month in range(1,11):
            rows.append({
                "date":f"{month}/1/16","time":"10:00","grid":"1","flag":"A1",
                "species":"PEMA","unique_ID":f"x{month}",
            })
        rows.append({
            "date":"1/1/16","time":"1:00","grid":"1","flag":"A2",
            "species":"PEMA","unique_ID":"x1",
        })
        valid,_=m.prepare(rows)
        same=[
            x for x in valid
            if x["species"]=="PEMA" and x["unique_ID"]=="x1" and x["date"]=="2016-01-01"
        ]
        self.assertEqual(len(same),2)


if __name__=="__main__":
    unittest.main()
