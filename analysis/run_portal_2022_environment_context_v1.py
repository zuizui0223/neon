#!/usr/bin/env python3
"""Independent environmental *context* for opened 2022-sensitive Portal result.

This is post-outcome, not a biological confirmation or weather-adjusted model.
No animal, plant or previously fit ecological data are loaded.
"""
from __future__ import annotations

from datetime import datetime,timezone
from pathlib import Path
from statistics import mean
import json

from analysis.audit_portal_2022_site_climate_source_v1 import (
    verify_sources, YEARS, SOURCE_REPO, SOURCE_COMMIT
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_portal_2022_environment_context_20261121.json"
PROTOCOL="docs/NEON_PORTAL_2022_ENVIRONMENT_POSTRESULT_DESIGN_20261121.md"

def source_year_differences(values):
    """Three consecutive, unselected signed and absolute yearly contrasts."""
    if values is None:
        return None
    if sorted(values)!=list(YEARS):
        raise ValueError("ENV_2022_FROZEN_FOUR_YEAR_DOMAIN_DRIFT")
    out={}
    for yr in YEARS[:-1]:
        v=values[yr+1]-values[yr]
        out[f"{yr}_to_{yr+1}"]={"signed":v,"absolute":abs(v)}
    pivot=out["2022_to_2023"]["absolute"]
    all_vals=sorted([z["absolute"] for z in out.values()],reverse=True)
    return {
        "all_unselected_transitions":out,
        "2022_to_2023_absolute_change_rank_largest_first":
            1+sum(x>pivot for x in all_vals),
        "2022_to_2023_rank_has_tie":
            sum(x==pivot for x in all_vals)>1,
        "n_admissible_year_transitions":3,
        "no_significance_test_from_three_year_transitions":True,
    }

def run():
    rain,ndvi,gate=verify_sources()
    sums=None
    vegetation=None
    if gate["rain_gate_pass"]:
        sums={y:sum(value for value in rain[y].values()
                    if value is not None) for y in YEARS}
    if gate["ndvi_gate_pass"]:
        vegetation={y:mean(ndvi[y]) for y in YEARS}
    if sums is None and vegetation is None:
        state="SOURCE_STOP_BOTH_INDICATORS_NO_EFFECT"
    elif sums is None:
        state="ENVIRONMENT_NDVI_ONLY_RAIN_QUALITY_STOP"
    elif vegetation is None:
        state="ENVIRONMENT_RAIN_ONLY_LANDSAT8_QUALITY_STOP"
    else:
        state="ENVIRONMENT_SOURCE_GO_BOTH_SITE_CONTEXT_INDICATORS"
    return {
        "schema":"neon.portal_postresult_2022_monsoon_site_environment_context.v1",
        "status":state,
        "source":{
            "provider_repository":SOURCE_REPO,
            "immutable_git_commit":SOURCE_COMMIT,
            "original_git_blob_sha_validated":True,
            "source_only_QC":gate,
        },
        "original_site_hourly_precipitation_monsoon":{
            "value_units":"millimetres, only measured source hours; missing NOT imputed",
            "year_observed_hour_sums_if_source_go":(
                {str(y):sums[y] for y in YEARS} if sums else None),
            "three_consecutive_year_differences":source_year_differences(sums),
            "year_level_site_weather_one_station_not_experimental_plot":True,
        },
        "original_Landsat8_monsoon_NDVI":{
            "value_units":"unitless site-area NDVI ~1km radius; not biomass",
            "mean_per_valid_cloud_filtered_image_if_gate_go":(
                {str(y):vegetation[y] for y in YEARS} if vegetation else None),
            "three_consecutive_year_differences":source_year_differences(vegetation),
            "same_sensor_and_cloud_rule_all_four_years":True,
        },
        "prior_opened_biological_evidence":{
            "source_receipt":"results/neon_portal_resource_competitor_year_stability_20261120.json",
            "2022_startyear_pair_fraction_in_full_original":65/114,
            "prior_2022_omission_reversed_both_coefficients":True,
            "prior_mammal_outcomes_not_loaded_or_refit":True,
            "climate_not_regressed_against_posthoc_mammal_coefficients":True,
        },
        "limits":{
            "POST_RESULT_CONTEXT_ONLY":True,
            "site_climate_shared_across_all_Portal_plot_treatments":True,
            "rainfall_and_NDVI_not_plot_food_or_rodent_learning":True,
            "no_individual_movement_or_encounters_measured":True,
            "three_transitions_not_independent_assemblages":True,
            "no_universal_year_robust_competition_buffering_result":True,
            "one_NEON_Manuscript_Draft_SUBMISSION_HOLD":True,
        },
        "protocol":PROTOCOL,
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
    }

def main():
    try:
        result=run()
        status=0
    except Exception as exc:
        result={
            "schema":"neon.portal_postresult_2022_monsoon_site_environment_context.v1",
            "status":"SOURCE_STOP_NO_BIOLOGICAL_ENVIRONMENT_INTERPRETATION",
            "error_type":type(exc).__name__,
            "stop_reason":str(exc)[:160],
            "all_prior_Portal_NEON_and_Finland_effects_unchanged":True
        }
        status=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True,indent=2))
    return status

if __name__=="__main__":
    raise SystemExit(main())
