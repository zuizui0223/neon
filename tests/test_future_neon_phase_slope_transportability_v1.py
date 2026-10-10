import unittest
import importlib.util
from analysis.audit_future_neon_phase_slope_transportability_v1 import (
    site_phase_difference, future_varying_cohort, join_new,
)


@unittest.skipUnless(
    importlib.util.find_spec("pandas")
    and importlib.util.find_spec("scipy")
    and importlib.util.find_spec("statsmodels"),
    "Optional phase-transportability statistics dependencies are not installed",
)
class TimeSplitTransportabilityTests(unittest.TestCase):
    def test_source_matched_fixed_effects_identify_phase_slopes(self):
        old=[];new=[]
        for s in range(12):
            site=f"S{s:02d}"
            for plot in ("P1","P2"):
                for e in range(5):
                    row={
                        "taxon":"PEMA","genus":"Peromyscus",
                        "site":site,"plot_id":plot,
                        "series_id":f"PEMA|{site}|{plot}",
                        "site_month":f"{site}|07",
                        "mnka":5+2*e,
                    }
                    error=((s+e)%5-2)*.07
                    old.append({**row,"year":"2023",
                        "D_m2":2*row["mnka"]+100+s+error})
                    new.append({**row,"year":"2025",
                        "D_m2":-3*row["mnka"]+110+s-error})
        out=site_phase_difference(old,new)
        self.assertEqual(out["sites"],12)
        self.assertAlmostEqual(out["dev_beta_delta"],2,delta=.06)
        self.assertAlmostEqual(out["provisional_beta_delta"],-3,delta=.06)
        self.assertAlmostEqual(out["provisional_minus_dev_delta_slope"],-5,delta=.12)
        self.assertLess(out["CI95_site_cluster_t_df_sites_minus1"][1],0)

    def test_future_provisional_mnka_varying_qualification(self):
        rows=[]
        for i,n in enumerate((5,6,7,7)):
            rows.append({"series_id":"PEMA|HARV|P1","genus":"Peromyscus",
                         "mnka":n})
        self.assertEqual(len(future_varying_cohort(rows)),4)
        rows=[{**r,"mnka":5} for r in rows]
        self.assertFalse(future_varying_cohort(rows))

    def test_cross_artifact_event_mismatch_stops_before_slopes(self):
        metrics=[{
            "taxon":"PEMA","genus":"Peromyscus","site":"HARV",
            "plot_id":"P1","event_id":str(i),"D_m2":1.0
        } for i in range(287)]
        predictors=[{
            "taxon":"PEMA","genus":"Peromyscus","site":"HARV",
            "plot_id":"P1","event_id":str(i),"date":"2025-07-01",
            "genus_mnka":5
        } for i in range(287)]
        predictors[0]["event_id"]="MISMATCH"
        with self.assertRaisesRegex(RuntimeError,"drift"):
            join_new(metrics,predictors)


if __name__=="__main__":
    unittest.main()
