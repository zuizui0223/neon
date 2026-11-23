from __future__ import annotations

# AI assistance disclosure: This test file was drafted or refactored with OpenAI ChatGPT (GPT-5.6 Sol, September 2026); it remains under author responsibility and is verified in repository workflows.

import unittest

from analysis import live_trap_aliasing_denominator_audit_v1 as m


class AliasingDenominatorAuditTests(unittest.TestCase):
    def test_distance_one_spacing(self):
        self.assertAlmostEqual(m.distance("A1","A2"),6.25)

    def test_single_capture_night_cannot_create_shift(self):
        rows=[
            {"species":"PEMA","unique_ID":"x","grid":"1","date":"1/1/16","flag":"A1","time":"10:00"},
            {"species":"PEER","unique_ID":"y","grid":"2","date":"1/1/16","flag":"A1","time":"10:00"},
        ]
        frozen={
            "species":{
                "PEMA":{"repeat_capture_nights":0,"one_spacing_shift_count":0},
                "PEER":{"repeat_capture_nights":0,"one_spacing_shift_count":0},
            }
        }
        out=m.audit(rows,frozen)
        self.assertEqual(out["species"]["PEMA"]["repeat_capture_fraction"],0.0)
        self.assertEqual(
            out["species"]["PEMA"]["observed_one_spacing_aliasing_lower_bound_fraction_all_nights"],
            0.0,
        )


if __name__=="__main__":
    unittest.main()
