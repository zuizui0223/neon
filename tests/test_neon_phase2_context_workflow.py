from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/".github"/"workflows"/"public-mammal-phase2-neon.yml"


class NeonPhase2ContextWorkflowTests(unittest.TestCase):
    def test_workflow_runs_session_context_sensitivity(self):
        text=WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("analysis/neon_phase2_context_sensitivity_v1.py",text)
        self.assertIn("neon_phase2_context_sensitivity_v1.json",text)
        frozen="results/generated/phase2_inputs/neon/neon_diversity_space_use_sessions_v1.csv"
        self.assertGreaterEqual(text.count(frozen),3)

    def test_context_sensitivity_changes_retrigger_workflow(self):
        text=WORKFLOW.read_text(encoding="utf-8")
        paths_block=text.split("paths:",1)[1].split("workflow_dispatch:",1)[0]
        self.assertIn("analysis/neon_phase2_context_sensitivity_v1.py",paths_block)
        self.assertIn("tests/test_neon_phase2_context_sensitivity.py",paths_block)
        self.assertIn("tests/test_neon_phase2_context_workflow.py",paths_block)

    def test_context_sensitivity_is_uploaded_with_primary_artifact(self):
        text=WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("public-mammal-phase2-neon-myodes-v1",text)
        self.assertIn(
            "results/generated/neon_phase2_context_sensitivity_v1.json",
            text,
        )


if __name__=="__main__":
    unittest.main()
