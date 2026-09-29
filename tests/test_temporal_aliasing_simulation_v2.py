from __future__ import annotations

import math
import random
import unittest

from analysis import simulate_temporal_aliasing_diagnostic_v2 as m


class TemporalAliasingSimulationV2Tests(unittest.TestCase):
    def test_rayleigh_tail_probability(self):
        self.assertAlmostEqual(
            m.latent_material_probability(1.0),
            math.exp(-0.5),
            places=12,
        )
        self.assertAlmostEqual(
            m.latent_material_probability(0.5),
            math.exp(-2.0),
            places=12,
        )

    def test_wilson_endpoints_are_exact(self):
        self.assertEqual(m.wilson(0,50)[0],0.0)
        self.assertEqual(m.wilson(50,50)[1],1.0)

    def test_lower_bound_never_exceeds_realized_latent_fraction(self):
        rng=random.Random(1)
        for beta in (-2,0,2):
            for _ in range(200):
                out=m.one_replicate(
                    rng,
                    n=100,
                    shift_sigma=1,
                    repeat_base=0.5,
                    repeat_beta=beta,
                )
                self.assertFalse(
                    out["lower_bound_exceeds_realized_latent_fraction"]
                )

    def test_zero_beta_estimates_generating_probability(self):
        out=m.run_cell(
            seed=4,
            replicates=2000,
            n=500,
            shift_sigma=1,
            repeat_base=0.5,
            repeat_beta=0,
        )
        self.assertLess(
            abs(out["mean_repeat_conditioned_bias_vs_probability"]),
            0.02,
        )
        self.assertGreater(
            out["wilson_coverage_latent_probability"],
            0.90,
        )

    def test_informative_repeat_bias_direction(self):
        high=m.run_cell(
            seed=5,replicates=800,n=500,shift_sigma=1,
            repeat_base=0.5,repeat_beta=1,
        )
        low=m.run_cell(
            seed=6,replicates=800,n=500,shift_sigma=1,
            repeat_base=0.5,repeat_beta=-1,
        )
        self.assertGreater(
            high["mean_repeat_conditioned_bias_vs_probability"],0
        )
        self.assertLess(
            low["mean_repeat_conditioned_bias_vs_probability"],0
        )


if __name__=="__main__":
    unittest.main()
