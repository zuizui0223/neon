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


    def test_neon_strict_site_replication_requires_five_n5_sessions_per_site(self):
        portal=[]
        neon=[]
        for i in range(5):
            neon.append({"species":"Strong","site":"S1","nlcd_class":"deciduousForest","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False})
            neon.append({"species":"Strong","site":"S2","nlcd_class":"evergreenForest","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False})
        for i in range(9):
            neon.append({"species":"Weak","site":"S1","nlcd_class":"deciduousForest","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False})
        neon.append({"species":"Weak","site":"S2","nlcd_class":"deciduousForest","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False})
        report=m.audit_estimability(portal,neon,neon_secondary={})
        self.assertEqual(report["neon"]["species_with_n5_ge5_sessions_in_ge2_sites"],["Strong"])
        self.assertNotIn("Weak",report["neon"]["species_with_n5_ge5_sessions_in_ge2_sites"])
        self.assertEqual(
            report["neon"]["n5_species_site_session_counts"]["Strong"],
            {"S1":5,"S2":5},
        )

    def test_neon_habitat_identifiability_requires_within_site_or_cross_site_replication(self):
        portal=[]
        neon=[]
        # Within-site contrast: two habitats with >=5 sessions each at one site.
        for i in range(5):
            neon.append({"species":"Within","site":"S1","nlcd_class":"deciduousForest","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False})
            neon.append({"species":"Within","site":"S1","nlcd_class":"grasslandHerbaceous","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False})
        # Cross-site replicated contrast: two habitats, each represented by >=2 sites with >=3 sessions/site.
        for site,hab in (("F1","deciduousForest"),("F2","evergreenForest"),("G1","grasslandHerbaceous"),("G2","grasslandHerbaceous")):
            for i in range(3):
                neon.append({"species":"Cross","site":site,"nlcd_class":hab,"primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False})
        # Confounded: two habitats but each only one site, no within-site contrast.
        for i in range(5):
            neon.append({"species":"Confounded","site":"A","nlcd_class":"deciduousForest","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False})
            neon.append({"species":"Confounded","site":"B","nlcd_class":"grasslandHerbaceous","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False})
        report=m.audit_estimability(portal,neon,neon_secondary={})
        self.assertEqual(
            report["neon"]["species_with_primary_habitat_identifiability"],
            ["Cross","Within"],
        )
        self.assertNotIn(
            "Confounded",
            report["neon"]["species_with_primary_habitat_identifiability"],
        )
        self.assertEqual(
            report["neon"]["n5_species_site_habitat_session_counts"]["Within"]["S1"],
            {"forest":5,"grassland_herbaceous":5},
        )


    def test_session_inventory_rows_are_source_and_context_specific(self):
        portal=[
            {"species":"A","treatment":"control","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False},
            {"species":"A","treatment":"exclosure","primary_n5_eligible":False,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False},
        ]
        neon=[
            {"species":"A","nlcd_class":"Deciduous Forest","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":False},
            {"species":"A","nlcd_class":"Grassland/Herbaceous","primary_n5_eligible":True,"sensitivity_n3_eligible":True,"sensitivity_n8_eligible":True},
        ]
        rows=m.session_inventory_rows(portal,neon)
        self.assertIn({
            "source":"Portal","species":"A","context":"control",
            "session_count":1,"eligible_n3":1,"eligible_n5":1,"eligible_n8":0,
        },rows)
        self.assertIn({
            "source":"NEON","species":"A","context":"forest",
            "session_count":1,"eligible_n3":1,"eligible_n5":1,"eligible_n8":0,
        },rows)

    def test_estimability_memo_states_no_ecological_models_were_fit(self):
        report=m.audit_estimability([],[],neon_secondary={})
        memo=m.render_estimability_memo(report)
        self.assertIn("No ecological models were fit",memo)
        self.assertIn("Phase-1 estimability",memo)
        self.assertIn("Strict Phase-2 structure",memo)
        self.assertIn("primary habitat-identifiable species",memo)
        self.assertIn(">=5 N>=5 sessions at >=2 sites",memo)
        self.assertNotIn("p =",memo)


if __name__=="__main__":
    unittest.main()
