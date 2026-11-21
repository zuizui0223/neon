"""Effect-blind author-first-retained-species replication of MOSA ID filtering."""
import unittest
from datetime import date

from analysis.audit_mosa_author_first_species_v1 import classify_first_species_provenance

FIELDS=["DATE","GRID","SPECIES","TOE","X","Y","FLAGS"]
D1="15/03/1994"
D2="16/03/1994"
D3="17/03/1994"
OUTSIDE="18/03/1994"
DATES={date(1994,3,i) for i in (15,16,17)}


def rec(tag, species, day):
    return {"DATE":day,"GRID":"MOSA","SPECIES":species,
            "TOE":tag,"X":"3","Y":"B","FLAGS":""}


class FirstRetainedSpeciesTests(unittest.TestCase):
    def test_first_retained_species_displaces_later_MN_taxon(self):
        records=[
            rec("kept","MN",D1),
            rec("other","TA",D1),rec("other","MN",D2),
            rec("unknown","NA",D1),rec("unknown","MN",D3),
            rec("off","MN",OUTSIDE),
            rec("needs_check","MN",D2),rec("needs_check","MN",D3),
        ]
        matrix=[("MN","kept"),("NA","unknown"),("TA","other")]
        r=classify_first_species_provenance(
            records,FIELDS,matrix,DATES,expected_raw_mn=None,
            expected_author_mn=None,expected_missing=None)
        self.assertEqual(r["raw_MN_codes_absent_author_MN"],4)
        self.assertEqual(r["missing_with_any_author_date_capture"],3)
        self.assertEqual(r["missing_first_retained_species"]["NA"],1)
        self.assertEqual(r["missing_first_retained_species"]["OTHER"],1)
        self.assertEqual(r["missing_first_retained_species"]["MN"],1)
        self.assertEqual(r["missing_first_retained_species"]["NO_RETAINED_RECORD"],1)
        self.assertEqual(r["first_MN_missing_from_author_MN_without_NA_row"],1)
        self.assertFalse(r["species_NA_reassigned_to_MN"])
        self.assertFalse(r["individual_ids_disclosed"])
        self.assertFalse(r["MNA_W_B_density_effects_opened"])

    def test_raw_first_species_not_same_as_first_retained_species(self):
        records=[
            rec("a","NA",OUTSIDE),rec("a","MN",D1),
            rec("b","MN",D1)
        ]
        r=classify_first_species_provenance(records,FIELDS,
            [("MN","a"),("MN","b")],DATES,
            expected_raw_mn=None,expected_author_mn=None,
            expected_missing=None)
        self.assertEqual(r["author_MN_codes_first_retained_as_MN"],2)
        self.assertEqual(r["author_MN_codes_first_retained_not_MN"],0)

    def test_exact_versus_whitespace_normalized_author_duplicates(self):
        records=[rec("a","MN",D1)]
        matrix=[("MN","a"),("MN","a "),("MN","a")]
        r=classify_first_species_provenance(records,FIELDS,matrix,DATES,
            expected_raw_mn=None,expected_author_mn=None,
            expected_missing=None)
        self.assertEqual(r["author_MN_exact_duplicate_rows"],1)
        self.assertEqual(r["author_MN_normalized_duplicate_rows"],2)
        self.assertEqual(r["author_MN_duplicate_rows_created_by_normalization"],1)


if __name__=="__main__":
    unittest.main()
