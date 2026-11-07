"""Synthetic independent camera source: station / season / genus validity."""
from __future__ import annotations
import unittest
from datetime import date
from analysis.neon_camera_independent_source_gate_v1 import (
    parse_deployments,parse_camera_sequences,candidate_e5_pairs,
    exact_station_camera_sources,haversine_m
)

def deployment_csv():
    return ("deployment_id,latitude,longitude,start_date,end_date,subproject_name\n"
            "c1,36,-80,2022-04-01,2022-09-30,Candidate forest\n"
            "c2,36.02,-80,2022-04-01,2022-04-30,Far away\n").encode()
def unit():
    A=(date(2022,4,1),date(2022,4,2),date(2022,4,3))
    B=(date(2022,9,1),date(2022,9,2),date(2022,9,3))
    return {"site":"SYNTH","site_plot":("SYNTH","P"),"capture_dates_A":A,"capture_dates_B":B}
class IndependentCameraSourceTests(unittest.TestCase):
    def test_cameras_hardware_and_genus_labels_not_unknown_small_mammals(self):
        dep,_=parse_deployments(deployment_csv())
        self.assertEqual(len(dep),2)
        src=("deployment_id,sequence_id,class,order,family,genus,common_name,start_time\n"
             "c1,seq1,Mammalia,Rodentia,Cricetidae,Peromyscus,Deer Mouse,4/1/22 01:02\n"
             "c1,seq2,Mammalia,Rodentia,Cricetidae,Peromyscus,Deer Mouse,9/1/22 01:02\n"
             "c1,seq3,Mammalia,NA,NA,NA,Small Mammal,4/2/22 01:02\n"
             "c1,seq4,Mammalia,Rodentia,Sciuridae,Sciurus,Squirrel,4/3/22 01:02\n").encode()
        r=parse_camera_sequences(src,dep)
        self.assertEqual(r["census"]["target_small_rodent_genus_sequences"],2)
        self.assertEqual(r["census"]["unidentified_small_mammal_sequences"],1)
        self.assertEqual(len(r["small_rodent_genus_by_deployment_day"]),2)
    def test_verified_same_station_not_plot_nearby(self):
        dep,_=parse_deployments(deployment_csv())
        coords={("SYNTH","P"):(36,-80)}
        report,near=candidate_e5_pairs([unit()],coords,dep,
            expected_pairs=1,expected_sites=1,expected_plots=1)
        self.assertEqual(report["camera_plot_links_E5_250m_with_capture_day_overlap"],1)
        self.assertEqual(len(near[("SYNTH","P")]),1)
        real=[(36.0,-80.0)]*100
        gen={("c1",date(2022,4,1)):{"Peromyscus"},
             ("c1",date(2022,9,1)):{"Peromyscus"}}
        result=exact_station_camera_sources([unit()],{("SYNTH","P"):real},
            dep,near,gen,expected_pairs=1)
        self.assertEqual(result["source_observation_support"]["original_pairs_with_camera_rodent_genus_detected_both_seasons"],1)
        self.assertEqual(result["source_observation_support"]["original_pairs_with_at_least_2_camera_rodent_genera_shared_A_B"],0)
        self.assertFalse(result["strict_source_20pair_8site_12plot_two_genus_GO"])
    def test_camera_a_kilometer_away_is_not_station_use(self):
        dep,_=parse_deployments(deployment_csv())
        report,near=candidate_e5_pairs([unit()],{("SYNTH","P"):(37,-80)},
            dep,expected_pairs=1,expected_sites=1,expected_plots=1)
        self.assertEqual(report["camera_plot_links_E5_250m_with_capture_day_overlap"],0)
        self.assertEqual(len(near),0)
    def test_source_coordinates_not_derived_from_camera_bounds(self):
        self.assertAlmostEqual(haversine_m(36,-80,36,-80),0)
        self.assertGreater(haversine_m(36,-80,36.02,-80),2000)
    def test_invalid_camera_deployment_never_becomes_null_detection(self):
        dep,_=parse_deployments(
            b"deployment_id,latitude,longitude,start_date,end_date,subproject_name\n"
            b"c1,not_a_lat,-80,2022-04-01,2022-05-01,X\n"
        )
        self.assertFalse(dep["c1"]["valid"])
    def test_duplicate_deployment_id_rejected(self):
        raw=deployment_csv()+b"c1,36,-80,2022-04-01,2022-09-30,X\n"
        with self.assertRaises(ValueError):
            parse_deployments(raw)

if __name__=="__main__":
    unittest.main()
