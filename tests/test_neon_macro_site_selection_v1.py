"""Purely synthetic tests of the NEON macrogeographic inclusion mechanism.

These tests do not open ecological effects or identifiers.
"""
import json
import unittest
from datetime import date,timedelta

from analysis.audit_neon_crossseason_genus_support_v1 import season_ordinal
from analysis.neon_macro_site_selection_v1 import (
    site_metadata_index,audit_geographic_selection,latitude_band
)


def fixture():
    plots=[]
    traps=[]
    units=[]
    for site in ("FAKESITE_A","FAKESITE_B"):
        plot=site+"_1"
        for q,d0 in enumerate((date(2025,3,1),date(2025,6,1))):
            event=site+"_"+str(q)
            for dayindex in range(3):
                day=d0+timedelta(days=dayindex)
                n=event+"_N"+str(dayindex)
                plots.append({
                    "_site":site,"siteID":site,
                    "plotID":plot,"eventID":event,
                    "nightuid":n,"collectDate":day.isoformat(),
                    "gridCompletion":"setting complete, processing complete",
                })
                for row in "ABCDEFGHIJ":
                    for col in range(1,11):
                        traps.append({
                            "_site":site,"plotID":plot,
                            "nightuid":n,"trapCoordinate":row+str(col),
                        })
        if site=="FAKESITE_A":
            units.append({
                "site":site,"site_plot":(site,plot),
                "season_ordinal":season_ordinal(date(2025,3,1)),
            })
    metadata=site_metadata_index([
        {"siteCode":"FAKESITE_A","domainCode":"D01",
         "siteType":"CORE","siteLatitude":32.5},
        {"siteCode":"FAKESITE_B","domainCode":"D17",
         "siteType":"GRADIENT","siteLatitude":48.5},
    ])
    return plots,traps,units,metadata


def source_audit(data=None):
    plots,traps,units,metadata=(data or fixture())
    return audit_geographic_selection(
        plots,traps,units,metadata,
        expected_eligible_pairs=1,expected_eligible_sites=1,
        expected_effort_valid_events=4,expected_candidates=2,
    )


class MacroSourceSelectionTests(unittest.TestCase):
    def test_original_effort_and_geo_denominators(self):
        z=source_audit()
        self.assertEqual(z["status"],"SOURCE_ONLY_MACRO_SELECTION_RECONSTRUCTED")
        d=z["original_source_denominators"]
        self.assertEqual(d["effort_valid_three_night_bouts"],4)
        self.assertEqual(d["original_adjacent_season_pairs"],2)
        self.assertEqual(d["original_primary_three_genus_eligible_pairs"],1)
        self.assertEqual(d["physical_sites_with_one_or_more_candidate_pairs"],2)
        self.assertEqual(d["primary_independent_physical_sites"],1)
        self.assertEqual(d["primary_eligibility_fraction_of_candidates"],.5)

    def test_domain_and_latitude_inclusion_is_not_effect(self):
        z=source_audit()
        a=z["domain_grouped_source_only"]
        self.assertEqual(a["D01"]["source_adjacent_season_candidate_pairs"],1)
        self.assertEqual(a["D01"]["primary_eligible_pairs"],1)
        self.assertEqual(a["D17"]["primary_eligible_pairs"],0)
        self.assertEqual(a["D17"]["source_adjacent_season_candidate_pairs"],1)
        self.assertEqual(z["latitude_band_grouped_source_only"]["lt35"]["primary_eligible_pairs"],1)
        self.assertEqual(z["latitude_band_grouped_source_only"]["45to55"]["primary_eligible_pairs"],0)
        self.assertFalse(z["effect_boundary"]["macro_habitat_or_latitude_effect_fit"])
        self.assertTrue(z["effect_boundary"]["nonqualified_sites_not_declared_zero_recurrence"])

    def test_output_is_aggregate_and_has_no_fake_source_identity(self):
        z=source_audit()
        serialized=json.dumps(z,sort_keys=True)
        for secret in ("FAKESITE_A","FAKESITE_B","FAKESITE_A_1","2025-03-01"):
            self.assertNotIn(secret,serialized)
        self.assertFalse(z["effect_boundary"]["historical_recurrence_Z_or_p_read"])
        self.assertFalse(z["effect_boundary"]["historical_W_B_or_density_slopes_read"])

    def test_missing_official_site_metadata_stops(self):
        plot,traps,units,metadata=fixture()
        del metadata["FAKESITE_A"]
        with self.assertRaisesRegex(ValueError,"domain/latitude metadata"):
            source_audit((plot,traps,units,metadata))

    def test_locked_original_eligible_pair_must_be_subset(self):
        plot,traps,units,metadata=fixture()
        units[0]["season_ordinal"]+=2
        with self.assertRaisesRegex(ValueError,"candidate subset"):
            source_audit((plot,traps,units,metadata))

    def test_bad_raw_domain_or_latitude_stops(self):
        with self.assertRaisesRegex(ValueError,"domain missing"):
            site_metadata_index([{
                "siteCode":"FAKESITE_A","domainCode":"",
                "siteType":"CORE","siteLatitude":32.5,
            }])
        with self.assertRaisesRegex(ValueError,"latitude invalid"):
            latitude_band(200)

    def test_missing_station_effort_denominator_stops(self):
        plot,traps,units,metadata=fixture()
        # Eleven missing distinct station positions reduce one night to 89.
        missing={"A"+str(j) for j in range(1,11)} | {"B1"}
        traps=[r for r in traps if not(
            r["nightuid"]=="FAKESITE_B_0_N0"
            and r["trapCoordinate"] in missing)]
        with self.assertRaisesRegex(ValueError,"effort-complete bouts changed"):
            source_audit((plot,traps,units,metadata))


if __name__=="__main__":
    unittest.main()
