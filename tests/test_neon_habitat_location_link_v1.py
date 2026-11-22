import json
import unittest
from analysis.neon_habitat_location_link_v1 import (
    capture_named_locations, current_projected_location, grid_anchor_geometry,
    source_grid_issue_summary,
)

class HabitatLocationLinkTests(unittest.TestCase):
    def test_named_locations_from_actual_source_only(self):
        raw=b'nightuid,plotID,namedLocation\nn1,TEST_001,TEST_001.mammalGrid.mam\nn2,TEST_002,TEST_002.mammalGrid.mam\n'
        out=capture_named_locations(raw,{'n1'})
        self.assertEqual(out,{'TEST_001':{'TEST_001.mammalGrid.mam'}})
        with self.assertRaisesRegex(ValueError,'namedLocation'):
            capture_named_locations(b'nightuid,plotID\nn1,TEST_001\n',{'n1'})
    def test_ragged_source_rejected(self):
        with self.assertRaisesRegex(ValueError,'ragged'):
            capture_named_locations(b'nightuid,plotID,namedLocation\na,b\n',{'a'})
    def test_exact_location_identity_and_one_current_history(self):
        body={'data':{'locationName':'SECRET.A1','locationHistory':[
            {'current':False,'locationUtmEasting':2,'locationUtmNorthing':4},
            {'current':True,'locationUtmEasting':100,'locationUtmNorthing':200,
             'locationUtmZone':18,'locationUtmHemisphere':'N',
             'locationProperties':[{'locationPropertyName':'Value for Coordinate uncertainty','locationPropertyValue':'2.5'}]}
        ]}}
        got=current_projected_location(body,'SECRET.A1')
        self.assertEqual(got['xy'],(100.,200.))
        self.assertEqual(got['uncertainty_m'],2.5)
        self.assertEqual(got['history_records'],2)
        self.assertFalse(got['historic_capture_date_link_verified'])
        with self.assertRaisesRegex(ValueError,'identity'):
            current_projected_location(body,'OTHER.A1')
    def test_missing_uncertainty_not_zero(self):
        body={'data':{'locationName':'TEST.A1','locationUtmEasting':100,'locationUtmNorthing':200,'locationUtmZone':18,'locationUtmHemisphere':'N'}}
        got=current_projected_location(body,'TEST.A1')
        self.assertIsNone(got['uncertainty_m'])
        self.assertNotIn('TEST',str(got))
    def test_multiple_current_records_rejected(self):
        b={'data':{'locationName':'X','locationHistory':[{'current':True},{'current':True}]}}
        with self.assertRaisesRegex(ValueError,'unique current'):
            current_projected_location(b,'X')
    def test_anchor_orientation_and_no_coordinates_exported(self):
        p={'A1':(500,600),'A10':(500,510),'J1':(410,600),'J10':(410,510),'E5':(460,560)}
        a=grid_anchor_geometry(p)
        self.assertTrue(a['five_anchor_rectangular_geometry'])
        self.assertTrue(a['standard_A10_south_J1_west_orientation'])
        self.assertEqual(a['edge_A1_A10_m'],90.)
        self.assertFalse(a['all_100_station_geolocations_verified'])
        self.assertNotIn('500',str(a))
        p['A10'],p['J1']=p['J1'],p['A10']
        self.assertFalse(grid_anchor_geometry(p)['standard_A10_south_J1_west_orientation'])
    def test_incomplete_or_nonfinite_coords_not_inferred(self):
        with self.assertRaisesRegex(ValueError,'five'):
            grid_anchor_geometry({'A1':(0,0)})
        p={s:(0,float('nan')) for s in ('A1','A10','J1','J10','E5')}
        with self.assertRaisesRegex(ValueError,'finite'):
            grid_anchor_geometry(p)
    def test_issue_count_uses_grid_not_whole_site(self):
        r=source_grid_issue_summary({('BLAN','BLAN_003'),('BLAN','BLAN_999'),('TEAK','TEAK_004')})
        self.assertEqual(r['original_plots'],3)
        self.assertEqual(r['historically_affected_grids'],2)
        self.assertEqual(r['special_layout_grids'],1)
        self.assertFalse(r['nominal_recurrence_invalidated'])
        self.assertNotIn('BLAN',str(r))
        with self.assertRaisesRegex(ValueError,'site'):
            source_grid_issue_summary({('X','BLAN_003')})

if __name__=='__main__': unittest.main()
