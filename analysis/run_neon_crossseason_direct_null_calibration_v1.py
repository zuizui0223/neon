#!/usr/bin/env python3
"""Rerun original fixed-fixed chains and propagate private nulls to site mean.

Post-result statistical calibration ONLY, not a preregistered confirmatory
test or a rescue of the older failed NEON W/B hypothesis. Uses the same
immutable RELEASE-2026 source, every original season pair and null seed,
without accessing novel mammals, genomics, habitat covariates or W/B.

No source site ID, animal tag, trap coordinate, genus label, BOLD sampleID
or sequence is exported; all unit-level 2,000-step null vectors are held
in ephemeral process memory and excluded from output artifacts.
"""
from __future__ import annotations

from collections import defaultdict
import json
from math import isclose
import os
from pathlib import Path

from analysis.run_neon_crossseason_genus_template_ecology_v1 import (
    PRODUCT, RELEASE, START, END, PRODUCT_URL, QUERY_URL, TOKEN_ENV,
    MAX_DOWNLOAD_WORKERS, _request_json, _site_codes, _inventory,
    _download_many, _read_plot_rows, _read_trap_rows, _candidate_nights,
    _taxonomy, source_event_support, verified_support_gate,
    fixed_fixed_null_for_unit, crossseason_template_inference,
    FROZEN as STRUCTURAL_FROZEN, N_DRAWS, N_BURN, SWAPS,
    MIN_ESS, SEED as ORIGINAL_UNIT_SEED,
)
from analysis.neon_crossseason_direct_null_calibration_v1 import (
    direct_site_weighted_product_null, season_sharing_diagnostic,
    reused_physical_site_ids_from_source_units,
)
from analysis.neon_crossseason_direct_site_null_v1 import (
    direct_site_null_calibration,
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_crossseason_direct_null_calibration_v1.json"
ORIGINAL_ECOLOGY=ROOT/"results/neon_crossseason_genus_template_ecology_receipt_20261019.json"

JOINT_REPLICATES=100_000
JOINT_SEED=2026101902
ABS_NUMERIC_TOL=1e-9


def require(yes:bool, reason:str)->None:
    if not yes:
        raise RuntimeError("FROZEN_ORIGINAL_SOURCE_DRIFT: "+reason)


def close(a:float,b:float)->bool:
    return isclose(float(a),float(b),rel_tol=1e-10,abs_tol=ABS_NUMERIC_TOL)


def audit_identical_original_unit(effect:dict, archival:dict, index:int)->None:
    """Preserve ALL original unit and MCMC quantities before aggregation."""
    for old,new in (
        ("source_genera","source_genera"),
        ("observed_genus_trap_cells_season_A","season_A_observed_genus_trap_cells"),
        ("observed_genus_trap_cells_season_B","season_B_observed_genus_trap_cells"),
    ):
        require(int(archival[old])==int(effect[new]),
                "archival per-unit source geometry changed")
    require(effect["status"]==archival["status"]=="INFORMATIVE_FIXED_FIXED_NULL",
            "original informative fixed-fixed unit changed")
    for old,new in (
        ("z","z"),
        ("lag1_overlap_autocorrelation","lag1_overlap_autocorrelation"),
        ("approx_effective_null_draws_lag1","approx_effective_null_draws_lag1"),
        ("swap_acceptance_rate","swap_acceptance_rate"),
    ):
        require(close(effect[new],archival[old]),
                "original deterministic unit result/chain changed")
    require(effect["null_draws_requested"]==N_DRAWS,
            "null replicate count changed")
    require(effect["observed_same_genus_same_trap_overlap"]>=0,
            "invalid original observed recurrence count")


def run() -> dict:
    support=json.loads(STRUCTURAL_FROZEN.read_text(encoding="utf-8"))
    archival=json.loads(ORIGINAL_ECOLOGY.read_text(encoding="utf-8"))
    old=archival["independent_site_ecology"]
    original_units=archival[
        "informative_unit_source_geometry_summary"
    ]["unlabelled_unit_diagnostics"]
    require(
        archival["status"]=="SUPPORT_MULTI_SITE_GENUS_TEMPLATE_REASSEMBLY"
        and old["physical_sites"]==14
        and old["informative_seasonal_units"]==58
        and old["positive_site_means"]==11
        and close(old["site_mean_Z_mean"],0.8007420166137748)
        and close(old["one_sided_site_signflip_p"],0.00115966796875)
        and len(original_units)==58,
        "original preregistered source result not recovered",
    )
    require(
        RELEASE=="RELEASE-2026" and START=="2015-04" and END=="2026-09"
        and (N_DRAWS,N_BURN,SWAPS,MIN_ESS,ORIGINAL_UNIT_SEED)==
            (2000,1000,40,200,2026101901),
        "released source or per-unit randomization settings were changed",
    )

    token=os.environ.get(TOKEN_ENV,"").strip()
    require(bool(token),"original RELEASE-2026 source authorization unavailable")
    all_target,genus_by_taxon,_=_taxonomy()
    require(bool(all_target),"historical target genus taxonomy unavailable")
    sites=_site_codes(_request_json(PRODUCT_URL))
    manifest=_inventory(_request_json(
        QUERY_URL,token=token,body={
            "productCode":PRODUCT,"siteCodes":sites,
            "startDateMonth":START,"endDateMonth":END,
            "release":RELEASE,"package":"basic","includeProvisional":False,
        },
    ))
    plot_files=[r for r in manifest if "mam_perplotnight" in r["name"]]
    require(len(manifest)==3547 and len(plot_files)==1773,
            "original checksum-verified NEON manifest changed")
    plots=[]
    for meta,raw in zip(
        plot_files,_download_many(plot_files,token,max_workers=MAX_DOWNLOAD_WORKERS)
    ):
        plots.extend(_read_plot_rows(raw,meta["site"],meta["month"]))
    nights,site_months=_candidate_nights(plots)
    trap_files=[
        r for r in manifest
        if "mam_pertrapnight" in r["name"]
        and (r["site"],r["month"]) in site_months
    ]
    require(len(trap_files)==1707,"historical checksum-verified trap cohort changed")
    traps=[]
    for meta,raw in zip(
        trap_files,_download_many(trap_files,token,max_workers=MAX_DOWNLOAD_WORKERS)
    ):
        for capture in _read_trap_rows(raw,nights):
            capture["_site"]=meta["site"]
            traps.append(capture)
    require(len(plots)==21363 and len(traps)==1505827,
            "original live-trap source-row universe changed")

    units=[]
    structural=source_event_support(
        plots,traps,genus_by_taxon,internal_units=units
    )
    verified_support_gate(structural,support)
    require(len(units)==58,"source did not reproduce 58 original eligible units")
    units.sort(key=lambda r:(r["site"],r["site_plot"],r["season_ordinal"]))
    season_dependency=season_sharing_diagnostic(units)
    reused_source_sites=reused_physical_site_ids_from_source_units(units)
    require(len(reused_source_sites)==2,
            "exactly two original season-reused source sites must be removed")
    require(season_dependency["physical_sites_with_any_adjacent_pair_season_reuse"]==2,
            "original dependency diagnostic changed")

    private_unit_nulls=[]
    observed_z_by_site=defaultdict(list)
    for index,source_unit in enumerate(units):
        null_overlap_draws=[]
        fitted=fixed_fixed_null_for_unit(
            source_unit["A"],source_unit["B"],
            seed=ORIGINAL_UNIT_SEED+index,
            n_draws=N_DRAWS,
            burn_in=N_BURN,
            swaps_per_draw=SWAPS,
            min_effective_draws=MIN_ESS,
            private_draws_out=null_overlap_draws,
        )
        audit_identical_original_unit(fitted,original_units[index],index)
        require(len(null_overlap_draws)==N_DRAWS,
                "private original null MCMC draws were not fully retained")
        normalized=[
            (float(raw)-fitted["null_mean"])/fitted["null_sd"]
            for raw in null_overlap_draws
        ]
        private_unit_nulls.append({
            "unit_index":index,
            "site":source_unit["site"],
            "observed_z":fitted["z"],
            "null_z_draws":normalized,
        })
        observed_z_by_site[source_unit["site"]].append(fitted["z"])

    old_recomputed=crossseason_template_inference(
        observed_z_by_site,seed=ORIGINAL_UNIT_SEED
    )
    require(
        old_recomputed["physical_sites"]==old["physical_sites"]==14
        and old_recomputed["informative_seasonal_units"]==58
        and old_recomputed["positive_site_means"]==old["positive_site_means"]
        and close(old_recomputed["site_mean_Z_mean"],old["site_mean_Z_mean"])
        and close(old_recomputed["one_sided_site_signflip_p"],
                  old["one_sided_site_signflip_p"]),
        "original 14 physical site Zs and sign-flip p not reproduced",
    )
    for got,want in zip(
        old_recomputed["site_Z_means_sorted_ascending"],
        old["site_Z_means_sorted_ascending"],
    ):
        require(close(got,want),"original physical site means not reproduced")

    conditional=direct_site_weighted_product_null(
        private_unit_nulls,seed=JOINT_SEED,n_replicates=JOINT_REPLICATES
    )
    require(
        close(
            conditional["observed_equal_site_weighted_mean_z"],
            old["site_mean_Z_mean"],
        )
        and conditional["physical_sites"]==14
        and conditional["seasonal_units"]==58,
        "conditional null statistic not identical to frozen site mean",
    )

    # Separately committed POST-RESULT dependence sensitivity: remove
    # EVERY unit at either original physical site where one source season
    # participates in more than one adjacent pair. Site selection uses
    # source keys only, NEVER the observed genus trap recurrence Z.
    independent_source_units=[
        u for u in units if u["site"] not in reused_source_sites
    ]
    independent_units=[
        u for u in private_unit_nulls if u["site"] not in reused_source_sites
    ]
    clean_dependency=season_sharing_diagnostic(independent_source_units)
    require(clean_dependency["season_keys_used_in_multiple_pair_roles"]==0,
            "reused seasons remain in source-dependence site exclusion")
    require(len({u["site"] for u in independent_source_units})==12,
            "expected 12 original season-disjoint physical sites")
    require(len(independent_units)==len(independent_source_units),
            "season exclusion altered unit identity/count")

    cleaner_by_site=defaultdict(list)
    for u in independent_units:
        cleaner_by_site[u["site"]].append(u["observed_z"])
    cleaner_site=crossseason_template_inference(
        cleaner_by_site,seed=ORIGINAL_UNIT_SEED
    )
    require(cleaner_site["physical_sites"]==12,
            "excluded-source site-block signflip not 12 sites")

    cleaner_direct=direct_site_weighted_product_null(
        independent_units,seed=2026101903,n_replicates=100_000
    )
    require(
        close(
            cleaner_direct["observed_equal_site_weighted_mean_z"],
            cleaner_site["site_mean_Z_mean"],
        )
        and cleaner_direct["physical_sites"]==12
        and cleaner_direct["seasonal_units"]==len(independent_units),
        "season-disjoint source unit contrast differs from direct product-null test"
    )

    cleaner_coupled=direct_site_null_calibration(
        [{
            "site":item["site"],
            "observed_unit_z":item["observed_z"],
            "null_unit_z_draws":item["null_z_draws"],
        } for item in sorted(independent_units,key=lambda z:z["unit_index"])],
        seed=2026101932,n_replicates=20_000,
    )
    require(
        cleaner_coupled["source_independent_physical_sites"]==12
        and cleaner_coupled["source_original_seasonal_units"]==len(independent_units)
        and close(
            cleaner_coupled["observed_equal_site_weighted_mean_Z"],
            cleaner_site["site_mean_Z_mean"],
        ),
        "season-disjoint within-site coupled sensitivity changed observed Z"
    )
    cleaner_comonotone=cleaner_coupled["comonotone_within_site_marginal_null"]
    cleaner_result={
        "schema":"neon.crossseason.site_reuse_exclusion_post_result.v1",
        "status":(
            "SECONDARY_12SITE_SOURCE_DEPENDENCE_EXCLUSION_SUPPORTS_DIRECTION"
            if cleaner_direct["one_sided_p_with_plus_one"]<0.05
            and cleaner_comonotone["one_sided_p"]<0.05
            and cleaner_site["site_mean_Z_mean"]>0
            else "SECONDARY_12SITE_SOURCE_DEPENDENCE_EXCLUSION_WEAKENS_INFERENCE"
        ),
        "source_only_excluded_sites":len(reused_source_sites),
        "original_physical_sites":14,
        "remaining_physical_sites":12,
        "source_units_excluded":58-len(independent_units),
        "source_units_remaining":len(independent_units),
        "source_shared_season_keys_remaining":0,
        "original_primary_statistic_unchanged":True,
        "excluded_sites_based_on_source_keys_not_spatial_outcomes":True,
        "post_result_exclusion_not_preregistered_primary_inference":True,
        "remaining_original_site_signflip_exploratory":cleaner_site,
        "remaining_direct_independent_unit_product_null":cleaner_direct,
        "remaining_within_site_comonotone_stress":cleaner_comonotone,
        "within_site_comonotone_not_upper_bound_on_all_joint_nulls":True,
        "remaining_sites_do_not_eliminate_genus_detection_bias":True,
        "site_geographic_identifiers_exported":False,
        "animal_or_source_trap_records_exported":False,
    }

    # Explicit, no-post-hoc-retuning labels. The p<.05 threshold is a
    # secondary calibration descriptor, not a newly preregistered decision.
    supported=conditional["one_sided_p_with_plus_one"]<0.05
    state=(
        "SECONDARY_CONDITIONAL_PRODUCT_NULL_SUPPORTS_DIRECTION_WITH_DEPENDENCE_CAVEAT"
        if supported else
        "SECONDARY_PRODUCT_NULL_DOES_NOT_SUPPORT_PRIMARY_DIRECTION"
    )
    return {
        "schema":"neon.crossseason.site_mean_direct_conditional_null.v1",
        "status":state,
        "record_date":"2026-10-19",
        "source":{
            "release":RELEASE,"product":PRODUCT,
            "checksum_MD5_verified_files":len(manifest),
            "original_plot_csvs":len(plot_files),
            "original_trap_csvs":len(trap_files),
            "same_original_58_unit_14_site_cohort":True,
            "same_genus_trap_A_and_B_and_tag_exclusion_as_primary":True,
            "source_identity_and_location_values_not_exported":True,
        },
        "original_primary_result_unmodified":{
            "status":archival["status"],
            "original_physical_sites":old["physical_sites"],
            "original_seasonal_units":old["informative_seasonal_units"],
            "positive_physical_site_means":old["positive_site_means"],
            "site_mean_Z":old["site_mean_Z_mean"],
            "site_signflip_one_sided_p":old["one_sided_site_signflip_p"],
            "all_original_58_null_chain_Zs_and_14_site_means_reproduced":True,
        },
        "direct_null_calibration":conditional,
        "reused_season_dependence_diagnostic":season_dependency,
        "site_reuse_exclusion_post_result_sensitivity":cleaner_result,
        "interpretation":{
            "post_result_conditional_calibration_not_independent_confirmation":True,
            "no_site_sign_exchangeability_assumed_in_conditional_product_null":True,
            "shared_season_dependence_not_jointly_preserved":True,
            "site_genus_detection_and_habitat_filters_unresolved":True,
            "positive_site_template_pattern_if_supported_bounded_to_capture_locations":True,
            "genetic_species_identity_or_demographic_replacement_established":False,
            "original_density_space_generality":"FAILED_5_OF_8",
            "original_Peromyscus_temporal_directional_validation":"NOT_REPLICATED_IMPRECISE",
            "original_fixed_total_FC_conservative_matching":"ZERO_SAME_SEASON_PAIRS",
            "MOSA_W_B_effects":"SEALED",
            "next":"Treat this as secondary post-result site statistic calibration. Do not upgrade biological mechanism or publication readiness without independent review of shared-season source dependence and persistent genus-specific capture heterogeneity.",
        },
        "raw_source_coordinates_genus_taxon_site_or_animal_identifiers_exported":False,
        "raw_unit_null_MCMC_draws_exported":False,
        "old_density_W_B_responses_reanalysed":False,
    }


def main()->int:
    try:
        result=run()
    except Exception as exc:
        result={
            "schema":"neon.crossseason.site_mean_direct_conditional_null.v1",
            "status":"STOP_DIRECT_NULL_SOURCE_OR_ORIGINAL_RESULT_DRIFT",
            # Do not leak actual source token, taxon or hidden animal/site IDs.
            "diagnostic_class":type(exc).__name__,
            "raw_unit_null_MCMC_draws_exported":False,
            "old_density_W_B_responses_reanalysed":False,
            "original_primary_result_not_reclassified":True,
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 3 if result["status"].startswith("STOP_") else 0


if __name__=="__main__":
    raise SystemExit(main())
