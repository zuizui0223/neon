"""Synthetic-only tests for literal same-N same-U composition comparisons.

No spatial W/B, no animal IDs, no real NEON per-event output is consumed.
"""
import unittest

from analysis.audit_neon_fixed_total_observed_pairs_v1 import (
    observed_fixed_total_pairs,
)


def record(site,event,month,F,U=2,N=10,year="2020",taxon="PEMA"):
    return {
        "genus":"Peromyscus",
        "taxon":taxon,
        "site":site,"plot_id":"P","event_id":event,
        "year":year,"site_month":f"{site}|{month}",
        "series_id":f"{taxon}|{site}|P",
        "F":F,"C":N-F-U,"U":U,"N":N,
        "strictly_resolved_response_taxon":True,
    }


def rows():
    return [
        record("SITE_A","E1","07",3,year="2020"),
        record("SITE_A","E2","07",4,year="2021"),
        record("SITE_A","E3","07",3,year="2022"),
        record("SITE_B","E4","06",2,year="2020"),
        record("SITE_B","E5","07",3,year="2021"),
        record("SITE_B","E6","08",2,year="2022"),
    ]


def frozen():
    return {
        "state":"PREDICTOR_ONLY_POTENTIALLY_IDENTIFIABLE",
        "species_sessions_all":6,
        "species_sessions_in_3plus_series":6,
        "sites_in_3plus_series":2,
        "species_series_with_3plus_sessions":2,
    }


class FixedTotalPairsTests(unittest.TestCase):
    def test_literal_equal_N_U_same_month_matches_only_F_changes(self):
        out=observed_fixed_total_pairs(rows(),genus="Peromyscus",
                                       previous_frozen_support=frozen())
        primary=out["primary_same_calendar_month"]
        self.assertEqual(primary["qualifying_contexts"],1)
        self.assertEqual(primary["distinct_event_pairs"],2)
        self.assertEqual(primary["physical_sites_with_pairs"],1)
        self.assertEqual(primary["sessions_in_matched_contexts"],3)
        self.assertEqual(primary["absolute_F_change_median"],1.)
        self.assertFalse(out["no_literal_same_season_fixed_total_pair"])

    def test_broader_cross_season_match_must_be_labelled_noncomparable(self):
        out=observed_fixed_total_pairs(rows(),genus="Peromyscus",
                                       previous_frozen_support=frozen())
        broad=out["broader_within_series_any_season"]
        self.assertEqual(broad["qualifying_contexts"],2)
        self.assertEqual(broad["distinct_event_pairs"],4)
        self.assertEqual(broad["physical_sites_with_pairs"],2)
        self.assertEqual(out["additional_cross_season_pairs"],2)
        self.assertTrue(broad["seasonally_not_equivalent_to_primary"])

    def test_all_same_f_composition_has_no_direct_evidence(self):
        rr=rows()
        for r in rr:r["F"]=3;r["C"]=r["N"]-r["U"]-3
        out=observed_fixed_total_pairs(rr,genus="Peromyscus",
                                       previous_frozen_support=frozen())
        self.assertEqual(out["primary_same_calendar_month"]["distinct_event_pairs"],0)
        self.assertTrue(out["no_literal_same_season_fixed_total_pair"])

    def test_different_U_does_not_count_as_equal_total_composition_swap(self):
        rr=rows()
        rr[1]["U"]=3;rr[1]["C"]=rr[1]["N"]-rr[1]["F"]-rr[1]["U"]
        out=observed_fixed_total_pairs(rr,genus="Peromyscus",
                                       previous_frozen_support=frozen())
        self.assertEqual(out["primary_same_calendar_month"]["distinct_event_pairs"],0)
        self.assertFalse(out["primary_same_calendar_month"]["qualifying_contexts"])

    def test_frozen_cohort_drift_is_rejected(self):
        prior=frozen();prior["species_sessions_in_3plus_series"]=5
        with self.assertRaisesRegex(ValueError,"denominator"):
            observed_fixed_total_pairs(rows(),genus="Peromyscus",
                                       previous_frozen_support=prior)

    def test_no_sites_taxa_events_or_species_counts_are_exported(self):
        out=observed_fixed_total_pairs(rows(),genus="Peromyscus",
                                       previous_frozen_support=frozen())
        for private in ("SITE_A","SITE_B","E1","E2","E6","PEMA"):
            self.assertNotIn(private,str(out))
        self.assertFalse(out["ecological_W_B_effects_opened"])
        self.assertTrue(out["no_original_site_or_event_ids_exported"])

    def test_order_invariant_pair_counts(self):
        original=observed_fixed_total_pairs(rows(),genus="Peromyscus",
                                            previous_frozen_support=frozen())
        reverse=observed_fixed_total_pairs(list(reversed(rows())),genus="Peromyscus",
                                           previous_frozen_support=frozen())
        self.assertEqual(original,reverse)


if __name__=="__main__":
    unittest.main()
