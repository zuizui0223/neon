#!/usr/bin/env python3
"""Retrospective Finland vole spatial-dyad falsification: independent site fidelity.

Previously opened identity-label-shuffle rho is not a test beyond individual
site fidelity. This script compares the fixed same-tag, same-pair response
to stationary *within-tag* source-trap preferences, keeping all source counts.
No social contact or true movement is measured.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from random import Random
from statistics import mean, median
import json

from analysis.run_neon_external_bank_vole_centroid_v1 import (
    FACTOR_CELLS, SOURCE_COMMIT, SOURCE_FILES, centroid, original_csv,
    original_data, require,
)
from analysis.run_neon_bank_vole_dyad_geometry_v1 import (
    pair_distances, pearson_ranks, source_and_site_centroids,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/neon_bank_vole_individual_stationarity_20261115.json"
PROTOCOL = "docs/NEON_VOLE_DYAD_INDIVIDUAL_STATIONARITY_NULL_FROZEN_20261115.md"
RNG_SEED = 2026111567
PERMUTATIONS = 2000
MIN_ESTIMABLE_NULLS = 1900
SITE_BOOTSTRAPS = 5000
EXPECTED_SITES = 10
EXPECTED_ANIMALS_AT_SITES = 47
EXPECTED_DYADS = 102
STAGE = "CHECKSUM_PINNED_SOURCE"

def fixed_identity_observed_rho(summer, fall):
    """Same pair identities, tie-aware rank correlation."""
    require(len(summer) == len(fall) and len(summer) >= 3, "SITE_AT_LEAST_THREE_ANIMALS")
    return pearson_ranks(pair_distances(summer), pair_distances(fall))

def stationary_individual_rho(obs_by_individual, rng):
    """ONE replicate: shuffle season labels separately for EACH individual.

    obs_by_individual: [(summer captured xy list, fall captured xy list), ...]
    Pooled trap coordinates, repeats and per-season sample size remain fixed.
    """
    a, b = [], []
    for summer, fall in obs_by_individual:
        require(len(summer) >= 2 and len(fall) >= 2, "FROZEN_TWO_EACH")
        coords = list(summer) + list(fall)
        rng.shuffle(coords)
        a.append(centroid(coords[:len(summer)]))
        b.append(centroid(coords[len(summer):]))
    return fixed_identity_observed_rho(a, b)

def original_fixed_cohort():
    """Validate exact prior 51/12 source cohort and recover original per-ID xy."""
    global STAGE
    prior, assignments, census = source_and_site_centroids()
    records, headers = original_csv(
        original_data("fulltrap21_volecapturedata.csv"),
        ("year", "season", "site", "tag", "trap", "x", "y")
    )
    require(len(records) == 2012 and census["same_frozen_51_tags"] == 51
            and census["original_12_sampling_sites"] == 12
            and census["source_station_name_to_coordinate_identities"] == 563,
            "ORIGINAL_SOURCE_CENSUS")
    observed = defaultdict(lambda: {"summer": [], "fall": []})
    for row in records:
        site, tag, season = (
            (row["site"] or "").strip(), (row["tag"] or "").strip(),
            (row["season"] or "").strip()
        )
        require(row["year"] == "2021" and season in ("summer", "fall")
                and site and tag, "ORIGINAL_SEASON_AND_IDENTITIES")
        try:
            xy = (float(row["x"]), float(row["y"]))
        except (TypeError, ValueError):
            raise ValueError("SOURCE_NON_NUMERIC_XY") from None
        require(all(isfinite(z) for z in xy), "FINITE_SOURCE_POSITION")
        observed[(site, tag)][season].append(xy)
    require(len(observed) == 742, "FROZEN_742_KEYS")
    prior_keys = {(site, tag) for site, rows in prior.items() for tag, _, _ in rows}
    selected = {
        key: coords for key, coords in observed.items()
        if min(len(coords["summer"]), len(coords["fall"])) >= 2
    }
    require(len(selected) == 51 and set(selected) == prior_keys,
            "EXACT_ORIGINAL_FIFTY_ONE")
    out = defaultdict(list)
    for site, rows in sorted(prior.items()):
        for tag, summer_cent, fall_cent in rows:
            original = selected[(site, tag)]
            calc_s, calc_f = centroid(original["summer"]), centroid(original["fall"])
            require(all(abs(a - b) < 1e-10 for a, b in zip(calc_s, summer_cent))
                    and all(abs(a - b) < 1e-10 for a, b in zip(calc_f, fall_cent)),
                    "ORIGINAL_SAME_SITE_TAG_CENTROIDS")
            out[site].append((original["summer"], original["fall"]))
    eligible = {}
    by_cell = defaultdict(list)
    for site, entries in sorted(out.items()):
        if len(entries) < 3:
            continue
        a = [centroid(s) for s, _ in entries]
        b = [centroid(f) for _, f in entries]
        if min(len({round(d, 10) for d in pair_distances(a)}),
               len({round(d, 10) for d in pair_distances(b)})) < 3:
            continue
        eligible[site] = entries
        by_cell[assignments[site]].append(site)
    dyads = sum(len(v) * (len(v) - 1) // 2 for v in eligible.values())
    require(len(eligible) == EXPECTED_SITES
            and sum(len(x) for x in eligible.values()) == EXPECTED_ANIMALS_AT_SITES
            and dyads == EXPECTED_DYADS
            and all(len(by_cell[c]) >= 2 for c in FACTOR_CELLS)
            and sorted(len(by_cell[c]) for c in FACTOR_CELLS) == [2, 2, 3, 3],
            "EXACT_FROZEN_10_SITE_47_ANIMAL_102_DYAD_COHORT")
    STAGE = "FROZEN_TEN_SITE_COHORT_VERIFIED"
    return eligible, by_cell, census

def percentile95(values):
    v = sorted(values)
    return [v[int(0.025 * len(v))], v[int(0.975 * len(v))-1]]

def run():
    global STAGE
    cohort, by_cell, census = original_fixed_cohort()
    STAGE = "INDIVIDUAL_STATIONARITY_NULL"
    rng = Random(RNG_SEED)
    per_site = {}
    for site, entries in sorted(cohort.items()):
        summer = [centroid(s) for s, _ in entries]
        fall = [centroid(f) for _, f in entries]
        observed = fixed_identity_observed_rho(summer, fall)
        valid = []
        invalid = 0
        for _ in range(PERMUTATIONS):
            try:
                valid.append(stationary_individual_rho(entries, rng))
            except ValueError:
                invalid += 1
        require(len(valid) >= MIN_ESTIMABLE_NULLS,
                "SITE_NULL_DEGENERACY_OVER_5_PERCENT")
        per_site[site] = {
            "observed": observed, "null": mean(valid),
            "residual": observed - mean(valid), "valid": len(valid),
            "invalid": invalid,
        }
    STAGE = "SITE_STRATIFIED_BOOTSTRAP"
    values = list(per_site.values())
    residuals = [x["residual"] for x in values]
    bootstrap = []
    for _ in range(SITE_BOOTSTRAPS):
        chosen = []
        for group in FACTOR_CELLS:
            sites = sorted(by_cell[group])
            chosen.extend(per_site[sites[rng.randrange(len(sites))]]["residual"]
                          for _ in range(len(sites)))
        bootstrap.append(mean(chosen))
    return {
        "schema": "neon.external_vole_dyad_individual_stationarity_sensitivity.v1",
        "status": "RETROSPECTIVE_SITE_FIDELITY_NULL_FALSIFICATION_NO_DIRECT_CONTACT",
        "provenance": {
            "protocol": PROTOCOL,
            "source_repository": "jmistrick/vole-spatial-manuscript",
            "source_commit": SOURCE_COMMIT,
            "original_file_git_blob_shas": {
                name: val[0] for name, val in SOURCE_FILES.items()
            },
            "original_source_census_reverified": {
                "capture_rows": census["raw_capture_rows"],
                "source_animal_keys": census["all_source_animal_keys"],
                "both_season_tags": census["both_seasons_tags"],
                "original_two_per_season_animal_subset": census["same_frozen_51_tags"],
                "physical_sites_with_source_captures": census["original_12_sampling_sites"],
            },
            "same_frozen_dyad_sites": len(cohort),
            "same_frozen_dyad_animal_count": sum(len(x) for x in cohort.values()),
            "same_frozen_dyads_not_independent": EXPECTED_DYADS,
            "factorial_cells_physical_site_counts": {
                "__".join(cell): len(by_cell[cell]) for cell in FACTOR_CELLS
            },
            "this_null_added_after_original_positive_dyad_result": True,
        },
        "primary_retrospective_sensitivity": {
            "estimand": "mean physical-site rho_observed minus mean per-site rho under within-individual stationary pooled captured locations",
            "observed_site_equal_rho": mean(x["observed"] for x in values),
            "stationary_individual_null_site_equal_rho": mean(x["null"] for x in values),
            "site_equal_residual_rho": mean(residuals),
            "residual_site_bootstrap95_descriptive": percentile95(bootstrap),
            "positive_residual_sites": sum(x > 0 for x in residuals),
            "negative_residual_sites": sum(x < 0 for x in residuals),
            "zero_residual_sites": sum(x == 0 for x in residuals),
            "null_per_site_draws": PERMUTATIONS,
            "null_min_valid_per_site": min(x["valid"] for x in values),
            "null_max_degenerate_draws_per_site": max(x["invalid"] for x in values),
            "whole_site_cell_stratified_bootstrap_draws": SITE_BOOTSTRAPS,
            "rng_seed": RNG_SEED,
            "source_grid_coordinate_units_not_assumed_metres": True,
        },
        "boundaries": {
            "not_a_social_pair_contact_or_reproductive_partner_test": True,
            "individual_stationarity_null_does_not_preserve_season_specific_trap_effort_or_habitat": True,
            "site_bootstrap_descriptive_not_preregistered_confirmation": True,
            "individual_capture_centroids_not_true_home_range_centres": True,
            "original_id_shuffle_rho_unchanged": True,
            "original_NEON_Portal_Structural_results_untouched": True,
            "single_unified_manuscript_stays_DRAFT_SUBMISSION_HOLD": True,
            "no_individual_ID_site_name_or_coordinate_exported": True,
        },
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
    }

def main():
    global STAGE
    try:
        result, code = run(), 0
    except Exception as error:
        result, code = {
            "schema": "neon.external_vole_dyad_individual_stationarity_sensitivity.v1",
            "status": "STOP_ORIGINAL_SOURCE_OR_FIXED_NULL",
            "stopped_phase": STAGE,
            "error_class": type(error).__name__,
            "no_biological_sensitivity_result_promoted": True,
            "historical_effects_unchanged": True,
        }, 3
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True, indent=2))
    return code

if __name__ == "__main__":
    raise SystemExit(main())
