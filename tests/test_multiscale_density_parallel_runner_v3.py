from __future__ import annotations

import unittest
from unittest.mock import patch

from analysis.run_multiscale_density_estimability_release2026_v3 import (
    MAX_DOWNLOAD_WORKERS,
    START,
    _candidate_nights,
    _download_many,
)


class MultiscaleDensityParallelRunnerTests(unittest.TestCase):
    def test_protocol_boundary_is_unchanged(self):
        self.assertEqual(START, "2015-04")
        self.assertEqual(MAX_DOWNLOAD_WORKERS, 6)

    def test_parallel_download_preserves_inventory_order(self):
        rows = [{"name": "a"}, {"name": "b"}, {"name": "c"}]
        with patch(
            "analysis.run_multiscale_density_estimability_release2026_v3._download_one",
            side_effect=lambda row, token: row["name"].encode("ascii"),
        ):
            out = _download_many(rows, "token", max_workers=3)
        self.assertEqual(out, [b"a", b"b", b"c"])

    def test_candidate_rule_remains_pathogen_three_night(self):
        rows = [
            {
                "nightuid": n,
                "eventID": "E1",
                "plotID": "P1",
                "mammalGridSamplingType": "pathogen",
                "_site": "ABBY",
                "_month": "2025-06",
            }
            for n in ("n1", "n2", "n3")
        ]
        nights, months = _candidate_nights(rows)
        self.assertEqual(nights, {"n1", "n2", "n3"})
        self.assertEqual(months, {("ABBY", "2025-06")})


if __name__ == "__main__":
    unittest.main()
