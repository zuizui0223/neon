import unittest
from datetime import date,timedelta

from analysis.audit_mosa_effect_blind_structure_v1 import (
    effect_blind_support,published_field_map,parse_all_dates,
)
from analysis.audit_mosa_zenodo_source_schema_v1 import PublishedSourceError

FIELDS=["DATE","GRID","SPECIES","X","Y","TOE-ID"]


def synth(start=2000,end=2010,months=(1,2,3,4,5,6),night_count=3):
    out=[]
    for year in range(start,end):
        for month in months:
            first=date(year,month,5)
            for night in range(night_count):
                day=(first+timedelta(days=night)).isoformat()
                for person in range(5):
                    out.append({
                        "DATE":day,"GRID":"MOSA","SPECIES":"MN",
                        "X":str(person+1),"Y":"A",
                        "TOE-ID":f"{year}-{month}-{person}",
                    })
    return out


class MOSAStructuralSupportTests(unittest.TestCase):
    def test_29year_one_site_support_without_WB_or_MNA(self):
        result=effect_blind_support(FIELDS,synth())
        self.assertEqual(result["status"],"GO_MOSA_ONE_SITE_LONGITUDINAL_SUPPORT_ONLY")
        self.assertEqual(result["consecutive_three_day_MN_months"],60)
        self.assertEqual(result["months_with_at_least_five_distinct_two_night_MN_tags"],60)
        self.assertEqual(result["distinct_years_with_support"],10)
        self.assertFalse(result["historical_MNA_support_or_variation_opened"])
        self.assertFalse(result["W_B_or_individual_spatial_centres_computed"])

    def test_incomplete_months_do_not_borrow_future_month_or_nights(self):
        result=effect_blind_support(FIELDS,synth(night_count=2))
        self.assertEqual(result["months_with_at_least_five_distinct_two_night_MN_tags"],0)
        self.assertEqual(result["status"],"STOP_MOSA_PRE_EFFECT_STRUCTURAL_SUPPORT")

    def test_ambiguous_alias_or_date_stops(self):
        with self.assertRaisesRegex(PublishedSourceError,"ambiguous"):
            published_field_map(FIELDS+["TOEID"])
        with self.assertRaisesRegex(PublishedSourceError,"ambiguous"):
            parse_all_dates(["01/02/2000","03/04/2000"])

    def test_legacy_column_aliases_exact(self):
        self.assertEqual(published_field_map(FIELDS)["tag"],"TOE-ID")

    def test_real_source_header_and_DMY_date_format(self):
        header="NUMBER;DATE;GRID;SPECIES;X;Y;WEIGHT;TOE;SX;SEXCON;FLAGS".split(";")
        fmap=published_field_map(header)
        self.assertEqual(fmap["tag"],"TOE")
        self.assertEqual(fmap["x"],"X")
        dates=parse_all_dates(["15/03/1994","16/03/1994","17/03/1994"])
        self.assertEqual(dates["15/03/1994"].isoformat(),"1994-03-15")

    def test_more_than_three_distinct_days_same_month_excluded(self):
        base=synth(start=1994,end=1995,months=(3,),night_count=3)
        extension={**base[0],"DATE":"22/03/1994","TOE-ID":"extra"}
        # Use ISO dates for the whole fixture, keeping the fourth event
        # in a different week of the same month, as in early MOSA records.
        extension["DATE"]="1994-03-22"
        result=effect_blind_support(FIELDS,base+[extension])
        self.assertEqual(result["consecutive_three_day_MN_months"],0)


if __name__=="__main__":
    unittest.main()
