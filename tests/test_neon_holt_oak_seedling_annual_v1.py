import unittest
import numpy as np
from analysis.run_neon_holt_oak_seedling_annual_v1 import plant_annual,analyze,YEARS

class HoltAnnualTest(unittest.TestCase):
    def test_constant_plot_and_duplicate_guard(self):
        def row(y,p,ht="1"):return {"YEAR":str(y),"LINE":"N","PLOT":str(p),"SPEC":"5","FIASP":"833","HT1":ht}
        yrs=(1988,1989)
        seed=[row(y,p) for y in yrs for p in (1,11,21)]
        seedlings=[row(y,p) for y in yrs for p in (1,11,21)]+[row(1988,21)]
        ys,s=plant_annual(seed,seedlings,years=yrs,min_plots=2)
        self.assertEqual(s["fixed_surveyed_plots"],2)
        self.assertEqual(s["excluded_entire_plots_duplicate_oak_key"],1)
        self.assertEqual(ys,{1988:100,1989:100})
    def test_frozen_positive_interaction_synthetic(self):
        rng=np.random.default_rng(78)
        a=rng.normal(size=(len(YEARS),5));a[:,0]=np.arange(len(YEARS))
        std=(a-a.mean(0))/a.std(0)
        response=3+0.1*std[:,0]+0.2*std[:,1]+0.1*std[:,2]+0.1*std[:,3]-0.3*std[:,4]+0.25*std[:,1]*std[:,4]
        out=analyze(dict(zip(YEARS,np.expm1(response))),dict(zip(YEARS,a.tolist())))
        self.assertEqual(out["status"],"DESCRIPTIVE_DELAYED_CONSUMER_PATTERN_SUPPORTED")
        self.assertLess(out["effect"]["low_seed_mouse_slope_at_minus_1SD"],0)
        self.assertGreater(out["effect"]["mouse_by_seed_interaction"],0)
    def test_support_stop(self):
        self.assertIsNone(analyze({1988:1},{1988:[1,1,1,1,1]})["effect"])
if __name__=="__main__":unittest.main()
