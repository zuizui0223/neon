"""Synthetic evidence-independent geographic split and post-result gate.

No biological spatial overlap or existing site-mean Z used for inclusion.
"""
import unittest
from analysis.run_neon_exact_two_new_site_sensitivity_v1 import (
    split_geographically,variance_gate,
)

def pair(site:str,i:int,genera:int):
    gs=[f"G{x}" for x in range(genera)]
    return {"site":site,"site_plot":(site,"P"+str(i//10)),
            "season_ordinal":8080+i,
            "A":{g:{"A1","A2"} for g in gs},
            "B":{g:{"B1","B2"} for g in gs}}

def groups():
    oldsites=[f"OLD{i:02d}" for i in range(14)]
    twosites=oldsites[:13]+[f"NEW{i:02d}" for i in range(17)]
    strict=[pair(oldsites[i%14],i,3) for i in range(58)]
    two=[pair(twosites[i%30],i,2) for i in range(158)]
    return strict,two

class NewSourceGeographyTests(unittest.TestCase):
    def test_original_site_exclusion_is_source_only_and_nonoverlapping(self):
        strict,two=groups()
        summary=split_geographically(strict,two)
        self.assertEqual(summary["exact_two_new_site_count"],17)
        self.assertEqual(summary["original_58_three_plus_site_count"],14)
        self.assertEqual(len(summary["old_sites"]&summary["new_sites"]),0)
        self.assertEqual(summary["source_pairs_covered"]+summary["source_pairs_excluded_at_old_sites"],158)
        self.assertTrue(all(u["site"].startswith("NEW") for u in summary["new_source_units"]))

    def test_exact_marginal_variance_gate_pass_without_observed_effect(self):
        strict,two=groups()
        selected=split_geographically(strict,two)["new_source_units"]
        marginal=[{"status":"EXACT_NONDEGENERATE"} for u in selected]
        value=variance_gate(selected,marginal)
        self.assertTrue(value["passed"])
        self.assertGreaterEqual(value["informative_physical_site_count"],8)
        self.assertTrue(value["no_observed_pair_overlap_yet_computed"])

    def test_no_informative_unit_forbids_new_site_outcome(self):
        strict,two=groups()
        selected=split_geographically(strict,two)["new_source_units"]
        marginal=[{"status":"EXACT_ZERO_VARIANCE"} for u in selected]
        value=variance_gate(selected,marginal)
        self.assertFalse(value["passed"])
        self.assertEqual(value["status"],"STOP_GEOGRAPHICAL_SOURCE_OR_EXACT_NULL_SUPPORT")
        self.assertEqual(value["exact_null_zero_variance_pairs"],len(selected))

    def test_requiring_disjoint_old_site_count_is_immutable(self):
        strict,two=groups()
        bad=two[:-1]+[pair("ANOTHER_NEW",158,2)]
        with self.assertRaisesRegex(RuntimeError,"old 14 and exactly-two new 17"):
            split_geographically(strict,bad)

if __name__=="__main__":
    unittest.main()
