import importlib.util
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"audit_mammal_scale_validity_v1.py"
spec=importlib.util.spec_from_file_location("audit_scale",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MammalScaleValidityTests(unittest.TestCase):
    def test_grid_id_is_sampling_grid_prefix(self):
        self.assertEqual(
            m.grid_id("JORN_001.mammalGrid.mam.A10"),
            "JORN_001.mammalGrid.mam",
        )

    def test_same_grid_pair_fraction(self):
        node_ids=[
            "TEST_001.mammalGrid.mam.A1",
            "TEST_001.mammalGrid.mam.A2",
            "TEST_001.mammalGrid.mam.A3",
            "TEST_002.mammalGrid.mam.A1",
            "TEST_002.mammalGrid.mam.A2",
        ]
        dist=np.array([
            [0,0.01,0.02,1,1],
            [0.01,0,0.015,1,1],
            [0.02,0.015,0,1,1],
            [1,1,1,0,0.01],
            [1,1,1,0.01,0],
        ],dtype=float)
        x=m.same_grid_pair_stats(node_ids,dist,[0.012,0.02])
        self.assertEqual(x["same_grid_pair_count"],4)
        self.assertAlmostEqual(x["within_grid_max_distance_km"],0.02)
        self.assertAlmostEqual(x["thresholds"][0]["adjacent_same_grid_pair_fraction"],0.5)
        self.assertEqual(x["thresholds"][1]["adjacent_same_grid_pair_fraction"],1.0)

    def test_threshold_above_max_grid_diameter_makes_all_same_grid_pairs_adjacent(self):
        node_ids=[
            "TEST_001.mammalGrid.mam.A1",
            "TEST_001.mammalGrid.mam.A2",
        ]
        dist=np.array([[0,0.127],[0.127,0]],dtype=float)
        x=m.same_grid_pair_stats(node_ids,dist,[0.13])
        self.assertEqual(x["thresholds"][0]["adjacent_same_grid_pair_fraction"],1.0)
        self.assertTrue(x["thresholds"][0]["threshold_at_least_within_grid_max"])


if __name__=="__main__":
    unittest.main()
