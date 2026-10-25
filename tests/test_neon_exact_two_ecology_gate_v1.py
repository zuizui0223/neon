"""Synthetic source-wide gate before opening any exactly-two genus effect."""
import unittest

from analysis.neon_exact_two_row_fixedmargin_v1 import two_row_exact_marginal
from analysis.run_neon_exact_two_genus_ecology_v1 import (
    marginal_source_gate,reuse_physical_sites
)


def all_units():
    units=[]
    for i in range(158):
        site=f"FAKESITE{i%22}"
        plot=f"PLOT{i//22}"
        units.append({
            "site":site,
            "site_plot":(site,plot),
            "season_ordinal":8000+i//22,
            "A":{"G1":{"A1","A2","A4"},"G2":{"A2","A3","A5"}},
            "B":{"G1":{"A1","A3","A5","A6"},"G2":{"A2","A3","A4","A7"}},
        })
    return units


class TwoGenusVarianceGateTests(unittest.TestCase):
    def test_all_informative_source_variance_go_before_observation(self):
        source=all_units()
        marginals=[two_row_exact_marginal(u["A"],u["B"]) for u in source]
        out=marginal_source_gate(source,marginals)
        self.assertEqual(out["null_informative_pairs"],158)
        self.assertAlmostEqual(out["null_informative_fraction"],1)
        self.assertEqual(out["null_informative_physical_sites"],22)
        self.assertTrue(out["marginal_variance_gate_does_not_compute_observed_recurrence"])
        self.assertTrue(out["passed"])

    def test_75pct_support_stop_even_if_8sites_remain(self):
        source=all_units()
        marginals=[two_row_exact_marginal(u["A"],u["B"]) for u in source]
        for i in range(41):
            marginals[i]={**marginals[i],"status":"EXACT_ZERO_VARIANCE","null_sd":0}
        out=marginal_source_gate(source,marginals)
        self.assertEqual(out["null_informative_pairs"],117)
        self.assertFalse(out["passed"])
        self.assertEqual(out["status"],"STOP_EXACT_NULL_TOO_FEW_INFORMATIVE_UNITS")

    def test_source_key_reuse_is_entire_physical_site(self):
        arr=all_units()
        # Force two season pairs at same plot to share a season key.
        arr[0]["site"]="FAKESITE0"
        arr[0]["site_plot"]=("FAKESITE0","SAME")
        arr[0]["season_ordinal"]=8000
        arr[22]["site"]="FAKESITE0"
        arr[22]["site_plot"]=("FAKESITE0","SAME")
        arr[22]["season_ordinal"]=8001
        reused=reuse_physical_sites(arr)
        self.assertIn("FAKESITE0",reused)
        self.assertNotIn("FAKESITE1",reused)


if __name__=="__main__":
    unittest.main()
