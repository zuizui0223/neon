"""Future NEON inventory comparison never opens capture or W/B outcomes."""
import unittest
from analysis.audit_future_neon_mammal_availability_v1 import audit


class FutureInventoryTests(unittest.TestCase):
    def sample(self):
        return {"data":{"siteCodes":[
            {"siteCode":"ABBY","availableMonths":["2026-08","2026-09","2026-10","2026-11"],
             "availableReleases":[{"release":"RELEASE-2026","availableMonths":["2026-08","2026-09"]}]},
            {"siteCode":"HARV","availableMonths":["2026-09"],
             "availableReleases":[{"release":"RELEASE-2026","availableMonths":["2026-09"]}]},
        ]}}

    def test_full_new_month_only(self):
        r=audit(self.sample(),as_of="2026-10-10")
        self.assertEqual(r["new_site_month_candidates"],1)
        self.assertEqual(r["site_month_candidates"],[{"site":"ABBY","month":"2026-10"}])
        self.assertFalse(r["W_B_effects_opened"])
        self.assertFalse(r["future_independent_replication_confirmed"])

    def test_no_new_release(self):
        r=audit(self.sample(),as_of="2026-09-30")
        self.assertEqual(r["status"],"NO_FULLY_NEW_SITE_MONTHS_IN_INVENTORY")

    def test_missing_release_metadata_stops(self):
        bad=self.sample()
        del bad["data"]["siteCodes"][1]["availableReleases"]
        r=audit(bad)
        self.assertEqual(r["status"],"STRUCTURAL_METADATA_STOP")
        self.assertFalse(r["captures_downloaded"])

    def test_no_frozen_release_metadata_stops(self):
        bad={"data":{"siteCodes":[{"siteCode":"ABBY","availableMonths":["2026-10"],
              "availableReleases":[{"release":"RELEASE-2025","availableMonths":["2026-10"]}]}]}}
        with self.assertRaisesRegex(ValueError,"RELEASE-2026"):
            audit(bad)


if __name__=="__main__":
    unittest.main()
