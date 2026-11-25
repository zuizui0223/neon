import unittest
from fractions import Fraction
from analysis.run_neon_exact_two_recurrence_absolute_magnitude_v1 import row,summarize
class AbsoluteMagnitudeTests(unittest.TestCase):
    def test_exact_expected_fraction(self):
        a={"g":{"A1","A2"},"h":{"B1","B2"}}
        v=row({"site":"s","A":a,"B":a})
        self.assertEqual(v["obs"],4);self.assertEqual(v["mu"],Fraction(2));self.assertEqual(v["den"],4)
        q=summarize([v])
        self.assertEqual(q["equal_site_observed_fraction"],1)
        self.assertEqual(q["equal_site_null_expected_fraction"],.5)
        self.assertEqual(q["equal_site_excess_fraction"],.5)
    def test_equal_site_not_pooled_and_degenerate(self):
        rows=[{"site":"a","den":4,"obs":2,"mu":Fraction(1),"z":1.},
              {"site":"a","den":4,"obs":2,"mu":Fraction(1),"z":1.},
              {"site":"b","den":8,"obs":2,"mu":Fraction(2),"z":None}]
        q=summarize(rows)
        self.assertEqual(q["equal_site_excess_fraction"],.125)
        self.assertEqual(q["null_degenerate_pairs"],1)
        self.assertEqual(q["all_pair_cell_counts_descriptive"]["excess_matches"],2)
        self.assertEqual(q["equal_site_mean_Z_informative_only"],1)
if __name__=="__main__":unittest.main()
