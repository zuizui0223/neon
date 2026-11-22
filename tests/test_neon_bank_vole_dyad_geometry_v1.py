"""Synthetic-only tests of same-identified-vole seasonal partner geometry.

Never open original animal positions in tests. Primary dyad and secondary
directional randomization must use DIFFERENT reference keys.
"""
from __future__ import annotations
from random import Random
import unittest
from analysis.run_neon_bank_vole_dyad_geometry_v1 import (
    average_ranks,pearson_ranks,pair_distances,dyad_reshuffle,
    directional_alignment,SEED,DYAD_PERM_DRAWS,
    MIN_INFORMATIVE_SITES,MIN_INFORMATIVE_PAIRS
)

class BankVolePairIdentityGeometryTests(unittest.TestCase):
    def test_average_ranks_preserve_tie_groups(self):
        self.assertEqual(average_ranks([1.,1.,3.]),[1.5,1.5,3.])
        self.assertEqual(average_ranks([4.,2.,3.]),[3.,1.,2.])
    def test_distance_ranks_are_symmetric_and_signed(self):
        self.assertAlmostEqual(pearson_ranks([1,2,3],[1,2,3]),1.)
        self.assertAlmostEqual(pearson_ranks([1,2,3],[3,2,1]),-1.)
        with self.assertRaises(ValueError):
            pearson_ranks([1,1,1],[1,2,3])
    def test_fixed_pair_distances_translation_does_not_change_rank(self):
        a=[(0.,0.),(0.,3.),(4.,0.),(5.,5.)]
        b=[(x+10.,y-2.) for x,y in a]
        z=dyad_reshuffle(a,b,Random(2),draws=1200)
        self.assertAlmostEqual(z["observed"],1.)
        self.assertGreater(z["identity_excess"],0.)
        self.assertLess(z["identity_shuffle_null_mean"],1.)
        self.assertEqual(len(pair_distances(a)),6)
    def test_fixed_source_seasonal_nonreplacement_of_ids(self):
        a=[(0.,0.),(0.,3.),(4.,0.),(5.,5.)]
        b=[a[1],a[0],a[3],a[2]]
        z=dyad_reshuffle(a,b,Random(2),draws=1200)
        self.assertLess(z["observed"],1.)
        self.assertEqual(z["permutation_count"],1200)
    def test_two_season_directional_coherence(self):
        a=[(0.,0.),(3.,0.),(0.,4.),(5.,5.)]
        b=[(x+2.,y) for x,y in a]
        z=directional_alignment(a,b,Random(3),draws=1200)
        self.assertTrue(z["estimable"])
        self.assertAlmostEqual(z["directional_observed"],1.)
        self.assertGreater(z["directional_excess"],0.)
        self.assertIn("directional_rotation_null_mean",z)
        self.assertNotIn("identity_shuffle_null_mean",z)
    def test_opposing_individual_displacements_are_not_translation(self):
        a=[(0.,0.),(3.,0.),(0.,4.),(5.,5.)]
        b=[(2.,0.),(1.,0.),(2.,4.),(3.,5.)]
        z=directional_alignment(a,b,Random(3),draws=1200)
        self.assertTrue(z["estimable"])
        self.assertAlmostEqual(z["directional_observed"],0.)
        self.assertLess(z["directional_excess"],0.)
    def test_zero_shift_is_nonestimable_not_positive_contact(self):
        a=[(0.,0.),(0.,3.),(4.,0.)]
        z=directional_alignment(a,list(a),Random(3),draws=100)
        self.assertFalse(z["estimable"])
        self.assertNotIn("directional_excess",z)
    def test_original_source_gate_is_fixed(self):
        self.assertEqual(MIN_INFORMATIVE_SITES,8)
        self.assertEqual(MIN_INFORMATIVE_PAIRS,60)
        self.assertEqual(DYAD_PERM_DRAWS,2000)
        self.assertEqual(SEED,2026111553)
    def test_original_site_relabel_null_is_seed_deterministic(self):
        a=[(0.,0.),(0.,3.),(4.,0.),(5.,5.)]
        b=[(1.,0.),(0.,4.),(3.,1.),(5.,4.)]
        self.assertEqual(dyad_reshuffle(a,b,Random(44),draws=120),
                         dyad_reshuffle(a,b,Random(44),draws=120))
if __name__=="__main__":
    unittest.main()
