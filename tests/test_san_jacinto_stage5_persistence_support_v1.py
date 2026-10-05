import unittest
from analysis.audit_san_jacinto_stage5_persistence_support_v1 import split_dates

class TestStage5PersistenceSupport(unittest.TestCase):
    def test_even_split(self):
        e,l,m=split_dates(["2026-01-01","2026-01-02","2026-01-03","2026-01-04"])
        self.assertEqual(e,{"2026-01-01","2026-01-02"})
        self.assertEqual(l,{"2026-01-03","2026-01-04"})
        self.assertIsNone(m)

    def test_odd_split_discards_middle(self):
        e,l,m=split_dates(["2026-01-01","2026-01-02","2026-01-03","2026-01-04","2026-01-05"])
        self.assertEqual(e,{"2026-01-01","2026-01-02"})
        self.assertEqual(l,{"2026-01-04","2026-01-05"})
        self.assertEqual(m,"2026-01-03")

if __name__=="__main__":
    unittest.main()
