from __future__ import annotations

import unittest

from analysis import san_jacinto_crossscale_effects_v1 as m


class SanJacintoEffectExtractionTests(unittest.TestCase):
    def base_rows(self):
        rows=[]
        # Ten monthly bouts so the frozen bout validator accepts the fixture.
        for month in range(1,11):
            rows.append({
                "date":f"{month}/1/16","time_bin":"early","time":"10:00",
                "grid":"1","flag":"A1","species":"CHFA",
                "unique_ID":f"x{month}","history":"NID","sex":"M",
            })
        return rows

    def test_first_selection_matches_frozen_estimability(self):
        rows=self.base_rows()
        rows.append({
            "date":"1/1/16","time_bin":"middle","time":"1:00",
            "grid":"1","flag":"B2","species":"CHFA",
            "unique_ID":"x1","history":"R","sex":"",
        })
        first,_=m.nightly_states_selection(rows,selection="first")
        state=next(x for x in first if x["unique_ID"]=="x1")
        self.assertEqual(state["flag"],"A1")

    def test_last_selection_uses_latest_nocturnal_capture(self):
        rows=self.base_rows()
        rows.append({
            "date":"1/1/16","time_bin":"middle","time":"1:00",
            "grid":"1","flag":"B2","species":"CHFA",
            "unique_ID":"x1","history":"R","sex":"",
        })
        last,_=m.nightly_states_selection(rows,selection="last")
        state=next(x for x in last if x["unique_ID"]=="x1")
        self.assertEqual(state["flag"],"B2")

    def test_zero_movement_is_retained(self):
        items=[
            {"date":"2016-01-01","flag":"A1","row_index":0},
            {"date":"2016-01-02","flag":"A1","row_index":1},
        ]
        self.assertEqual(m.individual_movement_value(items),0.0)

    def test_elapsed_days_standardize_gap(self):
        near=[
            {"date":"2016-01-01","flag":"A1","row_index":0},
            {"date":"2016-01-02","flag":"A2","row_index":1},
        ]
        gap=[
            {"date":"2016-01-01","flag":"A1","row_index":0},
            {"date":"2016-01-03","flag":"A2","row_index":1},
        ]
        self.assertGreater(
            m.individual_movement_value(near),
            m.individual_movement_value(gap),
        )


if __name__=="__main__":
    unittest.main()
