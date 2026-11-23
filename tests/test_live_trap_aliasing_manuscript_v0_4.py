from __future__ import annotations

# AI assistance disclosure: This test file was drafted or refactored with OpenAI ChatGPT (GPT-5.6 Sol, October 2026); it remains under author responsibility and is verified in repository workflows.

import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANUSCRIPT=ROOT/"MANUSCRIPT_MEE_LIVE_TRAP_ALIASING_V0_4.md"
SUPPLEMENT=ROOT/"SUPPLEMENTARY_METHODS_MEE_LIVE_TRAP_ALIASING_V0_3.md"
CONSEQUENCE=ROOT/"results"/"scr_sigma_consequence_simulation_v1.json"
EMPIRICAL=ROOT/"results"/"san_jacinto_positional_aliasing_result_v1.json"
DENOM=ROOT/"validation"/"live_trap_aliasing_v1"/"denominator_audit_v1.json"
HOME_SUPPORT=ROOT/"validation"/"live_trap_aliasing_v1"/"downstream_home_range_support_summary_v1.json"
CAPTIONS=ROOT/"docs"/"FIGURE_CAPTIONS_V3.md"


class LiveTrapAliasingManuscriptV04Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=MANUSCRIPT.read_text(encoding="utf-8")
        cls.supp=SUPPLEMENT.read_text(encoding="utf-8")
        cls.consequence=json.loads(CONSEQUENCE.read_text())
        cls.emp=json.loads(EMPIRICAL.read_text())
        cls.den=json.loads(DENOM.read_text())
        cls.home=json.loads(HOME_SUPPORT.read_text())
        cls.captions=CAPTIONS.read_text(encoding="utf-8")

    def test_version_title_and_length(self):
        self.assertIn("**Version:** v0.4",self.text)
        self.assertIn("changes spatial scale inference",self.text)
        words=re.findall(r"\b\w+[\w'–-]*\b",self.text)
        self.assertGreaterEqual(len(words),4000)
        self.assertLessEqual(len(words),8500)

    def test_scr_consequence_is_main_result(self):
        self.assertIn("## 2.4 Empirically anchored SCR consequence benchmark",self.text)
        self.assertIn("## 3.1 SCR downstream consequence benchmark",self.text)
        self.assertNotIn("## 3.1 Simulation benchmark",self.text)
        self.assertIn("Diagnostic-estimator simulation benchmark (supplementary)",self.supp)

    def test_empirical_anchor_reproduces_frozen_counts(self):
        a=self.consequence["empirical_anchor"]
        self.assertEqual(a["pooled"]["all_valid_captured_nights"],1520)
        self.assertEqual(a["pooled"]["repeat_capture_nights"],592)
        self.assertEqual(a["pooled"]["changed_repeat_nights"],426)
        self.assertAlmostEqual(a["pooled"]["effective_transition_probability"],0.2803,places=4)
        self.assertEqual(self.emp["species"]["PEMA"]["repeat_capture_nights"],485)
        self.assertEqual(self.emp["species"]["PEER"]["repeat_capture_nights"],107)

    def test_stationary_negative_control_passes(self):
        d=self.consequence["diagnostic_checks"]
        self.assertTrue(d["stationary_null_within_10pct"])
        self.assertLess(d["stationary_max_abs_median_relative_bias"],0.04)
        rows=[
            r for r in self.consequence["paired_contrasts"]
            if r["family"]=="stationary_null"
        ]
        self.assertEqual(len(rows),3)
        for r in rows:
            self.assertLess(abs(r["median_last_first_ratio"]-1),0.05)

    def test_transition_rule_sensitivity_mirrors(self):
        rows=self.consequence["paired_contrasts"]
        post={float(r["sigma_true"]):float(r["median_last_first_ratio"]) for r in rows if r["family"]=="empirical_transition" and r["orientation"]=="POST"}
        pre={float(r["sigma_true"]):float(r["median_last_first_ratio"]) for r in rows if r["family"]=="empirical_transition" and r["orientation"]=="PRE"}
        self.assertGreater(post[6.25],1.3)
        self.assertGreater(post[12.5],1.1)
        self.assertGreater(post[25.0],1.1)
        self.assertLess(pre[6.25],0.8)
        self.assertLess(pre[12.5],0.9)
        self.assertLess(pre[25.0],0.9)
        for token in ("1.347","1.154","1.124","0.766","0.856","0.894"):
            self.assertIn(token,self.supp)

    def test_no_empirical_sigma_effect_is_claimed(self):
        self.assertFalse(self.consequence["diagnostic_checks"]["empirical_real_data_sigma_opened"])
        self.assertIn("No empirical FIRST or LAST SCR sigma estimate was opened",self.text)
        self.assertIn("real-data two-species SCR gate remains stopped",self.supp)

    def test_mcp_stop_is_preserved(self):
        self.assertFalse(self.home["mcp_areas_inspected"])
        self.assertEqual(self.home["eligible_individuals"]["PEMA"],17)
        self.assertEqual(self.home["eligible_individuals"]["PEER"],6)
        self.assertIn("only 17 PEMA and six PEER",self.text)

    def test_denominator_context_is_preserved(self):
        self.assertAlmostEqual(
            self.den["species"]["PEMA"]["observed_one_spacing_aliasing_lower_bound_fraction_all_nights"],
            352/1219,
        )
        self.assertAlmostEqual(
            self.den["species"]["PEER"]["observed_one_spacing_aliasing_lower_bound_fraction_all_nights"],
            74/301,
        )
        self.assertIn("29% and 25%",self.text)

    def test_figure2_caption_is_new_downstream_result(self):
        phrase="Temporal representation changes SCR spatial scale only when the within-night observation process changes state"
        self.assertIn(phrase,self.captions)
        self.assertIn(phrase,self.text)
        self.assertNotIn("Corrected simulation benchmark for informative repeat observation",self.captions)

    def test_check_level_claim_is_bounded(self):
        lower=self.text.lower()
        self.assertIn("within-night encounter dependence",lower)
        self.assertIn("not automatically sufficient",lower)
        self.assertNotIn("check-level analysis is biased",lower)
        self.assertNotIn("check is biased",lower)

    def test_forbidden_overclaims_are_absent(self):
        lower=self.text.lower()
        for phrase in (
            "we show that handling caused",
            "we demonstrate that handling caused",
            "proves home-range bias",
            "first is biologically correct",
            "last is biologically correct",
            "all live-trapping studies are affected",
        ):
            self.assertNotIn(phrase,lower)


if __name__=="__main__":
    unittest.main()
