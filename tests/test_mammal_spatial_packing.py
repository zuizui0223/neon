import importlib.util
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"mammal_spatial_packing_v1.py"
spec=importlib.util.spec_from_file_location("packing",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MammalSpatialPackingTests(unittest.TestCase):
    def test_mean_pairwise_distance_two_points(self):
        xy=np.array([[0.0,0.0],[3.0,4.0]])
        self.assertAlmostEqual(m.mean_pairwise_distance(xy),5.0)

    def test_mean_pairwise_distance_three_points(self):
        xy=np.array([[0.0,0.0],[3.0,0.0],[0.0,4.0]])
        self.assertAlmostEqual(m.mean_pairwise_distance(xy),(3+4+5)/3)

    def test_exact_null_enumerates_small_combination_space(self):
        traps=np.array([[0.,0.],[1.,0.],[2.,0.],[3.,0.]])
        out=m.packing_null(traps,2,replicates=999,seed=7)
        self.assertEqual(out["mode"],"exact")
        self.assertEqual(out["draw_count"],6)
        self.assertAlmostEqual(out["mean"],10/6)

    def test_monte_carlo_null_is_deterministic(self):
        traps=np.array([[float(i),0.] for i in range(60)])
        a=m.packing_null(traps,5,replicates=999,seed=123)
        b=m.packing_null(traps,5,replicates=999,seed=123)
        self.assertEqual(a,b)
        self.assertEqual(a["mode"],"monte_carlo")
        self.assertEqual(a["draw_count"],999)

    def test_n_greater_than_active_traps_raises(self):
        traps=np.array([[0.,0.],[1.,0.]])
        with self.assertRaises(ValueError):
            m.packing_null(traps,3,replicates=999,seed=1)

    def test_packing_score_marks_too_few_individuals_non_estimable(self):
        obs=np.array([[0.,0.]])
        traps=np.array([[0.,0.],[1.,0.],[2.,0.]])
        out=m.packing_score(obs,traps,replicates=999,seed=1)
        self.assertFalse(out["estimable"])
        self.assertEqual(out["non_estimable_reason"],"fewer_than_two_individuals")
        self.assertIsNone(out["packing_z"])

    def test_packing_score_marks_zero_null_variance_non_estimable(self):
        # With N == active traps, every random sample is the same geometry.
        obs=np.array([[0.,0.],[1.,0.],[2.,0.]])
        traps=obs.copy()
        out=m.packing_score(obs,traps,replicates=999,seed=1)
        self.assertFalse(out["estimable"])
        self.assertEqual(out["non_estimable_reason"],"zero_null_variance")
        self.assertIsNone(out["packing_z"])

    def test_packing_score_returns_negative_for_clustered_observation(self):
        traps=np.array([[0.,0.],[1.,0.],[2.,0.],[10.,0.],[20.,0.]])
        obs=np.array([[0.,0.],[1.,0.]])
        out=m.packing_score(obs,traps,replicates=999,seed=2)
        self.assertTrue(out["estimable"])
        self.assertLess(out["packing_z"],0)

    def test_packing_score_from_precomputed_null_matches_direct_score(self):
        traps=np.array([[0.,0.],[1.,0.],[2.,0.],[10.,0.],[20.,0.]])
        obs=np.array([[0.,0.],[1.,0.]])
        null=m.packing_null(traps,2,replicates=999,seed=2)
        cached=m.packing_score_from_null(obs,null)
        direct=m.packing_score(obs,traps,replicates=999,seed=2)
        self.assertEqual(cached["packing_z"],direct["packing_z"])
        self.assertEqual(cached["mpd_null_mean"],direct["mpd_null_mean"])
        self.assertEqual(cached["mpd_null_sd"],direct["mpd_null_sd"])
        self.assertEqual(cached["null_mode"],direct["null_mode"])
        self.assertEqual(cached["null_draw_count"],direct["null_draw_count"])


if __name__=="__main__":
    unittest.main()
