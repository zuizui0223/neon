"""Synthetic exactly-two-genus source eligibility and geographic STOP tests.

No new same-genus trap recurrence overlap, model Z, environmental effect,
or private original NEON site, location or animal tag is accessed.
"""
from datetime import date,timedelta
import json
import unittest

from analysis.audit_neon_crossseason_genus_support_v1 import source_event_support
from analysis.neon_macro_site_selection_v1 import site_metadata_index
from analysis.run_neon_two_genus_source_v1 import selection_summary


def event(site,season,month,genera):
    plot=site+"_P"
    key=season
    first=date(2025,month,3)
    p=[];r=[]
    for i in range(3):
        uid=site+"_"+season+"_"+str(i)
        p.append({
            "_site":site,"siteID":site,"plotID":plot,"eventID":key,
            "nightuid":uid,"collectDate":(first+timedelta(days=i)).isoformat(),
            "gridCompletion":"setting complete, processing complete",
        })
        for letter in "ABCDEFGHIJ":
            for col in range(1,11):
                r.append({
                    "_site":site,"plotID":plot,"nightuid":uid,
                    "trapCoordinate":letter+str(col),"trapStatus":"No capture",
                    "tagID":"","taxonID":"",
                })
        for j,g in enumerate(genera):
            for individual in range(2):
                r.append({
                    "_site":site,"plotID":plot,"nightuid":uid,
                    "trapCoordinate":chr(65+j)+str(individual+1),
                    "trapStatus":"Capture",
                    "tagID":site+"_"+season+"_"+g+"_"+str(individual),
                    "taxonID":g,
                })
    return p,r


def pair(genera):
    p1,r1=event("FAKE1","SPR",4,genera)
    p2,r2=event("FAKE1","SUM",7,genera)
    return p1+p2,r1+r2,{g:g for g in genera}


def private(site,plot,q,genera):
    return {
        "site":site,"site_plot":(site,plot),"season_ordinal":q,
        "capture_dates_A":(date(2025,4,3),date(2025,4,4),date(2025,4,5)),
        "capture_dates_B":(date(2025,7,3),date(2025,7,4),date(2025,7,5)),
        "A":{g:{"A1","A2"} for g in genera},
        "B":{g:{"A1","A2"} for g in genera},
    }


class TwoGenusSourceTests(unittest.TestCase):
    def test_exactly_two_optin_keeps_original_frozen_public_output(self):
        p,t,taxa=pair(("G1","G2"))
        reference=source_event_support(p,t,taxa)
        two=[];three=[]
        repeat=source_event_support(p,t,taxa,internal_units=three,internal_two_genus_units=two)
        self.assertEqual(reference,repeat)
        self.assertEqual(reference["eligible_2genus_diagnostic_pairs"],1)
        self.assertEqual(reference["eligible_primary_pairs"],0)
        self.assertEqual(len(two),1)
        self.assertEqual(len(three),0)
        self.assertEqual(set(two[0]["A"]),{"G1","G2"})
        for token in ("FAKE1","2025-04","A1","_G1_"):
            self.assertNotIn(token,json.dumps(repeat))

    def test_three_genus_original_receipt_unaffected(self):
        p,t,taxa=pair(("G1","G2","G3"))
        standard=source_event_support(p,t,taxa)
        two=[];three=[]
        trial=source_event_support(p,t,taxa,internal_units=three,internal_two_genus_units=two)
        self.assertEqual(standard,trial)
        self.assertEqual(len(two),0)
        self.assertEqual(len(three),1)
        self.assertEqual(trial["eligible_primary_pairs"],1)

    def test_source_only_geography_and_privacy(self):
        two=[private("FAKE1","P1",8050,("G1","G2")),
             private("FAKE2","P2",8050,("G1","G2"))]
        three=[private("FAKE1","P3",8053,("G1","G2","G3"))]
        meta=site_metadata_index([
            {"siteCode":"FAKE1","domainCode":"D01","siteType":"CORE","siteLatitude":38.},
            {"siteCode":"FAKE2","domainCode":"D02","siteType":"GRADIENT","siteLatitude":45.},
        ])
        z=selection_summary(two,three,meta,expected_two=2,expected_three=1)
        self.assertEqual(z["exact_two_source"]["pairs"],2)
        self.assertEqual(z["exact_two_source"]["physical_sites"],2)
        self.assertEqual(z["exact_two_source"]["domains"],2)
        self.assertEqual(z["macro_geographical_comparison"]["exact_two_sites_not_in_strict_primary"],1)
        self.assertEqual(z["exact_two_source"]["source_season_reuse_physical_sites"],0)
        self.assertFalse(z["precommitted_source_gate"]["passed"])
        self.assertFalse(z["scientific_scope"]["new_null_distribution_or_Z_computed"])
        for forbidden in ("FAKE1","FAKE2","P1","A1","G1"):
            self.assertNotIn(forbidden,json.dumps(z))

    def test_reused_source_season_drops_entire_physical_site(self):
        two=[private("FAKE1","P1",8050,("G1","G2")),
             private("FAKE1","P1",8051,("G1","G2"))]
        three=[private("FAKE2","P2",8050,("G1","G2","G3"))]
        meta=site_metadata_index([
            {"siteCode":"FAKE1","domainCode":"D01","siteType":"CORE","siteLatitude":38.},
            {"siteCode":"FAKE2","domainCode":"D02","siteType":"GRADIENT","siteLatitude":45.},
        ])
        z=selection_summary(two,three,meta,expected_two=2,expected_three=1)
        self.assertEqual(z["exact_two_source"]["source_season_reuse_physical_sites"],1)
        self.assertEqual(z["exact_two_source"]["source_whole_site_disjoint_sensitivity_pairs"],0)

    def test_two_vs_three_cohort_key_collision_stops(self):
        a=private("FAKE1","P1",8050,("G1","G2"))
        b=private("FAKE1","P1",8050,("G1","G2","G3"))
        m=site_metadata_index([
            {"siteCode":"FAKE1","domainCode":"D01","siteType":"CORE","siteLatitude":38.},
        ])
        with self.assertRaisesRegex(RuntimeError,"overlap"):
            selection_summary([a],[b],m,expected_two=1,expected_three=1)


if __name__=="__main__":
    unittest.main()
