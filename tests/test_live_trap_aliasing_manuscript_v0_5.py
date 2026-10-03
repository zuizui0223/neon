from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANUSCRIPT=ROOT/"MANUSCRIPT_MEE_LIVE_TRAP_ALIASING_V0_5.md"
PEMA=ROOT/"results"/"san_jacinto_pema_scr_sigma_post_stop_receipt_v1.json"
CONSEQUENCE=ROOT/"results"/"scr_sigma_consequence_simulation_v1.json"
EMPIRICAL=ROOT/"results"/"san_jacinto_positional_aliasing_result_v1.json"
DENOM=ROOT/"validation"/"live_trap_aliasing_v1"/"denominator_audit_v1.json"
HOME=ROOT/"validation"/"live_trap_aliasing_v1"/"downstream_home_range_support_summary_v1.json"


class LiveTrapAliasingManuscriptV05Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=MANUSCRIPT.read_text(encoding="utf-8")
        cls.pema=json.loads(PEMA.read_text())
        cls.consequence=json.loads(CONSEQUENCE.read_text())
        cls.emp=json.loads(EMPIRICAL.read_text())
        cls.den=json.loads(DENOM.read_text())
        cls.home=json.loads(HOME.read_text())

    def test_version_and_core_reframe(self):
        self.assertIn("**Version:** v0.5",self.text)
        self.assertIn("Positional aliasing is a warning condition, not a bias estimate",self.text)
        self.assertIn("Temporal exchangeability and time-reversal limitation",self.text)
        words=re.findall(r"\b\w+[\w'–-]*\b",self.text)
        self.assertGreaterEqual(len(words),4000)
        self.assertLessEqual(len(words),8500)

    def test_pema_post_stop_receipt_matches_manuscript(self):
        p=self.pema["primary_model"]
        self.assertEqual(self.pema["status"],"post_stop_exploratory")
        self.assertEqual(
            self.pema["binding_confirmatory_programme_decision"],
            "stop_scr_sigma_sensitivity_not_estimable",
        )
        self.assertFalse(p["contextual_10pct_threshold_exceeded"])
        self.assertAlmostEqual(p["first"]["sigma_m"],8.8515,places=4)
        self.assertAlmostEqual(p["last"]["sigma_m"],8.5625,places=4)
        self.assertAlmostEqual(p["sigma_ratio_last_first"],0.9673,places=4)
        for token in ("8.8515","8.5625","0.9673","-3.27%"):
            self.assertIn(token,self.text)
        self.assertIn("post-stop exploratory",self.text.lower())
        self.assertIn("remained stopped",self.text.lower())

    def test_heldout_aliasing_remains_confirmatory(self):
        self.assertEqual(self.emp["species"]["PEMA"]["repeat_capture_nights"],485)
        self.assertEqual(self.emp["species"]["PEER"]["repeat_capture_nights"],107)
        self.assertAlmostEqual(self.emp["species"]["PEMA"]["one_spacing_shift_fraction"],352/485)
        self.assertAlmostEqual(self.emp["species"]["PEER"]["one_spacing_shift_fraction"],74/107)
        self.assertIn("72.6%",self.text)
        self.assertIn("69.2%",self.text)

    def test_exchangeability_null_matches_stationary_simulation(self):
        d=self.consequence["diagnostic_checks"]
        self.assertTrue(d["stationary_null_within_10pct"])
        self.assertLess(d["stationary_max_abs_median_relative_bias"],0.04)
        rows=[
            r for r in self.consequence["paired_contrasts"]
            if r["family"]=="stationary_null"
        ]
        self.assertEqual(len(rows),3)
        for r in rows:
            self.assertLess(abs(float(r["median_last_first_ratio"])-1),0.05)
        self.assertIn("1.007",self.text)
        self.assertIn("0.966",self.text)
        self.assertIn("1.025",self.text)

    def test_time_reversal_failure_mode_is_mirrored(self):
        rows=self.consequence["paired_contrasts"]
        post={float(r["sigma_true"]):float(r["median_last_first_ratio"])
              for r in rows if r["family"]=="empirical_transition" and r["orientation"]=="POST"}
        pre={float(r["sigma_true"]):float(r["median_last_first_ratio"])
             for r in rows if r["family"]=="empirical_transition" and r["orientation"]=="PRE"}
        self.assertGreater(post[6.25],1.3)
        self.assertGreater(post[12.5],1.1)
        self.assertGreater(post[25.0],1.1)
        self.assertLess(pre[6.25],0.8)
        self.assertLess(pre[12.5],0.9)
        self.assertLess(pre[25.0],0.9)
        for token in ("1.347","1.154","1.124","0.766","0.856","0.894"):
            self.assertIn(token,self.text)

    def test_denominator_and_mcp_stops_are_preserved(self):
        self.assertAlmostEqual(
            self.den["species"]["PEMA"]["observed_one_spacing_aliasing_lower_bound_fraction_all_nights"],
            352/1219,
        )
        self.assertAlmostEqual(
            self.den["species"]["PEER"]["observed_one_spacing_aliasing_lower_bound_fraction_all_nights"],
            74/301,
        )
        self.assertFalse(self.home["mcp_areas_inspected"])
        self.assertEqual(self.home["eligible_individuals"]["PEMA"],17)
        self.assertEqual(self.home["eligible_individuals"]["PEER"],6)
        self.assertIn("Seventeen PEMA and six PEER",self.text)

    def test_failed_dynamic_benchmark_is_not_rescued(self):
        lower=self.text.lower()
        self.assertIn("negative-control gate failed narrowly",lower)
        self.assertIn("10.22%",self.text)
        self.assertIn("non-zero-shift cells are not promoted",lower)

    def test_forbidden_overclaims_are_absent(self):
        lower=self.text.lower()
        for phrase in (
            "san jacinto positional aliasing biased scr sigma",
            "we show that handling caused",
            "we demonstrate that handling caused",
            "first is biologically correct",
            "last is biologically correct",
            "all live-trapping studies are affected",
            "aliasing necessarily biases",
        ):
            self.assertNotIn(phrase,lower)


if __name__=="__main__":
    unittest.main()
