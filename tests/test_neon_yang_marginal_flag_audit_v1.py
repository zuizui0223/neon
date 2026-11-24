import unittest
from fractions import Fraction
from analysis.run_neon_yang_marginal_flag_audit_v1 import inconsistent,contrast
class MarginalFlagAuditTests(unittest.TestCase):
    def test_all_nonnested_patterns_and_na(self):
        for z in [(0,1,0),(0,0,1),(1,0,1),(1,None,0)]:
            self.assertTrue(inconsistent(z))
        for z in [(0,0,0),(1,0,0),(1,1,0),(1,1,1)]:
            self.assertFalse(inconsistent(z))
    def test_uncertain_positive_not_retained_in_lower_bound(self):
        x={"mixed":{"released":120,"cache":18,"cache_verified_positive":16,"uncertain":3},"mono":{"released":120,"cache":10,"cache_verified_positive":9,"uncertain":4}}
        self.assertEqual(contrast(x,"cache"),(Fraction(8,120),Fraction(3,120),Fraction(10,120)))
if __name__=="__main__":unittest.main()
