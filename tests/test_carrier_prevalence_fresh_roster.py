import importlib.util
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"capture_carrier_prevalence_fresh_roster_v1.py"
spec=importlib.util.spec_from_file_location("roster",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class FreshRosterGeometryTests(unittest.TestCase):
    def setUp(self):
        self.protocol={
            "world_family":{
                "base_lcc_targets":[0.25,0.5,0.75,0.9],
                "adequacy":{
                    "min_largest_weak_component_fraction":0.9,
                    "max_isolated_node_fraction":0.05,
                },
            }
        }

    def test_completed_targets_include_finite_n_adequacy_targets(self):
        targets=m.completed_targets(20,self.protocol)
        self.assertEqual(targets,[0.25,0.5,0.75,0.9,0.95])

    def test_path_worlds_are_nested_and_gate_passes(self):
        # Four nodes equally spaced on a line.
        dist=np.array([
            [0,1,2,3],
            [1,0,1,2],
            [2,1,0,1],
            [3,2,1,0],
        ],dtype=float)
        w=m.worlds("TEST",dist,self.protocol)
        self.assertTrue(w["passed"])
        self.assertGreaterEqual(w["distinct_world_count"],1)
        thresholds=[x["distance_threshold_km"] for x in w["canonical_worlds"]]
        self.assertEqual(thresholds,sorted(thresholds))

    def test_exact_duplicate_adjacencies_are_deduplicated(self):
        dist=np.array([
            [0,1,1],
            [1,0,1],
            [1,1,0],
        ],dtype=float)
        w=m.worlds("TEST",dist,self.protocol)
        self.assertLess(w["distinct_world_count"],w["declared_world_count"])

    def test_biological_response_endpoints_forbidden(self):
        with self.assertRaises(RuntimeError):
            m.get_json("https://data.neonscience.org/api/v0/data/query")


if __name__=="__main__":
    unittest.main()
