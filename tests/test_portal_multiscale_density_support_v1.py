from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from analysis.audit_portal_multiscale_density_support_v1 import audit


class PortalMultiscaleDensitySupportTests(unittest.TestCase):
    def test_counts_repeat_capture_support_without_spatial_effects(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "Rodents").mkdir()

            with (root / "Rodents" / "Portal_rodent_species.csv").open("w", newline="", encoding="utf-8") as fh:
                w=csv.DictWriter(fh,fieldnames=["speciescode","scientificname","rodent","censustarget","unidentified"])
                w.writeheader()
                w.writerow({"speciescode":"PP","scientificname":"Species p","rodent":"1","censustarget":"1","unidentified":"0"})

            with (root / "Rodents" / "Portal_rodent_trapping.csv").open("w", newline="", encoding="utf-8") as fh:
                w=csv.DictWriter(fh,fieldnames=["year","month","period","plot","sampled","effort","qcflag"])
                w.writeheader()
                w.writerow({"year":"2010","month":"1","period":"1","plot":"1","sampled":"1","effort":"49","qcflag":"1"})

            rows=[
                {"year":"2010","month":"1","day":"1","period":"1","plot":"1","species":"PP","id":"a","stake":"11"},
                {"year":"2010","month":"1","day":"2","period":"1","plot":"1","species":"PP","id":"a","stake":"12"},
                {"year":"2010","month":"1","day":"1","period":"1","plot":"1","species":"PP","id":"b","stake":"13"},
                {"year":"2010","month":"1","day":"2","period":"1","plot":"1","species":"PP","id":"b","stake":"13"},
                {"year":"2010","month":"1","day":"1","period":"1","plot":"1","species":"PP","id":"c","stake":"99"},
            ]
            with (root / "Rodents" / "Portal_rodent.csv").open("w", newline="", encoding="utf-8") as fh:
                w=csv.DictWriter(fh,fieldnames=["year","month","day","period","plot","species","id","stake"])
                w.writeheader(); w.writerows(rows)

            out=audit(root)
            self.assertEqual(out["support"]["totals"]["n_sessions"],1)
            s=out["support"]["sessions"][0]
            self.assertEqual(s["n_unique_individuals"],3)
            self.assertEqual(s["n_repeat_capture_individuals"],2)
            self.assertEqual(s["n_repeat_coordinate_supported_individuals"],2)
            self.assertEqual(s["n_distinct_capture_days"],2)
            self.assertFalse(out["boundary"]["spatial_distances_calculated"])
            self.assertNotIn("distance", str(out["support"]).lower())


if __name__ == "__main__":
    unittest.main()
