import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"audit_public_mammal_estimability_v1.py"
spec=importlib.util.spec_from_file_location("estimability",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PublicMammalEstimabilityTests(unittest.TestCase):
    def test_audit_counts_portal_treatment_replication_and_neon_habitat_replication(self):
        portal=[
            {"species":"Species A","treatment":"control","plot_id":"1","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False},
            {"species":"Species A","treatment":"control","plot_id":"2","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False},
            {"species":"Species A","treatment":"control","plot_id":"3","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False},
            {"species":"Species A","treatment":"control","plot_id":"4","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False},
            {"species":"Species A","treatment":"control","plot_id":"5","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False},
            {"species":"Species A","treatment":"exclosure","plot_id":"6","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":True},
            {"species":"Species A","treatment":"exclosure","plot_id":"7","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":True},
            {"species":"Species A","treatment":"exclosure","plot_id":"8","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":True},
            {"species":"Species A","treatment":"exclosure","plot_id":"9","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":True},
            {"species":"Species A","treatment":"exclosure","plot_id":"10","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":True},
            {"species":"Species B","treatment":"control","plot_id":"1","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False},
        ]
        neon=[]
        for i in range(5):
            neon.append({"species":"Species A","site":"S1","plot_id":"S1_1","event_id":f"A{i}","nlcd_class":"Deciduous Forest","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False})
            neon.append({"species":"Species A","site":"S2","plot_id":"S2_1","event_id":f"B{i}","nlcd_class":"Grassland/Herbaceous","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False})
        neon.append({"species":"Species B","site":"S1","plot_id":"S1_2","event_id":"X","nlcd_class":"Deciduous Forest","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":True})

        report=m.audit_estimability(
            portal,
            neon,
            neon_secondary={"pathogen_species_with_estimable_recapture":3},
        )
        self.assertEqual(report["portal"]["species_with_n5_ge5_sessions_both_contexts"],["Species A"])
        self.assertEqual(report["neon"]["species_with_n5_ge5_sessions_in_ge2_habitats"],["Species A"])
        self.assertEqual(report["neon"]["species_with_n5_sessions_in_ge2_sites"],["Species A"])
        self.assertEqual(report["shared_species_meeting_source_specific_estimability"],["Species A"])
        self.assertEqual(report["neon"]["pathogen_species_with_estimable_recapture"],3)

    def test_report_contains_threshold_counts_and_no_effect_inference_fields(self):
        portal=[
            {"species":"A","treatment":"control","plot_id":"1","primary_n5_eligible":False,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False},
        ]
        neon=[
            {"species":"A","site":"S","plot_id":"P","event_id":"E","nlcd_class":"Shrub/Scrub","primary_n5_eligible":False,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False},
        ]
        report=m.audit_estimability(portal,neon,neon_secondary={})
        self.assertEqual(report["portal"]["eligible_n3_sessions"],1)
        self.assertEqual(report["portal"]["eligible_n5_sessions"],0)
        self.assertEqual(report["neon"]["eligible_n3_sessions"],1)
        self.assertEqual(report["neon"]["eligible_n5_sessions"],0)
        forbidden=("coefficient","p_value","p-value","effect_size","effect_direction")
        serialized=repr(report).lower()
        for token in forbidden:
            self.assertNotIn(token,serialized)

    def test_non_estimable_reasons_are_explicit(self):
        portal=[]
        neon=[]
        report=m.audit_estimability(portal,neon,neon_secondary={})
        self.assertIn("no_portal_n5_sessions",report["non_estimable_reasons"])
        self.assertIn("no_neon_n5_sessions",report["non_estimable_reasons"])
        self.assertIn("no_shared_species_meeting_source_specific_estimability",report["non_estimable_reasons"])


if __name__=="__main__":
    unittest.main()
