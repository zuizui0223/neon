import unittest
from datetime import date
from analysis.run_neon_seedfall_prior_autumn_spring_pregnancy_v1 import resource_pair,spring_pair,aggregate
class SeedfallPregnancyTests(unittest.TestCase):
    def test_fixed_matched_traps(self):
        g={}
        for i in range(3):
            ident=("p"+str(i),"Elevated","l"+str(i),"0.5")
            for y,w in [(2017,1),(2018,2)]:
                g["s",y,str(i)]=(set(range(60)),w,ident)
        self.assertEqual(resource_pair(g,"s",2019),(1,3))
        g["s",2018,"0"]=(set(range(20)),2,g["s",2018,"0"][2])
        self.assertIsNone(resource_pair(g,"s",2019))
    def test_spring_status_first_and_calendar(self):
        obs={}
        for y,n in [(2018,2),(2019,6)]:
            d=date(y,4,15)
            obs["s",y,"p"]=(d,[(d,str(i),"sp","pregnant" if i<n else "not") for i in range(10)])
        v,p=spring_pair(obs,"s",2019)
        self.assertAlmostEqual(v["sp"][0],.4)
        self.assertEqual(p,1)
        obs["s",2019,"p"]=(date(2019,5,15),obs["s",2019,"p"][1])
        self.assertEqual(spring_pair(obs,"s",2019),({},0))
    def test_thin_support_not_claimed_positive(self):
        self.assertEqual(aggregate([])["status"],"NO_ELIGIBLE_PAIRED_COMPARISON")
        x={"aligned_RD":.2,"unknown_status_lower":.1,"unknown_status_upper":.3,"n":3,"year_pairs":2,"n_positive":3,"n_zero":0}
        self.assertEqual(aggregate([x])["status"],"DESCRIPTIVE_ONLY_THIN_SUPPORT")
        self.assertEqual(aggregate([x.copy() for _ in range(8)])["status"],"EXPLORATORY_DIRECTION_SUPPORTED")
if __name__=="__main__":unittest.main()
