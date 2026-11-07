"""Source-backed figure 1 integrity tests (no new ecological fitting).

Assert that all eight genera and the provisional precision-limited holdout
match the *original frozen results*. Fail if a figure silently hides a genus,
changes a sign, narrows an interval or promotes MOSA to a biological outcome.
"""
from __future__ import annotations

import json
from math import isclose
from pathlib import Path
import xml.etree.ElementTree as ET
import unittest

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "manuscript/figures/figure_1_density_cross_scale.svg"
PAPER = ROOT / "manuscript/NEON_MAMMAL_DENSITY_SPACE_ECOLOGY_V0_2.md"
NS = {"s": "http://www.w3.org/2000/svg"}


def read(name):
    return json.loads((ROOT / "results" / name).read_text(encoding="utf-8"))


def fmt(v):
    return ("+" if v >= 0 else "−") + format(abs(v), ".2f")


def x_axis(v):
    # Declared figure B horizontal axis: -60..45 maps to 345..1060.
    return 345.0 + (v + 60.0) * (1060.0 - 345.0) / 105.0


class MammalFigureIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ET.fromstring(SVG.read_text(encoding="utf-8"))
        cls.all_text = cls.root.findall(".//s:text", NS)
        cls.genus = read("multiscale_density_heterogeneity_result_v1.json")
        cls.development = read("multiscale_density_development_result_v1.json")
        cls.future = read("future_neon_provisional_holdout_decision_v1.json")
        cls.precision = read("peromyscus_holdout_precision_calibration_receipt_v1.json")
        cls.paper = PAPER.read_text(encoding="utf-8")

    def test_svg_is_well_formed_and_accessible(self):
        self.assertEqual(self.root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertEqual(self.root.attrib["viewBox"], "0 0 1200 920")
        self.assertTrue(self.root.findall("s:title", NS))
        self.assertTrue(self.root.findall("s:desc", NS))

    def test_all_frozen_eight_genera_shown_including_one_site(self):
        dev = self.development
        taxa = self.genus["genus_diagnostics"]
        self.assertEqual(len(taxa),8)
        self.assertEqual(sum(x["sessions"] for x in taxa),1326)
        self.assertFalse(dev["preregistered_guard"]["passed"])
        for index, taxon in enumerate(taxa):
            y = str(208 + 39*index)
            row_text = [
                (t.attrib.get("x"),t.text)
                for t in self.all_text if t.attrib.get("y")==y
            ]
            content = [v for _x,v in row_text]
            self.assertIn(taxon["genus"],content)
            self.assertIn(fmt(taxon["beta_W"]),content)
            self.assertIn(fmt(taxon["beta_B_debiased"]),content)
            self.assertIn(fmt(taxon["beta_delta"]),content)
            self.assertIn(str(taxon["sessions"]),content)
            self.assertIn(str(taxon["sites"]),content)
            self.assertIn("positive" if taxon["beta_delta"]>0 else "negative",content)

    def test_five_positive_deltas_not_relabelled_success(self):
        pos=sum(x["beta_delta"]>0 for x in self.genus["genus_diagnostics"])
        self.assertEqual(pos,5)
        self.assertEqual(self.development["preregistered_guard"]["required_positive_genus_count"],6)
        texts=[(t.text or "") for t in self.all_text]
        self.assertTrue(any("5/8" in t and "FAIL" in t for t in texts))
        self.assertTrue(any("One-site estimates shown" in t for t in texts))

    def test_peromyscus_point_coordinates_source_matched(self):
        p=self.future["mode_replicability"]["Peromyscus"]
        diff=self.precision["rank_correction"]["new_phase_minus_old_beta"]["all"]
        pts={float(e.attrib["cy"]):float(e.attrib["cx"])
             for e in self.root.findall(".//s:circle",NS)
             if "cx" in e.attrib and "cy" in e.attrib}
        for y,value in [
            (686.0,p["development_beta_D"]),
            (730.0,p["future_beta_D"]),
            (774.0,diff),
        ]:
            self.assertIn(y,pts)
            self.assertTrue(isclose(pts[y],x_axis(value),rel_tol=0,abs_tol=1e-6))
        self.assertFalse(p["direction_matched"])

    def test_holdout_rank_aware_intervals_both_span_zero(self):
        hold=self.precision["interpretation"]["future_delta_CI95_site_cluster_t18"]
        diff=self.precision["rank_correction"]["corrected_CI95_rank"]["all"]
        for ci in [hold,diff]:
            self.assertLess(ci[0],0)
            self.assertGreater(ci[1],0)
        self.assertLess(hold[0],self.future["mode_replicability"]["Peromyscus"]["development_beta_D"])
        self.assertGreater(hold[1],self.future["mode_replicability"]["Peromyscus"]["development_beta_D"])
        verticals={}
        for elem in self.root.findall(".//s:line",NS):
            x0,x1=float(elem.attrib["x1"]),float(elem.attrib["x2"])
            y0,y1=float(elem.attrib["y1"]),float(elem.attrib["y2"])
            if abs(x0-x1)<1e-7 and abs(y1-y0-14)<1e-7 and y0 in {723.,767.}:
                verticals.setdefault(y0,[]).append(x0)
        self.assertEqual(len(verticals[723.]),2)
        self.assertEqual(len(verticals[767.]),2)
        for y, ci in ((723.,hold),(767.,diff)):
            for actual, expected in zip(sorted(verticals[y]),sorted(x_axis(v) for v in ci)):
                self.assertTrue(isclose(actual,expected,rel_tol=0,abs_tol=1e-6))

    def test_exploratory_component_shift_is_arithmetic_not_mechanism(self):
        p = self.future["mode_replicability"]["Peromyscus"]
        shift_w=p["future_beta_W"]-p["development_beta_W"]
        shift_b=p["future_beta_B"]-p["development_beta_B"]
        shift_d=p["future_beta_D"]-p["development_beta_D"]
        self.assertAlmostEqual(shift_d,shift_b-shift_w,places=7)
        self.assertAlmostEqual(shift_w,6.101397442065647,places=7)
        self.assertAlmostEqual(shift_b,-16.90162456634222,places=7)
        share=abs(shift_b)/abs(shift_d)*100
        self.assertAlmostEqual(share,73.4756701104945,places=6)
        self.assertIn("73.5%",self.paper)
        self.assertIn("−16.902",self.paper)
        self.assertIn("does not** identify a true population-footprint shift",self.paper)
        self.assertIn("genus-wide rather than necessarily focal-species-specific",self.paper)

    def test_conditional_sign_negative_example_stays_post_result(self):
        probability=self.precision["interpretation"][
            "post_result_normal_probability_of_negative_future_slope_if_old_beta_true"
        ]
        self.assertAlmostEqual(probability,0.2168357131793785,places=10)
        self.assertIn("**21.7%**",self.paper)
        self.assertIn("neither prospective power nor a test proving the old model",self.paper)

    def test_captions_and_limits_not_silently_promoted(self):
        self.assertIn("figures/figure_1_density_cross_scale.svg",self.paper)
        self.assertIn("**Figure 1.**",self.paper)
        self.assertIn("**Submission status:** **HOLD**",self.paper)
        self.assertIn("**NOT ESTIMABLE**",self.paper)
        self.assertIn("not proof that no population",self.paper.lower())
        self.assertIn("no mosa w, b, δ or mna–space ecological effect",self.paper.lower())
        self.assertIn("not a randomized treatment",self.paper)


if __name__=="__main__":
    unittest.main()
