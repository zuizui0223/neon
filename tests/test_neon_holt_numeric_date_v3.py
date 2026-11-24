import unittest
from datetime import date
from analysis.run_neon_holt_numeric_date_v3 import anchor,decode,calibrate,repair

class NumericDateTests(unittest.TestCase):
    def test_named_date_explicit_year(self):
        self.assertEqual(anchor("05Aug_19991",1999),date(1999,8,5))
        self.assertIsNone(anchor("05Aug_19981",1999))
    def test_calibration_does_not_use_season(self):
        h=[{"year":"1999","date":"405","date2":"05Apr_19991"},{"year":"2000","date":"805","date2":"05Aug_20002"}]
        mode,m,d=calibrate(h,years=(1999,2000),min_rows=2)
        self.assertEqual(mode,"MMDD")
        _,r=repair([{"year":"1999","date":"405","used":"1"}],m,mode,years=(1999,2000))
        self.assertEqual(r["counts"]["outside_frozen_summer"],1)
        h[0]["date"]="406"
        self.assertIsNone(calibrate(h,years=(1999,2000),min_rows=2)[0])
    def test_unanchored_not_guessed(self):
        _,d=repair([{"year":"1999","date":"805","used":"1"}],{},"MMDD",years=(1999,))
        self.assertEqual(d["counts"]["unverified_used_dates"],1)
if __name__=="__main__":unittest.main()
