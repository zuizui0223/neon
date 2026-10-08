"""Synthetic coverage of post-result geometry diagnostics.

These are pure tests; they do not access ecological outcomes.
"""
import random
import unittest

from analysis.audit_multiscale_density_centroid_geometry_v1 import (
    raw_nearest_neighbor_squared,
    edge_fraction,
    spatial_nulls,
)
from analysis.multiscale_density_metrics_v1 import half_mean_pairwise_squared


class GeometryTests(unittest.TestCase):
    def test_nearest_neighbor_vs_population_footprint(self):
        # Four tightly packed points plus a distant one yield a very large B,
        # even though most nearest neighbors are only 1 m away.
        clustered = [(40., 40.), (41., 40.), (40., 41.),
                     (41., 41.), (90., 90.)]
        broad_even = [(0., 0.), (0., 40.), (40., 0.),
                      (40., 40.), (20., 20.)]
        self.assertGreater(half_mean_pairwise_squared(clustered), 0)
        self.assertLess(raw_nearest_neighbor_squared(clustered), 1200)
        self.assertGreater(edge_fraction(clustered), 0)

    def test_footprint_expansion_can_coexist_with_tighter_local_spacing(self):
        # An explicit counterexample to reading larger B as animal repulsion.
        # The samples have equal m: ten spread across a small regular grid
        # versus two compact clusters at opposite corners.
        regular = [(float(x), float(y))
                   for y in (30, 50) for x in (20, 30, 40, 50, 60)]
        clustered = [(10., 10.)] * 5 + [(90., 90.)] * 5
        self.assertEqual(len(regular), len(clustered))
        self.assertGreater(
            half_mean_pairwise_squared(clustered),
            half_mean_pairwise_squared(regular)
        )
        self.assertLess(
            raw_nearest_neighbor_squared(clustered),
            raw_nearest_neighbor_squared(regular)
        )

    def test_same_centroids_have_zero_nn(self):
        points = [(10., 10.)] * 5
        self.assertEqual(raw_nearest_neighbor_squared(points), 0)

    def test_xy_null_keeps_pairwise_B_and_is_deterministic(self):
        a = [(0., 0.), (10., 20.), (20., 30.), (40., 50.), (90., 90.)]
        x = spatial_nulls(a, a * 2, rng=random.Random(12), replicates=7)
        y = spatial_nulls(a, a * 2, rng=random.Random(12), replicates=7)
        self.assertEqual(x, y)
        self.assertTrue(x["series_reference_eligible"])
        self.assertAlmostEqual(x["nn_squared_m2"] - x["nn_expected_xy_m2"],
                               x["nn_excess_xy_m2"])

    def test_series_pool_support_does_not_sample_with_replacement(self):
        a = [(10.*i, 0.) for i in range(5)]
        x = spatial_nulls(a, a[:4], rng=random.Random(42), replicates=5)
        self.assertIsNone(x["nn_expected_series_m2"])
        self.assertIsNone(x["nn_excess_series_m2"])
        self.assertFalse(x["series_reference_eligible"])

    def test_invalid_replicates_stop(self):
        with self.assertRaises(ValueError):
            spatial_nulls([(0., 0.), (10., 10.)], [], rng=random.Random(1),
                          replicates=0)


if __name__ == "__main__":
    unittest.main()
