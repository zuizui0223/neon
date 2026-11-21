"""Synthetic no-outcome source eligibility tests: original 2023 voles."""
from __future__ import annotations
import unittest
from analysis.audit_neon_figshare_2023_individual_resource_risk_join_v1 import (
    pid,original_number_available,source_only_join
)

class TestFigshareVoleResourceRiskSourceOnly(unittest.TestCase):
    def test_literal_PIT_preserved_without_numeric_guess(self):
        self.assertEqual(pid("000123456  "),"000123456")
        for x in ("",None,"NA","n/a","nan","unknown","UNK"):
            self.assertIsNone(pid(x))

    def test_seed_numeric_presence_not_usage_effect(self):
        for val in ("0","5","0.25","7e-3"):
            self.assertTrue(original_number_available(val))
        for val in ("NA","NaN","",-1,"-1","Infinity","None"):
            self.assertFalse(original_number_available(str(val)))

    def test_source_GO_from_synthetic_patches_and_matched_source_PIT(self):
        events=[]
        for j in range(40):
            events.append({"PIT":f"A{j%8:02d}","SESSION":str(1+j%2),
                           "GRID":str(1+j%3),
                           "SITE_ID":f"S{j%12}","TREAT":str(j%2),
                           "WP":"3","BF":"2","Seed_Choice":"DO NOT USE"})
        events.extend([{"PIT":"","WP":"","BF":""} for _ in range(603-40)])
        blups=[{"PIT":f"A{j%8:02d}"} for j in range(1069)]
        personality=[{"PIT":f"A{j%8:02d}"} for j in range(3712)]
        report=source_only_join({
            "2018 Vole Seed Data.csv":events,
            "Vole BLUPS.csv":blups,
            "Vole Personality Data.csv":personality
        },{},"synthetic")
        self.assertEqual(report["status"],
          "SOURCE_JOIN_GO_ORIGINAL_BAITED_FORAGING_OBSERVATIONS_NOT_ECOLOGY")
        self.assertEqual(report["eligible_exact_PIT_intersection_all_three_source_count"],8)
        self.assertEqual(report["eligible_complete_event_rows_with_original_PIT_in_all_three"],40)
        self.assertTrue(report["biological_limits"]["no_resource_effect_or_seed_use_proportion_computed"])

    def test_no_favorable_replacement_when_ID_links_absent(self):
        events=[{"PIT":f"A{j%8:02d}","SESSION":"1","GRID":"1",
                 "SITE_ID":str(j),"TREAT":"safe","WP":"3","BF":"4"}
                for j in range(603)]
        report=source_only_join({
            "2018 Vole Seed Data.csv":events,
            "Vole BLUPS.csv":[{"PIT":f"Other{i}"} for i in range(1069)],
            "Vole Personality Data.csv":[{"PIT":f"A{j%8:02d}"} for j in range(3712)]
        },{},"synthetic")
        self.assertEqual(report["status"],"SOURCE_JOIN_STOP_ID_PATCH_SEED_OR_FOREST_STRATUM_SUPPORT")
        self.assertEqual(report["eligible_exact_PIT_intersection_all_three_source_count"],0)

if __name__=="__main__":
    unittest.main()
