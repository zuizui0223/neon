from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class SubmissionHoldTests(unittest.TestCase):
    def test_root_readme_marks_v6_as_hold_not_submission_ready(self):
        text=(ROOT/'README.md').read_text(encoding='utf-8')
        self.assertIn('SUBMISSION HOLD',text)
        self.assertIn('MAMMAL_ECOLOGY_VALIDITY_AUDIT_V1.md',text)
        self.assertIn('MAMMAL_ECOLOGY_REDESIGN_V1.md',text)
        self.assertNotIn('The V6 scientific and anonymous-review package is CI-complete.',text)

    def test_active_lane_marks_v6_as_pre_audit_snapshot(self):
        text=(ROOT/'manuscript'/'neon_metacommunity_redundancy'/'README.md').read_text(encoding='utf-8')
        self.assertIn('pre-audit snapshot',text)
        self.assertIn('Do not submit V6',text)

    def test_hold_readiness_file_exists(self):
        text=(ROOT/'submission'/'OIKOS_READINESS_V4_HOLD.md').read_text(encoding='utf-8')
        self.assertIn('HOLD',text)
        self.assertIn('93/94',text)
        self.assertIn('p = 0.7568',text)

if __name__=='__main__':
    unittest.main()
