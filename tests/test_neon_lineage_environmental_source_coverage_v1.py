"""Synthetic source-only tests for independent NEON habitat-layer site coverage.

No animal movement, trap coordinates, original genus recurrence or
vegetation/habitat ecological effects enter these tests.
"""
import unittest
from analysis.audit_neon_lineage_environmental_source_coverage_v1 import (
    summarize_habitat_product_site_coverage, GEO_LOCATION_ISSUE_SITES
)


class HabitatSourceSiteCoverageTests(unittest.TestCase):
    def test_source_site_products_and_geolocation_issue_intersection(self):
        source={f"S{i:03d}" for i in range(14)}
        metas={
            "DP3.30015.001":set(list(sorted(source))[:12]),
            "DP1.10098.001":source,
            "DP1.10058.001":set(list(sorted(source))[:11]),
        }
        issues={"S001","S004","OTHER"}
        out=summarize_habitat_product_site_coverage(source,metas,issues)
        self.assertEqual(out["fixed_original_neon_ecology_sites"],14)
        self.assertEqual(out["metadata_chm_1m_sites"],12)
        self.assertEqual(out["metadata_vegetation_structure_sites"],14)
        self.assertEqual(out["metadata_plant_cover_sites"],11)
        self.assertEqual(out["known_geoneon_location_issue_sites_in_ecology_cohort"],2)
        self.assertEqual(out["advertised_all_three_products_sites"],11)
        self.assertFalse(out["trap_scale_habitat_covariate_links_verified"])

    def test_unknown_product_or_empty_original_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"original"):
            summarize_habitat_product_site_coverage(set(),{},set())
        with self.assertRaisesRegex(ValueError,"mandatory products"):
            summarize_habitat_product_site_coverage(
                {"S001"},{"DP3.30015.001":{"S001"}},set()
            )

    def test_site_codes_are_not_exported(self):
        source={"SECRET_SITE_1","SECRET_SITE_2"}
        out=summarize_habitat_product_site_coverage(
            source,{
                "DP3.30015.001":source,
                "DP1.10098.001":source,
                "DP1.10058.001":source,
            },{"SECRET_SITE_1"}
        )
        self.assertNotIn("SECRET_SITE",str(out))
        self.assertFalse(out["environmental_mechanism_test_opened"])
        self.assertFalse(out["W_B_density_ecological_effect_opened"])

    def test_geolocation_issue_codes_are_the_published_seven_not_newly_selected(self):
        self.assertEqual(GEO_LOCATION_ISSUE_SITES,{
            "BLAN","HEAL","KONZ","MOAB","ONAQ","SERC","TEAK",
        })
        self.assertFalse(summarize_habitat_product_site_coverage(
            {"BLAN","BART"},
            {"DP3.30015.001":{"BLAN","BART"},
             "DP1.10098.001":{"BLAN","BART"},
             "DP1.10058.001":{"BLAN","BART"}},
            GEO_LOCATION_ISSUE_SITES)["nominal_grid_result_invalidated_by_geolocation_issue"])

if __name__=="__main__":
    unittest.main()
