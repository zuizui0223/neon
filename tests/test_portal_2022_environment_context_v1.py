"""Numeric and no-significance checks for site-year environment context."""
from __future__ import annotations
import unittest
from analysis.run_portal_2022_environment_context_v1 import source_year_differences

class TestPortal2022Context(unittest.TestCase):
    def test_all_three_transitions_reported_and_2022_rank(self):
        z=source_year_differences({2021:1.,2022:3.,2023:7.,2024:6.})
        self.assertEqual(len(z["all_unselected_transitions"]),3)
        self.assertEqual(z["2022_to_2023_absolute_change_rank_largest_first"],1)
        self.assertEqual(z["all_unselected_transitions"]["2023_to_2024"]["signed"],-1.)
        self.assertTrue(z["no_significance_test_from_three_year_transitions"])

    def test_2022_transition_not_extreme(self):
        x=source_year_differences({2021:1.,2022:8.,2023:9.,2024:14.})
        self.assertEqual(x["2022_to_2023_absolute_change_rank_largest_first"],3)

    def test_no_substitute_if_missing_required_year(self):
        with self.assertRaisesRegex(ValueError,"FOUR_YEAR_DOMAIN_DRIFT"):
            source_year_differences({2021:1.,2022:3.,2023:7.})

if __name__=="__main__":
    unittest.main()
