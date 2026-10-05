from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from analysis.audit_multiscale_density_estimability_v1 import audit


class MultiscaleDensityEstimabilityAuditTests(unittest.TestCase):
    def test_effect_blind_support_counts_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plot = root / "mam_perplotnight.csv"
            trap = root / "mam_pertrapnight.csv"

            with plot.open("w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(
                    fh,
                    fieldnames=[
                        "nightuid", "eventID", "plotID", "siteID",
                        "mammalGridSamplingType", "gridCompletion", "collectDate"
                    ],
                )
                w.writeheader()
                for n, d in [("n1", "2026-01-01"), ("n2", "2026-01-02"), ("n3", "2026-01-03")]:
                    w.writerow({
                        "nightuid": n,
                        "eventID": "E1",
                        "plotID": "P1",
                        "siteID": "SITE",
                        "mammalGridSamplingType": "pathogen",
                        "gridCompletion": "complete",
                        "collectDate": d,
                    })

            rows = []
            # Structural effort rows.
            for night in ("n1", "n2", "n3"):
                for coord in ("A1", "A2", "A3"):
                    rows.append({
                        "nightuid": night,
                        "plotID": "P1",
                        "trapCoordinate": coord,
                        "trapStatus": "1 - no capture",
                        "tagID": "",
                        "taxonID": "",
                        "scientificName": "",
                    })

            # Taxon TX1: two tagged individuals, one changes coordinate across nights.
            rows += [
                {
                    "nightuid": "n1", "plotID": "P1", "trapCoordinate": "A1",
                    "trapStatus": "5 - capture", "tagID": "i1",
                    "taxonID": "TX1", "scientificName": "Species one",
                },
                {
                    "nightuid": "n2", "plotID": "P1", "trapCoordinate": "A2",
                    "trapStatus": "5 - capture", "tagID": "i1",
                    "taxonID": "TX1", "scientificName": "Species one",
                },
                {
                    "nightuid": "n1", "plotID": "P1", "trapCoordinate": "A3",
                    "trapStatus": "5 - capture", "tagID": "i2",
                    "taxonID": "TX1", "scientificName": "Species one",
                },
            ]

            with trap.open("w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(
                    fh,
                    fieldnames=[
                        "nightuid", "plotID", "trapCoordinate", "trapStatus",
                        "tagID", "taxonID", "scientificName"
                    ],
                )
                w.writeheader()
                w.writerows(rows)

            out = audit(plot, trap)
            self.assertEqual(out["status"], "effect_blind_structural_support_only")
            self.assertFalse(out["boundary"]["effect_values_opened"])
            self.assertFalse(out["boundary"]["spatial_distances_calculated"])

            sessions = out["support"]["sessions"]
            self.assertEqual(len(sessions), 1)
            s = sessions[0]
            self.assertEqual(s["taxon"], "TX1")
            self.assertEqual(s["n_trapping_nights"], 3)
            self.assertEqual(s["n_unique_tagged_individuals"], 2)
            self.assertEqual(s["n_repeat_capture_tagged_individuals"], 1)
            self.assertEqual(s["n_repeat_coordinate_supported_tagged_individuals"], 1)
            self.assertEqual(s["n_multi_night_tagged_individuals"], 1)
            self.assertEqual(s["n_coordinate_supported_tagged_individuals"], 2)
            self.assertNotIn("n_repeat_location_tagged_individuals", s)
            self.assertNotIn("n_distinct_capture_coordinates", s)

            support_text = json.dumps(out["support"]).lower()
            for forbidden in ("beta_w", "beta_b", "delta_beta", "habitat_effect", "distance"):
                self.assertNotIn(forbidden, support_text)

    def test_requires_event_and_spatial_support_identifiers(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plot = root / "p.csv"
            trap = root / "t.csv"
            plot.write_text("nightuid,plotID\nn1,P1\n", encoding="utf-8")
            trap.write_text(
                "nightuid,plotID,trapCoordinate,taxonID\nn1,P1,A1,TX1\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                audit(plot, trap)


if __name__ == "__main__":
    unittest.main()
