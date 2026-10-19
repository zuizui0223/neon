"""Synthetic RED/GREEN tests for real-source-ready U-adjusted predictor geometry.

No NEON individual, response W/B, trap coordinate or biological coefficient.
Tests only the precommitted fixed-total source-only estimand.
"""
import unittest

from analysis.audit_neon_u_adjusted_fixed_total_support_v1 import (
    fixed_total_genus_support,
)


def mock_rows(site_count=8, n_events=12, *, collinear_u=False, constant_u=False):
    out=[]
    for g in range(site_count):
        site=f"TEST_SITE_{g}"
        for event in range(n_events):
            focal=5+(3*g+2*event)%7
            other=2+(g+3*event)%6
            unknown=(focal if collinear_u else
                     4 if constant_u else 1+(2*g+4*event)%5  # U varies within site, not solely across site FE)
            out.append({
                "site":site,
                "genus":"Peromyscus",
                "taxon":"PEMA",
                "plot_id":"P",
                "event_id":f"E{event}",
                "year":str(2020+event%3),
                "site_month":f"{site}|07",
                "series_id":f"PEMA|{site}|P",
                "N":focal+other+unknown,
                "F":focal,"C":other,"U":unknown,
                "strictly_resolved_response_taxon":True,
            })
    return out


def frozen_go(sessions=96,sites=8,series=8,joint=8):
    return {
        "state":"PREDICTOR_ONLY_POTENTIALLY_IDENTIFIABLE",
        "species_sessions_in_3plus_series":sessions,
        "sites_in_3plus_series":sites,
        "species_series_with_3plus_sessions":series,
        "series_joint_F_C_variation":joint,
    }


class FixedTotalSourceTests(unittest.TestCase):
    def test_independent_N_F_U_contrast_is_identifiable_at_multiple_sites(self):
        d=fixed_total_genus_support(mock_rows(),genus="Peromyscus",
                                    previous_frozen_support=frozen_go())
        self.assertEqual(d["rank_FC_after_nuisance_and_U"],2)
        self.assertEqual(d["rank_FCU_after_nuisance"],3)
        self.assertTrue(d["fixed_total_replacement_contrast_estimable"])
        self.assertTrue(d["U_adjusted_predictor_only_candidate"])
        self.assertGreater(d["fixed_total_replacement_residual_SS"],0)
        site=d["fixed_total_information_by_site"]
        self.assertEqual(site["original_physical_sites"],8)
        self.assertGreater(site["effective_site_count_descriptive"],1)
        self.assertLessEqual(site["effective_site_count_descriptive"],8.00001)
        self.assertGreaterEqual(site["top_three_site_information_fraction"],site["top_one_site_information_fraction"])
        self.assertAlmostEqual(sum(v for v in site["information_share_distribution"]),1,places=8)
        self.assertFalse(d["W_B_or_ecological_effects_opened"])

    def test_U_equals_F_erases_conditional_fixed_total_substitution(self):
        d=fixed_total_genus_support(mock_rows(collinear_u=True),
                                    genus="Peromyscus",
                                    previous_frozen_support=frozen_go())
        self.assertEqual(d["rank_FC_after_nuisance"],2)
        self.assertEqual(d["rank_FC_after_nuisance_and_U"],1)
        self.assertFalse(d["fixed_total_replacement_contrast_estimable"])
        self.assertFalse(d["U_adjusted_predictor_only_candidate"])

    def test_constant_unknown_is_absorbed_and_does_not_cause_false_stop(self):
        d=fixed_total_genus_support(mock_rows(constant_u=True),
                                    genus="Peromyscus",
                                    previous_frozen_support=frozen_go())
        self.assertEqual(d["rank_FC_after_nuisance_and_U"],2)
        self.assertTrue(d["fixed_total_replacement_contrast_estimable"])
        self.assertTrue(d["U_adjusted_predictor_only_candidate"])

    def test_frozen_source_cohort_count_change_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"frozen session denominator"):
            fixed_total_genus_support(mock_rows(),genus="Peromyscus",
                                      previous_frozen_support=frozen_go(sessions=95))

    def test_duplicate_taxon_plot_event_is_rejected(self):
        rows=mock_rows()
        rows.append(rows[0].copy())
        with self.assertRaisesRegex(ValueError,"duplicate.*session"):
            fixed_total_genus_support(rows,genus="Peromyscus",
                                      previous_frozen_support=frozen_go())

    def test_W_or_B_payload_is_rejected_before_model(self):
        for col in ("W_m2","B_debiased_m2","D_m2","centroids","trapCoordinate"):
            rows=mock_rows()
            rows[0][col]=42
            with self.subTest(field=col):
                with self.assertRaisesRegex(ValueError,"spatial response"):
                    fixed_total_genus_support(rows,genus="Peromyscus",
                                              previous_frozen_support=frozen_go())

    def test_total_identity_must_be_exact(self):
        rows=mock_rows()
        rows[0]["N"]+=1
        with self.assertRaisesRegex(ValueError,"N=F\\+C\\+U"):
            fixed_total_genus_support(rows,genus="Peromyscus",
                                      previous_frozen_support=frozen_go())

    def test_prior_non_candidate_cannot_be_promoted(self):
        prior=frozen_go()
        prior["state"]="PREDICTOR_ONLY_STRUCTURAL_LIMIT"
        d=fixed_total_genus_support(mock_rows(),genus="Peromyscus",
                                    previous_frozen_support=prior)
        self.assertFalse(d["U_adjusted_predictor_only_candidate"])
        self.assertTrue(d["fixed_total_replacement_contrast_estimable"])

    def test_physical_site_ids_and_event_ids_not_exposed(self):
        d=fixed_total_genus_support(mock_rows(),genus="Peromyscus",
                                    previous_frozen_support=frozen_go())
        self.assertNotIn("TEST_SITE_",str(d))
        self.assertNotIn("E11",str(d))
        self.assertNotIn("PEMA",str(d))

    def test_input_order_does_not_change_primary_support(self):
        rows=mock_rows()
        x=fixed_total_genus_support(rows,genus="Peromyscus",
                                    previous_frozen_support=frozen_go())
        y=fixed_total_genus_support(list(reversed(rows)),genus="Peromyscus",
                                    previous_frozen_support=frozen_go())
        for key in ("U_adjusted_predictor_only_candidate",
                    "rank_FC_after_nuisance_and_U",
                    "fixed_total_replacement_contrast_estimable"):
            self.assertEqual(x[key],y[key])
        self.assertAlmostEqual(x["fixed_total_replacement_residual_SS"],
                               y["fixed_total_replacement_residual_SS"],places=6)

if __name__=="__main__":
    unittest.main()
