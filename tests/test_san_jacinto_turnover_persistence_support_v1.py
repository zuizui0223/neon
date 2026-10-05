import unittest
from analysis.audit_san_jacinto_turnover_persistence_support_v1 import split_dates

class TestTurnoverSupport(unittest.TestCase):
    def test_split_even(self):
        rows=[{"date_iso":f"2020-01-{i:02d}"} for i in range(1,9)]
        e,l,m=split_dates(rows)
        self.assertEqual(len(e),4); self.assertEqual(len(l),4); self.assertIsNone(m)
    def test_split_odd_discards_middle(self):
        rows=[{"date_iso":f"2020-01-{i:02d}"} for i in range(1,10)]
        e,l,m=split_dates(rows)
        self.assertEqual(len(e),4); self.assertEqual(len(l),4); self.assertEqual(m,"2020-01-05")
if __name__=="__main__": unittest.main()
