import unittest
from datetime import date
from analysis.run_neon_poland_calendar_session_v2 import decode,calendar_vector
class CalendarSessionTests(unittest.TestCase):
    def test_ambiguous_numeric_date_not_selected_by_season(self):
        v,d=calendar_vector([{"year":"2020","date":"06/07/2020"}])
        self.assertIsNone(v);self.assertTrue(d["ambiguous_global_mode"])
    def test_global_literal_date_format(self):
        rows=[{"year":"2020","date":"16/06/2020"},{"year":"2020","date":"06/07/2020"}]
        v,d=calendar_vector(rows)
        self.assertEqual(d["globally_valid_modes"],["day_first"])
        self.assertEqual(v[2020,"06/07/2020"],date(2020,7,6))
    def test_no_numeric_epoch_guess(self):
        self.assertIsNone(decode("43990",2020,"day_first"))
        self.assertEqual(decode("2021-06-01 00:00:00",2021,"month_first"),date(2021,6,1))
if __name__=="__main__":unittest.main()
