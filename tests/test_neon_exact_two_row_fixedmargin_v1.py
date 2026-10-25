"""Mathematically exact two-row fixed-margin null versus brute-force states.

Synthetic only, before opening any original NEON exactly-two genus effect.
"""
from itertools import combinations
from collections import Counter
from math import comb
import json
import unittest

from analysis.neon_exact_two_row_fixedmargin_v1 import (
    two_row_exact_marginal, observed_exact_unit, quantile_sampler,
    meta_exact_site_null,
)

def example():
    A={"G1":{"A1","A2","A4"},"G2":{"A2","A3","A5"}}
    B={"G1":{"A1","A3","A5","A6"},"G2":{"A2","A3","A4","A7"}}
    return A,B

def brute(A,B):
    g1,g2=sorted(A)
    shared=B[g1]&B[g2]
    single=B[g1]^B[g2]
    selected=len(B[g1]-B[g2])
    counts=Counter()
    states=0
    for chosen in combinations(sorted(single),selected):
        one=shared|set(chosen)
        two=shared|(single-set(chosen))
        assert len(one)==len(B[g1]) and len(two)==len(B[g2])
        assert {(t,int(t in one)+int(t in two)) for t in one|two} == {
            (t,int(t in B[g1])+int(t in B[g2])) for t in B[g1]|B[g2]
        }
        ov=len(A[g1]&one)+len(A[g2]&two)
        counts[ov]+=1
        states+=1
    return dict(counts),states

class ExactTwoGenusFixedMarginTests(unittest.TestCase):
    def test_exact_pmf_vs_all_admissible_binary_matrices(self):
        A,B=example()
        dist=two_row_exact_marginal(A,B)
        table,states=brute(A,B)
        self.assertEqual(dist["_private_mass"],table)
        self.assertEqual(dist["total_uniform_fixed_margin_matrices"],states)
        self.assertEqual(states,comb(dist["n_singleton_columns"],dist["genus1_singleton_count"]))
        self.assertEqual(dist["status"],"EXACT_NONDEGENERATE")
        self.assertGreater(dist["null_sd"],0)
        result=observed_exact_unit(A,B,dist)
        observed=sum(len(A[g]&B[g]) for g in A)
        exact_tail=sum(v for k,v in table.items() if k>=observed)/states
        self.assertAlmostEqual(result["exact_unit_tail_p"],exact_tail,places=14)

    def test_taxon_labels_exchange_invariant(self):
        A,B=example()
        left=two_row_exact_marginal(A,B)
        As={"G1":A["G2"],"G2":A["G1"]}
        Bs={"G1":B["G2"],"G2":B["G1"]}
        right=two_row_exact_marginal(As,Bs)
        self.assertEqual(left["_private_mass"],right["_private_mass"])
        self.assertEqual(left["total_uniform_fixed_margin_matrices"],right["total_uniform_fixed_margin_matrices"])
        self.assertAlmostEqual(left["null_mean"],right["null_mean"])
        self.assertAlmostEqual(left["null_sd"],right["null_sd"])

    def test_forced_double_columns_with_singletons(self):
        A={"G1":{"A1","A2"},"G2":{"A1","A3"}}
        B={"G1":{"A1","A2"},"G2":{"A1","A3"}}
        dist=two_row_exact_marginal(A,B)
        table,states=brute(A,B)
        self.assertEqual(dist["_private_mass"],table)
        self.assertEqual(dist["n_forced_double_columns"],1)
        self.assertEqual(dist["n_singleton_columns"],2)
        self.assertEqual(states,2)

    def test_zero_variance_is_not_a_favorable_informative_unit(self):
        A={"G1":{"A1","A2"},"G2":{"A1","A2"}}
        B={"G1":{"A1","A3"},"G2":{"A2","A3"}}
        dist=two_row_exact_marginal(A,B)
        self.assertEqual(dist["status"],"EXACT_ZERO_VARIANCE")
        self.assertEqual(dist["null_sd"],0)
        self.assertIsNone(observed_exact_unit(A,B,dist)["z"])
        with self.assertRaisesRegex(ValueError,"zero variance"):
            quantile_sampler(dist)

    def test_impossible_and_noncanonical_source_matrix_stop(self):
        with self.assertRaisesRegex(ValueError,"Exactly two"):
            two_row_exact_marginal({"G1":{"A1","A2"}},{"G1":{"A1","A2"}})
        with self.assertRaisesRegex(ValueError,"trap and taxon support"):
            two_row_exact_marginal({"G1":{"X1","A2"},"G2":{"A2","A3"}},
                                   {"G1":{"A1","A2"},"G2":{"A2","A3"}})

    def test_quantile_marginal_and_conditional_site_null_private(self):
        A,B=example()
        z=two_row_exact_marginal(A,B)
        o=observed_exact_unit(A,B,z)
        sample=quantile_sampler(z)
        self.assertTrue(all(isinstance(sample(q),float) for q in (0,.1,.5,.9,.999)))
        private=[
            {"site":"FAKESITE1","observed_z":o["z"],"exact_marginal":z},
            {"site":"FAKESITE1","observed_z":o["z"],"exact_marginal":z},
            {"site":"FAKESITE2","observed_z":o["z"],"exact_marginal":z},
        ]
        x=meta_exact_site_null(private,seed=101,n_replicates=500)
        y=meta_exact_site_null(private,seed=101,n_replicates=500)
        self.assertEqual(x,y)
        self.assertEqual(x["sites"],2)
        self.assertEqual(x["seasonal_pairs"],3)
        self.assertTrue(x["two_row_unit_nulls_mathematically_exact"])
        self.assertTrue(x["comonotone_not_a_proven_worst_case_bound"])
        self.assertEqual(x["independent_unit_exact_marginal_null"]["draws"],500)
        self.assertNotIn("FAKESITE",json.dumps(x))

if __name__=="__main__":
    unittest.main()
