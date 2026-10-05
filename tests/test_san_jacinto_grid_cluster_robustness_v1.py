import unittest
from analysis.audit_san_jacinto_grid_cluster_robustness_v1 import exact_signflip, grid_means

class TestGridClusterRobustness(unittest.TestCase):
    def test_grid_means_equal_weight_seasons_within_grid(self):
        rows=[{"grid":"1","z":1.0},{"grid":"1","z":3.0},{"grid":"2","z":-1.0}]
        self.assertEqual(grid_means(rows,"z"),{"1":2.0,"2":-1.0})

    def test_exact_signflip(self):
        out=exact_signflip([1.0,2.0])
        self.assertEqual(out["sign_patterns"],4)
        self.assertAlmostEqual(out["observed_mean_grid_cluster_statistic"],1.5)
        self.assertAlmostEqual(out["exact_one_sided_p_upper"],0.25)

if __name__=="__main__":
    unittest.main()
