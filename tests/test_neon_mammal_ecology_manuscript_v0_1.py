"""Guard the ecology-first manuscript against unsupported claims and numeric drift.

Tests only against already-recorded repository results. No raw outcomes are
read, no re-estimation occurs, and no publication/confirmation is authorized.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript/NEON_MAMMAL_DENSITY_SPACE_ECOLOGY_V0_1.md"


def receipt(file: str):
    return json.loads((ROOT / "results" / file).read_text(encoding="utf-8"))


class EcologyManuscriptContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = MANUSCRIPT.read_text(encoding="utf-8")
        cls.dev = receipt("multiscale_density_development_result_v1.json")
        cls.gen = receipt("multiscale_density_heterogeneity_result_v1.json")
        cls.holdout = receipt("future_neon_provisional_holdout_decision_v1.json")
        cls.prec = receipt("peromyscus_holdout_precision_calibration_receipt_v1.json")
        cls.mosa = receipt("mosa_warning_removal_support_receipt_20261016.json")
        cls.model = receipt("multiscale_density_joint_model_contract_v1.json")
        cls.simple_null = receipt("multiscale_density_single_catch_null_result_v1.json")

    def test_primary_development_coefficients_and_identity(self):
        pri = self.dev["primary"]
        self.assertAlmostEqual(
            pri["beta_B_debiased_m2_per_mnka"]-pri["beta_W_m2_per_mnka"],
            pri["delta_beta_m2_per_mnka"], places=9,
        )
        self.assertAlmostEqual(pri["delta_beta_m2_per_mnka"], 9.37176547246767, places=8)
        for value in ("−4.395", "+4.977", "+9.372"):
            self.assertIn(value, self.text)

    def test_original_generality_remains_failed(self):
        x=self.dev["preregistered_guard"]
        self.assertEqual(x["required_positive_genus_count"], 6)
        self.assertEqual(x["observed_positive_genus_count"], 5)
        self.assertFalse(x["passed"])
        self.assertTrue(self.gen["primary_guard_remains_failed"])
        self.assertIn("**FAILED**", self.text)
        self.assertIn("only **five of eight**", self.text)

    def test_eight_genus_table_is_exact_development_source(self):
        observed = self.dev["genus_specific_delta"]
        self.assertEqual(len(observed), 8)
        for g in observed:
            pattern = (r"^\| \*" + re.escape(g["genus"]) +
                       r"\* \| (\d+) \| (\d+) \| ([+−\-]\d+\.\d{2}) \|")
            m = re.search(pattern, self.text, re.MULTILINE)
            self.assertIsNotNone(m, g["genus"])
            self.assertEqual(int(m[1]), g["sessions"])
            self.assertEqual(int(m[2]), g["sites"])
            self.assertAlmostEqual(float(m[3].replace("−","-")),
                                   round(g["beta"],2),places=2)
        self.assertEqual(sum(g["sessions"] for g in observed), 1326)
        self.assertEqual(self.dev["support"]["sites"],40)

    def test_provisional_peromyscus_sign_failure_and_uncertainty(self):
        a=self.holdout["mode_replicability"]["Peromyscus"]
        self.assertEqual(a["n"],127)
        self.assertEqual(a["sites"],19)
        self.assertGreater(a["development_beta_D"],0)
        self.assertLess(a["future_beta_D"],0)
        self.assertFalse(a["direction_matched"])
        ci=self.prec["interpretation"]["future_delta_CI95_site_cluster_t18"]
        self.assertLess(ci[0],0)
        self.assertGreater(ci[1],a["development_beta_D"])
        self.assertIn("[−49.82, +35.67]",self.text)
        self.assertIn("**−7.073**",self.text)

    def test_precise_phase_difference_not_significant(self):
        ci=self.prec["rank_correction"]["corrected_CI95_rank"]["all"]
        d=self.prec["rank_correction"]["new_phase_minus_old_beta"]["all"]
        self.assertLess(ci[0],0)
        self.assertGreater(ci[1],0)
        self.assertAlmostEqual(d,-23.003022008407576,places=6)
        self.assertIn("[−53.61, +7.61]",self.text)
        self.assertIn("neither a negative biological effect nor a temporal-regime reversal",self.text)

    def test_five_genus_future_not_estimable(self):
        a=self.holdout["mode_replicability"]
        self.assertEqual(a["full_five_genus_result"],"NOT_ESTIMABLE_ALL_FIVE_FROZEN_GENERA")
        self.assertEqual(a["Chaetodipus"]["n"],0)
        self.assertEqual(a["Myodes"]["n"],7)
        self.assertEqual(a["Sigmodon"]["n"],7)
        self.assertIn("**NOT ESTIMABLE**",self.text)

    def test_single_catch_null_is_limited(self):
        null=self.simple_null
        self.assertGreater(null["observed_release2026"]["beta_D"],
                           null["broad_single_catch_null_envelope"]["maximum_beta_D"])
        self.assertIn("not a complete observation model",self.text.lower())

    def test_mosa_support_not_spatial_effect(self):
        x=self.mosa
        self.assertEqual(x["original_frozen_months"],153)
        self.assertEqual(x["months_m_ge5_after_worst_case_code_removal"],153)
        self.assertEqual(x["years_with_ge2_distinct_FROZEN_MNA_levels_after_removal"],22)
        self.assertFalse(x["ecological_effects_opened"])
        self.assertIn("**No MOSA W, B, Δ or MNA–space ecological effect",self.text)

    def test_manuscript_marked_hold_and_source_limits(self):
        self.assertIn("**Submission status:** **HOLD**",self.text)
        self.assertIn("**provisional**",self.text)
        self.assertIn("230 marked animal histories",self.text)
        self.assertIn("not a randomized treatment",self.text)
        self.assertIn("not full home ranges",self.text)
        self.assertIn("do not move this draft to any journal submission",self.text)
        self.assertTrue(self.model["primary_universe"]["no_new_response_based_filtering"])

    def test_external_literature_and_manifest_are_present(self):
        for doi in [
            "10.1007/s00442-025-05731-2",
            "10.1002/ecog.07936",
            "10.1186/s40462-023-00394-1",
            "10.1111/ecog.01511",
            "10.1038/s41597-023-02700-3",
        ]:
            self.assertIn(doi,self.text)
        for file in [
            "multiscale_density_development_result_v1.json",
            "future_neon_provisional_holdout_decision_v1.json",
            "peromyscus_holdout_precision_calibration_receipt_v1.json",
        ]:
            self.assertIn(file,self.text)


if __name__=="__main__":
    unittest.main()
