import unittest
from datetime import date
from analysis.run_neon_holt_acorn_date_repair_v2 import literal_candidates,date_diagnosis

class DateRepairTests(unittest.TestCase):
    def row(self,v,**kw):
        return {"year":"1999","id_new":"PRIVATE","STRAPSTAT":"S1","used":"1","date":v,**kw}
    def test_explicit_dates_and_century(self):
        self.assertEqual(literal_candidates("12-Aug-99",1999),{date(1999,8,12)})
        self.assertEqual(literal_candidates("1999-08-12",1999),{date(1999,8,12)})
        self.assertFalse(literal_candidates("36000",1999))
        self.assertFalse(literal_candidates("1998-08-12",1999))
    def test_no_season_based_ambiguity_resolution(self):
        v="08/05/99"
        self.assertEqual(literal_candidates(v,1999),{date(1999,8,5),date(1999,5,8)})
        _,d=date_diagnosis([self.row(v)],[])
        self.assertEqual(d["counts"]["unresolved_used_dates"],1)
    def test_exact_history_crosswalk(self):
        row=self.row("08/05/99")
        repaired,d=date_diagnosis([row],[self.row("08/05/99",date2="1999-08-05")])
        self.assertEqual(repaired[0]["date"],"1999-08-05")
        self.assertEqual(d["counts"]["resolved_used_dates"],1)
        _,d=date_diagnosis([row],[self.row("08/05/99",STRAPSTAT="S2",date2="1999-08-05")])
        self.assertEqual(d["counts"]["unresolved_used_dates"],1)
        self.assertNotIn("PRIVATE",str(d))
    def test_date2_contradiction_fails(self):
        _,d=date_diagnosis([self.row("1999-08-05")],[self.row("1999-08-05",date2="1999-08-06")])
        self.assertEqual(d["counts"]["unresolved_used_dates"],1)
    def test_outside_summer_not_reclassified(self):
        _,d=date_diagnosis([self.row("1999-04-05")],[])
        self.assertEqual(d["counts"]["resolved_outside_frozen_summer"],1)
if __name__=="__main__":unittest.main()
