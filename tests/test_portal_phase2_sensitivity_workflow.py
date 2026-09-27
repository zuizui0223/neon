from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/".github"/"workflows"/"public-mammal-phase2-portal.yml"


class PortalPhase2SensitivityWorkflowTests(unittest.TestCase):
    def test_workflow_pins_portal_source_and_runs_sensitivity(self):
        text=WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("repository: weecology/PortalData",text)
        self.assertIn("ref: 72d7ff8568052763bf6899dc462e285684cf20f6",text)
        self.assertIn("analysis/portal_cpen_phase2_sensitivity_v1.py",text)
        self.assertIn("portal_cpen_phase2_sensitivity_v1.json",text)
        self.assertIn("public-mammal-phase2-portal-v1",text)

    def test_workflow_uses_frozen_phase1_sessions_for_primary_and_robustness(self):
        text=WORKFLOW.read_text(encoding="utf-8")
        frozen="results/generated/phase2_inputs/portal/portal_space_use_sessions_v1.csv"
        self.assertGreaterEqual(text.count(frozen),2)


if __name__=="__main__":
    unittest.main()
