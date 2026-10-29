import unittest
from datetime import date
from analysis.audit_future_neon_mnka_support_v1 import future_only_mnka_support


class FutureOnlyMNKASupportTests(unittest.TestCase):
    def test_increasing_and_stable_future_only_index_is_effect_blind(self):
        events={}
        nights={}
        trap=[]
        for i in range(4):
            key=("HARV","HARV_P1",f"E{i}")
            events[key]={"date":date(2026,4,1+i),"nights":{f"N{i}"}}
            nights[f"N{i}"]=key
        captures={"a":[0,1,2,3],"b":[1,2],"c":[2,3],"d":[3]}
        for tag,idxs in captures.items():
            for i in idxs:
                trap.append({"nightuid":f"N{i}","trapStatus":"capture",
                             "taxonID":"PEMA","scientificName":"Peromyscus maniculatus",
                             "tagID":tag})
        sessions=[{"primary_complete_session":True,"taxon":"PEMA",
                   "n_repeat_coordinate_supported_tagged_individuals":5,
                   "all_capture_trap_night_fraction_of_observed":0.2,
                   "site_ids":["HARV"],"genus_labels":["Peromyscus"],
                   "plot_id":"HARV_P1","event_id":f"E{i}"} for i in range(4)]
        result=future_only_mnka_support(trap,{"events":events,"nights":nights},
                                        sessions,{"PEMA"})
        self.assertEqual(result["candidate_sessions"],4)
        self.assertEqual(result["unpaired_sessions"],0)
        self.assertEqual(result["mode_genera"]["Peromyscus"]["series_with_ge3_events_ge2_distinct_future_only_MNKA"],1)
        self.assertFalse(result["final_MNKA_support_authorized"])
        self.assertFalse(result["future_W_B_response_opened"])


if __name__=="__main__":
    unittest.main()
