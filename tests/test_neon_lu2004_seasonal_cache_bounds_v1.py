import json,unittest
from analysis.neon_lu2004_seasonal_cache_bounds_v1 import calculate,SOURCE,RESULT
class LuSeasonTests(unittest.TestCase):
    def test_reproduce_and_no_reconciliation_guess(self):
        x=calculate(json.loads(SOURCE.read_text()))
        self.assertEqual(x,json.loads(RESULT.read_text()))
        self.assertEqual(len(x["table_partition_mismatches"]),4)
        self.assertEqual(x["comparisons"]["spring_minus_summer"]["lower_numerator"],26)
        self.assertEqual(x["comparisons"]["autumn_minus_summer"]["lower_numerator"],147)
        self.assertLess(x["comparisons"]["autumn_minus_spring"]["lower_numerator"],0)
        for h,v in x["habitat_comparisons"].items():
            self.assertGreater(v["spring_minus_summer"]["lower_numerator"],0)
            self.assertGreater(v["autumn_minus_summer"]["lower_numerator"],0)
    def test_crosscheck_fail_closed(self):
        x=json.loads(SOURCE.read_text());x["rows"][0][5]+=1
        with self.assertRaises(ValueError):calculate(x)
if __name__=="__main__":unittest.main()
