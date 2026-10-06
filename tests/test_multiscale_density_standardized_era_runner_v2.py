from __future__ import annotations

import unittest

from analysis.run_multiscale_density_estimability_release2026_v2 import (
    START,
    _candidate_nights,
)


class MultiscaleDensityStandardizedEraRunnerTests(unittest.TestCase):
    def test_primary_era_begins_after_2015_design_change(self):
        self.assertEqual(START, "2015-04")

    def test_only_three_night_pathogen_events_are_candidates(self):
        rows = []
        for night in ("p1", "p2", "p3"):
            rows.append({
                "nightuid": night,
                "eventID": "EP",
                "plotID": "P1",
                "mammalGridSamplingType": "pathogen",
                "_site": "ABBY",
                "_month": "2025-06",
            })
        for night in ("r1", "r2", "r3"):
            rows.append({
                "nightuid": night,
                "eventID": "ER",
                "plotID": "P2",
                "mammalGridSamplingType": "recapture",
                "_site": "ABBY",
                "_month": "2025-06",
            })
        rows.append({
            "nightuid": "d1",
            "eventID": "ED",
            "plotID": "P3",
            "mammalGridSamplingType": "diversity",
            "_site": "ABBY",
            "_month": "2025-06",
        })
        for night in ("q1", "q2"):
            rows.append({
                "nightuid": night,
                "eventID": "E2",
                "plotID": "P4",
                "mammalGridSamplingType": "pathogen",
                "_site": "ABBY",
                "_month": "2025-07",
            })

        nights, site_months = _candidate_nights(rows)
        self.assertEqual(nights, {"p1", "p2", "p3"})
        self.assertEqual(site_months, {("ABBY", "2025-06")})


if __name__ == "__main__":
    unittest.main()
