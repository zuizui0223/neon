import unittest
from analysis.run_neon_capture_composition_season_v13 import prob,distance,predict,site_result,focal_result
class TestComposition(unittest.TestCase):
    def test_tv_and_simplex(self):
        a={'A':.8,'B':.2}
        self.assertAlmostEqual(distance(a,{'A':.5,'B':.5}),.3)
        self.assertAlmostEqual(sum(predict(a,{'A':.4,'B':-.4}).values()),1)
    def test_heldout_fixed(self):
        def row(y):
            return {'year':y,'counts':{'early':{'A':8,'B':2},'late':{'A':5,'B':5}}}
        x=site_result([row(2017),row(2021),row(2022)])
        self.assertAlmostEqual(x['baseline_TV'],.3)
        self.assertAlmostEqual(x['forecast_TV'],0)
        self.assertIsNone(site_result([row(2017),row(2022)]))
    def test_focal_bounds(self):
        def row(y):
            return {'year':y,'focal':{'early':{'PM':10,'MG_group':10,'unresolved_records':2},'late':{'PM':5,'MG_group':15,'unresolved_records':1}}}
        r=focal_result([row(2017),row(2018),row(2022)])
        self.assertLessEqual(r['test_bounds'][0],r['test_delta'])
        self.assertGreaterEqual(r['test_bounds'][1],r['test_delta'])
if __name__=='__main__':unittest.main()
