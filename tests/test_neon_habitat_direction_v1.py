"""Synthetic direction diagnostics; no observed habitat outcome or raw source points."""
import unittest
from analysis.neon_habitat_location_link_v1 import grid_anchor_geometry


class ActualSourceDirectionTests(unittest.TestCase):
    def test_other_orientation_is_reported_not_relabelled(self):
        source={'A1':(100,200),'A10':(190,200),'J1':(100,290),
                'J10':(190,290),'E5':(140,240)}
        r=grid_anchor_geometry(source)
        self.assertTrue(r['five_anchor_rectangular_geometry'])
        self.assertEqual(r['A1_to_A10_dominant_direction'],'east')
        self.assertEqual(r['A1_to_J1_dominant_direction'],'north')
        self.assertFalse(r['standard_A10_south_J1_west_orientation'])
        self.assertFalse(r['coordinates_rotated_or_relabelled'])
        self.assertFalse(r['historical_location_assignment_verified'])


if __name__=='__main__':unittest.main()
