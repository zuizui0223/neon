from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
ROOT_README=ROOT/"README.md"
LANE_README=ROOT/"manuscript"/"neon_metacommunity_redundancy"/"README.md"


class ActiveSubmissionPointerTests(unittest.TestCase):
    def test_root_readme_points_to_hold_and_redesign(self):
        text=ROOT_README.read_text(encoding="utf-8")
        self.assertIn("SUBMISSION HOLD",text)
        self.assertIn("MAMMAL_ECOLOGY_VALIDITY_AUDIT_V1.md",text)
        self.assertIn("MAMMAL_ECOLOGY_REDESIGN_V1.md",text)
        self.assertIn("OIKOS_READINESS_V4_HOLD.md",text)
        self.assertIn("submission/oikos-v6-2026-09-27",text)
        self.assertNotIn("active submission mainline",text.lower())

    def test_manuscript_lane_archives_v6(self):
        text=LANE_README.read_text(encoding="utf-8")
        self.assertIn("SUBMISSION HOLD",text)
        self.assertIn("MANUSCRIPT_V6_MECHANISM_VALIDATED_DRAFT.md",text)
        self.assertIn("COVER_LETTER_OIKOS_V5.md",text)
        self.assertIn("pre-audit snapshot",text)
        self.assertIn("Do not submit V6",text)
        self.assertIn("OIKOS_READINESS_V4_HOLD.md",text)


if __name__=="__main__":
    unittest.main()
