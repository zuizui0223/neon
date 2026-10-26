"""No outcome leakage: source-only exact 3-night first-capture cohorts.

Synthetic tags and plot names are not persisted to source receipt.
"""
from datetime import date,timedelta
import json,unittest

from analysis.neon_macro_firstnight_reencounter_source_v1 import source_first_night_cohort


def fixture():
    plots=[];traps=[];units=[]
    for site in ("FAKEA","FAKEB"):
        plot=site+"_P"
        seasons=(date(2025,4,2),date(2025,7,2))
        for ss,start in enumerate(seasons):
            ev=site+str(ss)
            n=[ev+"_N0",ev+"_N1",ev+"_N2"]
            for d in range(3):
                plots.append({
                    "_site":site,"siteID":site,"plotID":plot,
                    "eventID":ev,"nightuid":n[d],
                    "collectDate":(start+timedelta(days=d)).isoformat(),
                    "gridCompletion":"setting complete, processing complete",
                })
            for genus,letter in (("G1","A"),("G2","B")):
                for ind in range(5):
                    traps.append({
                        "_site":site,"plotID":plot,"nightuid":n[0],
                        "trapCoordinate":letter+str(ind+1),
                        "trapStatus":"5 - capture",
                        "tagID":ev+"_"+genus+"_"+str(ind),"taxonID":genus,
                    })
                traps.append({
                    "_site":site,"plotID":plot,"nightuid":n[1],
                    "trapCoordinate":"A1",
                    "trapStatus":"6 - trap set and empty",
                    "tagID":"","taxonID":"",
                })
        units.append({
            "site":site,"site_plot":(site,plot),
            "capture_dates_A":tuple(seasons[0]+timedelta(days=i) for i in range(3)),
            "capture_dates_B":tuple(seasons[1]+timedelta(days=i) for i in range(3)),
            "A":{"G1":{"A1","A2"},"G2":{"B1","B2"}},
            "B":{"G1":{"A1","A2"},"G2":{"B1","B2"}},
        })
    return units,plots,traps,{"G1":"G1","G2":"G2"}


def run_source(data=None,**kw):
    a,b,c,d=data if data is not None else fixture()
    return source_first_night_cohort(
        a,b,c,d,expected_pairs=2,expected_sites=2,
        expected_unique_bouts=4,
        minimum_firstnight_animals=20,minimum_sites_with_animal=2,
        minimum_genus_animals=10,minimum_genus_sites=2,
        minimum_shared_sites=2,minimum_per_genus_per_site=5,**kw
    )


class GenusFirstNightSourceTests(unittest.TestCase):
    def test_exact_three_date_order_and_unique_event_firstnight_cohorts(self):
        doc,private=run_source()
        self.assertEqual(doc["status"],"SOURCE_MATCHED_GENUS_REENCOUNTER_COMPARISON_GO")
        self.assertEqual(doc["unique_source_three_night_bouts"],4)
        self.assertEqual(doc["source_firstnight_marked_animals"],40)
        self.assertEqual(doc["independent_sites_with_firstnight_tagged_captures"],2)
        self.assertEqual(doc["preselected_genus_pair_if_pass"]["genera"],["G1","G2"])
        self.assertEqual(doc["preselected_genus_pair_if_pass"]["shared_qualified_physical_sites"],2)
        self.assertTrue(doc["predeclared_source_gate"]["no_nextnight_matching_outcomes_opened"])
        self.assertEqual(len(private["original_firstnight_tagged_animal_genus_by_event"]),40)
        self.assertNotIn("FAKEA",json.dumps(doc))
        self.assertNotIn("FAKEB",json.dumps(doc))
        self.assertNotIn("_G1_",json.dumps(doc))

    def test_extra_later_reencounters_do_not_change_source_support(self):
        fixturedata=fixture()
        base,_=run_source(fixturedata)
        units,plots,traps,mapping=fixturedata
        traps.append({
            "_site":"FAKEA","plotID":"FAKEA_P","nightuid":"FAKEA0_N2",
            "trapCoordinate":"C2","trapStatus":"5 - capture",
            "tagID":"FAKEA0_G1_1","taxonID":"G1",
        })
        next_result,_=run_source((units,plots,traps,mapping))
        self.assertEqual(base,next_result)

    def test_original_global_genus_conflict_invalidates_firstnight(self):
        units,plots,traps,mapping=fixture()
        traps.append({
            "_site":"FAKEA","plotID":"FAKEA_P","nightuid":"FAKEA0_N2",
            "trapCoordinate":"C3","trapStatus":"5 - capture",
            "tagID":"FAKEA0_G1_0","taxonID":"G2",
        })
        doc,priv=run_source((units,plots,traps,mapping))
        self.assertEqual(doc["source_firstnight_marked_animals"],39)
        self.assertEqual(doc["original_firstnight_capture_source_rejections"]["ambiguous_original_source_tag_genus"],1)
        self.assertFalse(any(tag=="FAKEA0_G1_0" for ev,tag in priv["original_firstnight_tagged_animal_genus_by_event"]))

    def test_multiple_firstnight_stations_for_same_tag_excluded(self):
        units,plots,traps,mapping=fixture()
        traps.append({
            "_site":"FAKEA","plotID":"FAKEA_P","nightuid":"FAKEA0_N0",
            "trapCoordinate":"J10","trapStatus":"5 - capture",
            "tagID":"FAKEA0_G1_0","taxonID":"G1",
        })
        d,_=run_source((units,plots,traps,mapping))
        self.assertEqual(d["original_firstnight_capture_source_rejections"]["multi_location_same_tag_first_night"],1)
        self.assertEqual(d["source_firstnight_marked_animals"],39)

    def test_missing_one_source_site_stops_and_not_declared_detection(self):
        units,plots,traps,mapping=fixture()
        docs,_=run_source((units,plots,traps,mapping),minimum_shared_sites=3)
        self.assertEqual(docs["status"],"STOP_GENUS_REENCOUNTER_COMPARATOR_SOURCE_SUPPORT")
        self.assertFalse(docs["predeclared_source_gate"]["passed"])
        self.assertTrue(docs["limits"]["nextnight_recapture_not_equal_true_genus_detection_p"])

    def test_missing_capture_mark_cannot_enter_source_cohort(self):
        units,plots,traps,mapping=fixture()
        for row in traps:
            if row["tagID"]=="FAKEA0_G1_0":
                row["tagID"]=""
        doc,_=run_source((units,plots,traps,mapping))
        self.assertEqual(doc["source_firstnight_marked_animals"],39)

if __name__=="__main__":
    unittest.main()
