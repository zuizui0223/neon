"""Source QA tests for fixed independent NOAA regional rain data."""
from __future__ import annotations
import unittest
from datetime import date,timedelta

from analysis.audit_portal_2022_regional_rain_context_v1 import (
    parse_original_station,changes,YEARS
)

class TestPortalRegionalRainContext(unittest.TestCase):
    def test_quoted_GHCN_attributes_and_92_day_coverage(self):
        h="year,month,day,station,date,prcp,prcp_attributes\n"
        rows=[]
        for y in YEARS:
            start=date(y,7,1)
            for n in range(92):
                day=start+timedelta(days=n)
                rows.append(
                    f'{day.year},{day.month},{day.day},USC00026716,'
                    f'{day.isoformat()},1.2,",,N"')
        vals,qc=parse_original_station((h+"\n".join(rows)+"\n").encode(),
                                        "USC00026716")
        self.assertTrue(qc["original_data_eligible_all_four_years"])
        self.assertEqual(len(vals[2022]),92)
        self.assertAlmostEqual(sum(vals[2022].values()),110.4)

    def test_missing_is_never_zero_filled(self):
        raw=("year,month,day,station,prcp\n"
             "2022,7,1,USC00026716,\n").encode()
        byyear,qc=parse_original_station(raw,"USC00026716")
        self.assertIsNone(byyear[2022][date(2022,7,1)])
        self.assertFalse(qc["original_data_eligible_all_four_years"])

    def test_no_second_station_or_conflicting_same_date(self):
        a=("year,month,day,station,prcp\n"
           "2022,7,1,US1AZCH0005,1.2\n").encode()
        with self.assertRaisesRegex(ValueError,"WRONG_OR_MULTIPLE_GHCN_STATIONS"):
            parse_original_station(a,"USC00026716")
        b=("year,month,day,station,prcp\n"
           "2022,7,1,USC00026716,1.2\n"
           "2022,7,1,USC00026716,1.3\n").encode()
        with self.assertRaisesRegex(ValueError,"CONFLICTING_DAY_RAIN_DUPLICATE"):
            parse_original_station(b,"USC00026716")

    def test_year_differences_do_not_select_best_comparison(self):
        r=changes({2021:100.,2022:200.,2023:130.,2024:129.})
        self.assertEqual(len(r["all_three_precommitted_differences"]),3)
        self.assertEqual(r["2022_to_2023_absolute_difference_rank"],2)
        self.assertEqual(r["all_three_precommitted_differences"]["2022_to_2023"]["signed_mm"],-70.)

if __name__=="__main__":
    unittest.main()
