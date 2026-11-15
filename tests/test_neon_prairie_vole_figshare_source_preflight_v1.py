"""Synthetic-only public metadata endpoints; no animal source values."""
import unittest
from unittest.mock import patch
from analysis.run_neon_prairie_vole_figshare_source_preflight_v1 import run, PROJECT, BASE
class FigsharePublicSourceTest(unittest.TestCase):
    def test_complete_manifest_never_implies_matched_dyad(self):
        def fake(url):
            if url==f"{BASE}/projects/{PROJECT}":return {"id":PROJECT}
            if url==f"{BASE}/projects/{PROJECT}/articles?page=1&page_size=100":
                return [{"id":123,"title":"public"}]
            if url==f"{BASE}/articles/123":
                return {"id":123,"files":[
                    {"id":1,"name":"capture.csv","size":100},
                    {"id":2,"name":"proxlogs.csv","size":100},
                    {"id":3,"name":"PIT_animal_deployments.csv","size":100}]}
            raise AssertionError(url)
        with patch("analysis.run_neon_prairie_vole_figshare_source_preflight_v1._get",side_effect=fake):
            x=run()
        self.assertEqual(x["source"]["number_files"],3)
        self.assertTrue(x["evidence_gate"]["filename_preflight_potential_both_observation_sources"])
        self.assertFalse(x["evidence_gate"]["true_dyad_match_confirmed"])
    def test_metadata_only_not_impute_no_animal_contacts(self):
        def fake(url):
            if url==f"{BASE}/projects/{PROJECT}":return {"id":PROJECT}
            if url==f"{BASE}/projects/{PROJECT}/articles?page=1&page_size=100":
                return [{"id":77}]
            if url==f"{BASE}/articles/77":
                return {"id":77,"files":[{"id":10,"name":"Data.RData","size":100}]}
            raise AssertionError(url)
        with patch("analysis.run_neon_prairie_vole_figshare_source_preflight_v1._get",side_effect=fake):
            x=run()
        self.assertFalse(x["evidence_gate"]["filename_preflight_potential_both_observation_sources"])
        self.assertFalse(x["evidence_gate"]["original_individual_animal_PIT_or_collared_IDs_exposed"])
    def test_missing_articles_fail_source_not_niche(self):
        def fake(url):
            return {"id":PROJECT} if url==f"{BASE}/projects/{PROJECT}" else []
        with patch("analysis.run_neon_prairie_vole_figshare_source_preflight_v1._get",side_effect=fake):
            with self.assertRaises(ValueError):run()
    def test_original_project(self):
        self.assertEqual(PROJECT,228462)
if __name__=="__main__":unittest.main()
