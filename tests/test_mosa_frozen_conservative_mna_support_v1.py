"""Original MOSA strict-month MNA support with verified author ID labels only."""
import unittest
from datetime import date, timedelta
from analysis.audit_mosa_frozen_conservative_mna_support_v1 import (
    conservative_month_mna_structure,
)


def row(tag, sp, d, *, x="3", y="B"):
    return {"TOE":tag,"SPECIES":sp,
            "DATE":d.strftime("%d/%m/%Y"),"X":x,"Y":y,"GRID":"MOSA"}


class ConservativeSupportTests(unittest.TestCase):
    def test_true_strict_month_and_first_last_known_alive(self):
        mar=date(2002,3,12); apr=date(2002,4,12);may=date(2002,5,12)
        rec=[]
        for day in (mar,apr,may):
            for i in range(3):
                d=day+timedelta(days=i)
                for t in "abcde":
                    if day==apr and t=="e" and i==1:
                        continue
                    rec.append(row(t,"MN",d))
        r,monthly=conservative_month_mna_structure(
            rec,["TOE","SPECIES","DATE","X","Y","GRID"],
            set("abcde"),set(),
            require_months=1,require_years=1,
        )
        self.assertEqual(r["eligible_original_conservative_months"],3)
        self.assertEqual(r["years_with_ge2_distinct_MNA_levels"],0)
        self.assertEqual(len(monthly),3)
        self.assertEqual({v["MNA"] for v in monthly},{5})
        self.assertEqual(r["tag_histories_exceed_24_months"],0)
        self.assertFalse(r["W_B_or_centroids_opened"])

    def test_ambiguous_tag_cannot_satisfy_five_support(self):
        m=date(2000,7,10)
        rec=[row(t,"MN",m+timedelta(days=i))
             for t in "abcde" for i in range(3)]
        r,monthly=conservative_month_mna_structure(
            rec,["TOE","SPECIES","DATE","X","Y","GRID"],
            set("abcde"),{"e"},require_months=1,require_years=1)
        self.assertEqual(r["eligible_original_conservative_months"],0)
        self.assertEqual(r["strict_three_night_months"],1)
        self.assertEqual(len(monthly),0)

    def test_month_with_four_valid_capture_days_not_redefined_to_three(self):
        m=date(2000,5,10)
        rec=[row(t,"MN",m+timedelta(days=i))
             for t in "abcde" for i in range(4)]
        r,monthly=conservative_month_mna_structure(
            rec,["TOE","SPECIES","DATE","X","Y","GRID"],
            set("abcde"),set(),require_months=1,require_years=1)
        self.assertEqual(r["strict_three_night_months"],0)
        self.assertEqual(monthly,[])

    def test_reused_tag_longer_than_two_years_blocks_mna(self):
        a=date(1994,1,10);b=date(1997,1,10)
        rec=[row("a","MN",d) for d in (a,a+timedelta(days=1),
                                         b,b+timedelta(days=1))]
        r,monthly=conservative_month_mna_structure(
            rec,["TOE","SPECIES","DATE","X","Y","GRID"],
            {"a"},set(),require_months=1,require_years=1)
        self.assertEqual(r["tag_histories_exceed_24_months"],1)
        self.assertEqual(r["status"],"STOP_LONG_TAG_REUSE_FROZEN_MNA")


if __name__=="__main__":
    unittest.main()
