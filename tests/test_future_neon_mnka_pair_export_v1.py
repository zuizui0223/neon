import unittest
from datetime import date
from analysis.audit_future_neon_mnka_pair_export_v1 import future_mnka_predictor_pairs

class MNKAPairExportTests(unittest.TestCase):
    def example(self):
        rows=[];events={};mnka={}
        for i in range(287):
            site="HARV";plot="P1";event=f"E{i:03d}"
            rows.append({
                "primary_complete_session":True,"taxon":"PEMA",
                "site_ids":[site],"genus_labels":["Peromyscus"],
                "plot_id":plot,"event_id":event,
                "n_repeat_coordinate_supported_tagged_individuals":5,
                "all_capture_trap_night_fraction_of_observed":.10
            })
            events[(site,plot,event)]={"date":date(2026,1,1)}
            mnka[(site,plot,event,"Peromyscus")]=5+i
        return rows,events,mnka

    def test_exact_frozen_cohort_and_no_spatial_fields(self):
        a,b,c=self.example()
        out=future_mnka_predictor_pairs(a,b,c,{"PEMA"})
        self.assertEqual(len(out),287)
        self.assertEqual(out[0]["genus_mnka"],5)
        self.assertNotIn("W_m2",out[0])
        self.assertNotIn("B_debiased_m2",out[0])
        self.assertNotIn("tagID",out[0])

    def test_missing_mnka_fails(self):
        a,b,c=self.example()
        c.pop(("HARV","P1","E000","Peromyscus"))
        with self.assertRaisesRegex(RuntimeError,"lacks continuous"):
            future_mnka_predictor_pairs(a,b,c,{"PEMA"})

if __name__=="__main__":
    unittest.main()
