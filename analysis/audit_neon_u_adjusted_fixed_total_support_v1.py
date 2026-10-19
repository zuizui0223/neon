#!/usr/bin/env python3
"""Effect-blind *real-source-ready* F/C/U fixed-total identifiability audit.

Only event-level abundance predictors and categorical fixed-effect keys enter.
Never read/fit NEON W, B, Δ, coordinates, animal IDs or detection outcomes.
"GO" here is source-predictor FEASIBILITY ONLY, not species validation or
authorization of any present/historical ecological effect fit.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import math

import numpy as np

from analysis.multiscale_density_fixed_effects_v1 import _design
from analysis.neon_fixed_total_contrast_v1 import predictor_support

UNSAFE_KEYS = {
    "w","b","d","w_m2","b_m2","d_m2","b_observed_m2","b_debiased_m2",
    "centroid","centroids","trapcoordinate","coordinates",
    "individual_centroid_coordinates_m","tagid","earsampleid",
}


def _validate_source_row(row: dict) -> None:
    if not isinstance(row, dict):
        raise ValueError("Predictor support requires only structured count rows")
    for field in row:
        k = str(field).casefold()
        if k in UNSAFE_KEYS or "centroid" in k or "trapcoordinate" in k:
            raise ValueError("No spatial response, coordinates or animal IDs in source-predictor audit")
    for field in ("genus","taxon","site","plot_id","event_id","series_id",
                  "site_month","year","N","F","C","U",
                  "strictly_resolved_response_taxon"):
        if field not in row:
            raise ValueError(f"Required source-predictor field missing: {field}")
    vals = [row[k] for k in ("N","F","C","U")]
    if any(isinstance(v,bool) or not isinstance(v,(int,np.integer)) or v<0 for v in vals):
        raise ValueError("N/F/C/U source counts must be nonnegative integers")
    if int(row["N"]) != int(row["F"])+int(row["C"])+int(row["U"]):
        raise ValueError("Exact source identity N=F+C+U was violated")
    if any(not str(row[x]) for x in ("genus","taxon","site","series_id","site_month","year")):
        raise ValueError("Source categorical fixed-effects identifiers must be nonblank")


def _analysis_cohort(
    rows: list[dict], genus: str, previous_frozen_support: dict
) -> list[dict]:
    if not isinstance(previous_frozen_support,dict):
        raise ValueError("Previously frozen genus support is required")
    if not genus or not isinstance(genus,str):
        raise ValueError("Genus must be a nonempty literal")
    for row in rows:
        _validate_source_row(row)
    active = [
        row for row in rows
        if row["genus"] == genus and row["strictly_resolved_response_taxon"]
    ]
    by_series=defaultdict(list)
    for r in active:
        by_series[r["series_id"]].append(r)
    kept=[
        r for key,items in by_series.items() if len(items)>=3
        for r in items
    ]
    expected=previous_frozen_support.get("species_sessions_in_3plus_series")
    if expected is not None and len(kept)!=int(expected):
        raise ValueError("Previously frozen session denominator drifted")
    if "species_sessions_all" in previous_frozen_support and len(active)!=int(previous_frozen_support["species_sessions_all"]):
        raise ValueError("Previously frozen full-species session denominator drifted")
    if "sites_in_3plus_series" in previous_frozen_support:
        if len({r["site"] for r in kept})!=int(previous_frozen_support["sites_in_3plus_series"]):
            raise ValueError("Previously frozen geographic site denominator drifted")
    if "species_series_with_3plus_sessions" in previous_frozen_support:
        if len({r["series_id"] for r in kept})!=int(previous_frozen_support["species_series_with_3plus_sessions"]):
            raise ValueError("Previously frozen series denominator drifted")
    if len(kept)!=len({
        (str(r["taxon"]),str(r["site"]),str(r["plot_id"]),str(r["event_id"]))
        for r in kept
    }):
        raise ValueError("Original source has duplicate taxon×site×plot×event session")
    return kept


def fixed_total_genus_support(
    rows: list[dict], *,
    genus: str,
    previous_frozen_support: dict,
) -> dict:
    """Report U-conditioned fixed-total neighbour composition FEASIBILITY.

    Uses the existing post-development hypothesis's *same* qualified
    taxon×site×plot >=3-event series, site×month and year fixed effects.
    Spatial outcomes are not accepted as input; only F,C,U,N and categories.
    """
    retained=_analysis_cohort(rows,genus,previous_frozen_support)
    if len(retained)<4:
        return {
            "schema":"neon.fixed_total.U_adjusted_source_site_support.v1",
            "genus":genus,
            "status":"INSUFFICIENT_SOURCE_ROWS",
            "session_count":len(retained),
            "U_adjusted_predictor_only_candidate":False,
            "W_B_or_ecological_effects_opened":False,
        }

    counts=np.asarray([[int(r[k]) for k in ("F","C","U")] for r in retained],dtype=float)
    z=_design(retained,("series_id","site_month","year"))
    source=predictor_support(counts,z)
    rank_before=int(source["rank_FC_after_nuisance"])
    expected_rank=previous_frozen_support.get("fixed_effects_predictor_geometry",{}).get("predictor_rank_after_FE")
    if expected_rank is not None and rank_before!=int(expected_rank):
        raise ValueError("Previously frozen F/C rank after original nuisance drifted")

    # Partial out Z, original genus total N and uncertain animals U.
    # The remaining F variance identifies the exact F-for-C fixed-total
    # composition shift; this uses NO W/B response, centroid or density slope.
    nuisance=np.column_stack((z, counts.sum(axis=1),counts[:,2]))
    target=counts[:,0]
    coef,*_=np.linalg.lstsq(nuisance,target,rcond=1e-11)
    residual=target-nuisance@coef
    square=np.square(residual)
    total=float(square.sum())
    expected_total=float(source["replacement_predictor_residual_SS"])
    if not math.isclose(total,expected_total,rel_tol=3e-6,abs_tol=1e-6):
        raise ValueError("FWL conditional F residual information differs from frozen pure algebra")
    sites=sorted({r["site"] for r in retained})
    site_ss={site:0. for site in sites}
    for row,info in zip(retained,square):
        site_ss[row["site"]]+=float(info)
    if not math.isclose(sum(site_ss.values()),total,rel_tol=1e-10,abs_tol=1e-7):
        raise ValueError("Conditional information did not add across original NEON sites")
    shares=sorted((value/total for value in site_ss.values()),reverse=True) if total>1e-10 else []
    effective_sites=1./sum(share*share for share in shares) if shares else None
    condition=source["condition_FC_after_nuisance_and_U"]
    support=(
        previous_frozen_support.get("state")=="PREDICTOR_ONLY_POTENTIALLY_IDENTIFIABLE"
        and source["rank_FC_after_nuisance_and_U"]==2
        and condition is not None and math.isfinite(condition) and condition<=30.
        and bool(source["fixed_total_replacement_contrast_estimable"])
        and total>1e-8
    )

    result={
        "schema":"neon.fixed_total.U_adjusted_source_site_support.v1",
        "genus":genus,
        "status":("PREDICTOR_ONLY_U_ADJUSTED_FIXED_TOTAL_CANDIDATE"
                  if support else "PREDICTOR_ONLY_U_ADJUSTED_SUPPORT_STOP"),
        "strictly_species_labelled_source_sessions":len(retained),
        "original_physical_sites":len(sites),
        "original_threeplus_event_series":len({r["series_id"] for r in retained}),
        "original_source_genus_N_equals_F_plus_C_plus_U":True,
        "rank_FC_after_nuisance":source["rank_FC_after_nuisance"],
        "rank_FC_after_nuisance_and_U":source["rank_FC_after_nuisance_and_U"],
        "rank_FCU_after_nuisance":source["rank_FCU_after_nuisance"],
        "condition_FC_after_nuisance_and_U":condition,
        "fixed_total_replacement_contrast_estimable":bool(source["fixed_total_replacement_contrast_estimable"]),
        "fixed_total_replacement_residual_SS":total,
        "fixed_total_nullspace_projection_norm":source["contrast_nullspace_projection_norm"],
        "fixed_total_information_by_site":{
            "original_physical_sites":len(sites),
            "sites_with_detectable_conditional_information":sum(
                value>max(1e-8,1e-7*total) for value in site_ss.values()
            ),
            "top_one_site_information_fraction":shares[0] if shares else None,
            "top_three_site_information_fraction":sum(shares[:3]) if shares else None,
            "effective_site_count_descriptive":effective_sites,
            "information_share_distribution":shares,
            "does_not_prove_independent_site_effects":True,
        },
        "previous_frozen_FC_feasibility_decision":previous_frozen_support.get("state"),
        "U_adjusted_predictor_only_candidate":bool(support),
        "U_adjusted_support_not_prospective_power_or_species_validation":True,
        "no_source_ids_site_codes_or_animal_tags_exported":True,
        "W_B_or_ecological_effects_opened":False,
        "prior_eight_genus_generalization":"FAILED_5_OF_8",
        "MOSA_spatial_effects":"SEALED",
    }
    return result
