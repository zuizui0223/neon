import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"build_portal_sex_packing_inventory_v1.py"
spec=importlib.util.spec_from_file_location("portal_sex",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PortalSexPackingInventoryTests(unittest.TestCase):
    def setUp(self):
        self.species=[
            {"speciescode":"PP","scientificname":"Chaetodipus penicillatus","censustarget":"1","unidentified":"0","rodent":"1"},
            {"speciescode":"DM","scientificname":"Dipodomys merriami","censustarget":"1","unidentified":"0","rodent":"1"},
            {"speciescode":"PX","scientificname":"Chaetodipus/Peromyscus sp.","censustarget":"1","unidentified":"1","rodent":"1"},
            {"speciescode":"PE","scientificname":"Peromyscus eremicus","censustarget":"1","unidentified":"0","rodent":"1"},
        ]

    def test_primary_portal_sex_sessions_use_all_positive_qc_complete_periods(self):
        captures=[
            {"recordID":"1","year":"1980","month":"1","period":"10","plot":"1","stake":"11","species":"PP","id":"a","sex":"M","pit_tag":"TRUE"},
            {"recordID":"2","year":"1980","month":"1","period":"10","plot":"1","stake":"12","species":"PP","id":"b","sex":"M","pit_tag":"TRUE"},
            {"recordID":"3","year":"1980","month":"1","period":"10","plot":"1","stake":"13","species":"PP","id":"c","sex":"M","pit_tag":"FALSE"},
            {"recordID":"4","year":"1980","month":"1","period":"10","plot":"1","stake":"14","species":"PP","id":"d","sex":"F","pit_tag":"TRUE"},
            {"recordID":"5","year":"1980","month":"1","period":"10","plot":"1","stake":"15","species":"PP","id":"e","sex":"F","pit_tag":"TRUE"},
            {"recordID":"6","year":"1980","month":"1","period":"10","plot":"1","stake":"16","species":"PP","id":"f","sex":"F","pit_tag":"TRUE"},
            {"recordID":"7","year":"1980","month":"1","period":"10","plot":"1","stake":"17","species":"PP","id":"g","sex":"U","pit_tag":"TRUE"},
        ]
        trapping=[
            {"year":"1980","month":"1","period":"10","plot":"1","sampled":"1","effort":"49","qcflag":"1"},
        ]
        rows=m.build_portal_sex_sessions(captures,trapping,self.species)
        self.assertEqual(len(rows),1)
        row=rows[0]
        self.assertEqual(row["species"],"Chaetodipus penicillatus")
        self.assertEqual(row["n_total"],7)
        self.assertEqual(row["n_male"],3)
        self.assertEqual(row["n_female"],3)
        self.assertTrue(row["paired_n3_eligible"])
        self.assertFalse(row["paired_n5_eligible"])
        self.assertAlmostEqual(row["known_sex_fraction"],6/7)
        self.assertAlmostEqual(row["pit_reliable_fraction"],6/7)

    def test_negative_period_bad_effort_and_nonheteromyids_are_excluded(self):
        captures=[
            {"recordID":"1","year":"2010","month":"1","period":"-1","plot":"1","stake":"11","species":"PP","id":"a","sex":"M","pit_tag":"TRUE"},
            {"recordID":"2","year":"2010","month":"1","period":"20","plot":"2","stake":"11","species":"DM","id":"b","sex":"F","pit_tag":"TRUE"},
            {"recordID":"3","year":"2010","month":"1","period":"21","plot":"3","stake":"11","species":"PE","id":"c","sex":"M","pit_tag":"TRUE"},
        ]
        trapping=[
            {"year":"2010","month":"1","period":"-1","plot":"1","sampled":"1","effort":"49","qcflag":"1"},
            {"year":"2010","month":"1","period":"20","plot":"2","sampled":"1","effort":"48","qcflag":"1"},
            {"year":"2010","month":"1","period":"21","plot":"3","sampled":"1","effort":"49","qcflag":"1"},
        ]
        self.assertEqual(m.build_portal_sex_sessions(captures,trapping,self.species),[])

    def test_duplicate_individual_is_counted_once(self):
        captures=[
            {"recordID":"9","year":"2010","month":"1","period":"30","plot":"1","stake":"17","species":"DM","id":"same","sex":"M","pit_tag":"FALSE"},
            {"recordID":"2","year":"2010","month":"1","period":"30","plot":"1","stake":"11","species":"DM","id":"same","sex":"M","pit_tag":"TRUE"},
            {"recordID":"3","year":"2010","month":"1","period":"30","plot":"1","stake":"12","species":"DM","id":"b","sex":"F","pit_tag":"TRUE"},
        ]
        trapping=[{"year":"2010","month":"1","period":"30","plot":"1","sampled":"1","effort":"49","qcflag":"1"}]
        rows=m.build_portal_sex_sessions(captures,trapping,self.species)
        self.assertEqual(rows[0]["n_total"],2)
        self.assertEqual(rows[0]["n_male"],1)
        self.assertEqual(rows[0]["n_female"],1)
        self.assertAlmostEqual(rows[0]["pit_reliable_fraction"],1.0)

    def test_inventory_reports_species_plot_replication_only(self):
        sessions=[
            {"species":"Chaetodipus penicillatus","plot_id":"1","year":2010,"paired_n2_eligible":True,"paired_n3_eligible":True,"paired_n5_eligible":False,"known_sex_fraction":1.0,"pit_reliable_fraction":0.9},
            {"species":"Chaetodipus penicillatus","plot_id":"2","year":2011,"paired_n2_eligible":True,"paired_n3_eligible":True,"paired_n5_eligible":True,"known_sex_fraction":0.9,"pit_reliable_fraction":0.8},
            {"species":"Dipodomys merriami","plot_id":"1","year":2010,"paired_n2_eligible":True,"paired_n3_eligible":False,"paired_n5_eligible":False,"known_sex_fraction":0.8,"pit_reliable_fraction":0.7},
        ]
        inv=m.summarize_portal_sex_sessions(sessions)
        self.assertEqual(inv["paired_n3_sessions"],2)
        self.assertEqual(inv["species"]["Chaetodipus penicillatus"]["paired_n3_sessions"],2)
        self.assertEqual(inv["species"]["Chaetodipus penicillatus"]["independent_plots"],2)
        self.assertEqual(inv["ecological_effects_inspected"],False)


if __name__=="__main__":
    unittest.main()
