from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANUSCRIPT=ROOT/"MANUSCRIPT_MEE_LIVE_TRAP_ALIASING_V0_2.md"
EMPIRICAL=ROOT/"results"/"san_jacinto_positional_aliasing_result_v1.json"
SIMULATION=ROOT/"results"/"temporal_aliasing_simulation_benchmark_v1.json"
DENOM=ROOT/"validation"/"live_trap_aliasing_v1"/"denominator_audit_v1.json"
HOME_STOP=ROOT/"validation"/"live_trap_aliasing_v1"/"downstream_home_range_stop_v1.json"


class LiveTrapAliasingManuscriptV02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=MANUSCRIPT.read_text(encoding="utf-8")
        cls.emp=json.loads(EMPIRICAL.read_text())
        cls.sim=json.loads(SIMULATION.read_text())
        cls.den=json.loads(DENOM.read_text())
        cls.home=json.loads(HOME_STOP.read_text())

    def test_manuscript_length_is_inside_target_envelope(self):
        words=re.findall(r"\b\w+[\w'–-]*\b",self.text)
        self.assertGreaterEqual(len(words),4000)
        self.assertLessEqual(len(words),8000)

    def test_no_nonprinting_control_characters_remain(self):
        forbidden=[
            (index,ord(char))
            for index,char in enumerate(self.text)
            if ord(char)<32 and char != "\n"
        ]
        self.assertEqual(forbidden,[])

    def test_mathematical_notation_is_well_formed(self):
        required=(
            r"\\delta_{it}",
            r"\\ge",
            r"\\le",
            r"\\frac",
            r"\\sum_{i<j}",
            r"\\beta",
            r"\\operatorname{logit}",
            r"\\texttt{authorize\\_live\\_trap\\_positional\\_aliasing\\_result}",
        )
        for token in required:
            self.assertIn(token,self.text)
        broken=(
            "Kge2",
            "ledelta",
            "2overline{",
            "(ge1)",
            "(ge6.25)",
        )
        for token in broken:
            self.assertNotIn(token,self.text)

    def test_no_placeholder_markers_remain(self):
        upper=self.text.upper()
        for token in ("[CITE","TODO","TBD","PLACEHOLDER"):
            self.assertNotIn(token,upper)

    def test_confirmatory_decision_matches_frozen_result(self):
        self.assertEqual(
            self.emp["programme_gate"]["decision"],
            "authorize_live_trap_positional_aliasing_result",
        )
        self.assertIn("72.6%",self.text)
        self.assertIn("69.2%",self.text)
        self.assertIn("68.4–76.4%",self.text)
        self.assertIn("59.9–77.1%",self.text)

    def test_denominator_language_and_values_are_present(self):
        self.assertIn("28.9%",self.text)
        self.assertIn("24.6%",self.text)
        self.assertIn("lower bound",self.text.lower())
        self.assertAlmostEqual(
            self.den["species"]["PEMA"][
                "observed_one_spacing_aliasing_lower_bound_fraction_all_nights"
            ],
            352/1219,
        )
        self.assertAlmostEqual(
            self.den["species"]["PEER"][
                "observed_one_spacing_aliasing_lower_bound_fraction_all_nights"
            ],
            74/301,
        )

    def test_simulation_failure_mode_is_not_hidden(self):
        s=self.sim["summary"]
        self.assertAlmostEqual(s["mcar_mean_abs_bias"],0.0006264510422274246)
        self.assertAlmostEqual(s["mcar_mean_wilson_coverage"],0.9529166666666667)
        self.assertGreater(s["span_enriched_mean_bias"],0)
        self.assertLess(s["span_depleted_mean_bias"],0)
        self.assertEqual(s["total_lower_bound_violations"],0)
        self.assertIn("informative repeat observation",self.text.lower())

    def test_home_range_nonestimability_is_explicit(self):
        self.assertFalse(self.home["mcp_areas_inspected"])
        self.assertIn("17",self.text)
        self.assertIn("six",self.text.lower())
        self.assertIn("non-estimable",self.text.lower())

    def test_all_four_figures_are_called_out(self):
        for i in range(1,5):
            self.assertIn(f"Figure {i}",self.text)
            self.assertTrue(any((ROOT/"figures").glob(f"figure{i}_*.png")))
            self.assertTrue(any((ROOT/"figures").glob(f"figure{i}_*.pdf")))

    def test_forbidden_overclaims_are_absent(self):
        lower=self.text.lower()
        forbidden=(
            "72.6% of all",
            "69.2% of all",
            "proves home-range bias",
            "all live-trapping studies",
            "first capture is the correct",
            "last capture is the correct",
            "we discovered temporal aggregation",
        )
        for phrase in forbidden:
            self.assertNotIn(phrase,lower)


if __name__=="__main__":
    unittest.main()
