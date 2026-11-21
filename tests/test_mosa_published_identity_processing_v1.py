import unittest
from analysis.audit_mosa_published_identity_processing_v1 import inspect_lines

class MOSAIdScriptTests(unittest.TestCase):
    def test_rmd_identity_only_source_excerpt(self):
        doc="# Processing Data\nTOE = as.character(TOE)\na = group_by(TOE)\nwe call n_distinct(TOE)\nW_B_density_effect = 123\n"
        r=inspect_lines(doc)
        self.assertEqual(r["total_lines"],5)
        self.assertGreaterEqual(r["matching_lines"],3)
        self.assertTrue(any("TOE" in entry["snippet"] for entry in r["excerpts"]))

if __name__=="__main__":
    unittest.main()
