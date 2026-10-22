from __future__ import annotations

import unittest

from analysis.run_multiscale_density_estimability_release2026_v2 import (
    START,
    _candidate_nights,
)


class MultiscaleDensityStandardizedEraRunnerTests(unittest.TestCase):
    def test_primary_era_begins_after_2015_design_change(self):
        self.assertEqual(START, "2015-04")

    def test_exact_three_night_plot_events_are_candidates(self):
        rows = []
        for night in ("p1", "p2", "p3"):
            rows.append({
                "nightuid": night,
                "eventID": "E3",
                "plotID": "P1",
                "mammalGridSamplingType": "",
                "_site": "ABBY",
                "_month": "2025-06",
            })
        for night in ("x1", "x2", "x3", "x4"):
            rows.append({
                "nightuid": night,
                "eventID": "E4",
                "plotID": "P2",
                "mammalGridSamplingType": "",
                "_site": "ABBY",
                "_month": "2025-06",
            })
        rows.append({
            "nightuid": "d1",
            "eventID": "E1",
            "plotID": "P3",
            "mammalGridSamplingType": "",
            "_site": "ABBY",
            "_month": "2025-06",
        })
        for night in ("q1", "q2"):
            rows.append({
                "nightuid": night,
                "eventID": "E2",
                "plotID": "P4",
                "mammalGridSamplingType": "",
                "_site": "ABBY",
                "_month": "2025-07",
            })

        nights, site_months = _candidate_nights(rows)
        self.assertEqual(nights, {"p1", "p2", "p3"})
        self.assertEqual(site_months, {("ABBY", "2025-06")})



if __name__ == "__main__":
    unittest.main()
