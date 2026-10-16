from __future__ import annotations

import unittest

from analysis.run_multiscale_density_estimability_release2026_v1 import (
    _candidate_nights,
    _inventory,
    _site_codes,
)


class MultiscaleDensityReleaseRunnerTests(unittest.TestCase):
    def test_site_codes_accept_string_and_object_forms(self):
        payload = {
            "data": {
                "siteCodes": [
                    "ABBY",
                    {"siteCode": "BART"},
                    {"code": "CPER"},
                    "bad",
                ]
            }
        }
        self.assertEqual(_site_codes(payload), ["ABBY", "BART", "CPER"])

    def test_inventory_keeps_only_two_structural_tables(self):
        payload = {
            "data": {
                "releases": [
                    {
                        "release": "RELEASE-2026",
                        "packages": [
                            {
                                "siteCode": "ABBY",
                                "month": "2026-01",
                                "packageType": "basic",
                                "files": [
                                    {
                                        "name": "x_mam_perplotnight.csv",
                                        "md5": "a" * 32,
                                        "url": "https://example.org/p.csv",
                                        "size": 10,
                                    },
                                    {
                                        "name": "x_mam_pertrapnight.csv",
                                        "md5": "b" * 32,
                                        "url": "https://example.org/t.csv",
                                        "size": 20,
                                    },
                                    {
                                        "name": "x_other.csv",
                                        "md5": "c" * 32,
                                        "url": "https://example.org/o.csv",
                                        "size": 30,
                                    },
                                ],
                            }
                        ],
                    }
                ]
            }
        }
        rows = _inventory(payload)
        self.assertEqual(len(rows), 2)
        self.assertTrue(any("perplotnight" in r["name"] for r in rows))
        self.assertTrue(any("pertrapnight" in r["name"] for r in rows))

    def test_candidate_nights_require_multi_night_event(self):
        rows = [
            {
                "nightuid": "n1",
                "eventID": "E1",
                "plotID": "P1",
                "_site": "ABBY",
                "_month": "2026-01",
            },
            {
                "nightuid": "n2",
                "eventID": "E1",
                "plotID": "P1",
                "_site": "ABBY",
                "_month": "2026-01",
            },
            {
                "nightuid": "n3",
                "eventID": "E2",
                "plotID": "P1",
                "_site": "ABBY",
                "_month": "2026-02",
            },
        ]
        nights, site_months = _candidate_nights(rows)
        self.assertEqual(nights, {"n1", "n2"})
        self.assertEqual(site_months, {("ABBY", "2026-01")})


if __name__ == "__main__":
    unittest.main()
