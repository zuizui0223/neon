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

    def test_unknown_species_rows_do_not_silently_become_MN_individuals(self):
        # Raw MN codes c,d are absent from author MN-labelled matrix rows,
        # but appear in author UNKNOWN SPECIES rows. Provenance overlap
        # does NOT license guessing their species or new animal identity.
        raw={"a","b","c","d"}
        rows=[
            ("MN","a"),("MN","b"),("MN","b"),
            ("NA","c"),("NA","d"),("NA","b"),("NA","z"),("NA",""),
            ("OTHER","c"),
        ]
        x=compare_tag_identity_rosters(raw,rows)
        self.assertEqual(x["raw_MN_tags_not_in_author_matrix"],2)
        self.assertEqual(x["matrix_unknown_species_rows"],5)
        self.assertEqual(x["matrix_unknown_species_distinct_nonblank_TOE"],4)
        self.assertEqual(x["unknown_species_TOE_matching_raw_MN_missing_from_MN_matrix"],2)
        self.assertEqual(x["unknown_species_TOE_already_in_MN_matrix"],1)
        self.assertEqual(x["unknown_species_TOE_absent_from_raw_MN"],1)
        self.assertEqual(x["raw_MN_TOE_missing_from_MN_and_unknown_species_rows"],0)
        self.assertFalse(x["unknown_species_rows_prove_MN_identity"])

    def test_cross_matrix_TOE_difference_blocks_identity_claim(self):
        raw={"a","b"}
        rows=[("MN","a"),("MN","new")]
        x=compare_tag_identity_rosters(raw,rows)
        self.assertEqual(x["raw_MN_tags_not_in_author_matrix"],1)
        self.assertEqual(x["author_matrix_MN_tags_not_in_raw"],1)
        self.assertFalse(x["raw_and_matrix_identity_rosters_match"])

if __name__=="__main__":
    unittest.main()
