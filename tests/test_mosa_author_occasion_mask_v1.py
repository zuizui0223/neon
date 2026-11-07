"""Effect-blind comparisons with authors' actual 3-consecutive-night calendar."""
import unittest
from datetime import date
from analysis.audit_mosa_author_occasion_mask_v1 import (
    validated_author_days, classify_missing_by_author_days, git_blob_sha1,
)

class AuthorOccasionMaskTests(unittest.TestCase):
    def test_git_blob_sha1_matches_known_content(self):
        self.assertEqual(
            git_blob_sha1(b"hello"),
            "b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0"
        )
        self.assertNotEqual(git_blob_sha1(b"hello\n"),git_blob_sha1(b"hello"))

    def test_three_night_author_primary_is_valid(self):
        rows=[{"date":f"15/03/1994","prim_capt":"1","sec_capt":"1"},
              {"date":"16/03/1994","prim_capt":"1","sec_capt":"2"},
              {"date":"17/03/1994","prim_capt":"1","sec_capt":"3"}]
        o=validated_author_days(rows,expected_sessions=None)
        self.assertEqual(o["primary_sessions"],1)
        self.assertEqual(o["secondary_nights"],3)
        self.assertIn(date(1994,3,15),o["_author_days"])

    def test_cross_month_three_nights_are_valid_by_primary_id(self):
        rows=[{"date":d,"prim_capt":"1","sec_capt":str(i+1)}
              for i,d in enumerate(("30/03/1994","31/03/1994","01/04/1994"))]
        o=validated_author_days(rows,expected_sessions=None)
        self.assertEqual(o["primary_sessions"],1)
        self.assertEqual(len(o["_author_days"]),3)

    def test_duplicate_author_primary_secondary_fails(self):
        rows=[{"date":d,"prim_capt":"1","sec_capt":v}
              for d,v in (("15/03/1994","1"),("16/03/1994","1"),("17/03/1994","3"))]
        with self.assertRaisesRegex(ValueError,"not exactly three"):
            validated_author_days(rows,expected_sessions=None)

    def test_multinight_retained_dates_explain_high_priority_id_cases(self):
        fields=["DATE","GRID","SPECIES","TOE","X","Y","FLAGS"]
        records=[]
        for tag,days,flag in (
            ("present",["15/03/1994"],""),
            ("once",["15/03/1994"],""),
            ("two",["15/03/1994","16/03/1994"],""),
            ("na",["15/03/1994","16/03/1994"],""),
            ("flagged",["15/03/1994","16/03/1994"],"Corrected")
        ):
            for d in days:
                records.append({
                    "DATE":d,"GRID":"MOSA","SPECIES":"MN",
                    "TOE":tag,"X":"4","Y":"B","FLAGS":flag})
        accepted={date(1994,3,15),date(1994,3,16),date(1994,3,17)}
        result=classify_missing_by_author_days(
            records,fields,[("MN","present"),("NA","na")],accepted,
            expected_original_MN=None)
        x=result["retained_date_missing_ID_subgroups"]
        self.assertEqual(x["any_author_date"],4)
        self.assertEqual(x["valid_station_and_two_distinct_dates"],3)
        self.assertEqual(x["valid_two_dates_without_flags_and_without_NA_row"],1)
        self.assertEqual(x["valid_two_dates_also_in_author_NA"],1)
        self.assertEqual(x["valid_two_dates_with_any_flag"],1)
        self.assertEqual(x["valid_two_dates_matching_author_NO_CAPTURE_placeholder"],0)


    def test_explicit_author_NO_CAPTURE_placeholder_not_counted_as_animal(self):
        fields=["DATE","GRID","SPECIES","TOE","X","Y","FLAGS"]
        rows=[]
        for d in ("15/03/1994","16/03/1994"):
            rows.append({"DATE":d,"GRID":"MOSA","SPECIES":"MN",
                         "TOE":"NO_CAPTURE","X":"1","Y":"A","FLAGS":""})
        result=classify_missing_by_author_days(
            rows,fields,[],{date(1994,3,15),date(1994,3,16)},
            expected_original_MN=None)
        x=result["retained_date_missing_ID_subgroups"]
        self.assertEqual(x["valid_two_dates_without_flags_and_without_NA_row"],1)
        self.assertEqual(x["valid_two_dates_matching_author_NO_CAPTURE_placeholder"],1)

    def test_missing_tag_retained_date_is_not_auto_reassigned(self):
        fields=["DATE","GRID","SPECIES","TOE","X","Y","FLAGS"]
        records=[
            {"DATE":"15/03/1994","GRID":"MOSA","SPECIES":"MN",
             "TOE":"tag_a","X":"1","Y":"A","FLAGS":""},
            {"DATE":"15/03/1994","GRID":"MOSA","SPECIES":"MN",
             "TOE":"tag_b","X":"1","Y":"A","FLAGS":""},
            {"DATE":"18/03/1994","GRID":"MOSA","SPECIES":"MN",
             "TOE":"tag_c","X":"1","Y":"A","FLAGS":"FLAG"},
            {"DATE":"18/03/1994","GRID":"MOSA","SPECIES":"NA",
             "TOE":"tag_c","X":"1","Y":"A","FLAGS":""},
        ]
        matrix=[("MN","tag_a"),("NA","tag_c")]
        d=classify_missing_by_author_days(
            records,fields,matrix,{date(1994,3,15)},
            expected_original_MN=None)
        self.assertEqual(d["raw_MN_missing_from_author_MN"],2)
        self.assertEqual(d["missing_with_any_capture_on_author_retained_dates"],1)
        self.assertEqual(d["missing_exclusively_off_author_retained_dates"],1)
        self.assertEqual(d["missing_also_in_author_NA"],1)
        self.assertFalse(d["all_omissions_explained_by_dates"])
        self.assertFalse(d["species_NA_reassigned"])

if __name__=="__main__":
    unittest.main()
