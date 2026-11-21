"""Synthetic source trap-opportunity alignment tests; no original animal effects."""
from datetime import date,timedelta
import json
import unittest

from analysis.neon_macro_six_night_effort_v1 import recorded_station_opportunity


def fixture():
    plots=[];traps=[];units=[]
    for site in ("FAKEA","FAKEB"):
        plot=site+"_P"
        starts=(date(2025,4,2),date(2025,7,2))
        for season,first in enumerate(starts):
            ev=site+("_SPR" if season==0 else "_SUM")
            for night in range(3):
                uid=ev+"_"+str(night)
                plots.append({
                    "_site":site,"siteID":site,"plotID":plot,"eventID":ev,
                    "nightuid":uid,"gridCompletion":"setting complete, processing complete",
                    "collectDate":(first+timedelta(days=night)).isoformat(),
                })
                for r in "ABCDEFGHIJ":
                    for k in range(1,11):
                        station=r+str(k)
                        # Eleven absent coordinates on exactly one of
                        # the six nights: common(all six) decreases to 89.
                        if site=="FAKEB" and season==1 and night==2 and station in {
                            "J1","J2","J3","J4","J5","J6","J7","J8","J9","J10","I10"
                        }:
                            continue
                        traps.append({
                            "_site":site,"plotID":plot,"nightuid":uid,
                            "trapCoordinate":station,
                            "trapStatus":"No capture",
                        })
        units.append({
            "site":site,"site_plot":(site,plot),
            "season_ordinal":4*2025+1,
            "capture_dates_A":tuple(starts[0]+timedelta(days=i) for i in range(3)),
            "capture_dates_B":tuple(starts[1]+timedelta(days=i) for i in range(3)),
            "A":{"GENA":{"A1","A2"},"GENB":{"B1","B2"}},
            "B":{"GENA":{"A1","A2"},"GENB":{"B1","B2"}},
        })
    return units,plots,traps,{"FAKEA":"D01","FAKEB":"D02"}


def source_audit(data=None,**kwargs):
    units,plots,traps,metadata=(data if data is not None else fixture())
    return recorded_station_opportunity(
        units,plots,traps,metadata,
        expected_pairs=2,expected_sites=2,
        min_selected_pairs=1,min_selected_sites=1,min_selected_domains=1,**kwargs
    )


class CommonTrapOpportunityTests(unittest.TestCase):
    def test_original_six_source_nights_intersect_not_union(self):
        summary,private=source_audit()
        self.assertEqual(summary["original_exact_two_genus_pairs"],2)
        self.assertEqual(summary["all_six_recorded_station_count_distribution"]["min"],89)
        self.assertEqual(summary["all_six_recorded_station_count_distribution"]["max"],100)
        self.assertEqual(summary["source_six_night_station_retention_categories"]["both_common90_and_two_genus_support"],1)
        self.assertEqual(summary["source_six_night_station_retention_categories"]["common_lt_90"],1)
        self.assertEqual(summary["retained_pairs"],1)
        self.assertEqual(len(private),1)
        self.assertTrue(summary["predeclared_effect_blind_gate"]["passed"])
        self.assertTrue(summary["scientific_scope"]["no_genus_x_trap_temporal_overlap_computed"])

    def test_common_positions_are_recorded_opportunity_not_trap_operability(self):
        source=fixture()
        units,plots,traps,metadata=source
        # The station is still present in the source file but status is
        # unspecified; it counts as recorded opportunity, not checked.
        for row in traps:
            if row["nightuid"]=="FAKEA_SUM_2" and row["trapCoordinate"]=="A1":
                row["trapStatus"]="TRAP_UNKNOWN"
        summary,private=source_audit(source)
        self.assertEqual(summary["all_six_recorded_station_count_distribution"]["max"],100)
        self.assertEqual(summary["all_six_explicit_capture_or_no_capture_station_count_distribution"]["max"],99)
        self.assertTrue(summary["scientific_scope"]["recorded_trap_not_proven_operable"])

    def test_original_genus_two_station_support_must_survive_common_filter(self):
        units,plots,traps,meta=fixture()
        traps=[row for row in traps if not(row["nightuid"]=="FAKEA_SPR_0"
                     and row["trapCoordinate"]=="A1")]
        summary,private=source_audit((units,plots,traps,meta))
        self.assertEqual(summary["source_six_night_station_retention_categories"]["original_genus_station_support_lost_after_common"],1)
        self.assertEqual(summary["retained_pairs"],0)
        self.assertEqual(summary["status"],"STOP_COMMON_SIX_NIGHT_STATION_COVERAGE")
        self.assertEqual(private,[])

    def test_source_missing_original_capture_event_date_is_error(self):
        units,plots,traps,meta=fixture()
        units[0]["capture_dates_B"]=tuple(date(2024,7,2)+timedelta(days=i) for i in range(3))
        with self.assertRaisesRegex(ValueError,"event dates"):
            source_audit((units,plots,traps,meta))

    def test_no_source_identifiers_or_animal_z_results_are_serialized(self):
        receipt,_=source_audit()
        raw=json.dumps(receipt)
        for secret in ("FAKEA","FAKEB","GENA","GENB","2025-04-02","A1"):
            self.assertNotIn(secret,raw)
        self.assertNotIn("site_mean_Z",raw)
        self.assertTrue(receipt["scientific_scope"]["cannot_exclude_genus_specific_catchability"])


if __name__=="__main__":
    unittest.main()
