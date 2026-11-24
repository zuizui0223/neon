import unittest
from collections import Counter
from fractions import Fraction
from analysis.run_neon_poland_all_rodent_stage_v1 import pair,positive,structure

class PolandAllRodentTests(unittest.TestCase):
    def test_exact_decomposition(self):
        a=Counter(offered=80,harvest=20,cache=10,unlocated=5)
        b=Counter(offered=80,harvest=60,cache=12,unlocated=20)
        v=pair(a,b)
        self.assertEqual(v["recorded_cache_per_offered_RD"],Fraction(2,80))
        self.assertEqual(v["harvest_component"]+v["post_harvest_component"],v["recorded_cache_per_offered_RD"])
        self.assertLess(v["cache_RD_lower"],0)
        self.assertGreater(v["cache_RD_upper"],0)
    def test_na_not_positive(self):
        self.assertFalse(positive("NA"))
        self.assertTrue(positive("1"))
        with self.assertRaises(ValueError):positive("2")
    def test_extra_row_not_a_known_release(self):
        x={"year":"2020","plot":"a","date":"x","day":"1","abundance":"3","removal":"NA","seed_status":"NA","cached":"1","eaten":"NA","surface":"","missing":"NA"}
        with self.assertRaises(ValueError):structure([x])
if __name__=="__main__":unittest.main()
