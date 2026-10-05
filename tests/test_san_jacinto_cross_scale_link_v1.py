import unittest
from analysis.audit_san_jacinto_cross_scale_link_v1 import pearson, grid_means

class TestCrossScaleLink(unittest.TestCase):
    def test_pearson(self):
        self.assertAlmostEqual(pearson([1,2,3],[2,4,6]),1.0)
    def test_grid_means(self):
        rows=[{"grid":"1","footprint_z":1,"community_ses":2},{"grid":"1","footprint_z":3,"community_ses":4},{"grid":"2","footprint_z":5,"community_ses":8}]
        out=grid_means(rows)
        self.assertEqual(out[0]["mean_footprint_z"],2)
        self.assertEqual(out[0]["mean_community_ses"],3)

if __name__=="__main__": unittest.main()
