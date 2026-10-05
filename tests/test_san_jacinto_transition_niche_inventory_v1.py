import unittest

from analysis.inventory_san_jacinto_transition_niche_v1 import summarize_capture_rows


class TestTransitionNicheInventory(unittest.TestCase):
    def test_counts_without_opening_transition_outcomes(self):
        rows = [
            {"species":"A","unique_ID":"1","grid":"g","date":"06/01/2016","time":"8:00","flag":"A1"},
            {"species":"A","unique_ID":"1","grid":"g","date":"06/01/2016","time":"10:00","flag":"A2"},
            {"species":"A","unique_ID":"1","grid":"g","date":"06/01/2016","time":"1:00","flag":"A3"},
            {"species":"B","unique_ID":"2","grid":"g","date":"08/01/2016","time":"8:00","flag":"B1"},
            {"species":"B","unique_ID":"2","grid":"g","date":"08/01/2016","time":"10:00","flag":"B1"},
        ]
        out = summarize_capture_rows(rows)
        self.assertEqual(out["required_capture_columns_missing"], [])
        self.assertEqual(out["species"]["A"]["repeat_capture_nights"], 1)
        self.assertEqual(out["species"]["A"]["consecutive_within_night_transition_count"], 2)
        self.assertEqual(out["species"]["A"]["may_july_2016_consecutive_transition_count"], 2)
        self.assertEqual(out["species"]["B"]["repeat_capture_nights"], 1)
        self.assertEqual(out["species"]["B"]["may_july_2016_consecutive_transition_count"], 0)
        self.assertNotIn("transition_distance", str(out).lower())
        self.assertNotIn("direction", str(out).lower())


if __name__ == "__main__":
    unittest.main()
