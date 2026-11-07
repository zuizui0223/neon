"""Original-mammal vs environmental pair-key crosswalk, synthetic test only."""
from __future__ import annotations
import unittest
from datetime import date
from analysis.neon_joint_environment_source_crosswalk_v1 import joint_source_crosswalk

def unit(site,plot,a,b):
    return {"site":site,"site_plot":(site,plot),
       "capture_dates_A":tuple(date(*d) for d in a),
       "capture_dates_B":tuple(date(*d) for d in b)}
A=[(2023,4,1),(2023,4,2),(2023,4,3)]
B=[(2023,7,1),(2023,7,2),(2023,7,3)]
C=[(2023,10,1),(2023,10,2),(2023,10,3)]
U=[unit("FAKE","P",A,B),unit("FAKE","P",B,C)]
M={"FAKE":["2023-04","2023-07","2023-10"]}
E={("FAKE","P"):{
   (date(2023,4,1),"e1"):True,
   (date(2023,7,1),"e2"):True,
   (date(2023,10,1),"e3"):True,
}}

class JointExactPairSourceTests(unittest.TestCase):
    def test_joint_matching_different_plant_visits(self):
        result=joint_source_crosswalk(U,M,E,expected_pairs=2,expected_sites=1,expected_plots=1)
        self.assertEqual(result["original_distinct_plot_capture_date_keys"],9)
        c=result["joint_source_support"]["within12__numeric365"]
        self.assertEqual(c["original_season_pairs"],2)
        self.assertEqual(c["independent_physical_sites"],1)
        self.assertEqual(c["original_mammal_grid_plotIDs"],1)
        self.assertFalse(c["source_minimum_met"])
        self.assertTrue(result["same_plotID_plant_base_plot_not_actual_mammal_trap_habitat"])
        self.assertNotIn("FAKE",str(result))
    def test_single_field_event_cannot_be_recycled(self):
        one={("FAKE","P"):{(date(2023,7,1),"e2"):True}}
        r=joint_source_crosswalk(U,M,one,expected_pairs=2,expected_sites=1,expected_plots=1)
        self.assertEqual(r["joint_source_support"]["within12__numeric365"]["original_season_pairs"],0)
    def test_metadata_month_and_field_window_are_strict(self):
        bad={"FAKE":["2013-03"]}
        r=joint_source_crosswalk(U,bad,E,expected_pairs=2,expected_sites=1,expected_plots=1)
        self.assertEqual(r["joint_source_support"]["within12__numeric365"]["original_season_pairs"],0)
    def test_missing_cover_does_not_impute_zero_cover_or_reuse(self):
        none={("FAKE","P"):{(date(2023,4,1),"e1"):False,(date(2023,7,1),"e2"):True}}
        r=joint_source_crosswalk([U[0]],M,none,expected_pairs=1,expected_sites=1,expected_plots=1)
        self.assertEqual(r["joint_source_support"]["within12__numeric365"]["original_season_pairs"],0)
    def test_geographic_denominator_drift_is_error(self):
        with self.assertRaises(ValueError):
            joint_source_crosswalk(U,M,E,expected_pairs=2,expected_sites=2,expected_plots=1)
    def test_duplicate_source_season_keys_not_double_counted(self):
        with self.assertRaises(ValueError):
            joint_source_crosswalk([U[0],U[0]],M,E,expected_pairs=2,expected_sites=1,expected_plots=1)

if __name__=="__main__":
    unittest.main()
