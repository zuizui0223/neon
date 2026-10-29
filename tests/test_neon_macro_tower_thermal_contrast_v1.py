"""Data-free correctness tests for one predefined NEON thermal macrocontrast."""
import unittest
from datetime import date,timedelta
from analysis.neon_macro_tower_thermal_contrast_v1 import (
    position,select_fixed_temperature_file,aggregate_qc_month,
    source_month_selection,_month_catalog,climate_site_model,
)

def row(pos):
    return {"name":f"NEON.D01.SITE.DP1.00002.001.00000.000.{pos}.030.SAAT_30min.2020-04.basic.20261025T020000Z.csv",
            "url":"https://example.test/file.csv","md5":"a"*32,"size":150000}

def pair():
    return {"site":"FAKESITE","site_plot":("FAKESITE","P"),
            "capture_dates_A":tuple(date(2020,4,1)+timedelta(days=i) for i in range(3)),
            "capture_dates_B":tuple(date(2020,7,1)+timedelta(days=i) for i in range(3))}

def sites(beta=-.25):
    out=[]
    for i in range(28):
        temp=2.1+((i*7)%25)*.9
        lat=27.0+(i*13)%31
        f=((i*9)%11)/10
        Y=1+beta*(temp/5)+.12*((lat-40)/10)+.18*f
        out.append({"site":f"FAKE{i:02d}",
            "site_mean_original_exact_Z":Y,
            "mean_abs_delta_C":temp,"site_latitude":lat,
            "fraction_summer_to_autumn":f})
    return out

class ThermalSourceAndModelTests(unittest.TestCase):
    def test_sensor_filename_position_choice_is_only_source_order(self):
        a=select_fixed_temperature_file([row("020"),row("010"),row("030")])
        self.assertEqual(a["position"],"010")
        self.assertEqual(position(a["name"]),"010")
        self.assertIsNone(position("BAD.SAAT_30min.csv"))

    def test_weather_table_30min_QF0_and_no_data_imputation(self):
        day=30;count=day*48
        csvrows=["startDateTime,endDateTime,tempSingleMean,finalQF"]
        csvrows += [f"2020-04-{i//48+1:02d}T00:00Z,2020-04-{i//48+1:02d}T00:30Z,10,{0 if i<1250 else 1}_{i}" for i in range(0)] # no-op
        csvrows += [f"2020-04-{i//48+1:02d}T{i%48//2:02d}:{(i%2)*30:02d}Z,2020-04-{i//48+1:02d}T{i%48//2:02d}:{(i%2)*30:02d}Z,{10+i%5},{'0' if i<1250 else '1'}" for i in range(count)]
        good=aggregate_qc_month(("\n".join(csvrows)+"\n").encode(),"2020-04")
        self.assertEqual(good["status"],"TOWER_TEMP_MONTH_QC_PASS")
        self.assertEqual(good["finite_QF0_rows"],1250)
        self.assertEqual(good["final_flag1_rows"],190)
        self.assertTrue(10 <= good["_private_mean_celsius"] <= 15)
        sparse=aggregate_qc_month(("\n".join(csvrows[:600])+"\n").encode(),"2020-04")
        self.assertEqual(sparse["status"],"STOP_TOWER_TEMP_MONTH_QC")

    def test_original_release_source_months_not_weather_values(self):
        sel,months=source_month_selection([pair()],{"FAKESITE":{"2020-04","2020-07"}})
        self.assertEqual(len(sel),1)
        self.assertEqual(len(months),2)
        no,absent=source_month_selection([pair()],{"FAKESITE":{"2020-04"}})
        self.assertEqual(no,[])
        self.assertEqual(absent,set())

    def test_provider_data_query_release_schemas(self):
        files={"data":{"releases":[{"release":"RELEASE-2026",
               "packages":[{"packageType":"basic","siteCode":"FAKESITE",
                            "month":"2020-04","files":[row("020"),row("010")]}]
        }]}}
        catalog=_month_catalog(files,{("FAKESITE","2020-04")})
        self.assertEqual(catalog[("FAKESITE","2020-04")]["position"],"010")

    def test_known_negative_thermal_slope_recovered_and_site_bootstrap(self):
        m=climate_site_model(sites(),seed=201,n_bootstrap=200)
        self.assertTrue(m["ecological_temperature_slope_fitted"])
        self.assertAlmostEqual(m["beta_recurrence_Z_per_5C_abs_seasonal_monthly_tower_temp_change"],-.25,places=9)
        self.assertAlmostEqual(m["site_cluster_bootstrap_95_interval"][0],-.25,places=7)
        self.assertAlmostEqual(m["site_cluster_bootstrap_95_interval"][1],-.25,places=7)
        self.assertEqual(m["physical_site_independent_units"],28)
        self.assertTrue(m["not_new_independent_observational_release"])
        self.assertTrue(m["genus_specific_detection_and_grid_habitat_unmeasured"])
        self.assertNotIn("FAKE",str(m))

    def test_collinear_environmental_variables_fail_without_p_hacking(self):
        xx=sites()
        for r in xx:
            r["mean_abs_delta_C"]=10.0
        m=climate_site_model(xx,seed=201,n_bootstrap=200)
        self.assertEqual(m["status"],"STOP_SITE_CLIMATE_LATITUDE_SEASON_DESIGN_RANK")
        self.assertFalse(m["ecological_temperature_slope_fitted"])

if __name__=="__main__":
    unittest.main()
