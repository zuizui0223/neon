import unittest
from analysis.test_neon_footprint_assortativity_v1 import jaccard, exact_signflip_p
class TestNeonFootprintAssortativity(unittest.TestCase):
    def test_jaccard(self):
        self.assertAlmostEqual(jaccard(frozenset({"A1","A2"}),frozenset({"A2","A3"})),1/3)
        self.assertEqual(jaccard(frozenset({"A1"}),frozenset({"B1"})),0)
    def test_signflip(self):
        p=exact_signflip_p([1.0,1.0,1.0])
        self.assertEqual(p,1/8)
if __name__=="__main__": unittest.main()
