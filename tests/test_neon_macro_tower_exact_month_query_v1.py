"""Prove original NEON temperature archives are queried by exact site/month.

The old 28-site ten-year broad archive request returned zero of 205
expected months, even though published month availability and a one-month
pre-effect pilot were positive. These tests prevent treating API query
shape/size failure as biological absence or zero thermal shift.
"""
from unittest import TestCase,main
from unittest.mock import patch
from analysis.run_neon_macro_original_tower_thermal_ecology_v1 import (
    _exact_month_query_body,provider_weather_months,
)

def record(site,month):
    return {
        "name":f"NEON.D01.{site}.DP1.00002.001.00000.000.010.030.SAAT_30min.csv",
        "url":"https://example.test/weather.csv",
        "size":321,
        "md5":"a"*32,
    }

class OriginalTowerExactMonthQueryTests(TestCase):
    def test_monthly_site_query_never_broadens_source_window(self):
        x=_exact_month_query_body("FAKESITE","2017-08")
        self.assertEqual(x["siteCodes"],["FAKESITE"])
        self.assertEqual(x["startDateMonth"],x["endDateMonth"])
        self.assertEqual(x["release"],"RELEASE-2026")
        self.assertFalse(x["includeProvisional"])

    def test_two_distant_months_each_receive_own_original_release_query(self):
        observed=[]
        def fake_get(url,*,token=None,body=None):
            self.assertEqual(len(body["siteCodes"]),1)
            self.assertEqual(body["startDateMonth"],body["endDateMonth"])
            site=body["siteCodes"][0]
            month=body["startDateMonth"]
            observed.append((site,month))
            return {
                "data":{
                    "releases":[{"release":"RELEASE-2026","packages":[
                        {"packageType":"basic","siteCode":site,"month":month,
                         "files":[record(site,month)]}
                    ]}]
                }
            }
        with patch("analysis.run_neon_macro_original_tower_thermal_ecology_v1._request_json",side_effect=fake_get), patch(
             "analysis.run_neon_macro_original_tower_thermal_ecology_v1._download_one",return_value=b"sourcebytes"), patch(
             "analysis.run_neon_macro_original_tower_thermal_ecology_v1.aggregate_qc_month",
             return_value={"status":"TOWER_TEMP_MONTH_QC_PASS","_private_mean_celsius":12.4}):
            qc,out=provider_weather_months(["FAKEA","FAKEB"],{("FAKEA","2015-03"),("FAKEB","2024-10")},"TOKEN")
        self.assertEqual(set(observed),{("FAKEA","2015-03"),("FAKEB","2024-10")})
        self.assertEqual(out["requested_source_site_months"],2)
        self.assertEqual(out["archive_30min_file_months_advertised"],2)
        self.assertEqual(out["QC_good_months"],2)
        self.assertEqual(len(qc),2)
        self.assertEqual(out["source_archive_query_mode"],"one_site_one_original_month")
        self.assertEqual(out["weather_metadata_error_class_counts"],{})
        self.assertNotIn("FAKEA",str(out))
        self.assertNotIn("FAKEB",str(out))

    def test_archive_metadata_failure_never_called_zero_temperature(self):
        def bad_query(url,*,token=None,body=None):
            raise ValueError("SECRET_SOURCE_ID_OR_ORIGINAL_SOURCE_DATE")
        with patch("analysis.run_neon_macro_original_tower_thermal_ecology_v1._request_json",side_effect=bad_query):
            qc,out=provider_weather_months(["FAKEA"],{("FAKEA","2024-10")},"TOKEN")
        self.assertEqual(qc,{})
        self.assertEqual(out["weather_metadata_error_class_counts"],{"ValueError":1})
        self.assertTrue(out["metadata_source_failure_not_declared_zero_temperature"])
        self.assertNotIn("SECRET_SOURCE",str(out))
        self.assertNotIn("FAKEA",str(out))

if __name__=="__main__":
    main()
