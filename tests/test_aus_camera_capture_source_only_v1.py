"""Synthetic tests for the Australian paired camera/trap source-only admission."""
import unittest
from unittest.mock import patch
import json

from analysis.audit_aus_camera_capture_source_only_v1 import (
    canonical_site_station, get_bytes, parse_csv, parsed_date,
    source_meta_and_csv, support_only,
)

class TestAustraliaPairedDetectorSourceGate(unittest.TestCase):
    def test_stake_link_uses_only_exact_source_prefix_or_exact_id(self):
        self.assertTrue(canonical_site_station("K-1", "K-1-A5", "A5"))
        self.assertTrue(canonical_site_station("K-1", "A5", "A5"))
        self.assertTrue(canonical_site_station("K-1", "K-1_A5", "A5"))
        self.assertFalse(canonical_site_station("K-1", "K-2-A5", "A5"))
        self.assertFalse(canonical_site_station("K-1", "K-1-A5-old", "A5"))
        self.assertFalse(canonical_site_station("K-1", "K-1-A6", "A5"))
        self.assertFalse(canonical_site_station("", "K-1-A5", "A5"))

    def test_explicit_day_parsing_with_no_overday_shift(self):
        self.assertEqual(parsed_date("2024:10:15 21:32:00"), "2024-10-15")
        self.assertEqual(parsed_date("2024-10-15 21:32:00"), "2024-10-15")
        self.assertEqual(parsed_date("15/10/2024"), "2024-10-15")
        self.assertIsNone(parsed_date("not-a-date"))
        self.assertIsNone(parsed_date(""))

    def test_header_missing_is_source_stop_before_effects(self):
        raw = b"site,station,species\nK-1,A1,Rattus\n"
        with self.assertRaisesRegex(ValueError, "HEADER_MISMATCH"):
            parse_csv(raw, "camera")

    def test_ragged_csv_stops_instead_of_truncating(self):
        header = ("site_type,site,station,species,season,"
                  "DateTimeOriginal,independent_capture,visit_ID,trap_state,individual_ID")
        raw = (header + "\nurban,K-1,A1,Rattus,spring,2024-05-01,1,v1,open\n").encode()
        with self.assertRaisesRegex(ValueError, "RAGGED_ROW"):
            parse_csv(raw, "camera")

    def test_provider_html_cannot_pass_as_csv(self):
        role = "traps"
        original = b"site_type,site,individual,date,season,trap_ID,genus,species,camera_capture\nurban,K-1,1,2024-05-01,spring,A5,Rattus,Rattus rattus,true\n"
        good = json.dumps({
            "path": "20250117_small_mammal_trapping.csv",
            "size": len(original),
            "digest": ""
        }).encode()
        with patch("analysis.audit_aus_camera_capture_source_only_v1.get_bytes",
                   side_effect=[good, b"<html>403 robot challenge</html>"]):
            with self.assertRaisesRegex(ValueError, "ORIGINAL_BYTE_COUNT"):
                source_meta_and_csv(role)
        with patch("analysis.audit_aus_camera_capture_source_only_v1.get_bytes",
                   side_effect=[good, original]):
            data, metadata = source_meta_and_csv(role)
            self.assertEqual(data, original)
            self.assertEqual(metadata["provider_size_and_actual_bytes"], len(original))

    def test_effect_blind_outputs_ignore_capture_and_behavior_values(self):
        row_camera = {"site_type": "urban reserve", "site": "K-1",
                      "station": "K-1-A5", "species": "Rattus rattus",
                      "season": "spring", "DateTimeOriginal": "2024:05:01 23:13:00",
                      "visit_ID": "v1", "trap_state": "open", "capture_pa": "0",
                      "interaction_pa": "0"}
        row_trap = {"site_type": "urban reserve", "site": "K-1",
                    "trap_ID": "A5", "season": "spring", "date": "01/05/2024",
                    "species": "Rattus rattus", "camera_capture": "no"}
        row_visit = {"site_type": "urban reserve", "site": "K-1",
                     "species": "Rattus rattus", "season": "spring",
                     "visit_ID": "v1", "interaction_pa": "0", "capture_pa": "0"}
        effort = {"site": "K-1", "sampling_effort": "25"}
        inputs = {
            "camera": [row_camera.copy()],
            "traps": [row_trap.copy()],
            "visits": [row_visit.copy()],
            "effort": [effort],
        }
        before = support_only(inputs)
        inputs["camera"][0]["capture_pa"] = "1"
        inputs["camera"][0]["interaction_pa"] = "1"
        inputs["visits"][0]["capture_pa"] = "1"
        inputs["visits"][0]["interaction_pa"] = "1"
        inputs["traps"][0]["camera_capture"] = "yes"
        after = support_only(inputs)
        self.assertEqual(before, after)
        self.assertFalse(before["all_structural_go_checks_passed"])
        self.assertEqual(before["strict_name_matched_station_keys"], 1)
        self.assertTrue(before["no_capture_outcomes_or_species_by_station_effect_unsealed"])

if __name__ == "__main__":
    unittest.main()
