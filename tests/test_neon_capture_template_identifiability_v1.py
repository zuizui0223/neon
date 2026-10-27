"""Exact checks for source-free two-genus observation-template counterexample."""
import math
import unittest
from itertools import combinations

from analysis.neon_capture_template_identifiability_v1 import (
    observation_only_counterexample, reference_sweep
)
from analysis.neon_exact_two_row_fixedmargin_v1 import two_row_exact_marginal


class ObservationOnlyFixedMarginTests(unittest.TestCase):
    def test_no_bias_matches_uniform_fixed_margin_null(self):
        for m, a, h in ((10, 5, 5), (20, 3, 7), (100, 50, 50)):
            v = observation_only_counterexample(
                stations=m, genus1_stations=a, high_preference_stations=h,
                high_to_low_log_relative_odds=0.0
            )
            self.assertAlmostEqual(v["observation_only_expected_z"], 0, places=10)
            self.assertAlmostEqual(v["genus1_record_probability_high"], a / m, places=10)

    def test_full_weighted_subset_enumeration(self):
        m, a, h, beta = 8, 4, 4, 1.25
        states = list(combinations(range(m), a))
        weights = [math.exp(beta * sum(i < h for i in sub)) for sub in states]
        total = sum(weights)
        p = [sum(w for sub, w in zip(states, weights) if i in sub) / total for i in range(m)]
        expected = sum(pi*pi+(1-pi)*(1-pi) for pi in p)
        v = observation_only_counterexample(
            stations=m, genus1_stations=a, high_preference_stations=h,
            high_to_low_log_relative_odds=beta
        )
        self.assertAlmostEqual(v["observation_only_expected_overlap"], expected, places=11)
        self.assertAlmostEqual(v["genus1_record_probability_high"], p[0], places=11)
        self.assertAlmostEqual(v["genus1_record_probability_low"], p[-1], places=11)

    def test_uniform_null_moments_equal_full_enumeration(self):
        m, a = 8, 4
        A = set(range(a))
        overlaps = [m-2*a+2*len(A & set(sub)) for sub in combinations(range(m), a)]
        mean = sum(overlaps) / len(overlaps)
        sd = math.sqrt(sum((x-mean)**2 for x in overlaps) / len(overlaps))
        v = observation_only_counterexample(
            stations=m, genus1_stations=a, high_preference_stations=4,
            high_to_low_log_relative_odds=0.0
        )
        self.assertAlmostEqual(v["uniform_fixed_margin_overlap_mean"], mean, places=12)
        self.assertAlmostEqual(v["uniform_fixed_margin_overlap_sd"], sd, places=12)

    def test_matches_existing_neon_exact_two_row_null_special_case(self):
        traps = [f"A{j}" for j in range(1, 11)]
        A = {"G1": set(traps[:5]), "G2": set(traps[5:])}
        B = {"G1": set(traps[:5]), "G2": set(traps[5:])}
        original_exact = two_row_exact_marginal(A, B)
        synthetic = observation_only_counterexample(
            stations=10, genus1_stations=5, high_preference_stations=5,
            high_to_low_log_relative_odds=0.0
        )
        self.assertEqual(original_exact["n_singleton_columns"], 10)
        self.assertAlmostEqual(original_exact["null_mean"], synthetic["uniform_fixed_margin_overlap_mean"])
        self.assertAlmostEqual(original_exact["null_sd"], synthetic["uniform_fixed_margin_overlap_sd"])

    def test_stable_observer_heterogeneity_creates_positive_z_no_memory(self):
        sweep = reference_sweep()["illustrations"]
        zs = [v["observation_only_expected_z"] for v in sweep]
        self.assertAlmostEqual(zs[0], 0, places=11)
        self.assertTrue(all(x < y for x, y in zip(zs, zs[1:])))
        self.assertAlmostEqual(zs[2], 0.6089711991041921, places=9)
        self.assertTrue(all(not v["between_season_true_use_memory_introduced"] for v in sweep))
        self.assertTrue(all(v["neon_capture_rows_read"] == 0 for v in sweep))

    def test_invalid_parameters_stop(self):
        for m, a, h, beta in ((4,0,2,0),(8,8,3,0),(8,3,8,0),(8,3,4,float("nan"))):
            with self.assertRaises(ValueError):
                observation_only_counterexample(
                    stations=m, genus1_stations=a, high_preference_stations=h,
                    high_to_low_log_relative_odds=beta
                )


if __name__ == "__main__":
    unittest.main()
