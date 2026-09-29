from __future__ import annotations

import itertools
import unittest

import numpy as np

from analysis import finite_slot_packing_exact_v1 as m


class FiniteSlotPackingTests(unittest.TestCase):
    def setUp(self):
        self.slots=np.asarray([
            (0.,0.),(0.,0.),
            (1.,0.),(1.,0.),
            (2.,0.),(2.,0.),
        ])

    def exhaustive(self,n):
        values=[]
        for indices in itertools.combinations(range(len(self.slots)),n):
            values.append(
                m.mean_pairwise_distance(self.slots[list(indices)])
            )
        return np.asarray(values,dtype=float)

    def test_exact_moments_match_slot_enumeration_with_duplicate_coordinates(self):
        for n in (2,3,4,5):
            with self.subTest(n=n):
                expected=self.exhaustive(n)
                got=m.exact_slot_null_moments(self.slots,n)
                self.assertAlmostEqual(
                    got["mean"],float(np.mean(expected)),places=12
                )
                self.assertAlmostEqual(
                    got["sd"],float(np.std(expected,ddof=0)),places=12
                )

    def test_two_animals_can_share_station_when_two_slots_exist(self):
        observed=np.asarray([(0.,0.),(0.,0.),(2.,0.)])
        support=m.support_check(observed,self.slots)
        self.assertTrue(support["supported"])
        out=m.packing_score_exact_slots(observed,self.slots)
        self.assertTrue(out["estimable"])

    def test_three_animals_at_two_slot_station_fail_closed(self):
        observed=np.asarray([(0.,0.),(0.,0.),(0.,0.)])
        support=m.support_check(observed,self.slots)
        self.assertFalse(support["supported"])
        out=m.packing_score_exact_slots(observed,self.slots)
        self.assertFalse(out["estimable"])
        self.assertEqual(
            out["non_estimable_reason"],
            "observed_coordinate_multiplicity_exceeds_trap_slot_capacity",
        )

    def test_null_mean_is_independent_of_sample_size(self):
        means=[
            m.exact_slot_null_moments(self.slots,n)["mean"]
            for n in (2,3,4,5)
        ]
        self.assertLess(max(means)-min(means),1e-12)


if __name__=="__main__":
    unittest.main()
