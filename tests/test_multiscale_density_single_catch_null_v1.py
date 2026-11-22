from __future__ import annotations

import unittest
import numpy as np

from analysis.simulate_multiscale_density_single_catch_null_v1 import (
    centre_pool,
    detection_probabilities,
    simulate_session,
    trap_label,
)


class SingleCatchNullTests(unittest.TestCase):
    def test_trap_labels_cover_standard_neon_grid(self):
        self.assertEqual(trap_label(0), "A1")
        self.assertEqual(trap_label(9), "A10")
        self.assertEqual(trap_label(90), "J1")
        self.assertEqual(trap_label(99), "J10")

    def test_centre_pools_have_expected_sizes(self):
        self.assertEqual(len(centre_pool("full_10x10")), 100)
        self.assertEqual(len(centre_pool("central_8x8")), 64)

    def test_detection_probabilities_are_normalized(self):
        pool = centre_pool("central_8x8")
        p = detection_probabilities(pool, 12.5)
        self.assertEqual(p.shape, (64, 100))
        self.assertTrue(np.allclose(p.sum(axis=1), 1.0))

    def test_session_outputs_are_bounded(self):
        rng = np.random.default_rng(123)
        pool = centre_pool("central_8x8")
        p = detection_probabilities(pool, 12.5)
        rows = [
            simulate_session(
                rng,
                n_individuals=30,
                pool=pool,
                trap_probs=p,
                p_capture=0.8,
                single_catch=True,
            )
            for _ in range(20)
        ]
        rows = [x for x in rows if x is not None]
        self.assertTrue(rows)
        for row in rows:
            self.assertGreaterEqual(row["repeat_supported_individuals"], 5)
            self.assertGreaterEqual(row["repeat_supported_fraction"], 0.0)
            self.assertLessEqual(row["repeat_supported_fraction"], 1.0)
            self.assertGreaterEqual(row["capture_trap_night_fraction"], 0.0)
            self.assertLessEqual(row["capture_trap_night_fraction"], 1.0)


if __name__ == "__main__":
    unittest.main()
