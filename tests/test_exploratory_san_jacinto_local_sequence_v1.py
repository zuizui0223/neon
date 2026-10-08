"""Synthetic checks for an explicitly exploratory capture-only analysis."""
import unittest

from analysis.exploratory_san_jacinto_local_sequence_v1 import (
    analyze, build_capture_index, case_rows, adjacent_flags,
)


def entry(day, slot, species, uid, flag="A1", grid="G1"):
    return {
        "grid": grid, "date": day, "time_bin": slot, "flag": flag,
        "species": species, "unique_ID": uid,
    }


class LocalSequenceTest(unittest.TestCase):
    def setUp(self):
        self.rows = [
            entry("2020-07-01", "early", "A", "a1"),
            entry("2020-07-01", "middle", "A", "a2"),
            entry("2020-07-01", "late", "B", "b1"),
            entry("2020-07-02", "early", "B", "b2"),
            entry("2020-07-02", "middle", "B", "b3"),
            entry("2020-07-02", "late", "A", "a3"),
        ]

    def test_matched_same_species_contrast(self):
        result = analyze(self.rows, replicates=0)
        a = result["analysis"]["early_to_middle"]
        self.assertEqual(result["qc"]["eligible_grid_nights"], 2)
        self.assertEqual(a["n"], 2)
        self.assertEqual(a["matched_difference"], 1.0)
        self.assertIsNone(a["cluster_bootstrap95"])
        self.assertEqual(result["matched_cases"], 4)

    def test_self_recaptures_not_included(self):
        rows = list(self.rows)
        rows[1] = entry("2020-07-01", "middle", "A", "a1")
        captures, _ = build_capture_index(rows)
        cases = case_rows(captures)
        self.assertFalse(any(
            r["date"] == "2020-07-01" and r["transition"] == "early_to_middle"
            for r in cases
        ))

    def test_ambiguous_duplicate_cell_rejected(self):
        rows = self.rows + [entry("2020-07-01", "early", "B", "b9")]
        captures, qc = build_capture_index(rows)
        self.assertEqual(qc["rejections"]["ambiguous_trap_check_cell"], 1)
        self.assertNotIn(("G1", "2020-07-01", "early", "A1"), captures)
        self.assertEqual(qc["eligible_grid_nights"], 1)

    def test_neighbor_reference_only_uses_other_flags(self):
        self.assertEqual(adjacent_flags("A1"), {"A2", "B1", "B2"})
        self.assertEqual(len(adjacent_flags("D4")), 8)
        rows = self.rows + [entry("2020-07-01", "early", "B", "bx", flag="A2")]
        result = analyze(rows, replicates=0)
        neighbor = result["analysis"]["early_to_middle"]["adjacent_trap_same_night_reference"]
        self.assertEqual(neighbor["matched_cases"], 1)
        self.assertAlmostEqual(neighbor["observed_minus_neighbor_fraction"], 1.0)

    def test_no_inferred_empty_as_ecological_absence(self):
        result = analyze(self.rows, replicates=0)
        self.assertTrue(result["no_capture_row_is_not_verified_absence"])
        self.assertEqual(result["source_data_type"], "capture_only")
        self.assertEqual(result["qc"]["capture_cells"], 6)


if __name__ == "__main__":
    unittest.main()
