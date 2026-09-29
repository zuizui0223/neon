from __future__ import annotations

import unittest

from analysis import heldout_heteromyid_crossscale_estimability_v1 as m


class HeldoutCrossscaleEstimabilityTests(unittest.TestCase):
    def test_inspected_species_are_excluded(self):
        for name in (
            "Chaetodipus baileyi",
            "Chaetodipus penicillatus",
            "Dipodomys merriami",
            "Dipodomys ordii",
        ):
            self.assertIn(name,m.EXCLUDED_INSPECTED_SPECIES)

    def test_support_duplicate_fails_primary(self):
        rows=[
            {"tagID":"M1","sex":"M","loc":"A1"},
            {"tagID":"M2","sex":"M","loc":"A2"},
            {"tagID":"M3","sex":"M","loc":"A3"},
            {"tagID":"M4","sex":"M","loc":"A4"},
            {"tagID":"M5","sex":"M","loc":"A5"},
            {"tagID":"F1","sex":"F","loc":"A1"},
            {"tagID":"F2","sex":"F","loc":"B2"},
            {"tagID":"F3","sex":"F","loc":"B3"},
            {"tagID":"F4","sex":"F","loc":"B4"},
            {"tagID":"F5","sex":"F","loc":"B5"},
        ]
        out=m.support_counts(
            rows,id_field="tagID",location_field="loc"
        )
        self.assertEqual(out["n_male"],5)
        self.assertEqual(out["n_female"],5)
        self.assertFalse(out["trap_support_valid"])
        self.assertFalse(out["paired_n5_eligible"])

    def test_crossscale_gate_requires_two_species_meeting_both(self):
        packing=[]
        movement=[]
        for species in ("Chaetodipus hispidus","Perognathus parvus"):
            for site in ("A","B"):
                for i in range(5):
                    packing.append({
                        "species":species,"site":site,
                        "paired_n3_eligible":True,
                        "paired_n5_eligible":True,
                    })
            for site in ("A","B"):
                for i in range(3):
                    movement.append({
                        "species":species,"site":site,
                        "paired_n3_eligible":True,
                        "paired_n5_eligible":True,
                    })
        out=m.summarize_crossscale(packing,movement)
        self.assertTrue(out["crossscale_gate"]["passed"])
        self.assertEqual(
            out["crossscale_gate"]["decision"],
            "authorize_heldout_crossscale_effect_lock",
        )
        self.assertEqual(out["crossscale_gate"]["qualifying_species_count"],2)

    def test_one_species_is_not_enough(self):
        packing=[
            {
                "species":"Chaetodipus hispidus",
                "site":"A" if i<5 else "B",
                "paired_n3_eligible":True,
                "paired_n5_eligible":True,
            }
            for i in range(10)
        ]
        movement=[
            {
                "species":"Chaetodipus hispidus",
                "site":"A" if i<3 else "B",
                "paired_n3_eligible":True,
                "paired_n5_eligible":True,
            }
            for i in range(6)
        ]
        out=m.summarize_crossscale(packing,movement)
        self.assertFalse(out["crossscale_gate"]["passed"])
        self.assertEqual(
            out["crossscale_gate"]["decision"],
            "stop_heldout_crossscale_not_estimable",
        )


if __name__=="__main__":
    unittest.main()
