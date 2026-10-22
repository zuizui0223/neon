"""Synthetic source-history coverage tests for original three-night NEON events.

No real animal records, site IDs, geographic coordinates, habitat values or
the already-opened 14-site seasonal ecology response are processed.
"""
from datetime import date,timedelta
import unittest

from analysis.audit_neon_dated_five_anchor_feasibility_v1 import (
    summarize_five_anchor_date_history, select_original_location_history
)

ANCHORS=("A1","A10","J1","J10","E5")


def unit(site="FAKE_SITE_A",plot="P",season=8089,first="2023-04-02",next_date="2023-07-02"):
    a=date.fromisoformat(first)
    b=date.fromisoformat(next_date)
    return {
        "site":site,"site_plot":(site,plot),"season_ordinal":season,
        "capture_dates_A":tuple(a+timedelta(days=i) for i in range(3)),
        "capture_dates_B":tuple(b+timedelta(days=i) for i in range(3)),
    }


def full(plots):
    return {
        (site,plot,anchor):[{
            "locationStartDate":"2014-01-01T00:00:00Z",
            "locationEndDate":None,
            "current":True
        }]
        for site,plot in plots for anchor in ANCHORS
    }


def audit(units, histories, **kw):
    plots={u["site_plot"] for u in units}
    sites={u["site"] for u in units}
    return summarize_five_anchor_date_history(
        units,histories,
        expected_pairs=len(units),
        expected_sites=len(sites),
        expected_plots=len(plots),
        min_pairs=1,min_sites=1,min_plots=1,**kw,
    )


class OriginalCaptureDateLocationTests(unittest.TestCase):
    def test_raw_historical_array_must_match_source_named_location(self):
        d={"data":{"locationName":"A_001.mam.A1","locationHistory":[
            {"locationStartDate":"2010-01-01T00:00:00Z",
             "locationEndDate":None,"current":True}
        ]}}
        selected=select_original_location_history(d,"A_001.mam.A1")
        self.assertEqual(len(selected),1)
        with self.assertRaisesRegex(ValueError,"identity"):
            select_original_location_history(d,"B_001.mam.A1")
        with self.assertRaisesRegex(ValueError,"history"):
            select_original_location_history(
                {"data":{"locationName":"A_001.mam.A1"}},"A_001.mam.A1"
            )

    def test_all_5_source_named_anchors_valid_on_exact_6_dates(self):
        u=[unit()]
        history=full({u[0]["site_plot"]})
        r=audit(u,history)
        self.assertEqual(r["status"],"HISTORICAL_FIVE_ANCHOR_CAPTURE_DATE_SOURCE_GO")
        self.assertEqual(r["fixed_original_anchor_date_attempts"],30)
        self.assertEqual(r["anchor_date_valid"],30)
        self.assertEqual(r["all_five_anchors_valid_for_all_six_original_dates_pairs"],1)
        self.assertEqual(r["plots_fully_valid_for_all_included_capture_days"],1)
        self.assertEqual(r["sites_with_at_least_one_fully_valid_plot"],1)
        self.assertTrue(r["historical_capture_day_location_gate_passed"])
        self.assertFalse(r["habitat_genus_trap_ecological_effect_opened"])

    def test_latest_current_record_never_backfills_pre_start_year(self):
        u=[unit(first="2018-04-02",next_date="2018-07-02")]
        hist=full({u[0]["site_plot"]})
        hist[(u[0]["site"],"P","A1")]=[
            {"locationStartDate":"2020-01-01","locationEndDate":None,"current":True}
        ]
        r=audit(u,hist)
        self.assertEqual(r["anchor_date_valid"],24)
        self.assertEqual(r["failure_categories"]["NO_DATE_VALID_HISTORY"],6)
        self.assertEqual(r["all_five_anchors_valid_for_all_six_original_dates_pairs"],0)
        self.assertEqual(r["status"],"STOP_HISTORICAL_FIVE_ANCHOR_DATE_SUPPORT")
        self.assertFalse(r["used_current_coordinates_outside_historical_interval"])

    def test_multiple_source_histories_crossing_a_date_are_ambiguous(self):
        u=[unit()]
        hist=full({u[0]["site_plot"]})
        hist[(u[0]["site"],"P","E5")]=[
            {"locationStartDate":"2020-01-01","locationEndDate":None},
            {"locationStartDate":"2022-01-01","locationEndDate":None},
        ]
        r=audit(u,hist)
        self.assertEqual(r["failure_categories"]["AMBIGUOUS_DATE_VALID_HISTORY"],6)
        self.assertEqual(r["anchor_date_valid"],24)

    def test_no_history_is_missing_not_zero_uncertainty(self):
        u=[unit()]
        hist=full({u[0]["site_plot"]})
        hist[(u[0]["site"],"P","A10")]=None
        r=audit(u,hist)
        self.assertEqual(r["failure_categories"]["NO_LOCATION_HISTORY"],6)
        self.assertEqual(r["anchor_date_valid"],24)

    def test_multiple_pairs_same_plot_count_attempts_not_unique_animals(self):
        u=[unit(),unit(season=8090,first="2023-07-02",next_date="2023-10-02")]
        hist=full({u[0]["site_plot"]})
        r=audit(u,hist)
        self.assertEqual(r["fixed_original_anchor_date_attempts"],60)
        self.assertEqual(r["all_five_anchors_valid_for_all_six_original_dates_pairs"],2)
        self.assertEqual(r["plots_fully_valid_for_all_included_capture_days"],1)
        self.assertEqual(r["plots"],1)
        self.assertTrue(r["reused_capture_dates_are_attempts_not_independent_animals"])

    def test_missing_original_dates_fails_closed(self):
        u=[unit()]
        u[0]["capture_dates_B"]=(date(2023,7,2),)
        with self.assertRaisesRegex(ValueError,"three"):
            audit(u,full({u[0]["site_plot"]}))

    def test_no_original_site_plot_or_exact_capture_day_in_public_output(self):
        u=[unit()]
        r=audit(u,full({u[0]["site_plot"]}))
        for private in ("FAKE_SITE_A","2023-04-02","2023-07-02","A10"):
            self.assertNotIn(private,str(r))
        self.assertTrue(r["no_original_site_plot_anchor_date_or_animal_ids_exported"])

    def test_predeclared_threshold_is_not_rewritten_for_poor_coverage(self):
        u=[unit()]
        p=full({u[0]["site_plot"]})
        r=summarize_five_anchor_date_history(
            u,p,expected_pairs=1,expected_sites=1,expected_plots=1,
            min_pairs=40,min_sites=8,min_plots=20,
        )
        self.assertEqual(r["status"],"STOP_HISTORICAL_FIVE_ANCHOR_DATE_SUPPORT")
        self.assertFalse(r["historical_capture_day_location_gate_passed"])

if __name__=="__main__":
    unittest.main()
