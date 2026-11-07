"""Synthetic-only tests of two non-equivalent small-mammal recording methods."""
from __future__ import annotations
import unittest
from analysis.neon_external_norway_two_detector_v1 import (
    original_rows, summarize_observation_channels
)

def fixture():
    rows=["site;year;season;species;count.live;count.cam;traptype",
          "S1;2018;fall;bank vole;1;1;cage",
          "S1;2019;fall;bank vole;0;3;cage",
          "S1;2020;fall;bank vole;0;2;cage",
          "S1;2019;spring;bank vole;1;0;cage",
          "S1;2020;spring;bank vole;1;0;cage",
          "S1;2018;fall;wood mouse;0;0;cage",
          "S1;2019;fall;wood mouse;1;1;cage",
          "S1;2020;fall;wood mouse;1;1;cage",
          "S1;2019;spring;wood mouse;0;1;cage",
          "S1;2020;spring;wood mouse;0;0;cage"]
    return ("\n".join(rows)+"\n").encode()

class PairedDetectorAuditTests(unittest.TestCase):
    def test_original_md5_is_required_before_source_claim(self):
        with self.assertRaises(ValueError):
            original_rows(fixture())
    def test_two_detectors_discordance_is_neither_true_absence_nor_event_rate(self):
        result=summarize_observation_channels(original_rows(fixture(),pinned=False))
        counts=result["paired_camera_capture_record"]["detector_discordance"]
        self.assertEqual(counts,{"both":3,"camera_only":3,"capture_only":2,"neither":2})
        self.assertTrue(result["scientific_limitations"]["camera_and_ordinary_trap_effort_not_equal"])
        self.assertTrue(result["scientific_limitations"]["camera_and_capture_are_not_same_date_replicates"])
        self.assertTrue(result["published_original_source"]["camera_counts_precede_trapping_by_30_calendar_days"])
    def test_capture_apparent_loss_can_coexist_with_camera_continuity(self):
        result=summarize_observation_channels(original_rows(fixture(),pinned=False))
        n=result["adjacent_same_season_year_comparison"]["totals"]
        self.assertEqual(n["original_site_taxon_year_transition"],6)
        self.assertEqual(n["apparent_capture_loss_camera_still_both"],1)
        self.assertEqual(n["camera_two_year_capture_not"],2)
        self.assertEqual(n["capture_two_year_camera_not"],1)
    def test_missing_campaign_taxon_is_not_a_negative_detection(self):
        raw=fixture()
        raw=raw.replace(b"S1;2019;fall;bank vole;0;3;cage\n",b"")
        result=summarize_observation_channels(original_rows(raw,pinned=False))
        self.assertEqual(result["adjacent_same_season_year_comparison"]["totals"]["original_site_taxon_year_transition"],4)
    def test_duplicate_or_bad_count_fails_closed(self):
        with self.assertRaises(ValueError):
            original_rows(fixture()+b"S1;2018;fall;bank vole;1;1;cage\n",pinned=False)
        with self.assertRaises(ValueError):
            original_rows(fixture().replace(b";0;3;cage",b";NA;3;cage"),pinned=False)
    def test_switched_capture_gear_separate(self):
        raw=fixture().replace(b"S1;2020;fall;bank vole;0;2;cage",b"S1;2020;fall;bank vole;0;2;snap").replace(b"S1;2020;fall;wood mouse;1;1;cage",b"S1;2020;fall;wood mouse;1;1;snap")
        result=summarize_observation_channels(original_rows(raw,pinned=False))
        changed=result["adjacent_same_season_year_comparison"]["by_trap_gear_stable_vs_switched"]
        self.assertEqual(changed["switched_capture_gear"]["original_site_taxon_year_transition"],2)
    def test_site_equal_bootstrap_does_not_turn_into_detection_probability(self):
        result=summarize_observation_channels(original_rows(fixture(),pinned=False))
        b=result["adjacent_same_season_year_comparison"]["site_equal_camera_minus_capture_both_year_positive_fraction"]
        self.assertEqual(b["sites"],1)
        self.assertLessEqual(b["site_bootstrap_95pct_descriptive_interval"][0],b["mean"])
        self.assertTrue(result["scientific_limitations"]["camera_presence_not_true_occupancy_or_individual_survival"])

if __name__=="__main__":
    unittest.main()
