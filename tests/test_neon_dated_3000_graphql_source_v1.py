"""Synthetic-only GraphQL-versus-REST source and 100×30 date gate tests.

All coordinates in this fixture are fake. Never opens the already
consumed NEON mammal genus spatial ecological response.
"""
from datetime import date
import unittest

from analysis.neon_graphql_dated_station_source_v1 import (
    GRAPHQL_QUERY, batch_names, parse_graphql_locations,
    canonical_station_history_for_comparison,
    validate_history_projection,
    summarize_full_station_dated_coverage,
)
from analysis.neon_graphql_source_diagnostic_v1 import (
    source_stop_receipt, SOURCE_PHASES, 
    safe_rest_graphql_diff_groups, summarize_preflight_diff_groups,
)


def record(u="2020-01-01",end=None,x=500123.,unc="1.5"):
    return {
        "current":True,"locationStartDate":u,"locationEndDate":end,
        "locationUtmEasting":x,"locationUtmNorthing":4200123.,
        "locationUtmZone":12,"locationUtmHemisphere":"N",
        "locationProperties":[
            {"locationPropertyName":"Value for Geodetic datum","locationPropertyValue":"WGS84"},
            {"locationPropertyName":"Value for Coordinate uncertainty","locationPropertyValue":unc},
        ],
    }


def document(name,hist=None):
    return {
        "locationName":name,
        "locationUtmZone":12,"locationUtmHemisphere":"N",
        "locationHistory":hist if hist is not None else [record()],
        "locationProperties":[
            {"locationPropertyName":"Value for Geodetic datum","locationPropertyValue":"WGS84"},
        ],
    }


def private_unit(site="TESTSITE",plot="P",start=date(2022,4,2),b=date(2022,7,2)):
    return {
        "site":site,"site_plot":(site,plot),"season_ordinal":8089,
        "capture_dates_A":(start,date(2022,4,3),date(2022,4,4)),
        "capture_dates_B":(b,date(2022,7,3),date(2022,7,4)),
    }


def names(site="TESTSITE",plot="P"):
    return {(site,plot,chr(65+i)+str(j)) for i in range(10) for j in range(1,11)}


def all100():
    return {(site,plot,station):document(site+"_"+plot+"."+station)
            for site,plot,station in names()}


class NEONGraphQLDateSourceTests(unittest.TestCase):
    def test_source_failure_phase_categorized_without_leaking_private_names(self):
        self.assertIn("REST_GRAPHQL_HISTORY_EQUIVALENCE",SOURCE_PHASES)
        o=source_stop_receipt(
            "REST_GRAPHQL_HISTORY_EQUIVALENCE",
            ValueError("BAD hidden source SITE.PLOT.A1 tag SECRET_ID token xyz"),
        )
        self.assertEqual(o["failure_stage"],"REST_GRAPHQL_HISTORY_EQUIVALENCE")
        self.assertEqual(o["error_class"],"ValueError")
        self.assertEqual(o["safe_reason_class"],"SOURCE_HISTORY_OR_COMPARISON_SCHEMA")
        self.assertNotIn("SITE.PLOT",str(o))
        self.assertNotIn("SECRET_ID",str(o))
        self.assertNotIn("xyz",str(o))

    def test_stop_reason_cannot_echo_arbitrary_unvalidated_stage(self):
        o=source_stop_receipt("SECRET_SOURCE_SITE",RuntimeError("privacy trap"))
        self.assertEqual(o["failure_stage"],"UNCLASSIFIED_SOURCE_PHASE")
        self.assertNotIn("SECRET",str(o))
        self.assertNotIn("privacy trap",str(o))

    def test_exact_approved_coverage_phase_is_preserved(self):
        o=source_stop_receipt("ALL_STATION_DATE_COVERAGE",
                              ValueError("Date projection refused"))
        self.assertEqual(o["failure_stage"],"ALL_STATION_DATE_COVERAGE")
        self.assertTrue(o["any_habitat_or_density_W_B_effect_computed"] is False)

    def test_source_api_diagnostic_groups_without_source_values(self):
        rest=document("SECRET.T.A1")
        gql=document("SECRET.T.A1")
        # Different current-field representation without changed date or XYZ.
        gql["locationHistory"][0]["current"]=None
        out=safe_rest_graphql_diff_groups(rest,gql)
        self.assertIn("HISTORY_CURRENT_FIELD",out)
        self.assertNotIn("SECRET",str(out))
        self.assertNotIn("500123",str(out))
        self.assertNotIn("2020-01-01",str(out))

        other=document("SECRET.T.A1",[record(x=500124.)])
        out=safe_rest_graphql_diff_groups(rest,other)
        self.assertIn("HISTORY_UTM_COORDINATES",out)
        self.assertNotIn("500124",str(out))

    def test_source_diagnostics_separate_properties_and_time(self):
        rest=document("SECRET.T.A1")
        gql=document("SECRET.T.A1")
        gql["locationProperties"][0]["locationPropertyValue"]="NAD83"
        gql["locationHistory"][0]["locationEndDate"]="2021-01-01T00:00:00Z"
        out=safe_rest_graphql_diff_groups(rest,gql)
        self.assertIn("ROOT_LOCATION_PROPERTIES",out)
        self.assertIn("HISTORY_VALIDITY_INTERVAL",out)
        self.assertNotIn("NAD83",str(out))
        self.assertNotIn("2021",str(out))

    def test_identical_source_equivalence_diff_is_empty(self):
        rest=document("SECRET.T.A1")
        gql=document("SECRET.T.A1")
        self.assertEqual(safe_rest_graphql_diff_groups(rest,gql),[])
        agg=summarize_preflight_diff_groups([
            safe_rest_graphql_diff_groups(rest,gql),
            safe_rest_graphql_diff_groups(rest,document("SECRET.T.A1",
                                  [record(x=500300.)]))
        ])
        self.assertEqual(agg["source_documents_compared"],2)
        self.assertEqual(agg["source_documents_with_differences"],1)
        self.assertEqual(agg["safe_field_group_counts"]["HISTORY_UTM_COORDINATES"],1)
        for secret in ("SECRET","500300"):
            self.assertNotIn(secret,str(agg))

    def test_api_query_is_official_batched_findLocations_with_history(self):
        self.assertIn("findLocations(query: $query)",GRAPHQL_QUERY)
        self.assertIn("locationHistory",GRAPHQL_QUERY)
        self.assertIn("locationStartDate",GRAPHQL_QUERY)
        self.assertIn("locationProperties",GRAPHQL_QUERY)
        self.assertEqual([len(x) for x in batch_names([str(i) for i in range(3000)],500)],
                         [500]*6)
        with self.assertRaisesRegex(ValueError,"batch"):
            batch_names(["A"],1001)

    def test_gql_response_requires_exact_names_and_no_duplicate(self):
        q=["P.A1","P.A2"]
        response={"data":{"locations":[document("P.A1"),document("P.A2")]}}
        parsed=parse_graphql_locations(response,q)
        self.assertEqual(set(parsed),set(q))
        with self.assertRaisesRegex(ValueError,"duplicate"):
            parse_graphql_locations({"data":{"locations":[document("P.A1"),document("P.A1")]}},q)
        with self.assertRaisesRegex(ValueError,"unexpected"):
            parse_graphql_locations({"data":{"locations":[document("P.X1")]}},q)
        with self.assertRaisesRegex(ValueError,"GraphQL errors"):
            parse_graphql_locations({"data":{},"errors":[{"message":"SECRET"}]},q)

    def test_equivalent_REST_and_GraphQL_histories_checked_semantically(self):
        g=document("TEST.P.A1")
        rest={"data":g}
        can1=canonical_station_history_for_comparison(g)
        can2=canonical_station_history_for_comparison(rest["data"])
        self.assertEqual(can1,can2)
        altered=document("TEST.P.A1",[record(x=500456.)])
        self.assertNotEqual(can1,canonical_station_history_for_comparison(altered))

    def test_history_is_required_no_root_current_fallback(self):
        d=document("T.P.A1")
        del d["locationHistory"]
        with self.assertRaisesRegex(ValueError,"history"):
            validate_history_projection(d,date(2022,4,2))
        d=document("T.P.A1",[record(u="2024-01-01")])
        with self.assertRaisesRegex(ValueError,"date-valid"):
            validate_history_projection(d,date(2022,4,2))

    def test_historic_projection_and_direct_uncertainty_are_finite(self):
        d=document("T.P.A1")
        info=validate_history_projection(d,date(2022,4,2))
        self.assertEqual(info["utm_epsg"],32612)
        self.assertEqual(info["direct_source_uncertainty_m"],1.5)
        self.assertEqual(info["xy"],(500123.,4200123.))
        d=document("T.P.A1",[record(unc="")])
        info=validate_history_projection(d,date(2022,4,2))
        self.assertIsNone(info["direct_source_uncertainty_m"])

    def test_all_100_anchors_source_valid_for_original_three_plus_three_dates(self):
        u=[private_unit()]
        report=summarize_full_station_dated_coverage(
            u,all100(),expected_pairs=1,expected_sites=1,expected_plots=1,
            min_pairs=1,min_sites=1,min_plots=1,
        )
        self.assertEqual(report["fixed_original_station_date_attempts"],600)
        self.assertEqual(report["historically_projected_valid_attempts"],600)
        self.assertEqual(report["plots_with_at_least_95_positions_valid_every_source_day"],1)
        self.assertEqual(report["pairs_with_at_least_95_station_positions_valid_every_day"],1)
        self.assertEqual(report["status"],"FULL_100_STATION_CAPTURE_DATE_SOURCE_GO")
        self.assertFalse(report["genus_habitat_ecological_effect_estimated"])

    def test_missing_station_is_reported_but_not_imputed_from_four_corners(self):
        data=all100()
        data[("TESTSITE","P","A1")]=None
        u=[private_unit()]
        report=summarize_full_station_dated_coverage(
            u,data,expected_pairs=1,expected_sites=1,expected_plots=1,
            min_pairs=1,min_sites=1,min_plots=1
        )
        self.assertEqual(report["historically_projected_valid_attempts"],594)
        self.assertEqual(report["station_name_documents_unavailable"],1)
        self.assertEqual(report["plots_with_at_least_95_positions_valid_every_source_day"],1)
        self.assertEqual(report["pairs_with_at_least_95_station_positions_valid_every_day"],1)
        self.assertFalse(report["unknown_positions_reconstructed_from_grid_geometry"])

    def test_no_e5_monument_U_causes_adjusted_uncertainty_stop(self):
        data=all100()
        for d in data.values():
            d["locationHistory"][0]["locationProperties"]=[
                {"locationPropertyName":"Value for Geodetic datum","locationPropertyValue":"WGS84"},
            ]
        out=summarize_full_station_dated_coverage(
            [private_unit()],data,expected_pairs=1,expected_sites=1,expected_plots=1,
            min_pairs=1,min_sites=1,min_plots=1
        )
        self.assertEqual(out["source_dates_without_direct_monument_uncertainty"],6)
        self.assertEqual(out["dates_with_full_geoNEON_assumed_uncertainty"],0)
        self.assertFalse(out["unreported_uncertainty_assumed_zero"])

    def test_duplicate_names_and_real_identifiers_not_exported(self):
        data=all100()
        data[("TESTSITE","P","B1")]=data[("TESTSITE","P","A1")]
        with self.assertRaisesRegex(ValueError,"location identity"):
            summarize_full_station_dated_coverage(
                [private_unit()],data,expected_pairs=1,expected_sites=1,expected_plots=1,
                min_pairs=1,min_sites=1,min_plots=1
            )
        report=summarize_full_station_dated_coverage(
            [private_unit()],all100(),expected_pairs=1,expected_sites=1,expected_plots=1,
            min_pairs=1,min_sites=1,min_plots=1
        )
        for literal in ("TESTSITE","TESTSITE_P.A1","2022-04-02","500123","A10"):
            self.assertNotIn(literal,str(report))
        self.assertTrue(report["source_geographic_and_animal_ids_not_exported"])

if __name__=="__main__":
    unittest.main()
