from pathlib import Path
import importlib.util
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"public_mammal_phase2_utils_v1.py"
spec=importlib.util.spec_from_file_location("phase2_utils",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Phase2UtilsTests(unittest.TestCase):
    def test_z_log_n_uses_population_sd(self):
        values=[5,10,20]
        out=m.z_log_n(values)
        logs=np.log(np.asarray(values,dtype=float))
        expected=(logs-logs.mean())/logs.std(ddof=0)
        np.testing.assert_allclose(out,expected,rtol=0,atol=1e-12)
        self.assertAlmostEqual(float(np.mean(out)),0.0,places=12)
        self.assertAlmostEqual(float(np.std(out,ddof=0)),1.0,places=12)

    def test_z_log_n_rejects_constant_or_nonpositive_values(self):
        with self.assertRaises(ValueError):
            m.z_log_n([5,5,5])
        with self.assertRaises(ValueError):
            m.z_log_n([5,0,6])

    def test_assert_full_rank_accepts_full_rank_and_rejects_aliasing(self):
        m.assert_full_rank(np.array([[1.,0.],[1.,1.],[1.,2.]]),["intercept","x"])
        with self.assertRaises(ValueError):
            m.assert_full_rank(
                np.array([[1.,1.,2.],[1.,2.,4.],[1.,3.,6.]]),
                ["intercept","x","twox"],
            )

    def test_bh_adjust_matches_known_values_and_preserves_order(self):
        p=[0.01,0.04,0.03,0.2]
        q=m.bh_adjust(p)
        np.testing.assert_allclose(q,[0.04,0.05333333333333334,0.05333333333333334,0.2])

    def test_bh_adjust_rejects_invalid_p_values(self):
        with self.assertRaises(ValueError):
            m.bh_adjust([0.1,-0.1])
        with self.assertRaises(ValueError):
            m.bh_adjust([0.1,1.1])

    def test_verify_phase2_artifact_metadata(self):
        lock={
            "artifact_id":12,
            "digest":"sha256:abc",
            "workflow_run_id":34,
            "workflow_head_sha":"deadbeef",
            "name":"frozen",
        }
        metadata={
            "id":12,
            "name":"frozen",
            "digest":"sha256:abc",
            "workflow_run":{"id":34,"head_sha":"deadbeef"},
        }
        m.verify_phase2_artifact_metadata(lock,"portal",metadata)
        bad=dict(metadata)
        bad["digest"]="sha256:changed"
        with self.assertRaises(ValueError):
            m.verify_phase2_artifact_metadata(lock,"portal",bad)


if __name__=="__main__":
    unittest.main()
