"""TDD: synthetic source-only support for seasonal genus spatial-template transfer.

No observed cross-season genus×trap recurrence, null effect, individual
movement, W/B or actual source animal IDs are processed in these tests.
"""
from __future__ import annotations

from datetime import date,timedelta
import unittest

from analysis.audit_neon_crossseason_genus_support_v1 import (
    season_ordinal, source_event_support
)

COMPLETE="setting complete, processing complete"


def row_session(site,plot,event,start):
    d=date.fromisoformat(start)
    return [{
        "nightuid":f"{site}-{event}-night{i}",
        "eventID":event,"plotID":plot,"_site":site,
        "siteID":site,"gridCompletion":COMPLETE,
        "collectDate":(d+timedelta(days=i)).isoformat(),
    } for i in range(3)]


def coord(k):
    return chr(65+(k//10)) + str(k%10+1)


def effort(site,plot,event,start,types=("GEN1","GEN2","GEN3"),tags_prefix="S"):
    out=[]
    for i in range(3):
        night=f"{site}-{event}-night{i}"
        for k in range(100):
            out.append({
                "_site":site,"plotID":plot,"nightuid":night,
                "trapCoordinate":coord(k),"trapStatus":"No capture",
                "tagID":"","taxonID":"",
            })
        for ix,genus in enumerate(types):
            for j in range(2):
                out.append({
                    "_site":site,"plotID":plot,"nightuid":night,
                    "trapCoordinate":coord(3*ix+j),"trapStatus":"Capture",
                    "tagID":f"{tags_prefix}-{genus}-{j}",
                    "taxonID":genus,
                })
    return out


def two_seasons(gen=("GEN1","GEN2","GEN3")):
    p=row_session("SITE","P","SPRING","2022-04-02")+row_session("SITE","P","SUMMER","2022-07-02")
    t=(effort("SITE","P","SPRING","2022-04-02",gen,tags_prefix="early")+
       effort("SITE","P","SUMMER","2022-07-02",gen,tags_prefix="late"))
    return p,t,{z:z for z in gen}


class CrossSeasonGenusSupportTests(unittest.TestCase):
    def test_calendar_season_edges_and_December_rollover(self):
        self.assertEqual(season_ordinal(date(2022,4,2))+1,season_ordinal(date(2022,7,2)))
        self.assertEqual(season_ordinal(date(2022,11,9))+1,season_ordinal(date(2022,12,18)))
        self.assertEqual(season_ordinal(date(2022,12,18)),season_ordinal(date(2023,1,4)))
        self.assertNotEqual(season_ordinal(date(2023,1,4)),season_ordinal(date(2023,3,4)))

    def test_exact_three_nights_two_seasons_three_genera_is_primary_pair(self):
        p,t,taxa=two_seasons()
        result=source_event_support(p,t,taxa)
        self.assertEqual(result["eligible_primary_pairs"],1)
        self.assertEqual(result["eligible_primary_sites"],1)
        self.assertEqual(result["primary_shared_genus_count_distribution"],{"3":1})
        self.assertFalse(result["crossseason_spatial_overlap_opened"])
        self.assertTrue(result["known_individuals_shared_betweenseason_excluded"])

    def test_two_genera_only_diagnostic_not_primary(self):
        p,t,taxa=two_seasons(("GEN1","GEN2"))
        result=source_event_support(p,t,taxa)
        self.assertEqual(result["eligible_primary_pairs"],0)
        self.assertEqual(result["eligible_2genus_diagnostic_pairs"],1)

    def test_shared_individuals_are_removed_from_both_seasons(self):
        p,t,taxa=two_seasons()
        for r in t:
            if r["tagID"]=="late-GEN3-0":
                r["tagID"]="early-GEN3-0"
        result=source_event_support(p,t,taxa)
        self.assertEqual(result["eligible_primary_pairs"],0)
        self.assertGreater(result["bridge_tag_histories_excluded"],0)

    def test_out_of_protocol_incomplete_or_less_effort_not_eligible(self):
        p,t,taxa=two_seasons()
        for r in p:
            if r["eventID"]=="SUMMER":
                r["gridCompletion"]="Incomplete"
        result=source_event_support(p,t,taxa)
        self.assertEqual(result["eligible_primary_pairs"],0)
        p,t,taxa=two_seasons()
        t=[r for r in t if not(
            r["nightuid"]=="SITE-SUMMER-night0"
            and r["trapStatus"]=="No capture"
            and r["trapCoordinate"] in {coord(j) for j in range(20)}
        )]
        result=source_event_support(p,t,taxa)
        self.assertEqual(result["eligible_primary_pairs"],0)

    def test_more_than_one_bout_per_season_first_only(self):
        p,t,taxa=two_seasons()
        second=row_session("SITE","P","LATE_SPRING","2022-05-04")
        p+=second
        t+=effort("SITE","P","LATE_SPRING","2022-05-04",tags_prefix="alternate")
        result=source_event_support(p,t,taxa)
        self.assertEqual(result["eligible_primary_pairs"],1)
        self.assertEqual(result["eligible_distinct_selected_events"],2)

    def test_genus_switch_source_tag_excluded_globally(self):
        p,t,taxa=two_seasons()
        t.append({
            "_site":"SITE","plotID":"P","nightuid":"SITE-SPRING-night0",
            "trapCoordinate":"J10","trapStatus":"Capture",
            "tagID":"early-GEN3-0","taxonID":"GEN2",
        })
        result=source_event_support(p,t,taxa)
        self.assertEqual(result["eligible_primary_pairs"],0)
        self.assertGreaterEqual(result["cross_genus_identity_conflicts"],1)

    def test_nonconsecutive_seasons_never_bridged(self):
        p,t,taxa=two_seasons()
        for r in p:
            if r["eventID"]=="SUMMER":
                r["collectDate"]=r["collectDate"].replace("-07-","-10-")
        result=source_event_support(p,t,taxa)
        self.assertEqual(result["eligible_primary_pairs"],0)

    def test_animal_IDs_and_source_trap_labels_not_exported(self):
        p,t,taxa=two_seasons()
        result=source_event_support(p,t,taxa)
        for forbidden in ("early-GEN1","late-GEN2","SITE","SPRING","A1"):
            self.assertNotIn(forbidden,str(result))
        self.assertTrue(result["no_source_individual_or_geographic_ids_exported"])

    def test_private_internal_units_keep_exact_original_three_night_dates(self):
        plot,trap,taxa=two_seasons()
        private=[]
        summary=source_event_support(plot,trap,taxa,internal_units=private)
        self.assertEqual(summary["eligible_primary_pairs"],1)
        self.assertEqual(len(private),1)
        self.assertEqual(
            tuple(d.isoformat() for d in private[0]["capture_dates_A"]),
            ("2022-04-02","2022-04-03","2022-04-04"),
        )
        self.assertEqual(
            tuple(d.isoformat() for d in private[0]["capture_dates_B"]),
            ("2022-07-02","2022-07-03","2022-07-04"),
        )
        for date_str in ("2022-04-02","2022-07-02"):
            self.assertNotIn(date_str,str(summary))

    def test_complete_session_without_genus_assignments_does_not_qualify(self):
        p,t,taxa=two_seasons()
        only_effort=[r for r in t if r["trapStatus"]=="No capture"]
        r=source_event_support(p,only_effort,taxa)
        self.assertEqual(r["eligible_primary_pairs"],0)


if __name__=="__main__":
    unittest.main()
