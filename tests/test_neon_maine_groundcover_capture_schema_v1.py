import unittest
from analysis.audit_neon_maine_groundcover_capture_schema_v1 import profile_table,source_notes,code_notes
class MaineSourceTests(unittest.TestCase):
    def test_context_counts_no_raw_values(self):
        q=profile_table(b"Grid,Year,Session,TrapID,Tag,Species\nPRIVATE,2018,2,A1,SECRET,Mg\nPRIVATE,2018,2,A2,SECRET,Mg\n")
        self.assertEqual(q["data_rows"],2)
        self.assertEqual(q["candidate_key_counts"]["grid+individual"]["distinct_complete_keys"],1)
        self.assertNotIn("SECRET",str(q))
        self.assertNotIn("PRIVATE",str(q))
    def test_ragged_rejected(self):
        with self.assertRaises(ValueError):profile_table(b"grid,tag,station\ns,1,A1\ns,2\n")
    def test_contact_omitted(self):
        q=source_notes(b"Grid: sampling grid\nemail: example@example.org\nYear: capture year\n")
        self.assertEqual(len(q),2)
    def test_R_codebook_patterns_compile_and_filter(self):
        x=code_notes(b"not relevant\nx <- merge(a,b)\ny <- read.table('file')\n# trap coordinate\n")
        self.assertEqual([v["line"] for v in x],[2,3,4])
if __name__=="__main__":unittest.main()
