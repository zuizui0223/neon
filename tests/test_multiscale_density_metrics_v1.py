from __future__ import annotations

import unittest

from analysis.multiscale_density_metrics_v1 import (
    individual_metric,
    parse_standard_trap_coordinate,
    session_metrics,
)


class MultiscaleDensityMetricsTests(unittest.TestCase):
    def test_nominal_grid_parser(self):
        self.assertEqual(parse_standard_trap_coordinate("A1"), (0.0, 0.0))
        self.assertEqual(parse_standard_trap_coordinate("A10"), (0.0, 90.0))
        self.assertEqual(parse_standard_trap_coordinate("J1"), (90.0, 0.0))
        self.assertIsNone(parse_standard_trap_coordinate("X1"))
        self.assertIsNone(parse_standard_trap_coordinate("K1"))

    def test_individual_two_night_metric(self):
        m = individual_metric("i1", [("n1", "A1"), ("n2", "A2")])
        self.assertIsNotNone(m)
        assert m is not None
        self.assertEqual(m.k_nights, 2)
        self.assertAlmostEqual(m.within_variance_m2, 50.0)
        self.assertEqual(m.centroid_m, (0.0, 5.0))

    def test_duplicate_same_night_same_coordinate_collapses(self):
        m = individual_metric(
            "i1",
            [("n1", "A1"), ("n1", "A1"), ("n2", "A2")],
        )
        self.assertIsNotNone(m)
        assert m is not None
        self.assertEqual(m.k_nights, 2)

    def test_same_night_conflicting_coordinates_excludes_individual(self):
        m = individual_metric(
            "i1",
            [("n1", "A1"), ("n1", "A2"), ("n2", "A3")],
        )
        self.assertIsNone(m)

    def test_session_metric_exact_values(self):
        records = {
            "i1": [("n1", "A1"), ("n2", "A3")],
            "i2": [("n1", "C1"), ("n2", "C3")],
            "i3": [("n1", "E1"), ("n2", "E3")],
            "i4": [("n1", "G1"), ("n2", "G3")],
            "i5": [("n1", "I1"), ("n2", "I3")],
        }
        out = session_metrics(records)
        # Each individual moves 20 m along the column axis:
        # W_i = 0.5 * 20^2 = 200 m^2.
        self.assertAlmostEqual(out["W_m2"], 200.0)
        # Centroids lie at row coordinates 0,20,40,60,80 and y=10.
        self.assertAlmostEqual(out["B_observed_m2"], 1000.0)
        # k=2 for each individual, so correction = 200/2 = 100.
        self.assertAlmostEqual(out["centroid_noise_correction_m2"], 100.0)
        self.assertAlmostEqual(out["B_debiased_m2"], 900.0)

    def test_minimum_individual_gate_is_five(self):
        records = {
            f"i{i}": [("n1", "A1"), ("n2", "A2")]
            for i in range(4)
        }
        with self.assertRaises(ValueError):
            session_metrics(records)


if __name__ == "__main__":
    unittest.main()
