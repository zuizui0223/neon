"""Synthetic corrected Figshare 2026 source-only v2 admission and fail-closed tests."""
import copy
import unittest
from analysis.audit_neon_figshare_2026_station_event_capture_source_v2 import (
    corrected_source_only,source_verified_calendar_year
)

def synthetic_original_source():
    stations=[]
    for i in range(288):
        key={"Grid":f"G{i%6}","Site":f"S{i}","Session":"1","Night":"1"}
        stations.append({
            **key,"Date":"2023-07-11" if i<136 else "",
            "Visitors?":"Visitors" if i<189 else "None",
            "Night.set":"2023-07-10","Morning.check":"2023-07-11",
            "WP.seeds.set":"5","WP.seeds.left":"4",
            "RO.seeds.set":"2","RO.seeds.left":"2",
            "PRED_PRES":""
        })
    # Exactly the original 3 summary ROW TYPES and original positions.
    blank={k:"" for k in stations[0]}
    row0=dict(blank);row0.update({
        "WP.seeds.set":"1440","WP.seeds.left":"1152",
        "RO.seeds.set":"576","RO.seeds.left":"576"})
    row1=dict(blank);row1.update({
        "WP.seeds.set":"288","RO.seeds.set":"0"})
    row2=dict(blank);row2.update({
        "WP.seeds.set":"0.2","RO.seeds.set":"0"})
    stations.extend((row0,row1,row2))
    events=[]
    for i in range(3243):
        key=stations[i%136]
        events.append({k:key[k] for k in ("Grid","Site","Session","Night")}
                     |{"Date":"2023-07-11","PIT":"0001","Visit.ID":f"v{i}",
                       "WP.available.OBS":"2","RO.available.OBS":""})
    capture=[]
    for i in range(11614):
        capture.append({"YEAR":"23","DATE":"2023-07-11",
                        "PIT":"0001","GRID":f"G{i%6}"})
    return {
        "2016-2023 Capture Data.csv":capture,
        "All Foraging Clean.csv":events,
        "All Station Nights.csv":stations,
        "Mouse Foraging Data Clean.csv":events[:883],
        "Vole Foraging Data Clean.csv":events[883:1834],
    }

class CorrectedFigshare2026SourceV2(unittest.TestCase):
    def test_exact_original_year_not_four_digits_guessed(self):
        self.assertEqual(source_verified_calendar_year({
            "YEAR":"23","DATE":"2023-07-11"}),2023)
        for year,day in (("23","2022-07-11"),("2023","2023-07-11"),
                         ("24","2024-07-11"),("","2023-07-11")):
            with self.subTest(year=year,day=day),self.assertRaisesRegex(
                ValueError,"SOURCE_V2_STOP"):
                source_verified_calendar_year({"YEAR":year,"DATE":day})

    def test_corrected_288_nights_3_verified_footers_and_PIT_match(self):
        z=corrected_source_only(synthetic_original_source(),{}, "metadata")
        self.assertEqual(z["status"],
            "CORRECTED_SOURCE_JOIN_GO_NOT_DETECTOR_OPERATION_OR_BIOLOGICAL_EFFECT")
        self.assertEqual(z["original_all_station_csv_rows_including_summaries"],291)
        self.assertEqual(z["original_verified_experimental_station_night_rows"],288)
        self.assertEqual(z["original_verified_summary_rows_not_observations"],3)
        self.assertEqual(z["capture_source_identity_census"]["all_11614_capture_YEAR_2DIGIT_DATE_verified"],11614)
        self.assertEqual(z["original_foraging_event_source_census"]["foraging_rows_exact_capture_PIT_GRID_DATE_YEAR_match"],3243)
        self.assertTrue(all(z["v2_original_source_only_admission_checks"].values()))
        self.assertTrue(z["original_v1_numerical_support_gates_unchanged"])
        self.assertEqual(z["original_station_rows_without_video_event_key"],152)

    def test_any_unverified_summary_row_fails_before_source_GO(self):
        z=synthetic_original_source()
        z["All Station Nights.csv"][-1]["WP.seeds.set"]="0.25"
        with self.assertRaisesRegex(ValueError,"Summary fraction"):
            corrected_source_only(z,{}, "meta")

    def test_unknown_extra_keyless_station_not_discarded_as_footer(self):
        z=synthetic_original_source()
        extra=copy.deepcopy(z["All Station Nights.csv"][0])
        extra.update({"Grid":"","Site":"","Session":"","Night":""})
        z["All Station Nights.csv"].insert(10,extra)
        with self.assertRaisesRegex(ValueError,"ORIGINAL_FIVE_CSV_ROWS_DRIFT"):
            corrected_source_only(z,{}, "meta")

    def test_bad_CAPTURE_YEAR_DATE_is_not_imputed(self):
        z=synthetic_original_source()
        z["2016-2023 Capture Data.csv"][0]["DATE"]="2022-07-11"
        with self.assertRaisesRegex(ValueError,"SOURCE_V2_STOP_ORIGINAL_CAPTURE_YEAR_AND_DATE"):
            corrected_source_only(z,{}, "meta")

    def test_nonmatching_capture_PIT_source_gives_source_STOP_not_biological_zero(self):
        z=synthetic_original_source()
        for row in z["All Foraging Clean.csv"]:
            row["PIT"]="no_capture_match"
        outcome=corrected_source_only(z,{}, "meta")
        self.assertEqual(outcome["status"],
            "CORRECTED_SOURCE_JOIN_STOP_THRESHOLD_OR_SOURCE_SUPPORT")
        self.assertFalse(outcome["v2_original_source_only_admission_checks"][
            "at_least_30_exact_capture_PIT_GRID_calendar_YEAR_matched_event_rows"])

    def test_date_shift_is_not_permitted_as_original_date_match(self):
        z=synthetic_original_source()
        for e in z["All Foraging Clean.csv"]:
            e["Date"]="2023-07-12"
        out=corrected_source_only(z,{}, "meta")
        self.assertEqual(out["status"],
            "CORRECTED_SOURCE_JOIN_STOP_THRESHOLD_OR_SOURCE_SUPPORT")
        self.assertEqual(out["original_foraging_event_source_census"][
            "source_event_and_station_dates_NOT_EQUAL"],3243)
        self.assertEqual(out["source_date_exact_equality_ratio"],0)

    def test_mouse_and_vole_views_not_added_as_independent_events(self):
        z=corrected_source_only(synthetic_original_source(),{}, "meta")
        self.assertEqual(z["original_foraging_event_source_census"][
            "all_foraging_rows_with_exact_source_station_night"],3243)
        self.assertEqual(z["mouse_view_is_subset_source"]["original_view_source_rows"],883)
        self.assertEqual(z["vole_view_is_subset_source"]["original_view_source_rows"],951)
        self.assertTrue(z["mouse_view_is_subset_source"][
            "overlapping_view_NOT_independent_observation_set"])

    def test_export_only_counts_never_pit_location_ids(self):
        import json
        z=corrected_source_only(synthetic_original_source(),{}, "meta")
        raw=json.dumps(z,sort_keys=True)
        for marker in ('"G0"','"S0"','"0001"','"v3000"'):
            self.assertNotIn(marker,raw)
        self.assertTrue(z["no_spatial_occupancy_or_mammal_niche_resource_learning_model"])
        self.assertTrue(z["one_NEON_ecological_manuscript_Draft_SUBMISSION_HOLD"])

if __name__=="__main__":
    unittest.main()
