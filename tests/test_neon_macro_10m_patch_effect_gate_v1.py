"""Synthetic gate for 10m local patch recurrence beyond EXACT trap self-match."""
from unittest import TestCase,main
from analysis.neon_macro_10m_patch_conditional_v1 import conditional_patch_profile
from analysis.run_neon_macro_10m_patch_ecology_v1 import conditional_variance_support


def example():
    A={"G1":{"A1","A2","B1","B2"},"G2":{"A1","B2","C1","C2"}}
    B={"G1":{"A1","B1","C1","D1"},"G2":{"A1","B2","C2","D2"}}
    return A,B


class PatchVarianceEligibilityTests(TestCase):
    def fixture(self):
        A,B=example()
        prof=conditional_patch_profile(A,B)
        rows=[{"site":f"FAKESITE{i%24}",
               "site_plot":("PSEUDO",str(i//24)),
               "A":A,"B":B} for i in range(158)]
        marginal=[prof for _ in rows]
        return rows,marginal

    def test_variance_allows_new_neighborhood_score_only_after_go(self):
        units,marginals=self.fixture()
        # If these specific synthetic matrices have no patch variance,
        # construct the eligibility statement with stubbed nondegenerate
        # nulls; this test exercises the external source guard only.
        marginals=[{"status":"EXACT_CONDITIONAL_NEIGHBOR_VARIANCE_POSITIVE"}
                   for _ in units]
        g=conditional_variance_support(units,marginals)
        self.assertTrue(g["passed"])
        self.assertEqual(g["exact_conditional_variance_positive_pairs"],158)
        self.assertEqual(g["informative_physical_sites"],24)
        self.assertTrue(g["new_neighborhood_observed_score_NOT_yet_opened"])
        self.assertTrue(g["source_same_trap_overlap_already_opened_and_conditioned"])

    def test_zero_variance_stops_before_patch_signal(self):
        units,marginals=self.fixture()
        marginals=[{"status":"EXACT_CONDITIONAL_NEIGHBOR_VARIANCE_ZERO"}
                   for _ in units]
        g=conditional_variance_support(units,marginals)
        self.assertFalse(g["passed"])
        self.assertEqual(g["status"],"STOP_EXACT_CONDITIONED_NEIGHBOR_VARIANCE_SUPPORT")

    def test_79_informative_pairs_fail_frozen_80_pair_guard(self):
        units,marginals=self.fixture()
        marginals=[{"status":"EXACT_CONDITIONAL_NEIGHBOR_VARIANCE_POSITIVE" if i<79 else
                     "EXACT_CONDITIONAL_NEIGHBOR_VARIANCE_ZERO"}
                   for i in range(158)]
        g=conditional_variance_support(units,marginals)
        self.assertEqual(g["exact_conditional_variance_positive_pairs"],79)
        self.assertFalse(g["passed"])
        self.assertEqual(g["minimum_predeclared_informative_pairs"],80)

    def test_fewer_than_18_sites_stop_even_with_many_pairs(self):
        units,marginals=self.fixture()
        units=[{**u,"site":"FAKEONE"} for u in units]
        marginals=[{"status":"EXACT_CONDITIONAL_NEIGHBOR_VARIANCE_POSITIVE"}
                   for _ in units]
        g=conditional_variance_support(units,marginals)
        self.assertFalse(g["passed"])
        self.assertEqual(g["informative_physical_sites"],1)

if __name__=="__main__":
    main()
