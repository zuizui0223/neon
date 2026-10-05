import unittest
from analysis.audit_san_jacinto_cross_season_turnover_support_v1 import season, nightly_first

class TestCrossSeasonTurnoverSupport(unittest.TestCase):
    def test_seasons(self):
        self.assertEqual(season(9),"fall")
        self.assertEqual(season(12),"winter")
        self.assertEqual(season(3),"spring")
        self.assertEqual(season(6),"summer")

    def test_nightly_first(self):
        rows=[
          {"species":"PEMA","grid":"1","unique_ID":"x","date":"09/01/2015","time":"8:00","flag":"A1"},
          {"species":"PEMA","grid":"1","unique_ID":"x","date":"09/01/2015","time":"10:00","flag":"A2"},
          {"species":"PEMA","grid":"1","unique_ID":"x","date":"12/01/2015","time":"8:00","flag":"B1"},
        ]
        z=nightly_first(rows)
        self.assertEqual(len(z),2)
        self.assertEqual({r["flag"] for r in z},{"A1","B1"})

if __name__=="__main__": unittest.main()
