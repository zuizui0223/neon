from __future__ import annotations

import itertools
import math
import unittest

import numpy as np

from analysis import mammal_spatial_packing_exact_v2 as m


class ExactPackingMomentsTests(unittest.TestCase):
    def setUp(self):
        self.traps=np.asarray([
            (0.0,0.0),
            (1.0,0.0),
            (0.0,2.0),
            (3.0,1.0),
            (4.0,4.0),
        ],dtype=float)

    def exhaustive_mpd(self,n):
        return np.asarray([
            m.mean_pairwise_distance(self.traps[list(indices)])
            for indices in itertools.combinations(range(len(self.traps)),n)
        ])

    def test_exact_moments_match_exhaustive_enumeration(self):
        for n in (2,3,4):
            with self.subTest(n=n):
                expected=self.exhaustive_mpd(n)
                got=m.exact_null_moments(self.traps,n)
                self.assertAlmostEqual(got["mean"],float(np.mean(expected)),places=12)
                self.assertAlmostEqual(got["sd"],float(np.std(expected,ddof=0)),places=12)

    def test_exact_mean_is_independent_of_subset_size(self):
        means=[
            m.exact_null_moments(self.traps,n)["mean"]
            for n in (2,3,4)
        ]
        self.assertLess(max(means)-min(means),1e-12)

    def test_exact_z_scores_are_standardized_over_complete_null(self):
        n=3
        zs=[]
        for indices in itertools.combinations(range(len(self.traps)),n):
            out=m.packing_score_exact(self.traps[list(indices)],self.traps)
            self.assertTrue(out["estimable"])
            zs.append(out["packing_z"])
        self.assertAlmostEqual(float(np.mean(zs)),0.0,places=12)
        self.assertAlmostEqual(float(np.std(zs,ddof=0)),1.0,places=12)

    def test_duplicate_observed_trap_locations_fail_closed(self):
        observed=np.asarray([(0.0,0.0),(0.0,0.0),(1.0,0.0)])
        out=m.packing_score_exact(observed,self.traps)
        self.assertFalse(out["estimable"])
        self.assertEqual(
            out["non_estimable_reason"],
            "duplicate_observed_trap_locations",
        )

    def test_all_traps_has_zero_null_variance(self):
        null=m.exact_null_moments(self.traps,len(self.traps))
        self.assertAlmostEqual(null["sd"],0.0,places=12)
        out=m.packing_score_exact(self.traps,self.traps)
        self.assertFalse(out["estimable"])
        self.assertEqual(out["non_estimable_reason"],"zero_null_variance")


if __name__=="__main__":
    unittest.main()
