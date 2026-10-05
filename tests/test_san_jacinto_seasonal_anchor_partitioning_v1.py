import unittest

from analysis.test_san_jacinto_seasonal_anchor_partitioning_v1 import (
    c_score,
    prepare_dataset,
    prepare_units,
    seasonal_anchor,
)


class TestSeasonalAnchorPartitioning(unittest.TestCase):
    def test_anchor_medoid_uses_nightly_first_locations(self):
        self.assertEqual(seasonal_anchor(["A1", "A1", "A3"]), "A1")
        self.assertEqual(seasonal_anchor(["A1", "A3"]), "A1")

    def test_cscore(self):
        x = {
            "A": {"A1", "A2"},
            "B": {"A2", "A3"},
            "C": {"G7"},
        }
        self.assertAlmostEqual(c_score(x, ("A", "B", "C")), 5 / 3)

    def test_later_within_night_records_do_not_enter_anchor(self):
        rows = [
            {"species":"CHFA","unique_ID":"i1","grid":"1","date":"06/01/2016","time":"8:00","flag":"A1"},
            {"species":"CHFA","unique_ID":"i1","grid":"1","date":"06/01/2016","time":"10:00","flag":"G7"},
            {"species":"CHFA","unique_ID":"i1","grid":"1","date":"06/02/2016","time":"8:00","flag":"A1"},
            {"species":"DKR","unique_ID":"i2","grid":"1","date":"06/01/2016","time":"8:00","flag":"C3"},
            {"species":"LAPM","unique_ID":"i3","grid":"1","date":"06/01/2016","time":"8:00","flag":"E5"},
        ]
        anchors, all_capture = prepare_dataset(rows)
        chfa = [a for a in anchors if a["species"] == "CHFA"][0]
        self.assertEqual(chfa["anchor_flag"], "A1")
        self.assertEqual(chfa["night_count"], 2)
        self.assertIn("G7", all_capture[("1", "summer")]["CHFA"])
        units = prepare_units(anchors, all_capture)
        self.assertEqual(len(units), 1)
        self.assertEqual(units[0]["species"], ("CHFA", "DKR", "LAPM"))


if __name__ == "__main__":
    unittest.main()
