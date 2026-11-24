import unittest
from analysis.run_neon_holt_acorn_preceding_upcoming_v1 import midranks,summer_date,evaluate,groups_for_window

class HoltFrozenTest(unittest.TestCase):
    def test_tied_rank(self):
        self.assertEqual(midranks({"a":0,"b":0,"c":5}),{"a":1/3,"b":1/3,"c":5/6})
    def test_dates(self):
        self.assertTrue(summer_date("1999-08-01",1999))
        self.assertFalse(summer_date("1998-08-01",1999))
        self.assertFalse(summer_date("1999-10-01",1999))
    def test_paired_positive_and_gate(self):
        # Alternating past/current rank maps, each year used station follows past.
        maps={1988:{"a":0.5,"b":0.5},1998:{"a":0.75,"b":0.25},1999:{"a":0.25,"b":0.75},2000:{"a":0.75,"b":0.25}}
        by={1999:[{1:{"a"},0:{"b"}}],2000:[{1:{"b"},0:{"a"}}]}
        o=evaluate(maps,by,ref_years=(1988,),min_years=2,min_groups_year=1,min_total=2)
        self.assertEqual(o["status"],"DESCRIPTIVE_PAST_RESOURCE_ASYMMETRY_SUPPORTED")
        self.assertEqual(o["effect"]["equal_year_difference"],1.0)
        self.assertIsNone(evaluate(maps,by,ref_years=(1988,),min_years=3,min_groups_year=1,min_total=2)["effect"])
    def test_bad_date_no_effect_and_no_ID_export(self):
        rows=[{"year":"1999","id_new":"PRIVATE_ID","STRAPSTAT":"a","used":"1","date":"1999-10-01"}]
        g,c,s=groups_for_window(rows,[{"year":"1999","id_new":"PRIVATE_ID"}],{"a"})
        self.assertIsNone(g);self.assertEqual(s,"STOP_ORIGINAL_SUMMER_DATE_ONTOLOGY")
        self.assertNotIn("PRIVATE_ID",str(c))
if __name__=="__main__":unittest.main()
