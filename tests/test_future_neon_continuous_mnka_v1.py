"""Synthetic boundary-crossing known-alive histories; no spatial outcomes."""
import unittest
from datetime import date
from analysis.audit_future_neon_continuous_mnka_v1 import (
    continuous_known_alive_mnka, future_series_variation,
)


def state(events):
    return {
        "events":{key:{"date":date.fromisoformat(d),"nights":{night}}
                  for key,d,night in events},
        "nights":{night:key for key,_d,night in events}
    }


class CrossReleaseMNKATests(unittest.TestCase):
    def setUp(self):
        self.old=state([
            (("HARV","P1","OLD1"),"2024-01-01","A"),
            (("HARV","P1","OLD2"),"2024-02-01","B"),
        ])
        self.new=state([
            (("HARV","P1","NEW1"),"2026-02-01","C"),
            (("HARV","P1","NEW2"),"2026-03-01","D"),
            (("HARV","P1","NEW3"),"2026-04-01","E"),
        ])
        self.old_trap=[{"nightuid":"A","trapStatus":"capture",
            "taxonID":"PEMA","tagID":"a"}]
        self.new_trap=[
            {"nightuid":"E","trapStatus":"capture","taxonID":"PEMA","tagID":"a"},
            {"nightuid":"D","trapStatus":"capture","taxonID":"PEMA","tagID":"b"},
            {"nightuid":"E","trapStatus":"capture","taxonID":"PEMA","tagID":"b"},
        ]
        self.target={"PEMA","CHHI"}
        self.genera={"PEMA":"Peromyscus","CHHI":"Chaetodipus"}

    def test_cross_boundary_history_contributes_known_alive_to_new_events(self):
        result=continuous_known_alive_mnka(
            self.old_trap,self.new_trap,self.old,self.new,self.genera,self.target)
        n=result["new_event_genus_mnka"]
        self.assertEqual(n[("HARV","P1","NEW1","Peromyscus")],1)
        self.assertEqual(n[("HARV","P1","NEW2","Peromyscus")],2)
        self.assertEqual(n[("HARV","P1","NEW3","Peromyscus")],2)
        self.assertEqual(result["history_audit"]["tag_histories_crossing_source_boundary"],1)
        sessions=[
            {"taxon":"PEMA","site_ids":["HARV"],"plot_id":"P1",
             "event_id":e,"genus_labels":["Peromyscus"],"primary_complete_session":True,
             "n_repeat_coordinate_supported_tagged_individuals":5,
             "all_capture_trap_night_fraction_of_observed":.1}
            for e in ("NEW1","NEW2","NEW3")
        ]
        support=future_series_variation(sessions,{"PEMA"},n)
        self.assertEqual(support["mode_genera"]["Peromyscus"]["varying_series"],1)
        self.assertEqual(support["mode_genera"]["Peromyscus"]["sessions_in_varying_series"],3)
        self.assertFalse(support["W_B_opened"])

    def test_cross_genus_tag_excluded_from_both_histories(self):
        old=self.old_trap+[{"nightuid":"B","trapStatus":"capture",
                    "tagID":"b","taxonID":"CHHI"}]
        result=continuous_known_alive_mnka(
            old,self.new_trap,self.old,self.new,self.genera,self.target)
        self.assertEqual(result["history_audit"]["tag_histories_excluded_cross_genus"],1)
        self.assertEqual(result["new_event_genus_mnka"][("HARV","P1","NEW2","Peromyscus")],1)

    def test_duplicate_event_identity_stops(self):
        overlapping=state([(("HARV","P1","OLD1"),"2026-01-01","C")])
        with self.assertRaisesRegex(RuntimeError,"event identity overlap"):
            continuous_known_alive_mnka(self.old_trap,[],self.old,overlapping,
                                         self.genera,self.target)


if __name__=="__main__":
    unittest.main()
