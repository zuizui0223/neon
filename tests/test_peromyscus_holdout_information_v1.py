import unittest
from analysis.audit_peromyscus_holdout_information_v1 import information

class HoldoutInformationTests(unittest.TestCase):
    def test_partial_MNKA_information_and_slope_recovered(self):
        rows=[]
        for s in range(12):
            for plot in ("P1","P2"):
                for i in range(5):
                    n=4+2*i
                    rows.append({
                        "site":f"S{s:02d}","genus":"Peromyscus",
                        "series_id":f"PEMA|S{s:02d}|{plot}",
                        "site_month":f"S{s:02d}|07",
                        "year":"2025",
                        "mnka":n,
                        "D_m2":4*n+100+s+((i+s)%3)*.01,
                    })
        result=information(rows)
        self.assertEqual(result["sessions"],120)
        self.assertEqual(result["sites"],12)
        self.assertGreater(result["mnka_residual_sum_squares"],0)
        self.assertAlmostEqual(result["beta_D_MNKA"],4.,delta=.003)
        self.assertGreater(result["residual_df"],20)

    def test_predictor_constant_within_every_series_cannot_identify(self):
        rows=[{
           "site":f"S{s:02d}",
           "series_id":f"S{s:02d}|P1",
           "site_month":f"S{s:02d}|07","year":"2025",
           "mnka":5+s,"D_m2":i+s,
        } for s in range(12) for i in range(5)]
        with self.assertRaisesRegex(ValueError,"not enough within-design"):
            information(rows)

if __name__=="__main__":
    unittest.main()
