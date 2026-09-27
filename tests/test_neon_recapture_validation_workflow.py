from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/".github"/"workflows"/"public-mammal-phase2-recapture.yml"


class NeonRecaptureValidationWorkflowTests(unittest.TestCase):
    def test_workflow_requires_token_and_runs_frozen_validation(self):
        text=WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("NEON_API_TOKEN",text)
        self.assertIn("analysis/run_neon_recapture_validation_phase2_v1.py",text)
        self.assertIn("analysis/neon_recapture_validation_phase2_v1.py",text)
        self.assertIn("public-mammal-phase2-recapture-v1",text)

    def test_workflow_outputs_event_table_and_model_result(self):
        text=WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("neon_recapture_validation_events_v1.csv",text)
        self.assertIn("neon_recapture_validation_phase2_v1.json",text)


if __name__=="__main__":
    unittest.main()
