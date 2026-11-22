"""Synthetic official NEON trap-status operability source-only QA.

Specifically verifies all six original source nights, code6 set/empty,
codes4/5 captures, 1/2/3 disturbed/unset, unknown/mislabelled values, and
retaining original season-exclusive tag-disjoint genus source matrices.
"""
import json,unittest
from datetime import date,timedelta
from analysis.neon_macro_6night_operable_trap_status_v1 import (
    published_trap_status,all_six_operable_source
)


def fixture():
    plots=[];traps=[];units=[]
    for site in ("FAKEA","FAKEB"):
        plot=site+"_P"
        starts=(date(2024,4,3),date(2024,7,3))
        for j,first in enumerate(starts):
            event=site+("_APR" if j==0 else "_JUL")
            for night in range(3):
                uid=event+"_N"+str(night)
                plots.append({
                    "_site":site,"siteID":site,"plotID":plot,
                    "eventID":event,"nightuid":uid,
                    "gridCompletion":"setting complete, processing complete",
                    "collectDate":(first+timedelta(days=night)).isoformat()
                })
                for letter in "ABCDEFGHIJ":
                    for row in range(1,11):
                        traps.append({
                            "_site":site,"plotID":plot,"nightuid":uid,
                            "trapCoordinate":letter+str(row),
                            "trapStatus":"6 - trap set and empty",
                        })
        units.append({
            "site":site,"site_plot":(site,plot),
            "season_ordinal":4*2024+1,
            "capture_dates_A":tuple(starts[0]+timedelta(days=i) for i in range(3)),
            "capture_dates_B":tuple(starts[1]+timedelta(days=i) for i in range(3)),
            "A":{"G1":{"A1","A2"},"G2":{"B1","B2"}},
            "B":{"G1":{"A1","A2"},"G2":{"B1","B2"}},
        })
    return units,plots,traps,{"FAKEA":"D01","FAKEB":"D02"}


def audit(*,items=None,minimum_pairs=1):
    units,plots,traps,meta=items or fixture()
    return all_six_operable_source(units,plots,traps,meta,expected_pairs=2,
       expected_sites=2,minimum_pairs=minimum_pairs,
       minimum_sites=1,minimum_domains=1)


class OfficialStatus456SourceTests(unittest.TestCase):
    def test_official_code_categories_conservatively_recognized(self):
        good=("4 - more than 1 capture in one trap","5 - capture",
              "6 - trap set and empty","4","5","6")
        for value in good:
            cat,yes=published_trap_status(value)
            self.assertTrue(yes,value)
            self.assertIn(cat,("4","5","6"))
        bad=("0 - no data","1 - trap not set / capture(s) not processed",
             "2 - trap disturbed/door closed but empty",
             "3 - trap door open w/ spoor left","","No capture",
             "6 - trap not set","6 - capture","5 - no capture",
             "unlabeled","7 - trap set")
        for value in bad:
            _,yes=published_trap_status(value)
            self.assertFalse(yes,value)

    def test_all_six_original_set_empty_stations_qualify(self):
        summary,private=audit()
        self.assertEqual(summary["status"],"SOURCE_SIX_NIGHT_OPERABLE_456_GO")
        self.assertEqual(summary["all_six_verified_status_456_stations"]["minimum"],100)
        self.assertEqual(summary["retained_pairs"],2)
        self.assertEqual(len(private),2)
        self.assertEqual(summary["source_status_code_row_counts"],{"6":1200})
        self.assertTrue(summary["inference_limits"]["no_original_genus_exact_trap_overlap_opened"])

    def test_disturbed_one_night_station_is_not_operable_entire_six(self):
        units,plots,traps,meta=fixture()
        row=next(x for x in traps if x["nightuid"]=="FAKEA_JUL_N2"
                 and x["trapCoordinate"]=="J10")
        row["trapStatus"]="2 - trap disturbed/door closed but empty"
        summary,private=audit(items=(units,plots,traps,meta))
        self.assertEqual(summary["all_six_verified_status_456_stations"]["minimum"],99)
        self.assertEqual(summary["retained_pairs"],2)
        self.assertEqual(summary["source_status_code_row_counts"]["2"],1)

    def test_not_set_and_unknown_multiple_rows_excludes_conservatively(self):
        units,plots,traps,meta=fixture()
        for row in traps:
            if row["nightuid"]=="FAKEA_APR_N0" and row["trapCoordinate"]=="A1":
                row["trapStatus"]="5 - capture"
        traps.append({
            "_site":"FAKEA","plotID":"FAKEA_P",
            "nightuid":"FAKEA_APR_N0","trapCoordinate":"A1",
            "trapStatus":"1 - trap not set / capture(s) not processed",
        })
        summary,private=audit(items=(units,plots,traps,meta))
        self.assertEqual(summary["all_six_verified_status_456_stations"]["minimum"],99)
        self.assertEqual(summary["retained_pairs"],1)
        self.assertEqual(summary["pair_genus_station_retention_reason_counts"].get(
              "genus_two_occupied_station_support_lost"),1)
        self.assertEqual(summary["source_status_duplicates_and_unknown_location"][
              "duplicate_original_station_night_row"],1)

    def test_at_least_11_unset_stations_fails_predeclared_common_90_gate(self):
        units,plots,traps,meta=fixture()
        for row in traps:
            if row["nightuid"]=="FAKEA_JUL_N2" and row["trapCoordinate"] in {
                 "J1","J2","J3","J4","J5","J6","J7","J8","J9","J10","I10"}:
                row["trapStatus"]="1 - trap not set"
        report,_=audit(items=(units,plots,traps,meta),minimum_pairs=2)
        self.assertFalse(report["original_source_rule"]["passed"])
        self.assertEqual(report["status"],"STOP_OPERABLE_456_SIX_NIGHT_SOURCE_SUPPORT")
        self.assertEqual(report["pair_genus_station_retention_reason_counts"][
              "fewer_than_90_all_six_operability_coded_stations"],1)

    def test_report_contains_no_source_site_taxon_station_or_dates(self):
        report,_=audit()
        val=json.dumps(report)
        for hidden in ("FAKEA","FAKEB","FAKEA_P","G1","A1","2024-04-03"):
            self.assertNotIn(hidden,val)


if __name__=="__main__":
    unittest.main()
