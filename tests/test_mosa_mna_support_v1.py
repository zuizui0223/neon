"""Effect-blind MOSA monthly MNA support and toe-ID series identity tests."""
import unittest
from analysis.audit_mosa_mna_support_v1 import (
    compute_mna_support, build_known_alive_by_month
)


def row(date,tag,x="1",y="A",species="MN"):
    return {"NUMBER":"1","DATE":date,"GRID":"MOSA","SPECIES":species,
            "X":x,"Y":y,"WEIGHT":"23","TOE":tag,"SX":"F",
            "SEXCON":"CSN","FLAGS":""}
FIELDS=list(row("13/03/1994","001").keys())


class MOSAMNASupportTests(unittest.TestCase):
    def test_prefix_identity_preserved_across_code_reuse(self):
        rows=[
            row("13/03/1994","1520"),row("14/03/1994","1520",x="2"),
            row("13/04/1994","1520",x="3"),
            row("13/03/1994","5/1520",x="4"),
            row("13/05/1994","5/1520",x="5"),
        ]
        data=build_known_alive_by_month(rows,FIELDS)
        self.assertEqual(data["unique_tags"],2)
        self.assertEqual(data["MNA_by_month"][(1994,3)],2)
        self.assertEqual(data["MNA_by_month"][(1994,4)],2)
        self.assertEqual(data["MNA_by_month"][(1994,5)],1)

    def test_monthly_MNA_bridges_no_recapture_month(self):
        rows=[
            row("13/03/1994","A"),row("14/03/1994","A",x="2"),
            row("13/04/1994","B"),row("14/04/1994","B",x="3"),
            row("13/05/1994","A"),row("14/05/1994","A",x="4"),
        ]
        data=build_known_alive_by_month(rows,FIELDS)
        self.assertEqual(data["MNA_by_month"][(1994,4)],2)
        self.assertEqual(data["unique_tags"],2)

    def test_calendar_month_must_have_three_consecutive_dates(self):
        rows=[]
        for month in (3,4):
            for day in (13,14,15):
                for tag in ("A","B","C","D","E"):
                    rows.append(row(f"{day:02d}/{month:02d}/1994",tag,x=str(day)))
        result,_=compute_mna_support(rows,FIELDS,expect_published=False)
        self.assertEqual(result["candidate_exact_three_night_months"],2)
        self.assertEqual(result["months_with_repeat_supported_m_ge5"],2)
        self.assertEqual(result["years_with_two_MNA_levels"],0)
        self.assertEqual(result["status"],"STOP_MOSA_MNA_VARIATION_SUPPORT")

    def test_same_toe_code_over_two_years_is_flagged(self):
        rows=[row("13/03/1994","A"),row("13/05/1997","A")]
        data=build_known_alive_by_month(rows,FIELDS)
        self.assertEqual(data["tag_histories_over_24_months"],1)

    def test_known_alive_never_below_observed_tags(self):
        rows=[row("13/03/1994","A"),row("13/03/1994","B"),
              row("13/04/1994","A"),row("13/06/1994","C")]
        data=build_known_alive_by_month(rows,FIELDS)
        for month,n in data["captured_unique_by_month"].items():
            self.assertGreaterEqual(data["MNA_by_month"][month],n)


if __name__=="__main__":
    unittest.main()
