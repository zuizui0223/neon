import json,unittest
from analysis.neon_li2021_seasonal_published_bounds_v1 import SOURCE,RESULT,calculate,season_bounds
class LiPublishedBoundsTests(unittest.TestCase):
    def test_fixed_receipt(self):
        out=calculate(json.loads(SOURCE.read_text()))
        self.assertEqual(out,json.loads(RESULT.read_text()))
        self.assertEqual(out["contrasts"]["spring_minus_autumn_predation"],[511,5689])
        self.assertEqual(out["contrasts"]["autumn_minus_spring_cache"],[-966,4212])
        self.assertTrue(out["predation_difference_positive_even_with_rounding"])
        self.assertFalse(out["cache_difference_sign_identified"])
    def test_invalid_partition(self):
        with self.assertRaises(ValueError):season_bounds({"IS":0,"PS":0,"PR":0,"IR":0,"HR":0,"MR":9999})
    def test_all_unknown(self):
        out=season_bounds({"IS":0,"PS":0,"PR":0,"IR":0,"HR":0,"MR":10000})
        self.assertEqual(out["predation"],[0,10000])
        self.assertEqual(out["predation_minus_cache"],[-10000,10000])
if __name__=="__main__":unittest.main()
