from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
ROOT_README=ROOT/"README.md"
LANE_README=ROOT/"manuscript"/"neon_metacommunity_redundancy"/"README.md"


class ActiveSubmissionPointerTests(unittest.TestCase):
    def test_root_readme_points_only_to_v6_active_submission(self):
        text=ROOT_README.read_text(encoding="utf-8")
        self.assertIn("MANUSCRIPT_V6_MECHANISM_VALIDATED_DRAFT.md",text)
        self.assertIn("Figure_5.png",text)
        self.assertIn("submission/OIKOS_READINESS_V3.md",text)
        self.assertIn("submission/SUBMISSION_FORM_FIELDS_V2.md",text)
        self.assertNotIn("Active main text:\n- `manuscript/neon_metacommunity_redundancy/MANUSCRIPT_V5",text)

    def test_manuscript_lane_promotes_v6_and_v5_cover(self):
        text=LANE_README.read_text(encoding="utf-8")
        self.assertIn("MANUSCRIPT_V6_MECHANISM_VALIDATED_DRAFT.md",text)
        self.assertIn("COVER_LETTER_OIKOS_V5.md",text)
        self.assertIn("OIKOS_READINESS_V3.md",text)
        self.assertIn("SIGNIFICANCE_STATEMENT_V3.md",text)
        self.assertIn("DATA_AVAILABILITY_STATEMENT_V3.md",text)
        self.assertIn("SUBMISSION_FORM_FIELDS_V2.md",text)
        self.assertIn("TITLE_PAGE_TEMPLATE_V2.md",text)


if __name__=="__main__":
    unittest.main()
