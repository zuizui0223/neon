import unittest
from datetime import date,datetime
from analysis.audit_neon_seasonal_seed_role_source_v1 import csv_schema,date_value,date_coverage
class SeasonalSourceTest(unittest.TestCase):
    def test_year_schema_not_outcomes(self):
        v=csv_schema(b"YEAR,ID,Count\n2018,A,9\n2019,B,3\n,NA,4\n")
        self.assertEqual(v["rows"],3)
        self.assertEqual(v["literal_year_counts_by_column_index"]["0"],{"2018":1,"2019":1,"missing_or_not_literal_four_digit_year":1})
        self.assertNotIn("'A'",str(v))
    def test_calendar_parsing_fail_closed(self):
        self.assertEqual(date_value("2019/3/1"),date(2019,3,1))
        self.assertEqual(date_value(datetime(2018,9,3)),date(2018,9,3))
        for x in ("03/04/2019","March","2019-02-30",43565,None):
            self.assertIsNone(date_value(x))
    def test_interval_only_not_fate(self):
        v=date_coverage([(date(2019,1,1),date(2019,1,10)),(date(2019,1,5),date(2019,1,2)),(None,None)],0,1)
        self.assertEqual(v["date_status_counts"]["both_parseable"],2)
        self.assertEqual(v["date_status_counts"]["reversed"],1)
        self.assertEqual(v["nonnegative_interval_counts"],{"8_30d":1})
if __name__=="__main__":unittest.main()
