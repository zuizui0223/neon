"""Unit tests for the vole individual-location stationarity null (no network)."""
import unittest
from random import Random

from analysis.run_neon_bank_vole_individual_stationarity_null_v1 import (
    fixed_identity_observed_rho,
    stationary_individual_rho,
    percentile95,
)

class TestVoleStationarityNull(unittest.TestCase):
    def test_constant_individual_positions_give_full_pair_rank_stability(self):
        locs = [(0., 0.), (1., 0.), (0., 2.), (3., 4.)]
        animals = [([p, p], [p, p]) for p in locs]
        observed = fixed_identity_observed_rho(locs, locs)
        self.assertAlmostEqual(observed, 1.0, places=12)
        for seed in (3, 17, 123):
            self.assertAlmostEqual(stationary_individual_rho(animals, Random(seed)), 1., places=12)

    def test_same_input_and_seed_are_deterministic(self):
        animals = [
            ([(0., 0.), (1., 0.)], [(1., 0.), (2., 0.)]),
            ([(4., 1.), (5., 2.)], [(5., 1.), (6., 2.)]),
            ([(0., 4.), (0., 5.)], [(1., 4.), (1., 5.)]),
            ([(6., 5.), (5., 4.)], [(6., 4.), (5., 5.)]),
        ]
        a = stationary_individual_rho(animals, Random(12345))
        b = stationary_individual_rho(animals, Random(12345))
        self.assertAlmostEqual(a, b, places=12)
        self.assertTrue(-1.00000001 <= a <= 1.00000001)
        self.assertEqual(animals[0][0], [(0., 0.), (1., 0.)])

    def test_degenerate_sample_never_forced_to_zero(self):
        same = [(0., 0.), (0., 0.), (0., 0.)]
        with self.assertRaises(ValueError):
            fixed_identity_observed_rho(same, same)

    def test_percentile_rule_prespecified(self):
        self.assertEqual(percentile95(list(range(100))), [2, 96])

if __name__ == "__main__":
    unittest.main()
