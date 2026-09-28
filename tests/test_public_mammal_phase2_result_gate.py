import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"freeze_public_mammal_phase2_results_v1.py"
spec=importlib.util.spec_from_file_location("phase2_gate",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def coef(est,lo,hi,p=0.5):
    return {
        "estimate":est,
        "ci95_low":lo,
        "ci95_high":hi,
        "p_value":p,
    }


class PublicMammalPhase2ResultGateTests(unittest.TestCase):
    def test_ci_excludes_zero(self):
        self.assertTrue(m.ci_excludes_zero(coef(0.5,0.1,0.9)))
        self.assertTrue(m.ci_excludes_zero(coef(-0.5,-0.9,-0.1)))
        self.assertFalse(m.ci_excludes_zero(coef(0.1,-0.2,0.4)))

    def test_weak_primary_family_stops_even_when_metric_audit_passes(self):
        portal={
            "coefficients":{
                "treatment":coef(0.03,-0.16,0.22),
                "interaction":coef(-0.10,-0.44,0.24),
            }
        }
        portal_sens={
            "direction_reversal_summary":{
                "treatment_reversal_labels":["n_min_8"],
                "interaction_reversal_labels":["n_min_8"],
            }
        }
        neon={
            "coefficients":{
                "habitat_shrub_scrub_vs_forest":coef(0.33,-0.42,1.08),
            }
        }
        secondary={
            "contrasts":[
                {"habitat_effect":{**coef(0.18,-1.00,1.36),"q_value_bh3":0.96}},
                {"habitat_effect":{**coef(-0.57,-1.26,0.11),"q_value_bh3":0.30}},
                {"habitat_effect":{**coef(-0.02,-0.99,0.95),"q_value_bh3":0.96}},
            ]
        }
        recapture={"coefficients":{"packing_z":coef(0.0007,-0.015,0.016)}}
        n_audit={"passes":True}
        gate=m.evaluate_result_gate(
            portal_primary=portal,
            portal_sensitivity=portal_sens,
            neon_primary=neon,
            neon_secondary=secondary,
            recapture_validation=recapture,
            packing_n_audit=n_audit,
        )
        self.assertEqual(gate["decision"],"stop_no_replicated_ecological_signal")
        self.assertTrue(gate["packing_metric_mechanical_audit_passed"])
        self.assertFalse(gate["portal_primary_supported"])
        self.assertFalse(gate["portal_robust"])
        self.assertFalse(gate["neon_myodes_primary_supported"])
        self.assertEqual(gate["secondary_neon_supported_count"],0)
        self.assertFalse(gate["movement_validation_supported"])

    def test_metric_failure_blocks_regardless_of_ecological_effects(self):
        strong=coef(0.8,0.4,1.2,0.001)
        gate=m.evaluate_result_gate(
            portal_primary={"coefficients":{"treatment":strong,"interaction":strong}},
            portal_sensitivity={"direction_reversal_summary":{"treatment_reversal_labels":[],"interaction_reversal_labels":[]}},
            neon_primary={"coefficients":{"habitat_shrub_scrub_vs_forest":strong}},
            neon_secondary={"contrasts":[]},
            recapture_validation={"coefficients":{"packing_z":strong}},
            packing_n_audit={"passes":False},
        )
        self.assertEqual(gate["decision"],"stop_metric_mechanical_dependence")
        self.assertFalse(gate["packing_metric_mechanical_audit_passed"])

    def test_replicated_primary_signal_can_authorize_manuscript_advance(self):
        strong=coef(0.5,0.2,0.8,0.002)
        gate=m.evaluate_result_gate(
            portal_primary={"coefficients":{"treatment":strong,"interaction":coef(0.1,-0.2,0.4)}},
            portal_sensitivity={"direction_reversal_summary":{"treatment_reversal_labels":[],"interaction_reversal_labels":[]}},
            neon_primary={"coefficients":{"habitat_shrub_scrub_vs_forest":strong}},
            neon_secondary={"contrasts":[]},
            recapture_validation={"coefficients":{"packing_z":coef(0.0,-0.1,0.1)}},
            packing_n_audit={"passes":True},
        )
        self.assertEqual(gate["decision"],"advance_to_manuscript")
        self.assertTrue(gate["portal_primary_supported"])
        self.assertTrue(gate["portal_robust"])
        self.assertTrue(gate["neon_myodes_primary_supported"])


if __name__=="__main__":
    unittest.main()
