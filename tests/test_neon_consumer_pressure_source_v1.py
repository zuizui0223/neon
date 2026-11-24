import unittest,json
from pathlib import Path
from analysis.audit_neon_consumer_pressure_source_v1 import schema,ROOT
class ConsumerPressureSourceTests(unittest.TestCase):
    def test_csv_schema_no_response_rows(self):
        s=schema(b"year,station,fate\n2020,PRIVATE,cache\n","data.csv")
        self.assertEqual(s["row_count"],1);self.assertNotIn("PRIVATE",str(s))
    def test_published_arithmetic(self):
        src=json.loads((ROOT/"data/neon_li_zhang2007_annual_reported_20261125.json").read_text())
        out=json.loads((ROOT/"results/neon_li_zhang2007_recorded_stage_arithmetic_20261125.json").read_text())
        for v,a in zip(src["rows"],out["annual"]):
            self.assertEqual(a["year"],v["year"])
            self.assertAlmostEqual(a["recorded_cache_rate"],v["recorded_caches"]/v["released"])
            self.assertAlmostEqual(a["recorded_germination_rate"],v["recorded_germinations"]/v["released"])
            self.assertAlmostEqual(a["recorded_germinations_per_recorded_cache"],v["recorded_germinations"]/v["recorded_caches"])
        self.assertAlmostEqual(out["mast_to_nonmast_recorded_cache_ratio"],344/89)
        self.assertEqual(out["mast_to_nonmast_recorded_germination_ratio"],1)
        self.assertAlmostEqual(out["mast_to_nonmast_recorded_germination_per_cache_ratio"],89/344)
if __name__=="__main__":unittest.main()
