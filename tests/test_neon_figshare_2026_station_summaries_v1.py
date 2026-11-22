"""Regression tests for reconciling station counts with the public event table."""
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from analysis.reconcile_neon_figshare_2026_station_summaries_v1 import reconcile


def source_rows():
    fields = ("Grid", "Site", "Session", "Night", "Visitors?", "WP.seeds.set",
              "WP.seeds.left", "RO.seeds.set", "RO.seeds.left")
    return [dict(zip(fields, values)) for values in [
        ("g", "a", "1", "1", "Visitors", 2, 1, 1, 0),
        ("g", "b", "1", "1", "Visitors", "2", "0", "1", "1"),
        ("g", "c", "1", "1", "None", 2, 1, 1, 1),
        ("g", "d", "1", "1", "NA", 0, 0, 0, 0),
        ("", "", "", "", "", 6, 2, 3, 2),
        ("", "", "", "", "", 4, "", 1, ""),
        ("", "", "", "", "", "0.666666667", "", "0.333333333", ""),
    ]]


class StationSummaryTests(unittest.TestCase):
    def test_visitors_without_event_rows_and_both_kinds_of_zero(self):
        stations = source_rows()
        response = reconcile(stations, [stations[0], stations[0]])
        self.assertEqual(response["station_source_rows"], 7)
        self.assertEqual(response["station_nights"], 4)
        self.assertEqual(response["event_rows"], 2)
        by_label = {(r["event_row_present"], r["station_visitor_label"]): r
                    for r in response["coverage"]}
        self.assertEqual(by_label[False, "Visitors"], {
            "event_row_present": False, "station_visitor_label": "Visitors",
            "station_nights": 1, "WP_offered": 2, "WP_missing": 2,
            "RO_offered": 1, "RO_missing": 0, "nights_with_any_missing": 1})
        self.assertEqual(by_label[False, "NA"]["nights_with_any_missing"], 0)
        self.assertEqual(by_label[False, "None"]["WP_missing"], 1)
        self.assertEqual(by_label[True, "Visitors"]["station_nights"], 1)

    def test_arbitrary_keyless_record_cannot_be_dropped(self):
        stations = source_rows()
        extra = dict.fromkeys(stations[0], "")
        with self.assertRaises(ValueError):
            reconcile(stations[:2] + [extra] + stations[2:], [])

    def test_footer_with_nonseed_metadata_is_not_an_aggregate(self):
        stations = source_rows()
        stations[-1]["Date"] = "1-Aug"
        with self.assertRaises(ValueError):
            reconcile(stations, [])

    def test_falsified_footer_numbers_and_unexpected_nonblank_cells(self):
        for index, field, value in [(-3, "WP.seeds.left", 3), (-2, "RO.seeds.set", 2),
                                     (-1, "RO.seeds.set", ".333333335"),
                                     (-2, "WP.seeds.left", 0)]:
            with self.subTest(index=index, field=field):
                stations = source_rows()
                stations[index][field] = value
                with self.assertRaises(ValueError):
                    reconcile(stations, [])

    def test_partial_and_duplicate_keys_fail_even_with_matching_seed_sums(self):
        for replacement in ("", "a"):
            stations = source_rows()
            stations[1]["Site"] = replacement
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                reconcile(stations, [])

    def test_event_key_must_be_complete_and_identify_a_real_station(self):
        stations = source_rows()
        for site in ("", "unlisted"):
            with self.subTest(site=site), self.assertRaises(ValueError):
                reconcile(stations, [dict(stations[0], Site=site)])

    def test_broken_seed_count_is_not_zero(self):
        for value in ("", None, "-1", "0.4", True):
            stations = source_rows()
            stations[3]["WP.seeds.left"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                reconcile(stations, [])

    def test_output_alias_of_source_rejected_before_loading_inputs(self):
        script = Path(__file__).resolve().parents[1] / "analysis" / (
            "reconcile_neon_figshare_2026_station_summaries_v1.py")
        with TemporaryDirectory() as directory:
            source_dir = Path(directory)
            for name in ("metadata.json", "All Station Nights.csv", "All Foraging Clean.csv",
                         "Main Analysis - Clean.R", "Repeatability.R"):
                source = source_dir / name
                source.write_bytes(b"untouched test input")
                symlink = source.with_name(name + ".symlink")
                symlink.symlink_to(source)
                hardlink = source.with_name(name + ".hardlink")
                hardlink.hardlink_to(source)
                for output in (source, symlink, hardlink):
                    with self.subTest(source=name, output=output.name):
                        result = subprocess.run(
                            [sys.executable, str(script), "--source-dir", directory,
                             "--output", str(output)], capture_output=True)
                        self.assertEqual(result.returncode, 2, result.stderr.decode())
                        self.assertEqual(source.read_bytes(), b"untouched test input")
