"""Synthetic visit-time and repeated patch source checks only, no seed outcome."""
import copy
import unittest
from analysis.audit_neon_figshare_2026_repeat_patch_visit_support_v1 import (
    count_source_support,clock_type,is_parseable_clock
)

class OriginalVoleCameraVisitSupport(unittest.TestCase):
    def fixture(self):
        stations=[]
        for n,date in (("1","2023-07-01"),("2","2023-07-02"),("3","2023-07-03")):
            for site in ("A","B"):
                stations.append({"Grid":"G1","Site":site,"Session":"1",
                                 "Night":n,"Date":date})
        def event(site,night,date,vid,pit,clock="21:10:11",wp="2"):
            return {
                "Grid":"G1","Site":site,"Session":"1","Night":night,
                "Visit.ID":vid,"PIT":pit,"Date":date,
                "Time.start":clock,"WP.available.OBS":wp,"RO.available.OBS":""
            }
        events=[
            event("A","1","2023-07-01","v1","00001"),
            event("A","1","2023-07-01","v1","00001"),  # two seed records one visit
            event("A","2","2023-07-02","v2","00001"),
            event("A","3","2023-07-03","v3","00001"),
            event("B","1","2023-07-01","v4","00002"),
            event("B","2","2023-07-02","v5","00002")
        ]
        return stations,events

    def test_distinct_visit_id_not_seed_interaction_rows(self):
        station,event=self.fixture()
        result=count_source_support(event,station)
        z=result["source_structural_counts"]
        self.assertEqual(z["original_unique_station_night_visitID_composites"],5)
        self.assertEqual(z["source_extra_seed_interaction_rows_beyond_unique_visitIDs"],1)
        self.assertEqual(z["source_visitIDs_with_multiple_interaction_rows"],1)
        self.assertEqual(z["source_clean_PIT_date_clock_visit_composites"],5)

    def test_literal_same_patch_revisit_on_later_source_days(self):
        station,event=self.fixture()
        z=count_source_support(event,station)["source_structural_counts"]
        self.assertEqual(z["source_distinct_PITs_revisiting_exact_same_GRID_Site_on_later_original_day"],2)
        self.assertEqual(z["source_return_visit_composites_later_than_first_original_day"],3)
        self.assertEqual(z["source_return_visit_composites_with_numeric_observed_seed_availability"],3)
        self.assertEqual(z["source_return_visit_composites_with_original_station_event_date_equal"],3)
        self.assertEqual(z["source_grid_session_night_occasions_with_two_or_more_station_sites"],3)

    def test_inconsistent_same_visit_PIT_fails_source_individual_status(self):
        station,event=self.fixture()
        event[1]["PIT"]="00099"
        z=count_source_support(event,station)["source_structural_counts"]
        self.assertEqual(z["source_visit_composites_PIT_missing_or_conflict"],1)
        self.assertEqual(z["source_clean_PIT_date_clock_visit_composites"],4)

    def test_inconsistent_same_visit_clock_cannot_be_sorted(self):
        station,event=self.fixture()
        event[1]["Time.start"]="22:10:11"
        z=count_source_support(event,station)["source_structural_counts"]
        self.assertEqual(z["source_visit_composites_start_time_missing_or_conflict"],1)
        self.assertEqual(z["source_clean_PIT_date_clock_visit_composites"],4)

    def test_same_date_repeat_visit_is_not_between_day_return(self):
        station,event=self.fixture()
        event[2]["Night"]="1";event[2]["Date"]="2023-07-01";event[2]["Visit.ID"]="v2"
        z=count_source_support(event,station)["source_structural_counts"]
        self.assertEqual(z["source_return_visit_composites_later_than_first_original_day"],2)

    def test_clock_formats_not_guessed(self):
        for t,kind in (("14:22:11","TIME_24H"),("9:12","TIME_24H"),
                       ("12:04:22 PM","TIME_12H_AMPM"),
                       ("2023-07-01 16:30:22","FULL_ISO_DATETIME"),
                       ("25:18:00","UNPARSED_OR_AMBIGUOUS"),
                       ("0.2572","NUMERIC_EXCEL_FRACTION_UNVERIFIED"),
                       ("","MISSING")):
            with self.subTest(raw=t):
                self.assertEqual(clock_type(t),kind)
        self.assertFalse(is_parseable_clock("NUMERIC_EXCEL_FRACTION_UNVERIFIED"))

    def test_unknown_original_source_seed_is_not_zero_and_no_resource_effect(self):
        station,event=self.fixture()
        for row in event:
            row["WP.available.OBS"]=""
            row["RO.available.OBS"]="NA"
            row["Seed.Found..Y.N."]="original outcome that must not be read"
        z=count_source_support(event,station)
        self.assertEqual(z["source_structural_counts"][
            "source_return_visit_composites_with_numeric_observed_seed_availability"],0)
        self.assertFalse(z["source_repeat_patch_all_checks_GO"])
        self.assertNotIn("original outcome that must not be read",str(z))

    def test_no_source_visit_ID_or_Grid_published_in_receipt(self):
        station,event=self.fixture()
        z=count_source_support(event,station)
        import json
        s=json.dumps(z,sort_keys=True)
        for marker in ('"G1"','"A"','"00001"','"v1"'):
            self.assertNotIn(marker,s)

if __name__=="__main__":
    unittest.main()
