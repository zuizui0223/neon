"""Metric-only NEON future QC gate: original estimator, no abundance join."""
import unittest
from unittest.mock import patch
from analysis.audit_future_neon_metric_qc_v1 import compute_metric_only

COMPLETE="setting complete, processing complete"

def synthetic_inputs(with_capture=True):
    events={}
    nightmap={}
    sessions=[]
    captures=[]
    for i in range(505):
        event=f"E{i:03d}"
        nights={f"N{i:03d}{k}" for k in "ABC"}
        events[("HARV","P1",event)]={"nights":nights}
        for n in nights:nightmap[n]=("HARV","P1",event)
        if i>=287:continue
        sessions.append({
            "taxon":"PEMA","plot_id":"P1","event_id":event,
            "site_ids":["HARV"],"genus_labels":["Peromyscus"],
            "primary_complete_session":True,
            "n_repeat_coordinate_supported_tagged_individuals":5,
            "all_capture_trap_night_fraction_of_observed":.20,
        })
        if with_capture:
            for j in range(5):
                for k,row in (("A","A"),("B","B")):
                    captures.append({
                        "nightuid":f"N{i:03d}{k}",
                        "plotID":"P1",
                        "trapCoordinate":f"{row}{j+1}",
                        "trapStatus":"capture",
                        "tagID":f"tag{i}-{j}",
                        "taxonID":"PEMA",
                        "scientificName":"Peromyscus maniculatus",
                        "identificationQualifier":"","taxonRank":"species",
                    })
    return {"events":events,"nights":nightmap},sessions,captures


class MetricOnlyTests(unittest.TestCase):
    def test_scores_fixed_future_cohort_without_mnka(self):
        selected,sessions,capture=synthetic_inputs()
        with patch("analysis.audit_future_neon_metric_qc_v1.select_complete_events",
                   return_value=selected),patch(
             "analysis.audit_future_neon_metric_qc_v1.structural_audit",
             return_value={"support":{"sessions":sessions}}):
            out,rows=compute_metric_only([],capture,{"PEMA"})
        self.assertEqual(len(rows),287)
        self.assertEqual(out["status"],"FUTURE_METRIC_QC_PASS")
        self.assertTrue(all(r["B_debiased_m2"]>0 for r in rows))
        self.assertFalse(out["new_MNKA_joined"])
        self.assertFalse(out["new_density_slopes_opened"])
        self.assertFalse(out["future_ecological_confirmation_declared"])

    def test_missing_capture_rows_stops_metric(self):
        selected,sessions,_=synthetic_inputs(False)
        with patch("analysis.audit_future_neon_metric_qc_v1.select_complete_events",
                   return_value=selected),patch(
             "analysis.audit_future_neon_metric_qc_v1.structural_audit",
             return_value={"support":{"sessions":sessions}}):
            out,rows=compute_metric_only([],[],{"PEMA"})
        self.assertEqual(out["status"],"STOP_FUTURE_METRIC_QC")
        self.assertEqual(out["successfully_scored_sessions"],0)
        self.assertEqual(len(rows),0)


if __name__=="__main__":
    unittest.main()
