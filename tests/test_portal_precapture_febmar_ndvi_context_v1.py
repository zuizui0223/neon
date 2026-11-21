"""Synthetic source checks for outcome-blind February–March NDVI context."""
import unittest

from analysis.run_portal_precapture_febmar_ndvi_context_v1 import (
    source_only_and_context,
)

class TestSourcePinnedPrecaptureFebruaryMarchNDVI(unittest.TestCase):
    def _record(self,y,m,d,ndvi,cloud=0,sensor="Landsat8",source="USGS"):
        return {
            "date":f"{y}-{m:02d}-{d:02d}", "ndvi":str(ndvi),
            "cloud_cover":str(cloud), "sensor":sensor,"source":source
        }

    def test_all_four_years_both_months_and_equal_weight(self):
        z=[]
        for year in range(2021,2025):
            z.append(self._record(year,2,1,0.1))
            z.append(self._record(year,2,16,0.2))
            z.append(self._record(year,3,1,0.6))
        output=source_only_and_context(z)
        self.assertEqual(output["status"],
            "SOURCE_GO_EARLY_GREENNESS_CONTEXT_ONLY_NOT_MAMMAL_MECHANISM")
        self.assertAlmostEqual(
            output["annual_NDVI"]["2022"]["February_March_equal_month_mean"],
            (0.15+0.6)/2
        )
        self.assertEqual(len(output["all_original_adjacent_year_differences"]),3)
        self.assertTrue(output["ecological_limits"]["no_rodent_composition_plant_count_weather_or_learning_source_read"])

    def test_one_missing_month_fails_closed_without_environment_means(self):
        z=[self._record(y,m,1,.3)
           for y in range(2021,2025) for m in (2,3)
           if (y,m)!=(2023,2)]
        out=source_only_and_context(z)
        self.assertEqual(out["status"],"SOURCE_STOP_ORIGINAL_FEBMAR_NDVI_COVERAGE")
        self.assertIsNone(out["annual_NDVI"])
        self.assertIsNone(out["all_original_adjacent_year_differences"])

    def test_cloud_and_sensor_filter_do_not_fill_missing_month(self):
        z=[self._record(y,m,1,.3)
           for y in range(2021,2025) for m in (2,3)
           if (y,m)!=(2023,2)]
        z.extend([
            self._record(2023,2,5,.6,55),
            self._record(2023,2,7,.6,0,"Landsat9"),
        ])
        out=source_only_and_context(z)
        self.assertFalse(out["pre_effect_source_support"]["all_four_years_have_at_least_one_Feb_and_one_Mar_image"])

    def test_duplicate_same_day_original_source_stops(self):
        z=[self._record(2023,2,5,.1),self._record(2023,2,5,.2)]
        with self.assertRaisesRegex(ValueError,"DUPLICATE_SOURCE_DATE_SENSOR_PROVIDER"):
            source_only_and_context(z)

    def test_out_of_range_ndvi_stops_before_year_means(self):
        with self.assertRaisesRegex(ValueError,"IMPOSSIBLE_NDVI_OR_CLOUD"):
            source_only_and_context([self._record(2023,2,5,1.4)])

if __name__=="__main__":
    unittest.main()
