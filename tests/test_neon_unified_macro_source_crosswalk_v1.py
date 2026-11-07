"""Synthetic source-only NEON macro crosswalk, including STOP and privacy.

Tests never open the historical R or W/B ecological outcomes. All source
names, dates and tag IDs below are invented.
"""
import json
import unittest
from datetime import date,timedelta

from analysis.audit_neon_unified_macro_source_crosswalk_v1 import source_crosswalk


def sample():
    units=[]
    selected={}
    trap_rows=[]
    taxonomy={"TAXONA":"GenA","TAXONB":"GenB","TAXONC":"GenC"}
    for site in ("FAKESITE_A","FAKESITE_B"):
        plot=site+"_1"
        dates_A=tuple(date(2025,3,1)+timedelta(days=i) for i in range(3))
        dates_B=tuple(date(2025,6,1)+timedelta(days=i) for i in range(3))
        units.append({
            "site":site,"site_plot":(site,plot),
            "capture_dates_A":dates_A,"capture_dates_B":dates_B,
            "A":{"GenA":{"A1","A2"},"GenB":{"B1","B2"},"GenC":{"C1","C2"}},
            "B":{"GenA":{"A1","A2"},"GenB":{"B1","B2"},"GenC":{"C1","C2"}},
        })
        for lab,days in (("A",dates_A),("B",dates_B)):
            event=site+"_"+lab
            key=(site,plot,event)
            nightids={site+"_"+lab+"_n"+str(i) for i in range(3)}
            selected[key]={"dates":days,"nights":nightids}
            for n in sorted(nightids):
                for row in "ABCDEFGHIJ":
                    for col in range(1,11):
                        trap_rows.append({
                            "_site":site,"plotID":plot,"nightuid":n,
                            "trapCoordinate":row+str(col),
                            "trapStatus":"6 - no capture",
                            "taxonID":"","tagID":"",
                        })
            for person in range(5):
                # Two different trap nights per marked individual.
                for ni in (0,1):
                    n=site+"_"+lab+"_n"+str(ni)
                    trap_rows.append({
                        "_site":site,"plotID":plot,"nightuid":n,
                        "trapCoordinate":"A"+str(person+1+ni),
                        "trapStatus":"5 - capture",
                        "tagID":event+"_tag"+str(person),
                        "taxonID":"TAXONA",
                    })
    return units,selected,trap_rows,taxonomy


class UnifiedMacroCrosswalkTests(unittest.TestCase):
    def run_audit(self, *, repeat_min_sites=2,repeat_min_pairs=2,
                  min_multi=1, data=None):
        units,selected,rows,tax=(data or sample())
        return source_crosswalk(
            units,selected,rows,{"TAXONA"},tax,
            expected_units=2,expected_sites=2,expected_plots=2,
            min_sites=repeat_min_sites,min_pairs=repeat_min_pairs,
            min_multi_site_genera=min_multi,
        )

    def test_two_source_matched_pairs_but_no_ecological_effect(self):
        report=self.run_audit()
        self.assertEqual(report["status"],"CANDIDATE_MATCHED_RESPONSES_SOURCE_GO")
        self.assertEqual(report["exact_pair_crosswalk"]["pairs_with_same_original_recurrence_genus_repeat_supported_in_both_events"],2)
        self.assertEqual(report["exact_pair_crosswalk"]["distinct_physical_sites_with_matched_pairs"],2)
        self.assertEqual(report["exact_pair_crosswalk"]["genera_with_matched_pairs_across_at_least_two_sites"],1)
        self.assertEqual(report["w_b_structural_opportunity"]["events_with_one_or_more_repeated_target_genera"],4)
        self.assertFalse(report["limitations"]["actual_W_B_m2_calculated"])
        self.assertFalse(report["limitations"]["recurrence_Z_recomputed"])
        self.assertFalse(report["limitations"]["joint_spatial_recurrence_density_effect_computed"])
        serialized=json.dumps(report)
        for secret in ("FAKESITE_A","FAKESITE_B","_tag0","TAXONA"):
            self.assertNotIn(secret,serialized)

    def test_threshold_failure_cannot_be_rescued_by_positive_effect(self):
        report=self.run_audit(repeat_min_sites=8,repeat_min_pairs=20,min_multi=3)
        self.assertEqual(report["status"],"STOP_MATCHED_RESPONSES_NOT_STRUCTURALLY_GENERAL")
        self.assertFalse(report["new_post_result_source_feasibility_gates"]["pass"])

    def test_unmatched_original_genus_cannot_be_counted(self):
        units,selected,rows,tax=sample()
        # All captures are of a taxon whose genus is not in the
        # original fixed genus×trap comparison.
        tax["TAXONA"]="UnrelatedGenus"
        report=self.run_audit(data=(units,selected,rows,tax))
        self.assertEqual(report["exact_pair_crosswalk"]["pairs_with_same_original_recurrence_genus_repeat_supported_in_both_events"],0)
        self.assertFalse(report["new_post_result_source_feasibility_gates"]["pass"])

    def test_same_night_double_trap_disqualifies_one_individual(self):
        units,selected,rows,tax=sample()
        for site in ("FAKESITE_A","FAKESITE_B"):
            for lab in ("A","B"):
                event=site+"_"+lab
                rows.append({
                    "_site":site,"plotID":site+"_1",
                    "nightuid":site+"_"+lab+"_n0",
                    "trapCoordinate":"J10","trapStatus":"5 - capture",
                    "tagID":event+"_tag0","taxonID":"TAXONA",
                })
        out=self.run_audit(data=(units,selected,rows,tax))
        self.assertEqual(out["exact_pair_crosswalk"]["pairs_with_same_original_recurrence_genus_repeat_supported_in_both_events"],0)
        self.assertFalse(out["new_post_result_source_feasibility_gates"]["pass"])

    def test_source_event_dating_is_exact(self):
        units,selected,rows,tax=sample()
        units[0]["capture_dates_B"]=tuple(date(2024,6,1)+timedelta(days=i) for i in range(3))
        with self.assertRaisesRegex(ValueError,"map to exact events"):
            self.run_audit(data=(units,selected,rows,tax))

    def test_source_saturation_is_an_independent_structural_stop(self):
        units,selected,rows,tax=sample()
        # Remove all noncapture effort rows: nearly all observed trap-nights
        # are capture-marked, so neither season qualifies.
        rows=[r for r in rows if r["trapStatus"]=="5 - capture"]
        out=self.run_audit(data=(units,selected,rows,tax))
        self.assertEqual(out["status"],"STOP_MATCHED_RESPONSES_NOT_STRUCTURALLY_GENERAL")
        self.assertEqual(out["w_b_structural_opportunity"]["qualifying_target_taxon_event_units"],0)


if __name__=="__main__":
    unittest.main()
