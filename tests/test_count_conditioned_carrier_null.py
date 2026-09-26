import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE_PATH=ROOT/"analysis"/"count_conditioned_carrier_null_v1.py"
spec=importlib.util.spec_from_file_location("ccnull",MODULE_PATH)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class CountConditionedCarrierNullTests(unittest.TestCase):
    def test_complete_graph_probability_one_for_k_ge_two(self):
        nodes=list(range(5))
        edges={(i,j) for i in nodes for j in nodes if i<j}
        self.assertEqual(
            m.count_conditioned_carrier_probability(nodes,2,[edges],replicates=999,seed=1),
            1.0,
        )

    def test_empty_graph_probability_zero(self):
        nodes=list(range(5))
        self.assertEqual(
            m.count_conditioned_carrier_probability(nodes,3,[set()],replicates=999,seed=1),
            0.0,
        )

    def test_path_k2_exact_probability_is_edge_fraction(self):
        nodes=[0,1,2,3]
        edges={(0,1),(1,2),(2,3)}
        # Six possible 2-node subsets, three are edges.
        self.assertEqual(
            m.count_conditioned_carrier_probability(nodes,2,[edges],replicates=999,seed=1),
            0.5,
        )

    def test_multiple_worlds_require_all_worlds(self):
        nodes=[0,1,2]
        world1={(0,1),(1,2)}
        world2={(0,2)}
        self.assertFalse(m.is_carrier({0,1},[world1,world2]))
        self.assertFalse(m.is_carrier({0,2},[world1,world2]))
        self.assertTrue(m.is_carrier({0,1,2},[world1,world2]))

    def test_excess_conditions_on_observed_count(self):
        nodes=[0,1,2,3]
        edges={(0,1),(1,2),(2,3)}
        observed,expected,excess=m.carrier_excess(
            {0,1},nodes,[edges],replicates=999,seed=1
        )
        self.assertEqual(observed,1)
        self.assertEqual(expected,0.5)
        self.assertEqual(excess,0.5)

    def test_seed_is_deterministic_and_species_specific(self):
        a=m.deterministic_seed("TEST","Species alpha")
        b=m.deterministic_seed("TEST","Species alpha")
        c=m.deterministic_seed("TEST","Species beta")
        self.assertEqual(a,b)
        self.assertNotEqual(a,c)

if __name__=="__main__":
    unittest.main()
