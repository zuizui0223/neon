from __future__ import annotations

import itertools
import unittest

import numpy as np

from analysis import conditional_sex_space_null_v1 as m


class ConditionalSexSpaceNullTests(unittest.TestCase):
    def test_exact_null_distribution_is_centered_by_construction(self):
        xy=np.asarray([
            (0.,0.),(1.,0.),(2.,0.),
            (0.,1.),(1.,1.),(2.,1.),
        ])
        strata=["A","A","A","B","B","B"]
        sex=["M","F","F","M","F","F"]
        out=m.conditional_sex_space_z(
            xy=xy,sex=sex,strata=strata,
            exact_max_assignments=1000,
        )
        self.assertTrue(out["estimable"])
        self.assertEqual(
            out["permutation_mode"],
            "exact_stratified_sex_label_permutation",
        )
        self.assertEqual(out["permutation_space_size"],9)

    def test_stratum_counts_are_preserved(self):
        xy=np.asarray([
            (0.,0.),(1.,0.),(2.,0.),
            (0.,1.),(1.,1.),(2.,1.),
        ])
        strata=["A","A","A","B","B","B"]
        sex=["M","M","F","M","F","F"]
        by=m._stratum_indices(strata)
        for mask in m._exact_masks(strata,sex):
            self.assertEqual(int(np.sum(mask[by["A"]])),2)
            self.assertEqual(int(np.sum(mask[by["B"]])),1)

    def test_no_within_stratum_exchange_fails_closed(self):
        xy=np.asarray([(0.,0.),(1.,0.),(0.,1.),(1.,1.)])
        out=m.conditional_sex_space_z(
            xy=xy,
            sex=["M","M","F","F"],
            strata=["Mdet","Mdet","Fdet","Fdet"],
        )
        self.assertFalse(out["estimable"])
        self.assertEqual(
            out["non_estimable_reason"],
            "no_within_stratum_sex_permutation",
        )

    def test_deterministic_mc_is_reproducible(self):
        xy=np.asarray([(float(i),float(i%3)) for i in range(14)])
        sex=["M"]*7+["F"]*7
        strata=["A"]*14
        a=m.conditional_sex_space_z(
            xy=xy,sex=sex,strata=strata,
            exact_max_assignments=1,
            monte_carlo_draws=1999,
        )
        b=m.conditional_sex_space_z(
            xy=xy,sex=sex,strata=strata,
            exact_max_assignments=1,
            monte_carlo_draws=1999,
        )
        self.assertTrue(a["estimable"])
        self.assertAlmostEqual(a["sex_space_z"],b["sex_space_z"],places=15)
        self.assertEqual(a["seed"],b["seed"])


if __name__=="__main__":
    unittest.main()
