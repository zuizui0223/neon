import unittest
from analysis.audit_multiscale_density_cohort_size_v1 import adjusted_slope

class CohortSensitivityTests(unittest.TestCase):
    def test_m_and_mnka_recover_distinct_synthetic_effects(self):
        rows=[]
        for i in range(12):
            site=f"S{i:02d}"
            for plot in ("P1","P2"):
                for event in range(5):
                    n=5+2*event
                    m=5+event+((i+event)%3)
                    w=-3*n+2*m+i
                    b=4*n+5*m-i
                    rows.append({
                        "site":site,"genus":"Peromyscus",
                        "series_id":f"PEMA|{site}|{plot}","site_month":f"{site}|07",
                        "year":"2020","mnka":n,"m":m,
                        "W_m2":w,"B_debiased_m2":b,"D_m2":b-w,
                    })
        x=adjusted_slope(rows,"W_m2",balanced=False)
        y=adjusted_slope(rows,"B_debiased_m2",balanced=False)
        d=adjusted_slope(rows,"D_m2",balanced=False)
        self.assertAlmostEqual(x["beta_MNKA"],-3,places=6)
        self.assertAlmostEqual(y["beta_MNKA"],4,places=6)
        self.assertAlmostEqual(d["beta_MNKA"],7,places=6)
        self.assertAlmostEqual(d["beta_m"],3,places=6)

if __name__=="__main__":
    unittest.main()
