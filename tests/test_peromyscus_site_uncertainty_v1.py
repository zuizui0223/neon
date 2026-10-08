import unittest
from analysis.audit_peromyscus_site_uncertainty_v1 import site_sandwich, abundance_level_summaries


class PostResultUncertaintyTests(unittest.TestCase):
    def test_site_cluster_uncertainty_preserves_exact_fixed_effects_slope(self):
        rows=[]
        for i in range(12):
            site=f"S{i:02d}"
            for plot in ("P1","P2"):
                for mnka in (5,7,9,11,13,15):
                    rows.append({
                        "site":site,"site_month":site+"|07","year":"2020",
                        "series_id":f"PEMA|{site}|{plot}",
                        "genus":"Peromyscus","taxon":"PEMA","mnka":mnka,
                        "nn_excess_xy_m2":2.0*mnka+i,
                        "nn_excess_series_m2":3.0*mnka-i,
                    })
        x=site_sandwich(rows, "nn_excess_xy_m2")
        y=site_sandwich(rows, "nn_excess_series_m2")
        self.assertAlmostEqual(x["beta"],2.0,places=7)
        self.assertAlmostEqual(y["beta"],3.0,places=7)
        self.assertEqual(x["sites"],12)
        summaries=abundance_level_summaries(rows)
        self.assertEqual(summaries["nn_excess_xy_m2"]["lower_within_series_mnka"]["n"],48)
        self.assertEqual(summaries["nn_excess_xy_m2"]["upper_within_series_mnka"]["n"],48)

    def test_site_cluster_rejects_too_few_independent_sites(self):
        rows=[{
            "site":"S1","site_month":"S1|07","year":"2020","series_id":"P1",
            "mnka":i,"genus":"Peromyscus","nn_excess_xy_m2":i
        } for i in range(90)]
        with self.assertRaisesRegex(ValueError,"fewer than ten"):
            site_sandwich(rows,"nn_excess_xy_m2")


if __name__=="__main__":
    unittest.main()
