"""Pure, outcome-blind checks on published MOSA marked-individual identity."""
import unittest

from analysis.audit_mosa_identity_discrepancy_v1 import identity_diagnostics


FIELDS=["NUMBER","DATE","GRID","SPECIES","X","Y","WEIGHT","TOE","SX","SEXCON","FLAGS"]


def sample(day,tag,sex="M",species="MN",number="1"):
    return {
        "NUMBER":number,"DATE":day,"GRID":"MOSA","SPECIES":species,
        "X":"1","Y":"A","WEIGHT":"22","TOE":tag,"SX":sex,
        "SEXCON":"NA","FLAGS":"",
    }


class IdentityDiscrepancyTests(unittest.TestCase):
    def test_full_toe_series_prefix_preserved_and_long_gap_not_silently_split(self):
        rows=[
            sample("13/03/1994","1520"),
            sample("14/03/1994","1520"),
            sample("13/06/1997","1520"),
            sample("13/03/1994","5/1520"),
        ]
        result=identity_diagnostics(rows,FIELDS)
        self.assertEqual(result["MN_capture_records"],4)
        self.assertEqual(result["distinct_verbatim_toe_ids"],2)
        self.assertEqual(result["tags_with_capture_gap_gt24_months"],1)
        self.assertEqual(result["extra_segments_if_gap_gt24_months"],1)
        self.assertEqual(result["hypothetical_distinct_segments"],3)
        self.assertFalse(result["toe_code_reuse_automatically_resolved"])

    def test_same_day_duplicate_and_sex_conflict_are_warnings_not_new_individuals(self):
        rows=[
            sample("13/03/1994","ID",sex="M"),
            sample("13/03/1994","ID",sex="F",number="2"),
            sample("14/03/1994","ID",sex="F",number="3"),
            sample("13/03/1994","OTHER",sex="F",species="TA")
        ]
        result=identity_diagnostics(rows,FIELDS)
        self.assertEqual(result["distinct_verbatim_toe_ids"],1)
        self.assertEqual(result["same_toe_same_date_extra_records"],1)
        self.assertEqual(result["tags_with_both_male_and_female_records"],1)
        self.assertEqual(result["MN_toe_labels_also_seen_in_other_species"],0)
        self.assertTrue(result["MNA_effects_unopened"])

    def test_empty_toe_is_an_identity_failure(self):
        rows=[sample("13/03/1994","")]
        with self.assertRaisesRegex(ValueError,"missing"):
            identity_diagnostics(rows,FIELDS)


if __name__=="__main__":
    unittest.main()
