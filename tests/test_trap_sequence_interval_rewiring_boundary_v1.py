import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"results"/"trap_sequence_interval_rewiring_summary_v1.json"

class TrapSequenceRewiringBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=json.loads(R.read_text())

    def test_rewiring_not_promoted(self):
        c=self.r["claim_boundary"]
        self.assertFalse(c["temporal_rewiring_supported"])
        self.assertFalse(c["temporal_constancy_proven"])
        self.assertFalse(c["natural_dominance_hierarchy_identified"])
        self.assertFalse(c["causal_competition_identified"])

    def test_focal_interval_uncertainty(self):
        s=self.r["all_complete_bin_nights"]
        q=s["focal_KR_to_LAPM"]
        self.assertAlmostEqual(q["early_middle"]["oe"],0.6290322580645162,places=8)
        self.assertAlmostEqual(q["middle_late"]["oe"],0.8155339805825242,places=8)
        self.assertLess(q["bootstrap95_interval_difference"][0],0)
        self.assertGreater(q["bootstrap95_interval_difference"][1],0)
        self.assertFalse(q["interval_difference_excludes_zero"])
        d=s["dyad_interval_comparison"]
        self.assertEqual(d["n_interval_difference_bootstrap95_excludes_zero"],0)
        self.assertEqual(d["n_interval_difference_bh_q_below_0_1"],0)

    def test_three_night_bout_caveat(self):
        d=self.r["exact_three_night_bouts"]["dyad_interval_comparison"]
        self.assertEqual(d["n_interval_difference_bootstrap95_excludes_zero"],1)
        self.assertEqual(d["n_interval_difference_bh_q_below_0_1"],0)

if __name__=="__main__":
    unittest.main()
