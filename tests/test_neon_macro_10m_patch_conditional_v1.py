"""Exact biological 10m rook patch test conditioned on old exact-station overlap.

Synthetic brute-force enumeration validates target distribution and exact
hypergeometric moments BEFORE any new original mammal patch effects open.
"""
from collections import Counter
from itertools import combinations
from statistics import mean
import math,unittest

from analysis.neon_macro_10m_patch_conditional_v1 import (
    conditional_patch_profile,observed_patch,iid_conditional_patch_null,
    NEIGHBOR,geometry_coverage,
)

def case():
    A={
        "G1":{"A1","A2","B1","B2"},
        "G2":{"A1","B2","C1","C2"},
    }
    B={
        "G1":{"A1","B1","C1","D1"},
        "G2":{"A1","B2","C2","D2"},
    }
    return A,B


def exact_states(A,B):
    g1,g2=sorted(A)
    both=B[g1]&B[g2]
    single=B[g1]^B[g2]
    k=len(B[g1]-both)
    observed_exact=sum(len(A[g]&B[g]) for g in A)
    masses=Counter()
    n_admissible=0
    n_conditioned=0
    for chosen in combinations(sorted(single),k):
        B1=both|set(chosen)
        B2=both|(single-set(chosen))
        assert len(B1)==len(B[g1]) and len(B2)==len(B[g2])
        n_admissible+=1
        if len(A[g1]&B1)+len(A[g2]&B2)!=observed_exact:
            continue
        n_conditioned+=1
        score=sum(bool(NEIGHBOR[t]&A[g1]) for t in B1)
        score+=sum(bool(NEIGHBOR[t]&A[g2]) for t in B2)
        masses[score]+=1
    return masses,n_conditioned,n_admissible


class ExactConditionedPatchTests(unittest.TestCase):
    def test_rook_grid_is_physical_10m_not_diagonal_or_self(self):
        g=geometry_coverage()
        self.assertEqual(g["station_count"],100)
        self.assertEqual(g["grid_neighbor_count_corner"],2)
        self.assertEqual(g["grid_neighbor_count_edge"],3)
        self.assertEqual(g["grid_neighbor_count_interior"],4)
        self.assertEqual(g["self_neighbor_count"],0)
        self.assertEqual(g["all_rook_edges_undirected"],180)
        self.assertNotIn("B2",NEIGHBOR["A1"])
        self.assertEqual(NEIGHBOR["A1"],frozenset({"A2","B1"}))

    def test_conditional_exact_uniform_moments_equal_brute_force_state_space(self):
        A,B=case()
        p=conditional_patch_profile(A,B)
        freq,n,total=exact_states(A,B)
        self.assertEqual(p["uniform_conditional_matrices"],n)
        self.assertGreater(n,1)
        self.assertLessEqual(n,total)
        mu=sum(score*count for score,count in freq.items())/n
        var=sum((score-mu)**2*count for score,count in freq.items())/n
        self.assertAlmostEqual(p["null_mean"],mu,places=12)
        self.assertAlmostEqual(p["null_sd"]**2,var,places=12)
        self.assertEqual(p["exact_conditioning_on_original_same_trap_overlap"],True)
        self.assertTrue(p["nominal_10m_rook_neighbor_excludes_self"])

    def test_conditioned_raw_observation_is_one_support_member(self):
        A,B=case()
        prof=conditional_patch_profile(A,B)
        values,n,total=exact_states(A,B)
        if prof["status"]!="EXACT_CONDITIONAL_NEIGHBOR_VARIANCE_POSITIVE":
            self.skipTest("This case has exact-conditioned zero variance")
        obs=observed_patch(A,B,prof)
        self.assertIn(obs["observed_nearest_neighbor_10m_score"],values)
        self.assertAlmostEqual(obs["Z_patch_given_exact_station_overlap"],
                               (obs["observed_nearest_neighbor_10m_score"]-prof["null_mean"])/prof["null_sd"])

    def test_fixed_station_overlap_not_randomized_in_every_conditional_state(self):
        A,B=case()
        g1,g2=sorted(A)
        forced=B[g1]&B[g2]
        singles=B[g1]^B[g2]
        k=len(B[g1]-forced)
        old_O=sum(len(A[g]&B[g]) for g in A)
        p=conditional_patch_profile(A,B)
        enumerated=0
        for subset in combinations(sorted(singles),k):
            newB={g1:forced|set(subset),g2:forced|(singles-set(subset))}
            if sum(len(A[g]&newB[g]) for g in A)==old_O:
                enumerated+=1
                self.assertEqual(sum(len(A[g]&newB[g]) for g in A),p["conditioned_fixed_original_overlap"])
                self.assertEqual([len(newB[g]) for g in (g1,g2)],[len(B[g]) for g in (g1,g2)])
        self.assertEqual(enumerated,p["uniform_conditional_matrices"])

    def test_label_swap_symmetry_of_exact_conditional_patch_distribution(self):
        A,B=case()
        revA={"G1":A["G2"],"G2":A["G1"]}
        revB={"G1":B["G2"],"G2":B["G1"]}
        a=conditional_patch_profile(A,B)
        b=conditional_patch_profile(revA,revB)
        self.assertAlmostEqual(a["null_mean"],b["null_mean"],places=12)
        self.assertAlmostEqual(a["null_sd"],b["null_sd"],places=12)
        self.assertEqual(a["uniform_conditional_matrices"],b["uniform_conditional_matrices"])
        self.assertEqual(exact_states(A,B)[0],exact_states(revA,revB)[0])

    def test_exact_zero_variance_reported_not_silently_included(self):
        A={"G1":{"A1","A2"},"G2":{"A1","A2"}}
        B={"G1":{"A1","B1"},"G2":{"A2","B2"}}
        p=conditional_patch_profile(A,B)
        self.assertEqual(p["status"],"EXACT_CONDITIONAL_NEIGHBOR_VARIANCE_ZERO")
        self.assertEqual(p["null_sd"],0)
        with self.assertRaisesRegex(ValueError,"degenerate"):
            iid_conditional_patch_null(p,seed=4,n_draws=200)

    def test_direct_iid_conditional_samples_approximate_exact_moments(self):
        A,B=case()
        p=conditional_patch_profile(A,B)
        if p["status"]!="EXACT_CONDITIONAL_NEIGHBOR_VARIANCE_POSITIVE":
            self.skipTest("No conditional variance in provided synthetic case")
        draws=iid_conditional_patch_null(p,seed=2026102531,n_draws=5000)
        self.assertEqual(draws,iid_conditional_patch_null(p,seed=2026102531,n_draws=5000))
        self.assertLess(abs(mean(draws)),0.08)
        self.assertLess(abs(sum(x*x for x in draws)/len(draws)-1),0.12)

if __name__=="__main__":
    unittest.main()
