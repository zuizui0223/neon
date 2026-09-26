import csv
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "data" / "derived" / "site_metrics_v1.csv"
LOCK = ROOT / "validation" / "neon_metacommunity_connectivity_v1" / "response_lock_v1.json"
CLOSURE = ROOT / "validation" / "neon_metacommunity_connectivity_v1" / "programme_closure_v1.json"

class FrozenResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with SITE.open(newline="", encoding="utf-8") as fh:
            cls.rows = list(csv.DictReader(fh))
        cls.lock = json.loads(LOCK.read_text(encoding="utf-8"))
        cls.closure = json.loads(CLOSURE.read_text(encoding="utf-8"))

    def test_denominator(self):
        self.assertEqual(len(self.rows), 16)
        self.assertEqual(self.lock["denominator"]["fixed_sites"], 16)
        self.assertEqual(self.lock["denominator"]["scored_sites"], 16)

    def test_no_positive_gain(self):
        gains = [float(r["emergent_connectivity_gain"]) for r in self.rows]
        self.assertEqual(sum(g > 0 for g in gains), 0)
        self.assertEqual(self.lock["primary"]["median_emergent_connectivity_gain"], 0)
        self.assertEqual(self.lock["primary"]["one_sided_sign_test_p"], 1)

    def test_species_sufficiency(self):
        self.assertTrue(all(float(r["max_species_survival_fraction"]) == 1.0 for r in self.rows))
        self.assertTrue(all(float(r["strict_emergent_world_fraction"]) == 0.0 for r in self.rows))

    def test_ornl(self):
        row = next(r for r in self.rows if r["site_code"] == "ORNL")
        self.assertEqual(float(row["community_survival_fraction"]), 0.25)
        self.assertEqual(float(row["max_species_survival_fraction"]), 1.0)
        self.assertEqual(float(row["emergent_connectivity_gain"]), -0.75)

    def test_endpoint_closed(self):
        self.assertFalse(self.lock["rerun_allowed"])
        self.assertFalse(self.lock["response_repair_allowed"])
        self.assertFalse(self.lock["post_response_rule_change_allowed"])
        self.assertEqual(self.closure["scientific_state"], "closed_after_once_only_fresh_response")

if __name__ == "__main__":
    unittest.main()
