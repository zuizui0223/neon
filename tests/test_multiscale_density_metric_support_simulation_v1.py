from __future__ import annotations

import unittest

from analysis.simulate_multiscale_density_metric_support_v1 import (
    choose_minimum_support,
    run,
)


class MultiscaleDensityMetricSupportSimulationTests(unittest.TestCase):
    def test_receipt_is_deterministic_and_effect_free(self):
        a = run(replicates=20, seed=12345)
        b = run(replicates=20, seed=12345)
        self.assertEqual(a, b)
        self.assertFalse(a["boundary"]["biological_data_read"])
        self.assertFalse(a["boundary"]["density_effects_estimated"])
        self.assertEqual(len(a["cells"]), 12)

    def test_support_rule_chooses_first_all_scenario_pass(self):
        def row(n, q90):
            return {
                "n_repeat_supported_individuals": n,
                "mean_target_b": 100.0,
                "mean_debiased_bias": 1.0,
                "fraction_debiased_b_nonpositive": 0.0,
                "median_absolute_relative_error_debiased": 0.20,
                "q90_absolute_relative_error_debiased": q90,
            }

        cells = [
            row(5, 0.40),
            row(5, 0.60),
            row(10, 0.40),
            row(10, 0.45),
            row(15, 0.30),
            row(15, 0.35),
        ]
        decision = choose_minimum_support(cells)
        self.assertEqual(
            decision["selected_minimum_repeat_supported_individuals"], 10
        )

    def test_debiasing_reduces_mean_bias_at_supported_sample_sizes(self):
        result = run(replicates=300, seed=20261005)
        for cell in result["cells"]:
            if cell["n_repeat_supported_individuals"] < 8:
                continue
            self.assertLess(
                abs(cell["mean_debiased_bias"]),
                abs(cell["mean_raw_bias"]),
            )


if __name__ == "__main__":
    unittest.main()
