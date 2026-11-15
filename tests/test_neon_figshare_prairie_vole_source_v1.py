"""Synthetic candidate-file classification. Does not inspect animal data."""
import unittest
from analysis.neon_figshare_prairie_vole_source_v1 import classify,PROJECT_ID
class PrairieVoleFigshareSourceTests(unittest.TestCase):
    def test_public_figshare_project_pin(self):
        self.assertEqual(PROJECT_ID,228462)
    def test_both_modalities_need_separate_raw_file_candidates(self):
        x=classify(["raw_proximity_2022.csv","livetrapping_raw.csv","figure.png"])
        self.assertEqual(x["candidate_contact_filenames"],["raw_proximity_2022.csv"])
        self.assertEqual(x["candidate_trap_filenames"],["livetrapping_raw.csv"])
    def test_figure_only_is_not_an_empirical_source(self):
        x=classify(["Fig5.png","network_figure.pdf","README.docx"])
        self.assertFalse(x["any_tabular_source"])
        self.assertFalse(x["candidate_contact_filenames"])
        self.assertFalse(x["candidate_trap_filenames"])
    def test_an_aggregated_only_file_is_not_preverified_contact(self):
        x=classify(["capture_summary.csv"])
        self.assertEqual(x["candidate_contact_filenames"],[])
        self.assertEqual(x["candidate_trap_filenames"],["capture_summary.csv"])
        self.assertTrue(x["metadata_names_only_not_verified_schema"])
if __name__=="__main__":unittest.main()
