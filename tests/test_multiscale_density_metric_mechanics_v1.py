from __future__ import annotations

import unittest

from analysis.validate_multiscale_density_metrics_v1 import (
    centroid_noise_correction,
    debiased_between_variance,
    exact_iid_expectation,
    half_mean_pairwise_squared,
    iid_pair_target,
    observed_between_variance,
    trace_population_denominator_variance,
    trace_unbiased_sample_covariance,
)


class MultiscaleDensityMetricMechanicsTests(unittest.TestCase):
    def test_pairwise_metric_equals_unbiased_covariance_trace(self):
        points = [(0.0, 0.0), (10.0, 0.0), (0.0, 20.0), (10.0, 20.0)]
        self.assertAlmostEqual(
            half_mean_pairwise_squared(points),
            trace_unbiased_sample_covariance(points),
            places=12,
        )

    def test_pairwise_u_statistic_expectation_is_sample_size_invariant(self):
        support = [(0.0, 0.0), (10.0, 0.0), (0.0, 10.0), (10.0, 10.0)]
        target = iid_pair_target(support)
        for m in (2, 3, 4, 5):
            got = exact_iid_expectation(
                support, m, half_mean_pairwise_squared
            )
            self.assertAlmostEqual(got, target, places=12)

    def test_centroid_noise_correction_is_exact_in_iid_benchmark(self):
        true_between = 200.0
        error_support = [(-5.0, 0.0), (5.0, 0.0)]
        observed = []
        correction = []
        debiased = []
        import itertools
        for e in itertools.product(range(2), repeat=4):
            captures = []
            for i, mu in enumerate(((0.0, 0.0), (20.0, 0.0))):
                a = error_support[e[2 * i]]
                b = error_support[e[2 * i + 1]]
                captures.append([
                    (mu[0] + a[0], mu[1] + a[1]),
                    (mu[0] + b[0], mu[1] + b[1]),
                ])
            observed.append(observed_between_variance(captures))
            correction.append(centroid_noise_correction(captures))
            debiased.append(debiased_between_variance(captures))

        self.assertGreater(sum(observed) / len(observed), true_between)
        self.assertGreater(sum(correction) / len(correction), 0.0)
        self.assertAlmostEqual(
            sum(debiased) / len(debiased), true_between, places=12
        )

    def test_denominator_n_variance_has_finite_sample_dependence(self):
        support = [(0.0, 0.0), (10.0, 0.0), (0.0, 10.0), (10.0, 10.0)]
        target = iid_pair_target(support)
        values = [
            exact_iid_expectation(
                support, m, trace_population_denominator_variance
            )
            for m in (2, 3, 4, 5)
        ]
        self.assertTrue(all(v < target for v in values))
        self.assertEqual(values, sorted(values))
        self.assertGreater(values[-1], values[0])


if __name__ == "__main__":
    unittest.main()
