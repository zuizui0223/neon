"""Effect-blind raw-versus-authored ID omission reasons, not animal reassignment."""
import unittest
from analysis.audit_mosa_author_missing_tag_sources_v1 import classify_missing_tags


class AuthorMissingTagSourceTests(unittest.TestCase):
    def setUp(self):
        records=[]
        for ds in ("2020-01-01","2020-01-02","2020-01-03"):
            records.append({"SPECIES":"MN","TOE":"a","DATE":ds,"GRID":"MOSA","X":"1","Y":"A","FLAGS":""})
        for ds in ("2020-01-01","2020-01-03"):
            records.append({"SPECIES":"MN","TOE":"c","DATE":ds,"GRID":"MOSA","X":"1","Y":"B","FLAGS":"flag"})
        for ds in ("2020-02-01","2020-02-04"):
            records.append({"SPECIES":"MN","TOE":"d","DATE":ds,"GRID":"MOSA","X":"2","Y":"B","FLAGS":""})
        records.append({"SPECIES":"MN","TOE":"b","DATE":"2020-01-01","GRID":"MOSA","X":"3","Y":"A","FLAGS":""})
        records.append({"SPECIES":"LR","TOE":"nonMNtag","DATE":"2020-01-01","GRID":"MOSA","X":"2","Y":"A","FLAGS":""})
        self.rows=records

    def test_separates_non_three_night_exclusion_and_unexplained_missing_tags(self):
        matrix=[("MN","a"),("MN","b"),("NA","c"),("NA","nonMNtag")]
        x=classify_missing_tags(self.rows,list(self.rows[0]),matrix, expected_raw_mn=None)
        self.assertEqual(x["raw_MN_unique_TOE"],4)
        self.assertEqual(x["matrix_MN_unique_TOE"],2)
        self.assertEqual(x["raw_MN_missing_from_matrix_MN"],2)
        self.assertEqual(x["missing_raw_MN_tags_with_capture_in_strict_three_day_month"],1)
        self.assertEqual(x["missing_raw_MN_tags_with_only_non_strict_month_captures"],1)
        self.assertEqual(x["missing_raw_MN_tags_with_ge2_capture_days_in_strict_three_day_month"],1)
        self.assertEqual(x["missing_raw_MN_tags_appearing_under_matrix_NA"],1)
        self.assertEqual(x["matrix_NA_tag_codes_found_in_raw_nonMN"],1)
        self.assertFalse(x["species_NA_code_identity_resolved"])
        self.assertFalse(x["MNA_or_WB_unsealed"])

    def test_fails_if_matrix_MN_code_not_present_in_raw_species_MN(self):
        with self.assertRaisesRegex(ValueError,"unknown in raw MN"):
            classify_missing_tags(self.rows,list(self.rows[0]),[("MN","ghost")],
                                  expected_raw_mn=None)


if __name__=="__main__":
    unittest.main()
