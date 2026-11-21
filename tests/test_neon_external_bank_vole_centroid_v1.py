"""Synthetic bank-vole seasonal centroid source tests, never use original field outcomes."""
from __future__ import annotations
from random import Random
import unittest
from analysis.run_neon_external_bank_vole_centroid_v1 import (
    centroid,distance,individual_reallocation,FACTOR_CELLS,FROZEN_N_BY_CELL
)
class BankVoleSeasonalCentroidTests(unittest.TestCase):
    def test_centroid_and_grid_coordinate_distance(self):
        self.assertEqual(centroid([(0,0),(2,0)]),(1,0))
        self.assertEqual(distance((0,0),(3,4)),5.)
    def test_same_location_all_seasons_does_not_move(self):
        a=[(2.,5.),(2.,5.)]
        z=individual_reallocation(a,a,Random(15),draws=100)
        self.assertEqual(z["observed"],0)
        self.assertEqual(z["reference"],0)
        self.assertEqual(z["excess"],0)
    def test_true_different_recorded_centroids_exceed_permutation(self):
        a=[(0.,0.),(0.,0.)];b=[(10.,0.),(10.,0.)]
        r=individual_reallocation(a,b,Random(9),draws=1000)
        self.assertAlmostEqual(r["observed"],10)
        self.assertGreater(r["excess"],0)
    def test_same_pooled_location_distribution_no_shift(self):
        a=[(0.,0.),(2.,0.)];b=[(0.,0.),(2.,0.)]
        r=individual_reallocation(a,b,Random(11),draws=1000)
        self.assertAlmostEqual(r["observed"],0)
        self.assertGreater(r["reference"],0)
        self.assertLess(r["excess"],0)
    def test_fixed_seed_reproduces_source_reallocation(self):
        a=[(0.,0.),(1.,1.),(2.,2.)];b=[(2.,0.),(4.,1.)]
        self.assertEqual(individual_reallocation(a,b,Random(42),draws=500),
                         individual_reallocation(a,b,Random(42),draws=500))
    def test_missing_and_nonfinite_coords_must_stop(self):
        with self.assertRaises(ValueError):
            individual_reallocation([(0.,0.)],[(0.,0.),(1.,1.)],Random(2))
        with self.assertRaises(ValueError):
            individual_reallocation([(float("nan"),0.),(1.,0.)],[(0.,0.),(0.,1.)],Random(2))
    def test_source_locked_cohort_size_and_four_factorial_groups(self):
        self.assertEqual(len(FACTOR_CELLS),4)
        self.assertEqual(sum(FROZEN_N_BY_CELL.values()),51)
        self.assertEqual(FROZEN_N_BY_CELL[("unfed","deworm")],8)
if __name__=="__main__":
    unittest.main()
