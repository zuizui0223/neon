from __future__ import annotations

import unittest

from analysis import san_jacinto_intranight_aliasing_v1 as m


class IntranightAliasingTests(unittest.TestCase):
    def test_wilson_interval(self):
        lo,hi=m.wilson_interval(50,100)
        self.assertLess(lo,0.5)
        self.assertGreater(hi,0.5)
        self.assertGreater(lo,0.39)

    def test_distance_one_spacing(self):
        self.assertAlmostEqual(m.distance_m("A1","A2"),6.25)

    def test_gate_requires_all_conditions(self):
        summary={
            "changed_fraction":0.5,
            "changed_fraction_ci95_low":0.4,
            "changed_distance_median_m":6.25,
            "repeat_capture_nights":100,
            "grid_count":2,
            "bout_count":6,
        }
        self.assertTrue(m.evaluate(summary)["passed"])
        summary["changed_fraction_ci95_low"]=0.2
        self.assertFalse(m.evaluate(summary)["passed"])


if __name__=="__main__":
    unittest.main()
