from __future__ import annotations
import random
import unittest
from analysis import simulate_temporal_aliasing_diagnostic_v1 as m

class TemporalAliasingSimulationTests(unittest.TestCase):
    def test_lower_bound_never_exceeds_latent_fraction(self):
        rng=random.Random(1)
        for beta in (-2,0,2):
            for _ in range(200):
                out=m.one_replicate(rng,n=100,shift_sigma=1,repeat_base=0.5,repeat_beta=beta)
                self.assertFalse(out["lower_bound_exceeds_true"])
    def test_zero_beta_small_bias(self):
        out=m.run_cell(seed=4,replicates=1000,n=500,shift_sigma=1,repeat_base=0.5,repeat_beta=0)
        self.assertLess(abs(out["mean_repeat_conditioned_bias"]),0.02)
    def test_informative_repeat_changes_bias_direction(self):
        high=m.run_cell(seed=5,replicates=400,n=500,shift_sigma=1,repeat_base=0.5,repeat_beta=1)
        low=m.run_cell(seed=6,replicates=400,n=500,shift_sigma=1,repeat_base=0.5,repeat_beta=-1)
        self.assertGreater(high["mean_repeat_conditioned_bias"],0)
        self.assertLess(low["mean_repeat_conditioned_bias"],0)
if __name__=="__main__": unittest.main()
