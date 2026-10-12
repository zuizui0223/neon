"""MOSA source-identity diagnostics prior to MNKA or spatial effects."""
import unittest
from analysis.audit_mosa_identity_integrity_v1 import examine_identity


def row(date,tag, species="MN", station="1",sex="F",flag=""):
    return {"NUMBER":"1","DATE":date,"GRID":"MOSA","SPECIES":species,
            "X":station,"Y":"A","WEIGHT":"22","TOE":tag,
            "SX":sex,"SEXCON":"CSN","FLAGS":flag}


FIELDS=list(row("13/03/1994","123").keys())


class IdentityIntegrityTests(unittest.TestCase):
    def test_colliding_toe_code_same_night_is_counted_but_not_repaired(self):
        rows=[
            row("13/03/1994","123","MN","1"),
            row("13/03/1994","123","MN","20"),
            row("14/03/1994","123","MN","3"),
            row("13/03/1994","2/123","MN","2"),
        ]
        out=examine_identity(FIELDS,rows,published_total=None)
        self.assertEqual(out["MN_distinct_raw_TOE"],2)
        self.assertEqual(out["MN_TOE_date_multiple_station_collision_groups"],1)
        self.assertEqual(out["MN_tags_with_series_prefix"],1)
        self.assertFalse(out["W_B_or_MNA_effects_opened"])

    def test_span_more_than_24_months_is_flagged(self):
        rows=[
            row("13/03/1994","123"),
            row("13/04/1997","123"),
            row("13/04/1997","3/123"),
        ]
        out=examine_identity(FIELDS,rows,published_total=None)
        self.assertEqual(out["MN_TOE_span_gt24_months"],1)
        self.assertEqual(out["MN_distinct_raw_TOE"],2)

    def test_published_id_count_mismatch_fails_closed(self):
        rows=[row("13/03/1994","A"),row("13/03/1994","B")]
        out=examine_identity(FIELDS,rows,published_total=3)
        self.assertEqual(out["status"],"STOP_MOSA_PUBLISHED_INDIVIDUAL_COUNT_MISMATCH")
        self.assertEqual(out["MN_individual_count_gap_published_minus_TOE"],1)

    def test_whitespace_and_case_are_not_silently_collapsed(self):
        rows=[row("13/03/1994","A"),row("14/03/1994","a"),
              row("13/03/1994","5/1520")]
        out=examine_identity(FIELDS,rows,published_total=None)
        self.assertEqual(out["MN_distinct_raw_TOE"],3)
        self.assertTrue(out["individual_identity_reassignment_prohibited"])


if __name__=="__main__":
    unittest.main()
