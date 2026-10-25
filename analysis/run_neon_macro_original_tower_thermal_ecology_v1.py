#!/usr/bin/env python3
"""Source-verified one-axis NEON macroclimate test: monthly tower thermal
displacement versus genus-associated trapping-place recurrence.

Same already inspected DP1.10072.001 RELEASE-2026 as historical exploratory
ecology. Provider QC and source completeness first, then exact original
two-row 150-unit Z replay, then ONE site-level climate association.
No site, genus, original capture date, individual tag, station or weather
file URL is serialized or logged. No precipitation mixture or Daymet fallback.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from statistics import mean,median
from datetime import date
import json,os

from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    _request_json,_download_one,QUERY_URL,TOKEN_ENV
)
from analysis.run_neon_macro_temporal_weather_source_v1 import (
    NEON_SITES,weather_release_months,PRODUCTS
)
from analysis.neon_macro_site_selection_v1 import site_metadata_index
from analysis.neon_macro_tower_thermal_contrast_v1 import (
    source_month_selection,_month_catalog,aggregate_qc_month,climate_site_model
)
from analysis.neon_exact_two_row_fixedmargin_v1 import two_row_exact_marginal,observed_exact_unit

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/"build/neon_macro_original_month_thermal_recurrence_v1.json"
SOURCE_QA=ROOT/"results/neon_macro_tower_weather_qc_pilot_20261025.json"
OLD=ROOT/"results/neon_exact_two_genus_ecological_receipt_20261025.json"
DESIGN="docs/NEON_MACRO_THERMAL_PERSISTENCE_SINGLE_CONTRAST_20261025.md"
TEMP="DP1.00002.001"
RELEASE="RELEASE-2026"
MIN_PAIRS=80
MIN_SITES=18
MIN_DOMAINS=10
SEED=2026102521


def require(ok:bool,msg:str)->None:
    if not ok:raise RuntimeError("ORIGINAL_RELEASE_THERMAL_MACRO_STOP: "+msg)


def prepare():
    trial=json.loads(SOURCE_QA.read_text(encoding="utf-8"))
    require(trial["status"]=="SOURCE_ONLY_ORIGINAL_NEON_TEMPERATURE_AND_TIPPING_30MIN_QA"
            and trial["monthly_product_QA"]["single_air_temperature"]["source_MD5_and_byte_count_verified"],
            "original temperature/QC provider pilot unavailable")
    old=json.loads(OLD.read_text(encoding="utf-8"))
    require(old["observed"]["informative_exact_two_genus_pairs"]==150
            and old["observed"]["physical_sites"]==30,
            "original exact-two fixed-margin observed effect changed")
    strict,all_two,src=original_sources_for_two_genus()
    require(len(strict)==58 and len(all_two)==158 and len({u["site"] for u in all_two})==30,
            "original source cohort changed")
    original_all_sorted=sorted(all_two,key=lambda z:(z["site"],tuple(z["site_plot"]),z["season_ordinal"]))
    listed=_request_json(NEON_SITES).get("data")
    require(isinstance(listed,list),"NEON release site metadata missing")
    needed_sites={u["site"] for u in original_all_sorted}
    meta={r.get("siteCode"):r for r in listed
          if isinstance(r,dict) and r.get("siteCode") in needed_sites}
    require(set(meta)==needed_sites,"original NEON site weather metadata incomplete")
    geo=site_metadata_index(list(meta.values()))
    availability={s:weather_release_months(row)[TEMP] for s,row in meta.items()}
    candidates,need_months=source_month_selection(original_all_sorted,availability)
    cats={geo[u["site"]]["domain"] for u in original_all_sorted}
    pred_domains={geo[u["site"]]["domain"] for u in (x["unit"] for x in candidates)}
    structural={
        "original_source_two_genus_pairs":len(original_all_sorted),
        "original_strict_threeplus_pairs_unmodified":len(strict),
        "candidate_exact_2026_temperature_release_month_pairs":len(candidates),
        "candidate_original_physical_sites":len({x["site"] for x in candidates}),
        "candidate_original_domains":len(pred_domains),
        "source_site_month_temperature_data_objects_requested":len(need_months),
        "original_all_source_domains":len(cats),
        "source_structural_thresholds":{
            "minimum_original_QC_paired_pairs":MIN_PAIRS,
            "minimum_physical_sites":MIN_SITES,
            "minimum_ecological_domains":MIN_DOMAINS,
        },
        "no_original_2026 ecological_Z_x_climate_contrast_opened":True,
    }
    return original_all_sorted,old,src,geo,candidates,need_months,structural


def provider_weather_months(sites:list[str],months:set[tuple[str,str]],token:str)->tuple[dict,dict]:
    """NEON released original site/month archives, fixed source file sort."""
    if not months:
        return {},{"requested":0,"metadata_found":0,"downloaded":0}
    month_names=[m for s,m in months]
    payload=_request_json(QUERY_URL,token=token,body={
        "productCode":TEMP,"siteCodes":sites,
        "startDateMonth":min(month_names),"endDateMonth":max(month_names),
        "release":RELEASE,"package":"basic","includeProvisional":False,
    })
    chosen=_month_catalog(payload,months)
    valid={key:row for key,row in chosen.items() if row is not None}
    wrong=len(months)-len(valid)
    qc={}
    errors=Counter()

    def process(item):
        key,row=item
        try:
            raw=_download_one(row,token)
            out=aggregate_qc_month(raw,key[1])
            return key,out,None
        except Exception as e:
            return key,None,type(e).__name__

    with ThreadPoolExecutor(max_workers=8) as pool:
        for key,out,error in pool.map(process,sorted(valid.items())):
            if error:
                errors[error]+=1
            elif out is not None:
                qc[key]={**out,"source_position":valid[key]["position"],
                          "provider_digest_verified":True}
    return qc,{
        "requested_source_site_months":len(months),
        "archive_30min_file_months_advertised":len(valid),
        "no_30min_file_months":wrong,
        "verified_and_parsed_months":len(qc),
        "QC_good_months":sum(x["status"]=="TOWER_TEMP_MONTH_QC_PASS" for x in qc.values()),
        "QC_bad_months":sum(x["status"]!="TOWER_TEMP_MONTH_QC_PASS" for x in qc.values()),
        "file_access_error_class_counts":dict(sorted(errors.items())),
        "provider_MD5_and_byte_counts_checked_on_each_readable_month":True,
        "one_preselected_sensor_file_per_original_site_month":True,
        "source_file_names_and_URLs_never_serialized":True,
    }


def run()->dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    require(bool(token),"official NEON source access token missing")
    two,old,src,geo,candidates,monthkeys,source_struct=prepare()
    base={
        "schema":"neon.macro.original_tower_month_thermal_recurrence.v1",
        "research_status":"HISTORICAL_POST_RESULT_EXPLORATORY_NOT_PROSPECTIVE",
        "source_metadata_and_selection":source_struct,
        "mammal_source":src,
        "original_3plus_positive_conditional_effect_unchanged":True,
        "original_8genus_WB_generalization_FAILED_5_of_8":True,
        "original_216pairs_31sites_macro_status_not_reclassified":True,
        "single_precommitted_climate_variable":"abs_differenced_original_source_monthly_SAAT_tempSingleMean",
        "physical_data_grain":"NEON released tower monthly QC mean versus mammal site-level average exact-two Z",
        "design":DESIGN,
    }
    if len(candidates)<MIN_PAIRS or len({x["site"] for x in candidates})<MIN_SITES:
        return {**base,"status":"STOP_ORIGINAL_MONTHLY_TEMP_SOURCE_SUPPORT",
                "weather_quality_stage_opened":False,
                "climate_effect_opened":False}
    weather,quality=provider_weather_months(sorted({s for s,m in monthkeys}),monthkeys,token)
    count_weather={
        **quality,
        "fixed_min_valid_30min_fraction":0.70,
        "NEON_original_release":RELEASE,
        "source_tower_is_not_mammal_grid_microhabitat":True,
    }
    valid=[]
    missing=Counter()
    for record in candidates:
        site=record["site"]
        a=weather.get((site,record["monthA"]))
        b=weather.get((site,record["monthB"]))
        if not a or not b:
            missing["NO_ARCHIVE_MONTH"]+=1
            continue
        if a["status"]!="TOWER_TEMP_MONTH_QC_PASS" or b["status"]!="TOWER_TEMP_MONTH_QC_PASS":
            missing["INSTRUMENT_MONTH_QC_FAILURE"]+=1
            continue
        if a["source_position"]!=b["source_position"]:
            missing["INSTRUMENT_VERTICAL_POSITION_MISMATCH"]+=1
            continue
        u=record["unit"]
        valid.append({
            **record,
            "thermal_displacement_abs_celsius":abs(b["_private_mean_celsius"]-a["_private_mean_celsius"]),
        })
    pair_domains={geo[x["site"]]["domain"] for x in valid}
    valid_sites={x["site"] for x in valid}
    observed_QC={
        "release_eligible_source_pairs":len(candidates),
        "source_pair_with_both_months_station_quality_verified":len(valid),
        "quality_verified_original_physical_sites":len(valid_sites),
        "quality_verified_ecological_domains":len(pair_domains),
        "failed_pair_source_QA_categories":dict(sorted(missing.items())),
        "temperature_overall_source_QC_data_grain_month_not_capture_night":True,
        "no_B_vs_A_weather_imputation":True,
    }
    prequalified=(len(valid)>=MIN_PAIRS and len(valid_sites)>=MIN_SITES
                  and len(pair_domains)>=MIN_DOMAINS)
    if not prequalified:
        return {**base,
            "status":"STOP_ORIGINAL_TOWER_TEMPERATURE_QC_OR_DOMAIN_SUPPORT",
            "weather_source_QA":count_weather,
            "weather_pair_pre_effect_feasibility":observed_QC,
            "climate_effect_opened":False}

    # Only NOW replay every old two-row ecological unit and validate
    # the anonymous original thirty physical-site effects.
    old_by_site=defaultdict(list)
    original_effect={}
    for u in two:
        m=two_row_exact_marginal(u["A"],u["B"])
        if m["status"]!="EXACT_NONDEGENERATE":
            continue
        obs=observed_exact_unit(u["A"],u["B"],m)
        z=obs["z"]
        require(z is not None,"exact marginal had unexplained missing Z")
        key=(u["site"],tuple(u["site_plot"]),u["season_ordinal"])
        original_effect[key]=z
        old_by_site[u["site"]].append(z)
    old_means=sorted(mean(v) for v in old_by_site.values())
    frozen=old["observed"]["site_means_sorted_anonymous"]
    require(len(old_means)==len(frozen)==30
            and all(abs(a-b)<1e-8 for a,b in zip(old_means,frozen))
            and len(original_effect)==150,
            "original old 30-site two-row Z source could not be bit-replayed")

    bysite=defaultdict(list)
    for r in valid:
        u=r["unit"]
        key=(u["site"],tuple(u["site_plot"]),u["season_ordinal"])
        z=original_effect.get(key)
        if z is not None:
            bysite[r["site"]].append({
                "Z":z,
                "thermal_displacement":r["thermal_displacement_abs_celsius"],
                "transition_q2":int(u["season_ordinal"]%4==2),
            })
    n_source_pairs=sum(len(x) for x in bysite.values())
    derived_domains={geo[s]["domain"] for s in bysite}
    ecological_gate={
        "finite_exact_QC_pair_Z_and_thermal_delta":n_source_pairs,
        "physical_sites":len(bysite),
        "ecological_domains":len(derived_domains),
        "minimum_original_pair_count":MIN_PAIRS,
        "minimum_physical_site_count":MIN_SITES,
        "minimum_domain_count":MIN_DOMAINS,
        "corrected_source_original_30_site_anonymous_effects_exactly_reproduced":True,
        "pass":(n_source_pairs>=MIN_PAIRS and len(bysite)>=MIN_SITES
                and len(derived_domains)>=MIN_DOMAINS),
    }
    if not ecological_gate["pass"]:
        return {**base,
            "status":"STOP_SOURCE_QC_BUT_TOO_FEW_INFORMATIVE_ECOLOGICAL_PAIRS",
            "weather_source_QA":count_weather,
            "weather_pair_pre_effect_feasibility":observed_QC,
            "ecological_complete_case_feasibility":ecological_gate,
            "climate_effect_opened":False}

    sites=[]
    vals=[]
    for s,items in sorted(bysite.items()):
        shift=mean(x["thermal_displacement"] for x in items)
        vals.extend(x["thermal_displacement"] for x in items)
        sites.append({
            "site":s,
            "mean_abs_delta_C":shift,
            "site_mean_original_exact_Z":mean(x["Z"] for x in items),
            "site_latitude":geo[s]["latitude"],
            "fraction_summer_to_autumn":mean(x["transition_q2"] for x in items),
        })
    model=climate_site_model(sites,seed=SEED,n_bootstrap=2000)
    return {
        **base,
        "status":(
            "EXPLORATORY_ORIGINAL_RELEASE_THERMAL_MACRO_ASSOCIATION_ESTIMATED"
            if model["ecological_temperature_slope_fitted"]
            else "STOP_SITE_THERMAL_MACRO_MODEL_RANK_OR_BOOTSTRAP"
        ),
        "weather_source_QA":count_weather,
        "weather_pair_pre_effect_feasibility":observed_QC,
        "ecological_complete_case_feasibility":ecological_gate,
        "source_original_30_site_Z_replayed_verbatim":True,
        "source_QC_pair_thermal_displacement_description":{
            "source_pairs":len(vals),
            "mean_abs_temperature_shift_C":mean(vals),
            "median_abs_temperature_shift_C":median(vals),
            "min_abs_temperature_shift_C":min(vals),
            "max_abs_temperature_shift_C":max(vals),
            "data_values_not_capture_dates_or_sites":True,
        },
        "climate_effect_opened":model["ecological_temperature_slope_fitted"],
        "site_level_thermal_climate_ecological_model":model,
        "causal_scope":{
            "same_historical_ecological_release_effect_already_inspected":True,
            "source_temperature_independent_measurement_not_independent_biological_replication":True,
            "weather_station_not_microhabitat_or_plant_cover":True,
            "taxon_specific_trap_catchability_not_calibrated":True,
            "site_month_not_capture_night_temperature":True,
            "no_absolute_temperature_or_precipitation_variable_search":True,
            "old_site_recurring_derived_Z_and_3plus_results_not_pooled":True,
            "cannot_identify_habitat_memory_competition":True,
        },
    }


def main()->int:
    try:
        value=run()
        code=0
    except Exception as e:
        value={
            "schema":"neon.macro.original_tower_month_thermal_recurrence.v1",
            "status":"STOP_ORIGINAL_CLIMATE_SOURCE_OR_INVARIANT_ERROR",
            "error_class":type(e).__name__,
            "old_neon_ecological_recurrence_unmodified":True,
            "no_private_source_credential_site_tag_filename_or_climate_series_exported":True,
        }
        code=3
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(value,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
