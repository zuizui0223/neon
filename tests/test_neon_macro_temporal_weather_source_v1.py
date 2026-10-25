"""Synthetic source-only lag, NEON tower-release weather product coverage.

No ecological recurrence effect, time-lag regression or weather value is opened.
"""
import json
import unittest
from datetime import date,timedelta
from analysis.run_neon_macro_temporal_weather_source_v1 import (
    temporal_climate_source_audit,bout_start_gap,weather_release_months,
)

def pair(site,plot,q,a,b,genera=2):
    da=date.fromisoformat(a)
    db=date.fromisoformat(b)
    gs=[f"G{i}" for i in range(genera)]
    return {
        "site":site,"site_plot":(site,plot),"season_ordinal":q,
        "capture_dates_A":tuple(da+timedelta(days=i) for i in range(3)),
        "capture_dates_B":tuple(db+timedelta(days=i) for i in range(3)),
        "A":{g:{"A1","A2"} for g in gs},
        "B":{g:{"B1","B2"} for g in gs},
    }

def product(code,months):
    return {"dataProductCode":code,
            "availableReleases":[
                {"release":"RELEASE-2025","availableMonths":["2025-04","2025-07"]},
                {"release":"RELEASE-2026","availableMonths":months},
            ]}

def meta(site,domain,months,precip=True):
    products=[product("DP1.00002.001",months)]
    if precip:products.append(product("DP1.00044.001",months))
    return {"siteCode":site,"domainCode":domain,
            "siteType":"CORE","siteLatitude":41.0,
            "dataProducts":products}

def fixtures():
    two=[
        pair("FAKE_A","P1",8101,"2025-04-01","2025-07-01"),
        pair("FAKE_A","P1",8102,"2025-07-01","2025-10-01"),
        pair("FAKE_B","P2",8101,"2025-04-01","2025-07-01"),
    ]
    three=[pair("FAKE_B","P2",8102,"2025-07-01","2025-10-01",3)]
    row=[
        meta("FAKE_A","D01",["2025-04","2025-07","2025-10"]),
        meta("FAKE_B","D02",["2025-04","2025-07"],precip=False),
    ]
    return two,three,row

class MacroTemporalWeatherSourceTests(unittest.TestCase):
    def test_original_calendar_elapsed_days(self):
        two,_,_=fixtures()
        self.assertEqual(bout_start_gap(two[0]),91)
        self.assertEqual(bout_start_gap(two[1]),92)
        self.assertRaisesRegex(ValueError,"between-season gap invalid",
            bout_start_gap,pair("FAKE","P",0,"2025-07-01","2025-04-01"))

    def test_release_specific_weather_product_never_falls_back_to_other_release(self):
        products=weather_release_months(meta("FAKE","D01",["2025-04"]))
        self.assertEqual(products["DP1.00002.001"],{"2025-04"})
        self.assertNotIn("2025-07",products["DP1.00002.001"])
        self.assertEqual(products["DP1.00045.001"],set())
        self.assertEqual(products["DP4.00001.001"],set())

    def test_source_geography_gaps_and_weather_availability_not_effect(self):
        two,three,sites=fixtures()
        out=temporal_climate_source_audit(two,three,sites,
                                         expected_two=3,expected_three=1,
                                         expected_two_sites=2,expected_three_sites=1)
        x=out["exactly_two_genera_source"]
        self.assertEqual(x["pairs"],3)
        self.assertEqual(x["calendar_gap_days_source_only"]["min"],91)
        self.assertEqual(x["calendar_gap_days_source_only"]["max"],92)
        self.assertEqual(x["source_weather_month_coverage"]["single_air_temperature"]["source_pair_complete_month_availability"],3)
        self.assertEqual(x["source_weather_month_coverage"]["precip_weighing"]["source_pair_complete_month_availability"],2)
        self.assertEqual(x["both_air_temperature_and_a_single_consistent_precip_product_pairs"],2)
        self.assertEqual(x["sites_with_air_temperature_and_consistent_precip_pairs"],1)
        self.assertTrue(out["scientific_scope"]["new_climate_by_R_or_gap_by_R_effect_computed"] is False)
        self.assertFalse(out["lag_effect_source_precheck"]["source_only_non_effect_prerequisites_pass"])
        for secret in ("FAKE_A","FAKE_B","FAKE_A_P1","2025-04-01"):
            self.assertNotIn(secret,json.dumps(out))

    def test_missing_site_metadata_stops_not_fill_from_latitude(self):
        two,three,sites=fixtures()
        with self.assertRaisesRegex(ValueError,"official metadata missing"):
            temporal_climate_source_audit(two,three,sites[:1],
                                          expected_two=3,expected_three=1,
                                          expected_two_sites=2,expected_three_sites=1)

    def test_frozen_disjoint_pair_keys_no_double_count(self):
        two,three,sites=fixtures()
        three[0]=pair("FAKE_A","P1",8101,"2025-04-01","2025-07-01",3)
        with self.assertRaisesRegex(ValueError,"not disjoint"):
            temporal_climate_source_audit(two,three,sites,
                                          expected_two=3,expected_three=1,
                                          expected_two_sites=2,expected_three_sites=1)

if __name__=="__main__":
    unittest.main()
