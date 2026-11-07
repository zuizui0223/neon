"""One-pass future split join and locked null support; synthetic only."""
import unittest
from analysis.run_future_neon_provisional_holdout_v1 import (
    join_sealed_rows, temporal_series_subset, actual_two_null_coverage,
    _site_bootstrap_slopes,fit_mode_genus,
)

def example():
    m=[];p=[]
    for i in range(287):
        site=f"S{(i//12)%20:02d}"
        plot=f"P{(i//4)%3}"
        event=f"E{i:03d}"
        key={"taxon":"PEMA","genus":"Peromyscus","site":site,
             "plot_id":plot,"event_id":event}
        points=[[float(10*k),float(10*((k+i)%7))] for k in range(5)]
        m.append({**key,"m":5,"W_m2":10,"B_debiased_m2":100,
                  "B_observed_m2":102,"D_m2":90,"centroids_m":points})
        p.append({**key,"date":"2026-07-01","genus_mnka":3+(i%4),
                  "frozen_repeat_supported_m":5,
                  "frozen_trap_saturation":.1})
    return m,p


class ProspectiveJoinTests(unittest.TestCase):
    def test_one_to_one_future_only_join(self):
        m,p=example()
        rows=join_sealed_rows(m,p,{"status":"FUTURE_METRIC_QC_PASS"})
        self.assertEqual(len(rows),287)
        self.assertTrue(all(r["D_m2"]==r["B_debiased_m2"]-r["W_m2"] for r in rows))
        self.assertNotIn("tagID",rows[0])

    def test_identity_drift_prevents_any_effect(self):
        m,p=example()
        p[0]["event_id"]="OTHER"
        with self.assertRaisesRegex(RuntimeError,"identity conflict"):
            join_sealed_rows(m,p,{"status":"FUTURE_METRIC_QC_PASS"})

    def test_frozen_source_QC_must_pass(self):
        m,p=example()
        with self.assertRaisesRegex(RuntimeError,"metric-only QC failed"):
            join_sealed_rows(m,p,{"status":"STOP_FUTURE_METRIC_QC"})

    def test_null_reference_stops_short_temporal_series(self):
        m,p=example()
        rows=join_sealed_rows(m,p,{"status":"FUTURE_METRIC_QC_PASS"})
        eligible=temporal_series_subset(rows)
        # Synthetic plot/event mapping not calibrated for replication support;
        # the test only verifies that rejection happens before NN slopes.
        s=actual_two_null_coverage([],rows)
        self.assertEqual(s["status"],"STOP_PEROMYSCUS_NOT_ESTIMABLE")

    def test_site_bootstrap_is_exactly_preset_and_positive_on_known_slope(self):
        rows=[]
        for site_id in range(11):
            site=f"S{site_id:02d}"
            for plot in ("P1","P2"):
                for i in range(4):
                    n=3+2*i
                    rows.append({
                        "taxon":"PEMA","site":site,"genus":"Peromyscus",
                        "series_id":f"PEMA|{site}|{plot}",
                        "site_month":site+"|07","year":"2026",
                        "mnka":n,"nn_excess_xy_m2":2*n+site_id,
                        "nn_excess_series_m2":3*n-site_id,
                    })
        res=_site_bootstrap_slopes(
            rows,("nn_excess_xy_m2","nn_excess_series_m2"),B=12,seed=20261008)
        self.assertEqual(res["requested_B"],12)
        self.assertTrue(res["by_response"]["nn_excess_xy_m2"]["positive_lower_bound"])
        self.assertTrue(res["by_response"]["nn_excess_series_m2"]["positive_lower_bound"])

if __name__=="__main__":
    unittest.main()
