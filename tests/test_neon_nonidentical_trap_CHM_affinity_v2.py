"""Synthetic-only validation of the canopy clock correction."""
import unittest
from fractions import Fraction
from itertools import product
from unittest.mock import patch
from analysis.neon_nonidentical_trap_CHM_affinity_v1 import TRAPS, rank100, exclusive_score
from analysis.neon_nonidentical_trap_CHM_affinity_v2 import corrected_unit_test
from analysis.neon_proposal_clock_v2 import exact_kernel

def example():
    a = {"g1":{"J1","J2"}, "g2":{"A1","A2"}, "g3":{"F1","F2"}}
    b = {"g1":{"J3","J4"}, "g2":{"A3","A4"}, "g3":{"F3","F4"}}
    h = {t: float(ord(t[0])-65) for t in TRAPS}
    return a,b,h

class CorrectedCanopyClockTests(unittest.TestCase):
    def test_uniform_target_despite_unequal_exit_probabilities(self):
        states = [s for s in product(range(1,16),repeat=3)
                  if tuple(x.bit_count() for x in s)==(1,2,2)
                  and tuple(sum((x>>i)&1 for x in s) for i in range(4))==(2,1,1,1)]
        kernels = {s:exact_kernel(s) for s in states}
        self.assertGreater(len({k.get(s,0) for s,k in kernels.items()}),1)
        for s,k in kernels.items():
            self.assertEqual(sum(k.values()),Fraction(1))
            self.assertTrue(set(k)<=set(states))
            for t in states:
                self.assertEqual(k.get(t,0),kernels[t].get(s,0))
        for t in states:
            self.assertEqual(sum(k.get(t,0) for k in kernels.values()),Fraction(1))

    def test_every_hold_counts_and_no_artificial_mixing(self):
        a,b,h=example()
        with patch("analysis.neon_nonidentical_trap_CHM_affinity_v2.proposal_step",return_value=False) as step:
            out=corrected_unit_test(a,b,h,h,seed=13,n_draws=20,burn=10,thin=3,min_ess=1)
        self.assertEqual(step.call_count,140)
        self.assertEqual(out["proposal_attempts"],140)
        self.assertEqual(out["accepted_moves"],0)
        self.assertEqual(out["status"],"UNINFORMATIVE_ZERO_NULL_VARIANCE")
        self.assertIsNone(out["z"])

    def test_observed_statistic_and_positive_synthetic_signal_unchanged(self):
        a,b,h=example()
        expected,_=exclusive_score(a,b,rank100(h),rank100(h))
        out=corrected_unit_test(a,b,h,h,seed=13,n_draws=500,burn=1000,thin=30,min_ess=10)
        self.assertEqual(out["observed_nonidentical_trap_canopy_affinity_score"],expected)
        self.assertEqual(out["status"],"INFORMATIVE_NONIDENTICAL_TRAP_CANOPY_NULL")
        self.assertGreater(out["z"],0)
        self.assertEqual(out["null_draws"],1000)
        self.assertEqual(out["proposal_attempts"],32000)

    def test_flat_canopy_remains_uninformative(self):
        a,b,h=example()
        out=corrected_unit_test(a,b,{t:0.0 for t in TRAPS},h,seed=13)
        self.assertEqual(out["status"],"UNINFORMATIVE_ONE_CANOPY_HEIGHT")
        self.assertNotIn("z",out)

if __name__=="__main__":
    unittest.main()
