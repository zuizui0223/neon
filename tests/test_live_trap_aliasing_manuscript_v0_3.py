from __future__ import annotations

# AI assistance disclosure: This test file was drafted or refactored with OpenAI ChatGPT (GPT-5.6 Sol, September 2026); it remains under author responsibility and is verified in repository workflows.

import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANUSCRIPT=ROOT/"MANUSCRIPT_MEE_LIVE_TRAP_ALIASING_V0_3.md"
SUPPLEMENT=ROOT/"SUPPLEMENTARY_METHODS_MEE_LIVE_TRAP_ALIASING_V0_2.md"
EMPIRICAL=ROOT/"results"/"san_jacinto_positional_aliasing_result_v1.json"
SIMULATION=ROOT/"results"/"temporal_aliasing_simulation_benchmark_v2.json"
DENOM=ROOT/"validation"/"live_trap_aliasing_v1"/"denominator_audit_v1.json"
CLUSTER=ROOT/"validation"/"live_trap_aliasing_v1"/"individual_cluster_sensitivity_v1.json"
HOME_STOP=ROOT/"validation"/"live_trap_aliasing_v1"/"downstream_home_range_stop_v1.json"


class LiveTrapAliasingManuscriptV03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=MANUSCRIPT.read_text(encoding="utf-8")
        cls.supp=SUPPLEMENT.read_text(encoding="utf-8")
        cls.emp=json.loads(EMPIRICAL.read_text())
        cls.sim=json.loads(SIMULATION.read_text())
        cls.den=json.loads(DENOM.read_text())
        cls.cluster=json.loads(CLUSTER.read_text())
        cls.home=json.loads(HOME_STOP.read_text())

    def test_version_and_length(self):
        self.assertIn("**Version:** v0.3",self.text)
        words=re.findall(r"\b\w+[\w'–-]*\b",self.text)
        self.assertGreaterEqual(len(words),4000)
        self.assertLessEqual(len(words),8000)

    def test_no_nonprinting_control_characters(self):
        for name,text in (("manuscript",self.text),("supplement",self.supp)):
            bad=[
                (i,ord(ch))
                for i,ch in enumerate(text)
                if ord(ch)<32 and ch!="\n"
            ]
            self.assertEqual(bad,[],name)

    def test_corrected_simulation_targets_are_frozen(self):
        self.assertEqual(
            self.sim["schema"],
            "temporal_aliasing_diagnostic.simulation_benchmark.v2",
        )
        s=self.sim["summary"]
        self.assertAlmostEqual(
            s["mcar_mean_abs_bias_vs_latent_probability"],
            0.0017558694757951665,
        )
        self.assertAlmostEqual(
            s["mcar_mean_wilson_coverage_latent_probability"],
            0.9520833333333334,
        )
        self.assertAlmostEqual(
            s["mcar_min_wilson_coverage_latent_probability"],
            0.86,
        )
        self.assertGreater(
            s["span_enriched_mean_bias_vs_latent_probability"],0
        )
        self.assertLess(
            s["span_depleted_mean_bias_vs_latent_probability"],0
        )
        self.assertEqual(
            s["total_lower_bound_realized_violations"],0
        )
        for token in ("0.00176","95.2%","86.0%","+0.0507","-0.0799"):
            self.assertIn(token,self.text)
        self.assertNotIn("0.00063",self.text)
        self.assertNotIn("95.3%",self.text)

    def test_simulation_target_language_is_unambiguous(self):
        lower=self.text.lower()
        self.assertIn("analytic generating probability",lower)
        self.assertIn("realized all-occasion material-shift fraction",lower)
        self.assertIn("deterministic lower-bound interpretation",lower)

    def test_confirmatory_empirical_values_match(self):
        self.assertEqual(
            self.emp["programme_gate"]["decision"],
            "authorize_live_trap_positional_aliasing_result",
        )
        for token in ("72.6%","69.2%","68.4–76.4%","59.9–77.1%"):
            self.assertIn(token,self.text)

    def test_denominator_values_match(self):
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
        self.assertIn("28.9%",self.text)
        self.assertIn("24.6%",self.text)

    def test_individual_cluster_robustness_is_non_rescuing_and_correct(self):
        self.assertTrue(self.cluster["primary_result_unchanged"])
        pema=self.cluster["species"]["PEMA"]
        peer=self.cluster["species"]["PEER"]
        self.assertGreater(pema["cluster_bootstrap_ci95_low"],0.25)
        self.assertGreater(peer["cluster_bootstrap_ci95_low"],0.25)
        self.assertEqual(pema["individual_grid_clusters"],170)
        self.assertEqual(peer["individual_grid_clusters"],34)
        for token in ("170 grid-specific individual clusters","34 individual clusters","68.0–77.0%","61.3–78.9%"):
            self.assertIn(token,self.text)

    def test_home_range_nonestimability_is_preserved(self):
        self.assertFalse(self.home["mcp_areas_inspected"])
        self.assertIn("Seventeen PEMA and six PEER",self.text)
        self.assertIn("non-estimable",self.text.lower())

    def test_math_is_clean(self):
        required=(
            "\\delta_{it}","\\ge","\\le","\\frac",
            "\\sum_{i<j}","\\beta","\\operatorname{logit}",
        )
        for token in required:
            self.assertIn(token,self.text)
        for token in ("Kge2","ledelta","2overline{","(ge1)","(ge6.25)"):
            self.assertNotIn(token,self.text)

    def test_all_four_figures_are_called_out(self):
        for i in range(1,5):
            self.assertIn(f"Figure {i}",self.text)
            self.assertTrue(any((ROOT/"figures").glob(f"figure{i}_*.png")))
            self.assertTrue(any((ROOT/"figures").glob(f"figure{i}_*.pdf")))

    def test_supplement_uses_v2_simulation(self):
        self.assertIn("simulate_temporal_aliasing_diagnostic_v2.py",self.supp)
        self.assertIn("0.001756",self.supp)
        self.assertIn("0.9521",self.supp)
        self.assertIn("0.860–0.995",self.supp)
        self.assertNotIn("simulate_temporal_aliasing_diagnostic_v1.py",self.supp)

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
