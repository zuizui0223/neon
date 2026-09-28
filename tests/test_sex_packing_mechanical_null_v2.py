from __future__ import annotations

import unittest

from analysis import audit_sex_packing_mechanical_null_v2 as m


class SexPackingMechanicalNullV2Tests(unittest.TestCase):
    def test_exact_audit_passes_without_relaxing_threshold(self):
        out=m.audit_standard_geometries()
        self.assertTrue(out["passes"])
        self.assertEqual(out["legacy_warning_threshold_abs_rho"],0.2)
        self.assertFalse(out["ecological_effects_inspected"])
        self.assertEqual(out["ecological_model_fits"],0)
        for geometry in out["geometries"]:
            self.assertTrue(geometry["passes"])
            self.assertEqual(
                geometry["spearman_sex_ratio_vs_expected_delta"],
                0.0,
            )
            self.assertEqual(geometry["mean_expected_delta"],0.0)
            self.assertTrue(
                all(row["expected_delta"]==0.0 for row in geometry["design_points"])
            )


if __name__=="__main__":
    unittest.main()
