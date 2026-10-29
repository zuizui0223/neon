"""Synthetic later-night re-encounter indicator, preserving site denominator.

No source NEON privacy identifiers, biology claims or station detection p.
"""
import json,unittest
from analysis.neon_macro_genus_reencounter_effect_v1 import firstnight_reencounter


def fixture():
    original={}
    idx={}
    first={}
    traps=[]
    for site in ("FAKEA","FAKEB"):
        for group in ("G1","G2"):
            event=(site,site+"_P",site+"_E")
            first[event]=site+"_N0"
            for n in range(3):
                idx[site+"_N"+str(n)]=event
            for i in range(5):
                tag=site+group+str(i)
                original[(event,tag)]=group
                if (group=="G1" and i<4) or (group=="G2" and i<(1 if site=="FAKEA" else 2)):
                    traps.append({
                        "_site":site,"plotID":site+"_P","nightuid":site+"_N2",
                        "trapCoordinate":"A"+str(i+1),
                        "trapStatus":"5 - capture","tagID":tag,"taxonID":group,
                    })
    private={
        "original_firstnight_tagged_animal_genus_by_event":original,
        "event_source_night_index":idx,
        "event_source_dates":first,
    }
    return private,traps,{"G1":"G1","G2":"G2"}


def go(data=None):
    p,t,g=data if data else fixture()
    return firstnight_reencounter(
        p,t,g,selected_genera=("G1","G2"),
        selected_sites={"FAKEA","FAKEB"},
        minimum_marked_animals_per_genus_site=5,
        minimum_sites=2,
        bootstrap_seed=2026102601,
        bootstrap_draws=2000,
    )


class GenusReencounterEffectTests(unittest.TestCase):
    def test_site_equal_reencounter_difference_from_source_selected_firstnight(self):
        x=go()
        self.assertEqual(x["status"],"OBSERVED_SITE_PAIRED_GENUS_REENCOUNTER_FRACTION_DESCRIBED")
        self.assertEqual(x["source_matched_physical_sites_retained"],2)
        self.assertAlmostEqual(x["site_equal_observed_genus_reencounter_fraction_difference"],.5)
        self.assertEqual(x["unique_firstnight_tag_histories_in_fitted_site_genus_pairs"],20)
        self.assertEqual(x["original_recapture_record_summary_by_genus"]["G1"]["recorded_reencountered_day2_or3"],8)
        self.assertEqual(x["original_recapture_record_summary_by_genus"]["G2"]["recorded_reencountered_day2_or3"],3)
        self.assertTrue(x["claim_boundaries"]["not_capture_detection_p_of_animal_at_trap"])
        for forbidden in ("FAKEA","FAKEB","_N2"):
            self.assertNotIn(forbidden,json.dumps(x))

    def test_repeated_capture_same_tag_two_nights_still_one_event(self):
        p,t,g=fixture()
        t.append({
            "_site":"FAKEA","plotID":"FAKEA_P","nightuid":"FAKEA_N1",
            "trapCoordinate":"B1","trapStatus":"5 - capture",
            "tagID":"FAKEAG10","taxonID":"G1",
        })
        x=go((p,t,g))
        self.assertEqual(x["original_recapture_record_summary_by_genus"]["G1"]["recorded_reencountered_day2_or3"],8)

    def test_source_nonmatching_identity_does_not_become_reencounter(self):
        p,t,g=fixture()
        t.append({
            "_site":"FAKEA","plotID":"FAKEA_P","nightuid":"FAKEA_N2",
            "trapCoordinate":"J10","trapStatus":"5 - capture",
            "tagID":"SOMEONE_NOT_IN_DAY1","taxonID":"G1",
        })
        x=go((p,t,g))
        self.assertEqual(x["original_recapture_record_summary_by_genus"]["G1"]["recorded_reencountered_day2_or3"],8)

    def test_ambiguous_later_capture_protected_by_site_gate(self):
        p,t,g=fixture()
        t.append({
            "_site":"FAKEA","plotID":"FAKEA_P","nightuid":"FAKEA_N2",
            "trapCoordinate":"J10","trapStatus":"5 - capture",
            "tagID":"FAKEAG10","taxonID":"G1",
        })
        out=go((p,t,g))
        self.assertEqual(out["status"],"STOP_SOURCE_PAIRED_SITE_SUPPORT_AFTER_LATE_CAPTURE_CONFLICT_QC")
        self.assertTrue(out["subsequent_rediscovery_rates_NOT_computed"])
        self.assertTrue(out["no_alternate_genus_pair_selected"])

    def test_recapture_stays_unknown_under_non_capture_status(self):
        p,t,g=fixture()
        for row in t:
            row["trapStatus"]="6 - trap set and empty"
        x=go((p,t,g))
        self.assertEqual(x["original_recapture_record_summary_by_genus"]["G1"]["recorded_reencountered_day2_or3"],0)
        self.assertEqual(x["original_recapture_record_summary_by_genus"]["G2"]["recorded_reencountered_day2_or3"],0)
        self.assertEqual(x["direction"],"zero")
        self.assertFalse(x["whole_physical_site_bootstrap"]["interval_excludes_zero"])

if __name__=="__main__":
    unittest.main()
