import unittest
from fractions import Fraction
from analysis.run_neon_poland_density_stage_v1 import parse,pair,stage,observations
from collections import Counter
class PolandStageTests(unittest.TestCase):
    def test_semicolon_decimal_comma(self):
        sep,h,rows=parse(b"year;abundance;distance\n2020;5;1,25\n2021;6;2,3\n")
        self.assertEqual(sep,";");self.assertEqual(rows[0][2],"1,25")
    def test_exact_decomposition_and_missing_bounds(self):
        lo=Counter(offered=80,mouse_removed=20,cache=10,missing=5)
        hi=Counter(offered=80,mouse_removed=60,cache=12,missing=20)
        v=pair(lo,hi)
        self.assertEqual(v["recorded_cache_per_offered_RD"],Fraction(2,80))
        self.assertGreater(v["harvest_component"],0)
        self.assertLess(v["post_harvest_component"],0)
        self.assertEqual(v["harvest_component"]+v["post_harvest_component"],v["recorded_cache_per_offered_RD"])
        self.assertLess(v["cache_RD_lower"],0)
        self.assertGreater(v["cache_RD_upper"],0)
    def test_no_invented_context(self):
        with self.assertRaises(ValueError):observations(["year","site","day"],[[2020,"a",1]])
if __name__=="__main__":unittest.main()
