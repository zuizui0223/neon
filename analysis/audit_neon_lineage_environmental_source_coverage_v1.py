"""Source-only habitat availability; no outcome, spatial fit or animal IDs.

Implements the existing four-test contract without changing the corrected
recurrence analysis. Site-level metadata is not trap-level habitat coverage.
The issue roster is published by NEON; affected sites are not excluded
wholesale because the actual issue pertains to eighteen named grids.
"""
from __future__ import annotations
from collections.abc import Mapping, Set

PRODUCTS = {
    'DP3.30015.001': 'metadata_chm_1m_sites',
    'DP1.10098.001': 'metadata_vegetation_structure_sites',
    'DP1.10058.001': 'metadata_plant_cover_sites',
}
GEO_LOCATION_ISSUE_GRIDS = frozenset({
    'BLAN_003','HEAL_002','HEAL_010','HEAL_014','HEAL_016','HEAL_031',
    'HEAL_033','HEAL_034','KONZ_006','MOAB_008','ONAQ_003','ONAQ_004',
    'ONAQ_005','ONAQ_019','ONAQ_020','ONAQ_023','SERC_011','TEAK_004',
})
GEO_LOCATION_ISSUE_SITES = {p.split('_')[0] for p in GEO_LOCATION_ISSUE_GRIDS}


def _valid_codes(values, description):
    if not isinstance(values, Set) or isinstance(values, (str, bytes)):
        raise ValueError(description+' must be a set of source identifiers')
    if any(not isinstance(v,str) or not v.strip() or v!=v.strip() for v in values):
        raise ValueError(description+' contains invalid identifiers')
    return set(values)


def summarize_habitat_product_site_coverage(original_sites, product_sites, issue_sites):
    """Return only aggregate intersections, never source site identifiers."""
    original = _valid_codes(original_sites, 'original sites')
    if not original:
        raise ValueError('original sites must not be empty')
    if not isinstance(product_sites, Mapping) or set(product_sites)!=set(PRODUCTS):
        raise ValueError('mandatory products must be exactly the three declared habitat products')
    supplied={p:_valid_codes(product_sites[p],'product site metadata') for p in PRODUCTS}
    issues = _valid_codes(issue_sites, 'issue sites')
    common=original.intersection(*(supplied[p] for p in PRODUCTS))
    return {
        'schema':'neon.lineage.habitat_product_site_coverage.v1',
        'fixed_original_neon_ecology_sites':len(original),
        **{field:len(original&supplied[p]) for p,field in PRODUCTS.items()},
        'advertised_all_three_products_sites':len(common),
        'known_geoneon_location_issue_sites_in_ecology_cohort':len(original&issues),
        'trap_scale_habitat_covariate_links_verified':False,
        'environmental_mechanism_test_opened':False,
        'W_B_density_ecological_effect_opened':False,
        'nominal_grid_result_invalidated_by_geolocation_issue':False,
        'metadata_availability_is_not_raster_pixel_or_temporal_coverage':True,
        'site_identifiers_exported':False,
    }
