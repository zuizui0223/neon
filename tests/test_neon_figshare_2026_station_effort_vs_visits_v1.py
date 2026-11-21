"""Synthetic effort-metadata versus positive-event tests, not biology."""
import unittest
from analysis.diagnose_neon_figshare_2026_station_effort_vs_visits_v1 import (
    source_only_table,
)

class TestCameraOpportunitySourceMetadata(unittest.TestCase):
    def fabricated(self):
        stations=[]
        events=[]
        for i in range(288):
            k={"Grid":"g","Site":f"s{i}","Session":"1","Night":"1"}
            row={**k,"Date":"2023-07-11" if i<136 else "",
                 "Night.set":"2023-07-10 18:00",
                 "Morning.check":"2023-07-11 06:00",
                 "WP.seeds.set":"5","RO.seeds.set":"2"}
            stations.append(row)
            if i<136:
                for j in range(23 if i<115 else 22):
                    events.append({**k,"Visit.ID":f"visit{j}"})
        # Ensure exact original observed event size of 3243.
        while len(events)>3243:events.pop()
        while len(events)<3243:events.append({**stations[0],
                                                  "Visit.ID":"additional"})
        for n in (2,2,4):
            row={k:"" for k in ("Grid","Site","Session","Night")}
            for j in range(n):
                row[f"other_source_{j}"]="has_original_metadata"
            stations.append(row)
        return {"All Station Nights.csv":stations,
                "All Foraging Clean.csv":events}

    def test_visits_cannot_define_camera_denominator(self):
        x=source_only_table(self.fabricated())
        self.assertEqual(x["original_complete_source_station_night_keys"],288)
        self.assertEqual(x["unique_keyed_station_nights_with_foraging_events"],136)
        self.assertEqual(x["keyed_station_nights_without_foraging_event"],152)
        self.assertTrue(x["source_Date_perfectly_conditional_on_observed_event_metadata"])
        self.assertTrue(x["source_original_291_row_full_key_GO_remains_FAILED"])

    def test_missing_original_nonblank_rows_not_coded_true_absence(self):
        x=self.fabricated()
        x["All Station Nights.csv"][-1]["other_source_0"]=""
        with self.assertRaisesRegex(ValueError,"KEYLESS_NONBLANK_RECORD_TYPE_DRIFT"):
            source_only_table(x)

    def test_duplicate_station_night_record_not_silently_deduplicated(self):
        x=self.fabricated()
        x["All Station Nights.csv"][10] = dict(x["All Station Nights.csv"][0])
        with self.assertRaisesRegex(ValueError,"DUPLICATE_ORIGINAL_COMPLETE_STATION_NIGHT_KEY"):
            source_only_table(x)

if __name__=="__main__":
    unittest.main()
