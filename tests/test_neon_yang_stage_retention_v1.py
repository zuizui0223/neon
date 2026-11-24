import unittest
from fractions import Fraction
from analysis.run_neon_yang_stage_retention_v1 import bounds,average_triplet,interval_sign,DESIGN,EXPECTED,PHYSICAL,resolve_pair,species,treatment,flag,summarize
class YangStageTests(unittest.TestCase):
    def test_source_roster(self):
        self.assertEqual(len(EXPECTED),45)
        self.assertEqual(len(PHYSICAL),42)
        self.assertEqual(resolve_pair(2018,'M','QS'),2)
        self.assertEqual(resolve_pair(2018,'M','CA'),6)
        with self.assertRaises(ValueError):resolve_pair(2018,'M','QV')
        self.assertEqual(len(DESIGN),6)
        self.assertEqual(species("Q. variabilis"),"QV")
        self.assertIsNone(treatment("1"))
        self.assertIsNone(flag("NA"))
    def test_explicit_na_bounds(self):
        a={"mixed":{"released":120,"cache":30,"cache_NA":5},"mono":{"released":120,"cache":10,"cache_NA":4}}
        d,lo,hi=bounds(a,"cache")
        self.assertEqual((d,lo,hi),(Fraction(20,120),Fraction(16,120),Fraction(25,120)))
        self.assertEqual(interval_sign((d,lo,hi)),1)
    def test_reversal_not_established_for_single_year_pair(self):
        b={}
        for g,y,p in EXPECTED:
            for s in DESIGN[g][0]:
                b[g,y,p,s]={"mixed":{"released":120,"removed":80,"removed_NA":0,"cache":40,"cache_NA":0,"winter":2,"winter_NA":0},
                          "mono":{"released":120,"removed":60,"removed_NA":0,"cache":20,"cache_NA":0,"winter":5,"winter_NA":0}}
        out=summarize(b)
        self.assertEqual(out["classification_counts"],{"REVERSED":12})
        self.assertEqual(out["strict_reversal_edges"],10)
if __name__=="__main__":unittest.main()
