"""Source-only gate for common-station observational-effect sensitivity."""
from unittest import TestCase,main
from analysis.run_neon_macro_six_night_effort_ecology_v1 import _variance_gate
from analysis.neon_exact_two_row_fixedmargin_v1 import two_row_exact_marginal

class CommonStationEffectGateTests(TestCase):
    def fixture(self):
        pair={"A":{"G1":{"A1","A2","A4"},"G2":{"A2","A3","A5"}},
              "B":{"G1":{"A1","A3","A5","A6"},"G2":{"A2","A3","A4","A7"}}}
        units=[{"site":f"FAKESITE{i%20}","site_plot":("PRIVATE","P"),
                "A":pair["A"],"B":pair["B"]} for i in range(100)]
        null=[two_row_exact_marginal(u["A"],u["B"]) for u in units]
        return units,null
    def test_source_support_go_before_opening_observed_overlap(self):
        units,null=self.fixture()
        gate=_variance_gate(units,null)
        self.assertTrue(gate["passed"])
        self.assertEqual(gate["informative_exact_null_pairs"],100)
        self.assertTrue(gate["no_observed_A_cross_B_overlap_or_Z_yet_computed"])
        self.assertNotIn("FAKESITE",str(gate))
    def test_25_percent_zero_variance_plus_one_fails(self):
        units,null=self.fixture()
        for i in range(26):
            null[i]={**null[i],"status":"EXACT_ZERO_VARIANCE"}
        gate=_variance_gate(units,null)
        self.assertFalse(gate["passed"])
        self.assertEqual(gate["status"],"STOP_SIX_NIGHT_EXACT_NULL_VARIANCE")
        self.assertEqual(gate["informative_exact_null_pairs"],74)
    def test_too_few_physical_sites_stops(self):
        units,null=self.fixture()
        for u in units:
            u["site"]="FAKESITE"
        gate=_variance_gate(units,null)
        self.assertFalse(gate["passed"])
        self.assertEqual(gate["informative_independent_physical_sites"],1)

if __name__=="__main__":
    main()
