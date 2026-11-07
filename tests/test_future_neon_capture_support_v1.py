import unittest
from analysis.audit_future_neon_capture_support_v1 import (
  select_complete_events, summarize_effect_blind_support,
)


class FutureCaptureSupportTests(unittest.TestCase):
    def test_complete_only_and_srer_exclusion(self):
        rows=[]
        for site, event, nights, status in [
          ("ABBY","A",3,"setting complete, processing complete"),
          ("ABBY","B",2,"setting complete, processing complete"),
          ("SRER","C",3,"setting complete, processing complete"),
          ("HARV","D",3,"not complete"),
        ]:
            rows.extend({
                "siteID":site,"plotID":site+"_P1","eventID":event,
                "nightuid":site+event+str(i),"gridCompletion":status,
                "collectDate":"2026-07-"+str(i+1).zfill(2)
            } for i in range(nights))
        a=select_complete_events(rows)
        self.assertEqual(len(a["events"]),1)
        self.assertEqual(len(a["nights"]),3)

    def test_frozen_target_and_repeat_support_only(self):
        def session(taxon="PEMA",m=5,saturation=.2):
            return {"primary_complete_session":True,"taxon":taxon,
                "n_repeat_coordinate_supported_tagged_individuals":m,
                "all_capture_trap_night_fraction_of_observed":saturation,
                "site_ids":["HARV"],"genus_labels":["Peromyscus"],
                "plot_id":"HARV_P1","event_id":"2026_07"}
        rows=[session(),session(m=4),session(saturation=.31),session(taxon="GLVO")]
        a=summarize_effect_blind_support(rows,{"PEMA"})
        self.assertEqual(a["eligible_target_taxon_sessions_m5_saturation30"],1)
        self.assertEqual(a["frozen_taxon_support"]["PEMA"]["eligible_response_sessions"],1)
        self.assertFalse(a["future_W_B_response_opened"])
        self.assertFalse(a["mnka_variation_checked"])


if __name__=="__main__":
    unittest.main()
