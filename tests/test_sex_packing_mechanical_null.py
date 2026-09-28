import importlib.util
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"audit_sex_packing_mechanical_null_v1.py"
spec=importlib.util.spec_from_file_location("sexnull",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class SexPackingMechanicalNullTests(unittest.TestCase):
    def test_random_delta_is_deterministic(self):
        traps=np.asarray([(x*6.25,y*6.25) for y in range(7) for x in range(7)],dtype=float)
        a=m.simulate_random_sex_delta(
            traps,
            n_male=3,
            n_female=5,
            sessions=100,
            packing_replicates=199,
            seed=42,
        )
        b=m.simulate_random_sex_delta(
            traps,
            n_male=3,
            n_female=5,
            sessions=100,
            packing_replicates=199,
            seed=42,
        )
        self.assertEqual(a,b)
        self.assertEqual(a["simulated_sessions"],100)
        self.assertAlmostEqual(a["sex_ratio"],3/8)

    def test_summary_reports_sex_ratio_independence(self):
        rows=[
            {"sex_ratio":0.25,"mean_delta":0.01},
            {"sex_ratio":0.40,"mean_delta":-0.02},
            {"sex_ratio":0.50,"mean_delta":0.00},
            {"sex_ratio":0.60,"mean_delta":0.03},
            {"sex_ratio":0.75,"mean_delta":-0.01},
        ]
        out=m.summarize_mechanical_null(rows)
        self.assertIn("spearman_sex_ratio_vs_delta",out)
        self.assertEqual(out["warning_threshold_abs_rho"],0.2)
        self.assertEqual(
            out["passes"],
            abs(out["spearman_sex_ratio_vs_delta"])<=0.2,
        )

    def test_identical_sex_counts_have_zero_expected_direction(self):
        traps=np.asarray([(x*10.0,y*10.0) for y in range(10) for x in range(10)],dtype=float)
        out=m.simulate_random_sex_delta(
            traps,
            n_male=5,
            n_female=5,
            sessions=200,
            packing_replicates=199,
            seed=123,
        )
        self.assertLess(abs(out["mean_delta"]),0.25)


if __name__=="__main__":
    unittest.main()
