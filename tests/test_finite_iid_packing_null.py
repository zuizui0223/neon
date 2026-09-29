from __future__ import annotations

import itertools
import unittest

import numpy as np

from analysis import finite_iid_packing_null_v1 as m


class ExactIIDPackingNullTests(unittest.TestCase):
    def setUp(self):
        self.support=np.asarray([
            (0.0,0.0),
            (1.0,0.0),
            (0.0,2.0),
        ])

    def exhaustive(self,n):
        values=[]
        zs=[]
        null=m.exact_iid_mpd_null_moments(self.support,n)
        for indices in itertools.product(range(len(self.support)),repeat=n):
            obs=self.support[list(indices)]
            mpd=m.mean_pairwise_distance(obs)
            values.append(mpd)
            zs.append((mpd-null["mean"])/null["sd"])
        return np.asarray(values),np.asarray(zs)

    def test_exact_moments_match_ordered_exhaustive_samples(self):
        for n in (2,3,4):
            with self.subTest(n=n):
                values,_=self.exhaustive(n)
                out=m.exact_iid_mpd_null_moments(self.support,n)
                self.assertAlmostEqual(out["mean"],float(np.mean(values)),places=12)
                self.assertAlmostEqual(out["sd"],float(np.std(values,ddof=0)),places=12)

    def test_exhaustive_z_is_standardized(self):
        for n in (2,3,4):
            with self.subTest(n=n):
                _,zs=self.exhaustive(n)
                self.assertAlmostEqual(float(np.mean(zs)),0.0,places=12)
                self.assertAlmostEqual(float(np.std(zs,ddof=0)),1.0,places=12)

    def test_null_mean_does_not_depend_on_n(self):
        means=[
            m.exact_iid_mpd_null_moments(self.support,n)["mean"]
            for n in (2,3,5,10)
        ]
        self.assertLess(max(means)-min(means),1e-12)

    def test_duplicate_observed_locations_are_allowed(self):
        observed=np.asarray([(0.,0.),(0.,0.),(1.,0.)])
        out=m.packing_score_iid_exact(observed,self.support)
        self.assertTrue(out["estimable"])
        self.assertIsNotNone(out["packing_z"])

    def test_canonical_grid_has_49_flags(self):
        grid=m.canonical_grid_7x7()
        self.assertEqual(len(grid),49)
        self.assertEqual(grid["A1"],(0.0,0.0))
        self.assertEqual(grid["G7"],(37.5,37.5))


if __name__=="__main__":
    unittest.main()
