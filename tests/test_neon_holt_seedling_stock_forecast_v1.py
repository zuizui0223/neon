import unittest
from unittest.mock import patch
import numpy as np
from analysis.run_neon_holt_seedling_stock_forecast_v1 import stock_support,predict,fit,YEARS

class StockForecastTests(unittest.TestCase):
    def row(self,y,p,ht="2"):
        return {"YEAR":str(y),"LINE":"N","PLOT":str(p),"FIASP":"833","SPEC":"5","HT1":ht}
    def test_latest_census_not_replaced_after_duplicate(self):
        rows=[self.row(y,p) for y in (1987,1988,1989) for p in (1,11)]
        rows.append(self.row(1988,11))
        stock,audit=stock_support(rows,{("N",1),("N",11)},years=(1988,1989,1990))
        self.assertIn(1988,stock)
        self.assertNotIn(1989,stock)
        self.assertEqual(audit["1989"]["previous_year"],1988)
        self.assertEqual(audit["1989"]["status"],"DUPLICATE_LITERAL_OAK")
        self.assertIn(1990,stock)
    def test_past_only_training_and_fixed_ridge(self):
        rng=np.random.default_rng(84)
        cov={y:[y,*rng.normal(size=4)] for y in YEARS}
        stock={y:(float(rng.normal(2,0.2)),1) for y in YEARS}
        ys={y:float(np.exp(2+0.3*cov[y][1]-0.4*cov[y][4]+0.2*cov[y][1]*cov[y][4])-1) for y in YEARS}
        seen=[]
        def audit_fit(x,z,aug):
            seen.append(tuple(x[:,0].astype(int)))
            return fit(x,z,aug)
        with patch("analysis.run_neon_holt_seedling_stock_forecast_v1.fit",side_effect=audit_fit):
            out=predict(ys,cov,stock)
        self.assertIsNotNone(out["effect"])
        self.assertEqual(seen[0],YEARS) # descriptive coefficient fit only
        for i,y in enumerate(out["prediction_years"]):
            self.assertEqual(seen[1+2*i],tuple(v for v in YEARS if v<y))
            self.assertEqual(seen[2+2*i],seen[1+2*i])
    def test_missing_years_stop(self):
        self.assertIsNone(predict({1988:1},{1988:[1988,1,1,1,1]},{1988:(1,1)})["effect"])
if __name__=="__main__":unittest.main()
