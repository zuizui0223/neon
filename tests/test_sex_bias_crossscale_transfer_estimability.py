from __future__ import annotations

import unittest

from analysis import sex_bias_crossscale_transfer_estimability_v1 as m


class CrossscaleTransferEstimabilityTests(unittest.TestCase):
    def test_previously_inspected_species_are_excluded(self):
        for name in (
            "Chaetodipus baileyi",
            "Chaetodipus penicillatus",
            "Dipodomys merriami",
            "Dipodomys ordii",
            "Peromyscus maniculatus",
            "Peromyscus leucopus",
        ):
            self.assertIn(name,m.EXCLUDED_SPECIES)

    def test_programme_gate_passes_with_crossed_replication(self):
        packing=[]
        movement=[]
        species_sites={
            "Species 0":("A","B"),
            "Species 1":("A","C"),
            "Species 2":("B","D"),
            "Species 3":("C","D"),
            "Species 4":("A","D"),
        }
        # 10 strata across 5 species and 4 sites; every species has two sites.
        for name,sites in species_sites.items():
            for site in sites:
                for _ in range(5):
                    packing.append({"species":name,"site":site})
                    movement.append({"species":name,"site":site})
        out=m.summarize(packing,movement)
        self.assertTrue(out["programme_gate"]["passed"])
        self.assertEqual(
            out["programme_gate"]["decision"],
            "authorize_crossscale_transfer_effect_lock",
        )
        self.assertEqual(
            out["programme_gate"]["qualifying_species_site_strata"],10
        )
        self.assertEqual(out["programme_gate"]["qualifying_site_count"],4)
        self.assertEqual(
            out["programme_gate"]["species_with_two_or_more_sites_count"],5
        )

    def test_many_rows_in_one_species_do_not_pass(self):
        packing=[]
        movement=[]
        for site in ("A","B","C","D"):
            for j in range(10):
                packing.append({"species":"Only species","site":site})
                movement.append({"species":"Only species","site":site})
        out=m.summarize(packing,movement)
        self.assertFalse(out["programme_gate"]["passed"])
        self.assertEqual(out["programme_gate"]["qualifying_species_count"],1)

    def test_support_duplicate_fails(self):
        rows=[
            {"id":"M1","sex":"M","loc":"A"},
            {"id":"M2","sex":"M","loc":"B"},
            {"id":"M3","sex":"M","loc":"C"},
            {"id":"F1","sex":"F","loc":"A"},
            {"id":"F2","sex":"F","loc":"D"},
            {"id":"F3","sex":"F","loc":"E"},
        ]
        out=m.support_counts(rows,id_field="id",location_field="loc")
        self.assertFalse(out["support_valid"])
        self.assertFalse(out["paired_n3_eligible"])


if __name__=="__main__":
    unittest.main()
