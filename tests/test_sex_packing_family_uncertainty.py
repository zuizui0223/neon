from __future__ import annotations

import unittest

from analysis import audit_sex_packing_family_uncertainty_v1 as m


class FamilyUncertaintyAuditTests(unittest.TestCase):
    def test_large_within_species_error_cannot_vanish_when_points_match(self):
        out=m.equal_weight_random_effects(
            [0.18,0.21,0.18],
            [0.27,0.03,0.09],
        )
        self.assertEqual(out["tau2_method_of_moments"],0.0)
        self.assertGreater(out["standard_error"],0.09)
        self.assertLess(out["ci95_low"],0.0)
        self.assertGreater(out["ci95_high"],0.0)

    def test_between_species_variance_is_retained(self):
        out=m.equal_weight_random_effects(
            [0.50,0.18,0.08],
            [0.07,0.12,0.14],
        )
        self.assertGreater(out["tau2_method_of_moments"],0.0)


if __name__=="__main__":
    unittest.main()
