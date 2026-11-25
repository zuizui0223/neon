import unittest
from analysis.run_neon_maine_station_key_diagnosis_v2 import distance_profile,metric
class MaineStationKeyTests(unittest.TestCase):
    def test_exact_partition_separates_metric_and_identity(self):
        grids={str(i):{f"{i}_{j}" for j in range(100)} for i in range(8)}
        sites={s:(g,"T") for g,ss in grids.items() for s in ss}
        rows=[{"SITE1":a,"SITE2":b,"DISTANCE":"0" if a==b else "10"} for ss in grids.values() for a in ss for b in ss]
        q=distance_profile(sites,grids,rows)
        self.assertTrue(q["full_metric_geometry_gate"])
        i=next(i for i,v in enumerate(rows) if v["SITE1"]!=v["SITE2"])
        rows[i]["DISTANCE"]="bad"
        q=distance_profile(sites,grids,rows)
        self.assertTrue(q["nominal_station_identity_gate"]);self.assertFalse(q["full_metric_geometry_gate"])
        rows[i]["SITE2"]=next(s for s in sites if sites[s][0]!=sites[rows[i]["SITE1"]][0])
        q=distance_profile(sites,grids,rows)
        self.assertFalse(q["nominal_station_identity_gate"])
        self.assertEqual(q["issue_counts"]["cross_grid_rows"],1)
        self.assertEqual(q["issue_counts"]["missing_expected_pairs"],1)
    def test_no_inferred_decimal_or_negative(self):
        self.assertIsNone(metric("10,2"));self.assertIsNone(metric("-1"))
        self.assertIsNone(metric("nan"));self.assertEqual(metric("0.0"),0)
if __name__=="__main__":unittest.main()
