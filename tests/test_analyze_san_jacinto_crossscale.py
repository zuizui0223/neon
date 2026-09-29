from __future__ import annotations

import unittest

from analysis import analyze_san_jacinto_crossscale_v1 as m


class SanJacintoHierarchicalAnalysisTests(unittest.TestCase):
    def test_family_uncertainty_includes_species_se(self):
        rows=[
            {"species":"A","effect":0.2,"standard_error":0.3},
            {"species":"B","effect":0.2,"standard_error":0.3},
            {"species":"C","effect":0.2,"standard_error":0.3},
            {"species":"D","effect":0.2,"standard_error":0.3},
        ]
        out=m.family_summary(rows)
        self.assertGreater(out["standard_error"],0.0)
        self.assertLess(out["ci95_low"],0.2)
        self.assertGreater(out["ci95_high"],0.2)

    def test_propagation_has_priority_when_both_directional_pass(self):
        endpoint={"directional_gate":{"passed":True}}
        eq={"passed":True}
        out=m.final_decision(endpoint,endpoint,eq)
        self.assertEqual(
            out["decision"],
            "authorize_crossscale_propagation_manuscript",
        )

    def test_decoupling_requires_movement_and_equivalence(self):
        packing={"directional_gate":{"passed":False}}
        movement={"directional_gate":{"passed":True}}
        eq={"passed":True}
        out=m.final_decision(packing,movement,eq)
        self.assertEqual(
            out["decision"],
            "authorize_crossscale_decoupling_manuscript",
        )

    def test_no_movement_confirmation_stops(self):
        packing={"directional_gate":{"passed":False}}
        movement={"directional_gate":{"passed":False}}
        eq={"passed":True}
        out=m.final_decision(packing,movement,eq)
        self.assertEqual(out["decision"],"stop_no_confirmatory_crossscale_result")


if __name__=="__main__":
    unittest.main()
