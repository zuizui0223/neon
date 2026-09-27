from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/".github"/"workflows"/"public-mammal-phase1-estimability.yml"


class Phase1EstimabilityWorkflowTests(unittest.TestCase):
    def test_cross_run_artifacts_use_official_download_action(self):
        text=WORKFLOW.read_text(encoding="utf-8")
        self.assertGreaterEqual(text.count("uses: actions/download-artifact@v4"),2)
        self.assertIn("github-token: ${{ secrets.GITHUB_TOKEN }}",text)
        self.assertIn("run-id: ${{ steps.discover.outputs.portal_run_id }}",text)
        self.assertIn("run-id: ${{ steps.discover.outputs.neon_run_id }}",text)
        self.assertNotIn('artifact["archive_download_url"]',text)


if __name__=="__main__":
    unittest.main()
