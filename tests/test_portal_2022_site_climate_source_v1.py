"""Synthetic, no-external-network source checks for Portal climate source rules."""
import unittest

from analysis.audit_portal_2022_site_climate_source_v1 import (
    weather_support,ndvi_support,EXPECTED_HOURLY
)

class TestPortalSiteClimateSource(unittest.TestCase):
    def test_rain_and_missing_hours_are_distinct(self):
        raw=("year,month,day,hour,precipitation\n"
             "2022,7,1,0,2.1\n2022,7,1,1,\n"
             "2022,7,1,2,0\n2021,7,1,0,99\n").encode()
        sample,report=weather_support(raw)
        self.assertEqual(len(sample[2022]),3)
        self.assertEqual(sum(v for v in sample[2022].values() if v is not None),2.1)
        self.assertEqual(report["per_year"]["2022"]["hours_with_valid_nonnegative_rain"],2)
        self.assertEqual(report["per_year"]["2022"]["total_expected_hour_slots"],EXPECTED_HOURLY)
        self.assertFalse(report["all_years_rain_quality_pass"])

    def test_documented_end_of_day_24hour_label(self):
        raw=("year,month,day,hour,precipitation\n"
             "2022,7,1,23,0\n2022,7,1,24,1.5\n").encode()
        series,report=weather_support(raw)
        self.assertEqual(series[2022][(7,1,24)],1.5)
        self.assertEqual(report["source_label_hour_24_row_count"],1)
        self.assertTrue(report["source_hour_24_preserved_without_date_shift"])

    def test_negative_precip_never_reclassified_as_meteorological_null(self):
        raw=("year,month,day,hour,precipitation\n"
             "2022,7,1,0,-0.1\n").encode()
        with self.assertRaisesRegex(ValueError,"NEGATIVE_OR_NONFINITE_RAIN"):
            weather_support(raw)

    def test_duplicate_conflicting_hour_source_stop(self):
        raw=("year,month,day,hour,precipitation\n"
             "2022,7,1,0,2\n2022,7,1,0,4\n").encode()
        with self.assertRaisesRegex(ValueError,"CONFLICTING_DUPLICATE_HOURLY_RAIN"):
            weather_support(raw)

    def test_ndvi_sensor_cloud_and_missingness_are_enforced(self):
        raw=("date,sensor,source,pixel_count,ndvi,cloud_cover\n"
             "2022-07-01,Landsat8,USGS,4422,0.22,12\n"
             "2022-07-03,Landsat9,USGS,4422,0.44,0\n"
             "2022-08-09,Landsat8,USGS,4422,0.33,45\n"
             "2022-09-01,Landsat8,USGS,4422,0.18,3\n"
             "2022-06-30,Landsat8,USGS,4422,0.88,0\n").encode()
        sample,report=ndvi_support(raw)
        self.assertEqual(sample[2022],[.22,.18])
        self.assertEqual(report["per_year"]["2022"]["valid_monsoon_Landsat8_images"],2)
        self.assertFalse(report["all_years_Landsat8_source_gate_pass"])

    def test_ndvi_out_of_bounds_rejected(self):
        raw=("date,sensor,source,pixel_count,ndvi,cloud_cover\n"
             "2023-09-01,Landsat8,USGS,4422,1.8,3\n").encode()
        with self.assertRaisesRegex(ValueError,"IMPOSSIBLE_NDVI_OR_CLOUD_RANGE"):
            ndvi_support(raw)

if __name__=="__main__":
    unittest.main()
