import unittest
from analysis.audit_mosa_encounter_toe_reconciliation_v1 import (
    compare_tag_identity_rosters,
)

class MosaAuthorTagReconciliationTests(unittest.TestCase):
    def test_matrix_duplicate_and_nonMN_rows_are_not_added_as_MN_animals(self):
        raw={"a","b","c"}
        rows=[("MN","a"),("MN","b"),("MN","b"),("MN","c"),("NO_CAPTURE","")]
        x=compare_tag_identity_rosters(raw,rows)
        self.assertEqual(x["matrix_total_rows"],5)
        self.assertEqual(x["matrix_MN_rows"],4)
        self.assertEqual(x["matrix_MN_distinct_TOE"],3)
        self.assertEqual(x["matrix_MN_duplicate_TOE_rows"],1)
        self.assertEqual(x["matrix_nonMN_rows"],1)
        self.assertEqual(x["raw_MN_tags_not_in_author_matrix"],0)
        self.assertEqual(x["author_matrix_MN_tags_not_in_raw"],0)

    def test_cross_matrix_TOE_difference_blocks_identity_claim(self):
        raw={"a","b"}
        rows=[("MN","a"),("MN","new")]
        x=compare_tag_identity_rosters(raw,rows)
        self.assertEqual(x["raw_MN_tags_not_in_author_matrix"],1)
        self.assertEqual(x["author_matrix_MN_tags_not_in_raw"],1)
        self.assertFalse(x["raw_and_matrix_identity_rosters_match"])

if __name__=="__main__":
    unittest.main()
