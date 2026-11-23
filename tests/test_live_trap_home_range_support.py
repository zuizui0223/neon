from __future__ import annotations
import unittest
from analysis import live_trap_home_range_support_v1 as m
class HomeRangeSupportTests(unittest.TestCase):
    def test_noncollinear(self):
        self.assertTrue(m.noncollinear(["A1","A2","B1"]))
        self.assertFalse(m.noncollinear(["A1","A2","A3","A4","A5"]))
    def test_time_order(self):
        self.assertLess(m.parse_time("10:00"),m.parse_time("1:00"))
if __name__=="__main__": unittest.main()
