from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

from analysis import temporal_aliasing_diagnostic_v1 as m

ROOT=Path(__file__).resolve().parents[1]


class TemporalAliasingExampleTests(unittest.TestCase):
    def test_checked_in_example_matches_expected_output(self):
        with (ROOT/"examples"/"repeated_locations_example.csv").open(
            newline="",encoding="utf-8-sig"
        ) as fh:
            records=list(csv.DictReader(fh))
        expected=json.loads(
            (ROOT/"examples"/"repeated_locations_example_expected.json").read_text()
        )

        spans,qc=m.first_last_spans(
            records,
            individual_col="animal_id",
            night_col="night_id",
            time_col="time_hours",
            coordinate_cols=["x_m","y_m"],
        )
        summary=m.summarize_spans(spans,material_scale=5.0)

        self.assertEqual(qc["input_rows"],expected["input_rows"])
        self.assertEqual(qc["individual_nights"],expected["individual_nights"])
        self.assertEqual(
            qc["repeat_observation_individual_nights"],
            expected["repeat_observation_individual_nights"],
        )
        self.assertEqual(
            qc["single_observation_individual_nights"],
            expected["single_observation_individual_nights"],
        )
        self.assertEqual(summary["material_shift_count"],expected["material_shift_count"])
        self.assertAlmostEqual(
            summary["material_shift_fraction"],
            expected["material_shift_fraction"],
        )


if __name__=="__main__":
    unittest.main()
