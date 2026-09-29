from __future__ import annotations
import unittest
from analysis import live_trap_home_range_sensitivity_v1 as m
class HomeRangeSensitivityTests(unittest.TestCase):
    def test_square_area(self):
        self.assertAlmostEqual(m.polygon_area([(0,0),(1,0),(1,1),(0,1)]),1.0)
    def test_rms_radius(self):
        self.assertAlmostEqual(m.rms_radius([(0,0),(2,0)]),1.0)
    def test_wilson(self):
        lo,hi=m.wilson(50,100)
        self.assertLess(lo,0.5); self.assertGreater(hi,0.5)
if __name__=="__main__": unittest.main()
