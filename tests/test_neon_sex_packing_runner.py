import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"run_neon_sex_packing_estimability_v1.py"
spec=importlib.util.spec_from_file_location("runner",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class NeonSexPackingRunnerTests(unittest.TestCase):
    def test_inventory_is_effect_blind_and_tracks_download_provenance(self):
        sessions=[
            {"species":"Dipodomys ordii","site":"JORN","plot_id":"p1","year":2020,"paired_n2_eligible":True,"paired_n3_eligible":True,"paired_n5_eligible":False,"known_sex_fraction":1.0},
            {"species":"Dipodomys ordii","site":"MOAB","plot_id":"p2","year":2021,"paired_n2_eligible":True,"paired_n3_eligible":True,"paired_n5_eligible":True,"known_sex_fraction":0.9},
        ]
        out=m.build_inventory(
            sessions,
            available_site_count=45,
            processed_site_count=2,
            target_taxon_count=100,
            data_query_requests=2,
            downloaded_required_file_count=6,
            downloaded_required_bytes=12345,
            site_stops=[],
        )
        self.assertEqual(out["product_code"],"DP1.10072.001")
        self.assertEqual(out["release"],"RELEASE-2026")
        self.assertEqual(out["paired_n3_sessions"],2)
        self.assertEqual(out["available_site_count"],45)
        self.assertEqual(out["processed_site_count"],2)
        self.assertEqual(out["data_query_requests"],2)
        self.assertEqual(out["downloaded_required_file_count"],6)
        self.assertEqual(out["downloaded_required_bytes"],12345)
        self.assertFalse(out["ecological_effects_inspected"])
        self.assertEqual(out["ecological_model_fits"],0)

    def test_primary_gate_sites_are_complete_from_phase1_n5_heteromyid_counts(self):
        phase1={
            "neon":{
                "n5_species_site_session_counts":{
                    "Dipodomys ordii":{"JORN":22,"MOAB":37},
                    "Perognathus parvus":{"ONAQ":38},
                    "Peromyscus maniculatus":{"WOOD":42},
                    "Chaetodipus hispidus":{"OAES":15,"STER":5},
                }
            }
        }
        self.assertEqual(
            m.primary_gate_sites_from_phase1(phase1),
            ["JORN","MOAB","OAES","ONAQ","STER"],
        )

    def test_primary_gate_site_rule_documents_completeness_logic(self):
        self.assertEqual(m.PRIMARY_SEX_COUNT_MIN,3)
        self.assertEqual(m.PHASE1_TOTAL_N_SCREEN,5)
        self.assertGreaterEqual(2*m.PRIMARY_SEX_COUNT_MIN,m.PHASE1_TOTAL_N_SCREEN)

    def test_primary_gate_query_can_use_basic_package(self):
        q=m.build_query_for_site("JORN",package="basic")
        self.assertEqual(q["productCode"],"DP1.10072.001")
        self.assertEqual(q["siteCodes"],["JORN"])
        self.assertEqual(q["release"],"RELEASE-2026")
        self.assertEqual(q["package"],"basic")
        self.assertFalse(q["includeProvisional"])


if __name__=="__main__":
    unittest.main()
