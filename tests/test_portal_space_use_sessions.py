import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"build_portal_space_use_sessions_v1.py"
spec=importlib.util.spec_from_file_location("portal_sessions",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PortalSpaceUseSessionTests(unittest.TestCase):
    def setUp(self):
        self.species=[
            {"speciescode":"DM","scientificname":"Dipodomys merriami","censustarget":"1","unidentified":"0","rodent":"1"},
            {"speciescode":"PX","scientificname":"Chaetodipus/Peromyscus sp.","censustarget":"1","unidentified":"1","rodent":"1"},
            {"speciescode":"AH","scientificname":"Ammospermophilus harrisi","censustarget":"0","unidentified":"0","rodent":"1"},
        ]
        self.trapping=[
            {"year":"2010","month":"1","period":"100","plot":"1","sampled":"1","effort":"49","qcflag":"1"},
            {"year":"2010","month":"1","period":"100","plot":"2","sampled":"0","effort":"0","qcflag":"1"},
            {"year":"2010","month":"1","period":"100","plot":"3","sampled":"1","effort":"48","qcflag":"1"},
            {"year":"2010","month":"1","period":"100","plot":"4","sampled":"1","effort":"49","qcflag":"0"},
        ]
        self.plots=[
            {"year":"2010","month":"1","plot":"1","treatment":"control"},
            {"year":"2010","month":"1","plot":"2","treatment":"exclosure"},
            {"year":"2010","month":"1","plot":"3","treatment":"control"},
            {"year":"2010","month":"1","plot":"4","treatment":"exclosure"},
        ]

    def test_stake_geometry_uses_7x7_six_point_two_five_metre_grid(self):
        self.assertEqual(m.stake_xy("11"),(0.0,0.0))
        self.assertEqual(m.stake_xy("12"),(6.25,0.0))
        self.assertEqual(m.stake_xy("21"),(0.0,6.25))
        self.assertEqual(m.stake_xy("77"),(37.5,37.5))
        with self.assertRaises(ValueError):
            m.stake_xy("88")

    def test_primary_capture_filter_excludes_negative_period_and_non_target_taxa(self):
        captures=[
            {"recordID":"1","month":"1","year":"2010","period":"100","plot":"1","stake":"11","species":"DM","id":"a","pit_tag":"TRUE"},
            {"recordID":"2","month":"1","year":"2010","period":"-1","plot":"1","stake":"12","species":"DM","id":"b","pit_tag":"TRUE"},
            {"recordID":"3","month":"1","year":"2010","period":"100","plot":"1","stake":"13","species":"PX","id":"c","pit_tag":"TRUE"},
            {"recordID":"4","month":"1","year":"2010","period":"100","plot":"1","stake":"14","species":"AH","id":"d","pit_tag":"TRUE"},
        ]
        rows=m.filter_primary_capture_rows(captures,self.species)
        self.assertEqual([r["recordID"] for r in rows],["1"])

    def test_session_filter_requires_sampled_full_effort_qc_and_allowed_treatment(self):
        captures=[]
        rid=1
        for plot in ("1","2","3","4"):
            for stake,ind in zip(("11","12","13","14","15"),("a","b","c","d","e")):
                captures.append({"recordID":str(rid),"month":"1","year":"2010","period":"100","plot":plot,"stake":stake,"species":"DM","id":plot+ind,"pit_tag":"TRUE"})
                rid+=1
        rows=m.build_portal_sessions(
            captures,
            self.trapping,
            self.plots,
            self.species,
            replicates=99,
        )
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["plot_id"],"1")
        self.assertEqual(rows[0]["treatment"],"control")
        self.assertTrue(rows[0]["primary_n5_eligible"])

    def test_treatment_join_uses_exact_year_month_plot(self):
        captures=[
            {"recordID":str(i+1),"month":"1","year":"2010","period":"100","plot":"2","stake":str(11+i),"species":"DM","id":f"x{i}","pit_tag":"TRUE"}
            for i in range(5)
        ]
        trapping=[{"year":"2010","month":"1","period":"100","plot":"2","sampled":"1","effort":"49","qcflag":"1"}]
        rows=m.build_portal_sessions(captures,trapping,self.plots,self.species,replicates=99)
        self.assertEqual(rows[0]["treatment"],"exclosure")

    def test_duplicate_individual_is_counted_once_deterministically(self):
        captures=[
            {"recordID":"9","month":"1","year":"2010","period":"100","plot":"1","stake":"17","species":"DM","id":"same","pit_tag":"FALSE"},
            {"recordID":"2","month":"1","year":"2010","period":"100","plot":"1","stake":"11","species":"DM","id":"same","pit_tag":"TRUE"},
            {"recordID":"3","month":"1","year":"2010","period":"100","plot":"1","stake":"12","species":"DM","id":"b","pit_tag":"TRUE"},
            {"recordID":"4","month":"1","year":"2010","period":"100","plot":"1","stake":"13","species":"DM","id":"c","pit_tag":"TRUE"},
            {"recordID":"5","month":"1","year":"2010","period":"100","plot":"1","stake":"14","species":"DM","id":"d","pit_tag":"TRUE"},
            {"recordID":"6","month":"1","year":"2010","period":"100","plot":"1","stake":"15","species":"DM","id":"e","pit_tag":"FALSE"},
        ]
        rows=m.build_portal_sessions(captures,[self.trapping[0]],self.plots,self.species,replicates=99)
        row=rows[0]
        self.assertEqual(row["n_unique_individuals"],5)
        self.assertAlmostEqual(row["pit_reliable_fraction"],4/5)
        # lowest recordID for the duplicate individual is stake 11 and PIT-reliable
        self.assertEqual(row["unique_individual_capture_count"],5)

    def test_n_threshold_flags_are_prespecified(self):
        stakes=("11","12","13","14","15","16","17","21")
        captures=[
            {"recordID":str(i+1),"month":"1","year":"2010","period":"100","plot":"1","stake":stake,"species":"DM","id":f"x{i}","pit_tag":"TRUE"}
            for i,stake in enumerate(stakes)
        ]
        rows=m.build_portal_sessions(captures,[self.trapping[0]],self.plots,self.species,replicates=99)
        row=rows[0]
        self.assertTrue(row["sensitivity_n3_eligible"])
        self.assertTrue(row["primary_n5_eligible"])
        self.assertTrue(row["sensitivity_n8_eligible"])


    def test_inventory_counts_eligibility_and_treatment_replication(self):
        sessions=[
            {"species":"Dipodomys merriami","treatment":"control","n_unique_individuals":5,"primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False,"pit_reliable_fraction":1.0},
            {"species":"Dipodomys merriami","treatment":"exclosure","n_unique_individuals":8,"primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":True,"pit_reliable_fraction":0.75},
            {"species":"Perognathus flavus","treatment":"control","n_unique_individuals":3,"primary_n5_eligible":False,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False,"pit_reliable_fraction":0.5},
        ]
        inv=m.summarize_portal_sessions(sessions)
        self.assertEqual(inv["session_count"],3)
        self.assertEqual(inv["eligible_n3"],3)
        self.assertEqual(inv["eligible_n5"],2)
        self.assertEqual(inv["eligible_n8"],1)
        self.assertEqual(inv["species_treatment_session_counts"]["Dipodomys merriami"]["control"],1)
        self.assertEqual(inv["species_treatment_session_counts"]["Dipodomys merriami"]["exclosure"],1)
        self.assertAlmostEqual(inv["median_pit_reliable_fraction"],0.75)


if __name__=="__main__":
    unittest.main()
