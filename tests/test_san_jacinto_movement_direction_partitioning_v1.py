import unittest

from analysis.test_san_jacinto_movement_direction_partitioning_v1 import (
    build_individual_nights,
    c_score,
    distance_matched_candidates,
    prepare_units,
    season_from_month,
    squared_grid_distance,
)


class TestSanJacintoMovementDirectionPartitioning(unittest.TestCase):
    def test_seasons(self):
        self.assertEqual(season_from_month(9), "fall")
        self.assertEqual(season_from_month(12), "winter")
        self.assertEqual(season_from_month(3), "spring")
        self.assertEqual(season_from_month(6), "summer")

    def test_exact_distance_candidates_preserve_length(self):
        candidates = distance_matched_candidates("D4", "D6")
        self.assertIn("D6", candidates)
        self.assertGreater(len(candidates), 1)
        d2 = squared_grid_distance("D4", "D6")
        self.assertTrue(all(squared_grid_distance("D4", x) == d2 for x in candidates))

    def test_edge_geometry_is_respected(self):
        candidates = distance_matched_candidates("A1", "A3")
        self.assertEqual(set(candidates), {"A3", "C1"})

    def test_cscore(self):
        x = {
            "A": {"A1", "A2"},
            "B": {"A2", "A3"},
            "C": {"G7"},
        }
        # A-B: (2-1)*(2-1)=1; A-C=2; B-C=2 => 5/3
        self.assertAlmostEqual(c_score(x, ("A", "B", "C")), 5 / 3)

    def test_singletons_remain_available_as_fixed_background(self):
        rows = []
        for sp, row in (("CHFA", "A"), ("DKR", "C"), ("LAPM", "E")):
            for i in range(5):
                rows += [
                    {
                        "species": sp,
                        "unique_ID": f"{sp}{i}",
                        "grid": "G1",
                        "date": f"06/{i+1:02d}/2016",
                        "time": "8:00",
                        "flag": f"{row}1",
                    },
                    {
                        "species": sp,
                        "unique_ID": f"{sp}{i}",
                        "grid": "G1",
                        "date": f"06/{i+1:02d}/2016",
                        "time": "10:00",
                        "flag": f"{row}2",
                    },
                ]
            rows.append(
                {
                    "species": sp,
                    "unique_ID": f"{sp}single",
                    "grid": "G1",
                    "date": "06/20/2016",
                    "time": "8:00",
                    "flag": f"{row}7",
                }
            )

        nights = build_individual_nights(rows)
        units = prepare_units(nights)
        self.assertEqual(len(units), 1)
        unit = units[0]
        self.assertEqual(unit["species"], ("CHFA", "DKR", "LAPM"))
        self.assertEqual(len(unit["repeat_rows"]), 15)
        self.assertEqual(len(unit["all_nights"]), 18)
        self.assertEqual(unit["singleton_flags"]["CHFA"], {"A7"})
        self.assertEqual(unit["singleton_flags"]["DKR"], {"C7"})
        self.assertEqual(unit["singleton_flags"]["LAPM"], {"E7"})


if __name__ == "__main__":
    unittest.main()
