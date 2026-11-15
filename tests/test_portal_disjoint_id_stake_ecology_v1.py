"""Synthetic ecological outcome code checks. No Portal outcome or NEON response."""
from __future__ import annotations
import unittest
from analysis.run_portal_disjoint_id_stake_ecology_v1 import (
    remove_shared_individuals,station_collision_and_reference,STAKES
)
class DisjointRodentCaptureSpaceTests(unittest.TestCase):
    def test_shared_observed_id_is_excluded_both_years(self):
        a={"id01":11,"id02":12,"id03":13}
        b={"id01":11,"id04":14}
        x,y,n=remove_shared_individuals(a,b)
        self.assertEqual(n,1)
        self.assertEqual(x,{"id02":12,"id03":13})
        self.assertEqual(y,{"id04":14})
    def test_crossyear_collision_observed_vs_capture_reference(self):
        a=[11,12,13];b=[11,12,14]
        reference=[11,12,13,14]
        out=station_collision_and_reference(a,b,reference,reference)
        self.assertAlmostEqual(out["observed"],2/9)
        self.assertAlmostEqual(out["source_reference"],1/4)
        self.assertAlmostEqual(out["speciesblind"],2/9-1/4)
        self.assertAlmostEqual(out["uniform"],2/9-1/49)
    def test_all_stakes_49_uniform_reference_not_10m_or_grid_identity(self):
        self.assertEqual(len(STAKES),49)
        self.assertEqual(len(set(STAKES)),49)
        self.assertEqual(STAKES[0],11)
        self.assertEqual(STAKES[-1],77)
        out=station_collision_and_reference([11],[11],STAKES,STAKES)
        self.assertAlmostEqual(out["observed"],1)
        self.assertAlmostEqual(out["source_reference"],1/49)
    def test_nonequivalent_reference_can_reverse_the_excess(self):
        a=[11,12];b=[11,13]
        heavy=[11]*8+[12]+[13]
        out=station_collision_and_reference(a,b,heavy,heavy)
        self.assertGreater(out["uniform"],0)
        self.assertLess(out["speciesblind"],0)
    def test_missing_or_fabricated_stake_does_not_enter(self):
        with self.assertRaises(ValueError):
            station_collision_and_reference([11,99],[11],[11],[11])
        with self.assertRaises(ValueError):
            station_collision_and_reference([],[],[11],[11])
if __name__=="__main__":
    unittest.main()
