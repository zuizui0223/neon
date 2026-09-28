from __future__ import annotations

import unittest

import numpy as np

from analysis import mammal_sex_effects_phase3_v1 as m


class SexEffectHelperTests(unittest.TestCase):
    def test_delta_is_difference_of_exact_z_scores(self):
        traps=np.asarray([
            (0.0,0.0),(1.0,0.0),(2.0,0.0),
            (0.0,1.0),(1.0,1.0),(2.0,1.0),
            (0.0,2.0),(1.0,2.0),(2.0,2.0),
        ])
        male=traps[[0,2,8]]
        female=traps[[3,4,5]]
        out=m.sex_packing_effect(traps,male,female)
        self.assertTrue(out["estimable"])
        self.assertAlmostEqual(
            out["delta_sex_packing"],
            out["packing_z_male"]-out["packing_z_female"],
            places=12,
        )

    def test_cross_sex_duplicate_location_fails_closed(self):
        traps=np.asarray([(0.,0.),(1.,0.),(0.,1.),(1.,1.),(2.,0.),(2.,1.)])
        male=np.asarray([(0.,0.),(1.,0.),(2.,0.)])
        female=np.asarray([(0.,0.),(1.,1.),(2.,1.)])
        out=m.sex_packing_effect(traps,male,female)
        self.assertFalse(out["estimable"])
        self.assertEqual(
            out["non_estimable_reason"],
            "duplicate_retained_trap_location",
        )


if __name__=="__main__":
    unittest.main()
