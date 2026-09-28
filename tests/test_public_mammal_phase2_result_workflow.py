from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/".github"/"workflows"/"public-mammal-phase2-result-gate.yml"
SOURCES=ROOT/"validation"/"public_mammal_space_use_v1"/"phase2_result_artifacts_v1.json"


class PublicMammalPhase2ResultWorkflowTests(unittest.TestCase):
    def test_result_artifact_manifest_is_frozen(self):
        src=json.loads(SOURCES.read_text(encoding="utf-8"))
        self.assertEqual(src["portal"]["artifact_id"],10934836351)
        self.assertEqual(src["portal"]["workflow_run_id"],36328080321)
        self.assertEqual(
            src["portal"]["digest"],
            "sha256:5f0161ad71fdf3652e0f3d0f95b82253396195397945ea6b5c9d140a0dc92ba2",
        )
        self.assertEqual(src["neon"]["artifact_id"],10948585014)
        self.assertEqual(src["neon"]["workflow_run_id"],36367773226)
        self.assertEqual(
            src["neon"]["digest"],
            "sha256:12d77b65704dfc850c3057730e2d9753e86a6206c60e0442677acac007fcd555",
        )
        self.assertEqual(src["recapture"]["artifact_id"],10934987820)
        self.assertEqual(src["recapture"]["workflow_run_id"],36328869087)
        self.assertEqual(
            src["recapture"]["digest"],
            "sha256:ce8c421ec5a8d03d0513db87c42222f7929cfbd348df07b805f5d5af8dc5a947",
        )

    def test_workflow_runs_n_audit_and_result_gate(self):
        text=WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("analysis/audit_packing_n_independence_v1.py",text)
        self.assertIn("analysis/freeze_public_mammal_phase2_results_v1.py",text)
        self.assertIn("results/public_mammal_phase2_summary_v1.json",text)
        self.assertIn("validation/public_mammal_space_use_v1/phase2_result_gate_v1.json",text)
        self.assertIn("docs/PUBLIC_MAMMAL_PHASE2_RESULT_V1.md",text)

    def test_workflow_downloads_exact_frozen_result_runs(self):
        text=WORKFLOW.read_text(encoding="utf-8")
        for run_id in ("36328080321","36367773226","36328869087"):
            self.assertIn(run_id,text)
        self.assertIn("public-mammal-phase2-portal-v1",text)
        self.assertIn("public-mammal-phase2-neon-myodes-v1",text)
        self.assertIn("public-mammal-phase2-recapture-v1",text)


if __name__=="__main__":
    unittest.main()
