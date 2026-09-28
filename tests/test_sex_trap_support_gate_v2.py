from __future__ import annotations

import unittest

from analysis import freeze_sex_trap_support_gate_v2 as m


def inventory(source,unit):
    species={}
    for name in ("A alpha","B beta","C gamma"):
        species[name]={
            "support_paired_n3_sessions":12,
            "count_only_paired_n3_sessions":13,
            unit:2,
            "trap_support_invalid_sessions":1,
        }
    return {
        "source":source,
        "species":species,
        "session_count":100,
        "count_only_paired_n3_sessions":40,
        "support_paired_n3_sessions":36,
        "support_paired_n5_sessions":10,
        "trap_support_invalid_sessions":4,
        "duplicate_location_sessions":4,
        "missing_or_invalid_location_sessions":0,
    }


class SupportGateTests(unittest.TestCase):
    def test_gate_passes_only_from_support_eligible_counts(self):
        portal=inventory("Portal","independent_plots")
        neon=inventory("NEON","independent_sites")
        out=m.freeze_gate(portal,neon)
        self.assertEqual(out["decision"],"authorize_effect_extraction")
        self.assertTrue(out["portal_family_gate"]["passed"])
        self.assertTrue(out["neon_family_gate"]["passed"])
        self.assertTrue(out["cross_source_gate"]["passed"])
        self.assertFalse(out["ecological_effects_inspected"])
        self.assertEqual(out["ecological_model_fits"],0)

    def test_gate_stops_if_support_removes_one_neon_species(self):
        portal=inventory("Portal","independent_plots")
        neon=inventory("NEON","independent_sites")
        neon["species"]["C gamma"]["support_paired_n3_sessions"]=9
        out=m.freeze_gate(portal,neon)
        self.assertEqual(
            out["decision"],
            "stop_trap_support_estimability_failed",
        )
        self.assertFalse(out["neon_family_gate"]["passed"])


if __name__=="__main__":
    unittest.main()
