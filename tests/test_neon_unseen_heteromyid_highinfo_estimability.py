from __future__ import annotations

import unittest

from analysis import neon_unseen_heteromyid_highinfo_estimability_v1 as m


class UnseenHeteromyidEstimabilityTests(unittest.TestCase):
    def test_discovery_species_are_excluded(self):
        for name in m.DISCOVERY_SPECIES:
            self.assertFalse(m.is_unseen_heteromyid(name))
        self.assertTrue(m.is_unseen_heteromyid("Perognathus parvus"))

    def test_gate_requires_three_species_and_three_sites(self):
        rows=[]
        for species,site in [
            ("A alpha","S1"),
            ("B beta","S2"),
            ("C gamma","S3"),
        ]:
            for i in range(5):
                rows.append({
                    "species":species,
                    "site":site,
                    "paired_n3_eligible":True,
                    "paired_n5_eligible":True,
                })
        out=m.summarize(rows)
        self.assertTrue(out["gate"]["passed"])
        self.assertEqual(
            out["gate"]["decision"],
            "authorize_unseen_species_movement_effects",
        )

    def test_two_species_cannot_advance(self):
        rows=[]
        for species,site in [("A alpha","S1"),("B beta","S2")]:
            for i in range(6):
                rows.append({
                    "species":species,
                    "site":site,
                    "paired_n3_eligible":True,
                    "paired_n5_eligible":True,
                })
        out=m.summarize(rows)
        self.assertFalse(out["gate"]["passed"])


if __name__=="__main__":
    unittest.main()
