from __future__ import annotations

# AI assistance disclosure: This test file was drafted or refactored with OpenAI ChatGPT (GPT-5.6 Sol, September 2026); it remains under author responsibility and is verified in repository workflows.

import random
import unittest

import numpy as np

from analysis import temporal_aliasing_bounds_v1 as m


class TemporalAliasingBoundsTests(unittest.TestCase):
    def test_movement_bound_is_sharp(self):
        out=m.movement_representative_sensitivity(
            (0.0,),(10.0,),(1.0,),(9.0,)
        )
        self.assertAlmostEqual(out["absolute_difference"],2.0)
        self.assertAlmostEqual(out["bound"],2.0)
        self.assertAlmostEqual(out["slack"],0.0)

    def test_mpd_bound_is_sharp_for_two_points(self):
        first=np.asarray([(0.0,),(10.0,)])
        last=np.asarray([(1.0,),(9.0,)])
        out=m.mpd_representative_sensitivity(first,last)
        self.assertAlmostEqual(out["absolute_difference"],2.0)
        self.assertAlmostEqual(out["bound"],2.0)

    def test_random_euclidean_movement_cases_respect_bound(self):
        rng=random.Random(20260929)
        for _ in range(1000):
            pts=[
                (rng.uniform(-10,10),rng.uniform(-10,10))
                for _ in range(4)
            ]
            out=m.movement_representative_sensitivity(
                pts[0],pts[1],pts[2],pts[3]
            )
            self.assertLessEqual(
                out["absolute_difference"],
                out["bound"]+1e-12,
            )

    def test_random_mpd_cases_respect_bound(self):
        rng=np.random.default_rng(20260929)
        for n in (2,3,5,10,30):
            for _ in range(100):
                first=rng.normal(size=(n,2))
                last=first+rng.normal(scale=0.5,size=(n,2))
                out=m.mpd_representative_sensitivity(first,last)
                self.assertLessEqual(
                    out["absolute_difference"],
                    out["bound"]+1e-12,
                )

    def test_standardized_bound_scales_by_null_sd(self):
        self.assertAlmostEqual(
            m.standardized_packing_sensitivity_bound(3.0,2.0),
            3.0,
        )


if __name__=="__main__":
    unittest.main()
