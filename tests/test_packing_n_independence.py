import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"audit_packing_n_independence_v1.py"
spec=importlib.util.spec_from_file_location("packing_n_audit",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PackingNIndependenceTests(unittest.TestCase):
    def test_regular_grid_geometry(self):
        xy=m.regular_grid_xy(rows=2,cols=3,spacing_m=10.0)
        self.assertEqual(xy.shape,(6,2))
        self.assertEqual(tuple(xy[0]),(0.0,0.0))
        self.assertEqual(tuple(xy[-1]),(20.0,10.0))

    def test_spearman_known_order(self):
        self.assertAlmostEqual(m.spearman([1,2,3],[3,2,1]),-1.0)
        self.assertAlmostEqual(m.spearman([1,2,3],[1,2,3]),1.0)

    def test_simulation_is_deterministic_and_near_independent_of_n(self):
        result=m.audit_geometry(
            label="toy",
            xy=m.regular_grid_xy(rows=4,cols=4,spacing_m=10.0),
            n_values=[3,4,5,6],
            sessions_per_n=60,
            null_replicates=199,
            seed=12345,
        )
        again=m.audit_geometry(
            label="toy",
            xy=m.regular_grid_xy(rows=4,cols=4,spacing_m=10.0),
            n_values=[3,4,5,6],
            sessions_per_n=60,
            null_replicates=199,
            seed=12345,
        )
        self.assertEqual(result,again)
        self.assertLessEqual(abs(result["spearman_n_vs_packing_z"]),0.2)
        self.assertLess(abs(result["mean_packing_z"]),0.2)
        self.assertTrue(result["passes_abs_rho_le_0_2"])


if __name__=="__main__":
    unittest.main()
