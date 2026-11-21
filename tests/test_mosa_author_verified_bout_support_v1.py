"""MOSA authored 363×3-night response-independent repeated-identity support."""
import unittest
from datetime import date,timedelta

from analysis.audit_mosa_author_verified_bout_support_v1 import author_bout_support

def row(tag,sp,date_text,x="1",y="A"):
    return {"TOE":tag,"SPECIES":sp,"DATE":date_text,"X":x,"Y":y,"GRID":"MOSA"}

def authored_date_rows(start,event):
    return [{"date":(start+timedelta(days=i)).strftime("%d/%m/%Y"),
             "prim_capt":str(event),"sec_capt":str(i+1)}
            for i in range(3)]

class MOSAAuthorBoutSupportTests(unittest.TestCase):
    def test_verified_author_MN_repeat_cohort_and_exclusion_of_NA(self):
        a=date(2001,5,14); b=date(2001,6,14)
        times=authored_date_rows(a,1)+authored_date_rows(b,2)
        records=[]
        for tag in ("a","b","c","d","e"):
            for start in (a,b):
                for i in (0,1):
                    records.append(row(tag,"MN",(start+timedelta(days=i)).strftime("%d/%m/%Y")))
        for i in (0,1,2):
            records.append(row("unknown","NA",(a+timedelta(days=i)).strftime("%d/%m/%Y")))
            records.append(row("other","TA",(a+timedelta(days=i)).strftime("%d/%m/%Y")))
        report=author_bout_support(records,["TOE","SPECIES","DATE","X","Y","GRID"],
                                   times,{"a","b","c","d","e"},set(),
                                   expected_primary=None)
        self.assertEqual(report["official_three_night_primary_occasions"],2)
        self.assertEqual(report["occasions_m_ge5"],2)
        self.assertEqual(report["supported_years"],1)
        self.assertEqual(report["tag_histories_exceed_24_months"],0)
        self.assertEqual(report["author_MN_tag_roster_verified"],True)
        self.assertFalse(report["MNA_W_B_or_density_effects_opened"])

    def test_whitespace_collision_excludes_entire_ambiguous_code(self):
        a=date(2002,1,15); times=authored_date_rows(a,1)
        records=[]
        for tag in "abcde":
            for i in (0,1):
                records.append(row(tag,"MN",(a+timedelta(days=i)).strftime("%d/%m/%Y")))
        report=author_bout_support(records,["TOE","SPECIES","DATE","X","Y","GRID"],
                                   times,set("abcde"),{"e"},
                                   expected_primary=None)
        self.assertEqual(report["occasions_m_ge5"],0)
        self.assertEqual(report["occasions_m_ge4"],1)
        self.assertEqual(report["ambiguous_normalized_TOE_codes_excluded"],1)

    def test_long_reused_toe_history_triggers_identity_stop(self):
        a=date(1995,1,10);b=date(1998,1,10)
        times=authored_date_rows(a,1)+authored_date_rows(b,2)
        records=[row("x","MN",d.strftime("%d/%m/%Y"))
                 for d in (a,a+timedelta(days=1),b,b+timedelta(days=1))]
        report=author_bout_support(records,["TOE","SPECIES","DATE","X","Y","GRID"],
                                   times,{"x"},set(),expected_primary=None)
        self.assertEqual(report["tag_histories_exceed_24_months"],1)
        self.assertEqual(report["status"],"STOP_LONG_TERM_REUSED_TAG_IDENTITIES")

if __name__=="__main__":
    unittest.main()
