import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"analysis"/"audit_heteromyid_sex_packing_estimability_v1.py"
spec=importlib.util.spec_from_file_location("gate",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class HeteromyidSexPackingGateTests(unittest.TestCase):
    def _portal(self):
        return {
            "species":{
                "Chaetodipus penicillatus":{"paired_n3_sessions":100,"independent_plots":10,"independent_sites":1},
                "Dipodomys merriami":{"paired_n3_sessions":40,"independent_plots":5,"independent_sites":1},
                "Dipodomys ordii":{"paired_n3_sessions":20,"independent_plots":3,"independent_sites":1},
                "Perognathus flavus":{"paired_n3_sessions":2,"independent_plots":1,"independent_sites":1},
            }
        }

    def _neon(self):
        return {
            "species":{
                "Chaetodipus penicillatus":{"paired_n3_sessions":12,"independent_plots":4,"independent_sites":2},
                "Dipodomys merriami":{"paired_n3_sessions":20,"independent_plots":5,"independent_sites":2},
                "Dipodomys ordii":{"paired_n3_sessions":15,"independent_plots":5,"independent_sites":3},
                "Perognathus flavus":{"paired_n3_sessions":3,"independent_plots":2,"independent_sites":1},
            }
        }

    def test_family_and_cross_source_gate_pass(self):
        out=m.evaluate_gate(self._portal(),self._neon())
        self.assertEqual(
            out["portal_family_qualifying_species"],
            ["Chaetodipus penicillatus","Dipodomys merriami","Dipodomys ordii"],
        )
        self.assertEqual(
            out["neon_family_qualifying_species"],
            ["Chaetodipus penicillatus","Dipodomys merriami","Dipodomys ordii"],
        )
        self.assertTrue(out["portal_family_gate_passed"])
        self.assertTrue(out["neon_family_gate_passed"])
        self.assertTrue(out["effect_modeling_authorized"])
        self.assertEqual(
            out["shared_species_with_ge10_paired_n3_sessions"],
            ["Chaetodipus penicillatus","Dipodomys merriami","Dipodomys ordii"],
        )
        self.assertTrue(out["cross_source_headline_authorized"])

    def test_neon_family_fails_with_fewer_than_three_species(self):
        neon=self._neon()
        neon["species"]["Dipodomys ordii"]["paired_n3_sessions"]=9
        out=m.evaluate_gate(self._portal(),neon)
        self.assertTrue(out["portal_family_gate_passed"])
        self.assertFalse(out["neon_family_gate_passed"])
        self.assertTrue(out["effect_modeling_authorized"])
        self.assertFalse(out["cross_source_headline_authorized"])

    def test_portal_requires_independent_plots(self):
        portal=self._portal()
        portal["species"]["Dipodomys ordii"]["independent_plots"]=1
        out=m.evaluate_gate(portal,self._neon())
        self.assertEqual(len(out["portal_family_qualifying_species"]),2)
        self.assertFalse(out["portal_family_gate_passed"])

    def test_gate_contains_no_effect_statistics(self):
        out=m.evaluate_gate(self._portal(),self._neon())
        forbidden={"packing_z","delta_sex_packing","estimate","p_value","ci95_low","ci95_high"}
        self.assertTrue(forbidden.isdisjoint(out.keys()))
        self.assertFalse(out["ecological_effects_inspected"])


if __name__=="__main__":
    unittest.main()
