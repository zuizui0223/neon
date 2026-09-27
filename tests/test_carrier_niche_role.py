import csv
from collections import Counter
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TRAITS = ROOT / "data" / "external" / "carrier_niche_evidence_v2_all32.csv"
SITES = ROOT / "data" / "derived" / "site_metrics_v1.csv"


class CarrierNicheRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with TRAITS.open(newline="", encoding="utf-8") as fh:
            cls.traits = list(csv.DictReader(fh))
        with SITES.open(newline="", encoding="utf-8") as fh:
            cls.sites = list(csv.DictReader(fh))
        cls.by_species = {r["species_name"]: r for r in cls.traits}

    def test_all_carriers_are_coded_once(self):
        observed = {
            species
            for site in self.sites
            for species in site["best_species_names"].split(";")
            if species
        }
        self.assertEqual(len(self.traits), 32)
        self.assertEqual(len(self.by_species), 32)
        self.assertEqual(set(self.by_species), observed)

    def test_trophic_group_counts(self):
        counts = Counter(r["primary_trophic_group"] for r in self.traits)
        self.assertEqual(
            counts,
            Counter({"granivore": 13, "herbivore": 10, "omnivore": 7, "predator": 2}),
        )

    def test_recurrent_carriers_span_three_groups(self):
        recurrent = [r for r in self.traits if int(r["carrier_site_count"]) == 3]
        self.assertEqual(len(recurrent), 4)
        self.assertEqual(
            {r["species_name"] for r in recurrent},
            {"Mus musculus", "Peromyscus boylii", "Reithrodontomys megalotis", "Sigmodon hispidus"},
        )
        self.assertEqual(
            {r["primary_trophic_group"] for r in recurrent},
            {"omnivore", "granivore", "herbivore"},
        )

    def test_multi_carrier_redundancy_is_usually_cross_trophic(self):
        multi = []
        cross = []
        all_four = []
        within_only = []
        for site in self.sites:
            carriers = [x for x in site["best_species_names"].split(";") if x]
            groups = {self.by_species[x]["primary_trophic_group"] for x in carriers}
            if len(carriers) >= 2:
                multi.append(site["site_code"])
                if len(groups) >= 2:
                    cross.append(site["site_code"])
                else:
                    within_only.append(site["site_code"])
            if len(groups) == 4:
                all_four.append(site["site_code"])

        self.assertEqual(len(multi), 13)
        self.assertEqual(len(cross), 12)
        self.assertEqual(within_only, ["NOGP"])
        self.assertEqual(set(all_four), {"MOAB", "OAES"})


if __name__ == "__main__":
    unittest.main()
