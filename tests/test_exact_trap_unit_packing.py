from __future__ import annotations

import itertools
import unittest

import numpy as np

from analysis import exact_trap_unit_packing_v1 as m


class ExactTrapUnitPackingTests(unittest.TestCase):
    def setUp(self):
        # A and B are distinct colocated traps.
        self.ids=["A","B","C","D","E"]
        self.xy=np.asarray([
            (0.0,0.0),
            (0.0,0.0),
            (1.0,0.0),
            (0.0,1.0),
            (2.0,1.0),
        ])

    def exhaustive(self,n):
        vals=[]
        for idx in itertools.combinations(range(len(self.ids)),n):
            vals.append(m.mean_pairwise_distance(self.xy[list(idx)]))
        return np.asarray(vals,dtype=float)

    def test_exact_moments_match_enumeration_with_colocated_units(self):
        for n in (2,3,4):
            with self.subTest(n=n):
                expected=self.exhaustive(n)
                got=m.exact_mpd_null_moments(self.xy,n)
                self.assertAlmostEqual(
                    got["null_mean_mpd"],
                    float(np.mean(expected)),
                    places=12,
                )
                self.assertAlmostEqual(
                    got["null_sd_mpd"],
                    float(np.std(expected,ddof=0)),
                    places=12,
                )

    def test_distinct_colocated_observed_units_are_valid(self):
        out=m.packing_from_trap_units(
            active_unit_ids=self.ids,
            active_unit_xy=self.xy,
            observed_unit_ids=["A","B","E"],
        )
        self.assertTrue(out["estimable"])
        self.assertEqual(out["n_individuals"],3)
        self.assertGreaterEqual(out["mpd_observed"],0.0)

    def test_duplicate_same_unit_fails_closed(self):
        out=m.packing_from_trap_units(
            active_unit_ids=self.ids,
            active_unit_xy=self.xy,
            observed_unit_ids=["A","A","E"],
        )
        self.assertFalse(out["estimable"])
        self.assertEqual(
            out["non_estimable_reason"],
            "duplicate_observed_trap_unit_id",
        )

    def test_missing_unit_fails_closed(self):
        out=m.packing_from_trap_units(
            active_unit_ids=self.ids,
            active_unit_xy=self.xy,
            observed_unit_ids=["A","Z","E"],
        )
        self.assertFalse(out["estimable"])
        self.assertEqual(
            out["non_estimable_reason"],
            "observed_trap_unit_not_active",
        )


if __name__=="__main__":
    unittest.main()
