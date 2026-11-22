"""Synthetic date-order tests only; original rodent and plant effects sealed."""
import unittest
from datetime import date
from analysis.audit_portal_2022_ndvi_capture_chronology_v1 import (
    phase, summary_from_entries,
)

class TestOriginalCapturedCommunityVersusSatelliteTiming(unittest.TestCase):
    def test_full_monsoon_mean_cannot_precede_earlier_survey(self):
        self.assertEqual(phase(date(2023,6,30)),"PRE_MONSOON")
        self.assertEqual(phase(date(2023,7,1)),"DURING_MONSOON")
        self.assertEqual(phase(date(2023,9,30)),"DURING_MONSOON")
        self.assertEqual(phase(date(2023,10,1)),"POST_MONSOON")

    def test_diagnostic_counts_all_original_timing_classes_not_best_subset(self):
        # 114 synthetic rows with the same FROZEN year support as original,
        # but no original biological or satellite outcome values.
        entries=[]
        for y,n in ((2021,21),(2022,65),(2023,28)):
            for j in range(n):
                p=("PRE_MONSOON","DURING_MONSOON","POST_MONSOON")[j%3]
                entries.append({
                    "start_year":y,
                    "plot":j%18+1,
                    "month":{"PRE_MONSOON":4,"DURING_MONSOON":8,"POST_MONSOON":11}[p],
                    "treatment":"control" if j%2==0 else "exclosure",
                    "baseline_phase":p,"followup_phase":p,
                    "plant_season_A":"summer","plant_season_B":"summer"
                })
        z=summary_from_entries(entries)
        self.assertEqual(z["all_original_years"]["2022"]["pair_count"],65)
        d=z["2022_to_2023_specific_chronology"]
        self.assertEqual(sum(x["matched_pairs"] for x in
                             d["followup_2023_capture_phase_counts"].values()),65)
        self.assertEqual(d["both_2022_and_2023_captures_post_september_30"],21)
        self.assertTrue(z["limits"]["postresult_chronology_diagnostic_not_independent_validation"])

    def test_wont_accept_any_other_cohort_size(self):
        with self.assertRaisesRegex(ValueError,"ORIGINAL_114_ENTRIES_REQUIRED"):
            summary_from_entries([])

if __name__=="__main__":
    unittest.main()
