"""Synthetic 30-minute tower-weather original-release source QA only."""
from datetime import date,timedelta
import unittest

from analysis.run_neon_macro_weather_pilot_v1 import (
    eligible_first_original_pair,_month_manifest,table_qa,
)

def unit(site="TEST_A"):
    return {
        "site":site,"site_plot":(site,"P"),"season_ordinal":8111,
        "capture_dates_A":tuple(date(2020,4,1)+timedelta(days=i) for i in range(3)),
        "capture_dates_B":tuple(date(2020,7,1)+timedelta(days=i) for i in range(3)),
    }

def product(code,months):
    return {"dataProductCode":code,
            "availableReleases":[{"release":"RELEASE-2026","availableMonths":months}]}

def response(site="TEST_A",month="2020-04",p="DP1.00002.001",name="SAAT_30min"):
    return {"data":{"releases":[{"release":"RELEASE-2026",
        "packages":[{"siteCode":site,"month":month,"packageType":"basic",
        "files":[{"name":f"NEON.TEST.{name}.csv",
                  "url":"https://example.org/data.csv",
                  "md5":"0"*32,"size":100}]}]
    }]}}

class TowerWeatherPilotSourceTests(unittest.TestCase):
    def test_first_eligible_source_month_no_ecological_Z(self):
        meta=[{"siteCode":"TEST_A","dataProducts":[
             product("DP1.00002.001",["2020-04","2020-07"]),
             product("DP1.00045.001",["2020-04","2020-07"])]}]
        self.assertEqual(eligible_first_original_pair([unit()],meta),("TEST_A","2020-04"))
        meta[0]["dataProducts"][1]["availableReleases"][0]["availableMonths"]=["2020-04"]
        with self.assertRaisesRegex(ValueError,"No original exact-two"):
            eligible_first_original_pair([unit()],meta)

    def test_original_release_metadata_30min_table_selection(self):
        m=_month_manifest(response(),"DP1.00002.001","TEST_A","2020-04","SAAT_30min")
        self.assertEqual(m["md5"],"0"*32)
        self.assertEqual(m["size"],100)
        with self.assertRaisesRegex(ValueError,"required 30min table"):
            _month_manifest(response(),"DP1.00002.001","TEST_A","2020-04","TIPPRE_30min")

    def test_QA_returns_only_counts_not_weather_values(self):
        for k,col in [("single_air_temperature","tempSingleMean"),
                      ("precip_tipping","precipBulk")]:
            rows=["startDateTime,endDateTime,"+col+",finalQF"]
            rows += [f"2020-01-01T{i%24:02d}:00Z,2020-01-01T{i%24:02d}:30Z,{i%10},0" for i in range(120)]
            report=table_qa(("\n".join(rows)+"\n").encode(),k)
            self.assertEqual(report["rows"],120)
            self.assertEqual(report["finite_numeric_rows_by_candidate"][col],120)
            self.assertEqual(report["summarized_final_quality_flag_counts"]["0"],120)
            self.assertTrue(report["has_start_and_end_time_schema"])
            self.assertTrue(report["no_ecological_effect_fitted"])
            self.assertNotIn("2020-01-01",str(report))

    def test_missing_column_not_silently_equivalent_precipitation(self):
        rows=["startDateTime,endDateTime,towerRainGaugeData,finalQF"]+[
            "2020-01-01T00:00Z,2020-01-01T00:30Z,2,1" for i in range(101)]
        z=table_qa(("\n".join(rows)+"\n").encode(),"precip_tipping")
        self.assertFalse(z["primary_physical_measurement_column_semantics_checked"])
        self.assertEqual(z["n_final_quality_flag_columns"],1)

if __name__=="__main__":
    unittest.main()
