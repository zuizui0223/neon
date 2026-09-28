import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"mammal_sex_packing_estimability_v1.py"
spec=importlib.util.spec_from_file_location("sexpack",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MammalSexPackingEstimabilityTests(unittest.TestCase):
    def test_heteromyid_scope_is_frozen_by_genus(self):
        for name in (
            "Chaetodipus penicillatus",
            "Dipodomys merriami",
            "Perognathus flavus",
            "Microdipodops megacephalus",
        ):
            self.assertTrue(m.is_heteromyid(name))
        for name in (
            "Peromyscus maniculatus",
            "Sigmodon hispidus",
            "Neotoma albigula",
            "Chaetodipus sp.",
            "",
        ):
            self.assertFalse(m.is_heteromyid(name))

    def test_sex_normalization(self):
        for value in ("M","m","male","Male","1 - Male"):
            self.assertEqual(m.normalize_sex(value),"M")
        for value in ("F","f","female","Female","2 - Female"):
            self.assertEqual(m.normalize_sex(value),"F")
        for value in ("","U","unknown","3 - Unknown",None):
            self.assertIsNone(m.normalize_sex(value))

    def test_sex_count_record_deduplicates_individuals(self):
        rows=[
            {"id":"a","sex":"M","pit_tag":"TRUE"},
            {"id":"a","sex":"M","pit_tag":"TRUE"},
            {"id":"b","sex":"F","pit_tag":"FALSE"},
            {"id":"c","sex":"U","pit_tag":"TRUE"},
            {"id":"d","sex":"F","pit_tag":"TRUE"},
        ]
        out=m.sex_count_record(rows,id_field="id",pit_field="pit_tag")
        self.assertEqual(out["n_total"],4)
        self.assertEqual(out["n_known_sex"],3)
        self.assertEqual(out["n_male"],1)
        self.assertEqual(out["n_female"],2)
        self.assertAlmostEqual(out["known_sex_fraction"],3/4)
        self.assertAlmostEqual(out["pit_reliable_fraction"],3/4)

    def test_paired_threshold_flags(self):
        rows=[]
        for i in range(5):
            rows.append({"id":f"m{i}","sex":"M"})
        for i in range(3):
            rows.append({"id":f"f{i}","sex":"F"})
        out=m.sex_count_record(rows,id_field="id")
        self.assertTrue(out["paired_n2_eligible"])
        self.assertTrue(out["paired_n3_eligible"])
        self.assertFalse(out["paired_n5_eligible"])

    def test_species_summary_counts_sessions_and_replicates(self):
        sessions=[
            {"species":"Dipodomys ordii","plot_id":"1","site":"Portal","paired_n3_eligible":True,"paired_n2_eligible":True,"paired_n5_eligible":False,"known_sex_fraction":1.0},
            {"species":"Dipodomys ordii","plot_id":"2","site":"Portal","paired_n3_eligible":True,"paired_n2_eligible":True,"paired_n5_eligible":True,"known_sex_fraction":0.9},
            {"species":"Chaetodipus penicillatus","plot_id":"1","site":"Portal","paired_n3_eligible":False,"paired_n2_eligible":True,"paired_n5_eligible":False,"known_sex_fraction":0.8},
        ]
        out=m.summarize_sex_estimability(sessions,source="Portal")
        self.assertEqual(out["session_count"],3)
        self.assertEqual(out["paired_n2_sessions"],3)
        self.assertEqual(out["paired_n3_sessions"],2)
        self.assertEqual(out["paired_n5_sessions"],1)
        self.assertEqual(out["species"]["Dipodomys ordii"]["paired_n3_sessions"],2)
        self.assertEqual(out["species"]["Dipodomys ordii"]["independent_plots"],2)
        self.assertAlmostEqual(out["median_known_sex_fraction"],0.9)


if __name__=="__main__":
    unittest.main()
