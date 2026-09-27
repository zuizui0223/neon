from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
MANUSCRIPT=ROOT/"manuscript"/"neon_metacommunity_redundancy"/"MANUSCRIPT_V6_MECHANISM_VALIDATED_DRAFT.md"


class ManuscriptV6MechanismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=MANUSCRIPT.read_text(encoding="utf-8")

    def test_abstract_remains_within_oikos_limit(self):
        abstract=self.text.split("## Abstract",1)[1].split("## 1. Introduction",1)[0]
        words=re.findall(r"\b\S+\b",abstract)
        self.assertLessEqual(len(words),300)

    def test_metric_is_narrowed_to_local_spatial_cohesion(self):
        self.assertTrue(
            self.text.startswith(
                "# Local spatial cohesion in small mammals is redundant across species but context-dependent across sites"
            )
        )
        self.assertIn("no-isolated-occurrence",self.text)
        self.assertNotIn("span the relevant trap network",self.text)

    def test_fresh_primary_values_are_frozen(self):
        for token in (
            "median site excess = -0.080",
            "4/11 positive sites",
            "p = 0.887",
            "11 remaining structurally eligible sites",
        ):
            self.assertIn(token,self.text)

    def test_grid_and_state_switch_results_are_present(self):
        self.assertIn("66 of 68",self.text)
        self.assertIn("10 of those 15 switched",self.text)
        self.assertIn("median within-grid organization component was **0**",self.text)

    def test_response_effect_reference_is_present(self):
        self.assertIn("Lavorel and Garnier 2002",self.text)
        self.assertIn("10.1046/j.1365-2435.2002.00664.x",self.text)


if __name__=="__main__":
    unittest.main()
