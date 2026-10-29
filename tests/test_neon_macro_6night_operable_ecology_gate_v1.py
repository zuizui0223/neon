"""Synthetic stage-gating for official NEON 4/5/6 operational-source ecology.

The source and exact conditional variance gates must pass before opening
observed animal genus×trap recurrence on the new operational subcohort.
"""
from unittest import TestCase,main
from analysis.run_neon_macro_6night_operable_ecology_v1 import exact_null_variance_gate
from analysis.neon_exact_two_row_fixedmargin_v1 import two_row_exact_marginal


def fixture():
    A={"G1":{"A1","A2","B1"},"G2":{"A2","B2","B3"}}
    B={"G1":{"A1","A3","B2","C3"},"G2":{"A2","A3","B3","C4"}}
    units=[{"site":f"FAKE{i%20}","A":A,"B":B} for i in range(100)]
    margins=[two_row_exact_marginal(u["A"],u["B"]) for u in units]
    return units,margins


class Code456EcologySourceGateTests(TestCase):
    def test_no_observed_recapture_overlap_before_gate(self):
        x,margin=fixture()
        support=exact_null_variance_gate(x,margin)
        self.assertTrue(support["passed"])
        self.assertEqual(support["positive_exact_null_variance_original_pairs"],100)
        self.assertEqual(support["informative_physical_sites"],20)
        self.assertTrue(support["new_observed_seasonal_genus_trap_overlap_unopened_at_this_stage"])
        self.assertNotIn("FAKE",str(support))

    def test_false_75percent_variance_fails_even_when_total_pairs_high(self):
        x,m=fixture()
        for i in range(26):
            m[i]={**m[i],"status":"EXACT_ZERO_VARIANCE"}
        result=exact_null_variance_gate(x,m)
        self.assertFalse(result["passed"])
        self.assertEqual(result["positive_exact_null_variance_original_pairs"],74)
        self.assertEqual(result["status"],"STOP_OPERABLE_ALL6_UNIFORM_NULL_INFORMATIVENESS")

    def test_fewer_than_twelve_sites_fails(self):
        x,m=fixture()
        x=[{**z,"site":"ONE"} for z in x]
        result=exact_null_variance_gate(x,m)
        self.assertFalse(result["passed"])
        self.assertEqual(result["informative_physical_sites"],1)

    def test_pair_total_not_sufficient_if_fewer_than_40_informative(self):
        x,m=fixture()
        for i in range(63):
            m[i]={**m[i],"status":"EXACT_ZERO_VARIANCE"}
        result=exact_null_variance_gate(x,m)
        self.assertFalse(result["passed"])
        self.assertEqual(result["positive_exact_null_variance_original_pairs"],37)

if __name__=="__main__":
    main()
