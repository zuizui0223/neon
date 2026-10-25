#!/usr/bin/env python3
"""Source-only NEON seasonal elapsed-time and source weather availability.

No observed same-genus trap overlap, corrected R or Z, population W/B,
climate values, trap coordinates or individual/source site IDs exported.
Source dates are real 3-night bout dates; weather availability is not
a meteorological measurement.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import date
from statistics import mean,median
import json,math
from pathlib import Path

from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.run_multiscale_density_estimability_release2026_v3 import _request_json
from analysis.neon_macro_site_selection_v1 import site_metadata_index

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_macro_temporal_weather_source_audit_v1.json"
NEON_SITES="https://data.neonscience.org/api/v0/sites?release=RELEASE-2026"
PRODUCTS={
    "single_air_temperature":"DP1.00002.001",
    "summary_weather":"DP4.00001.001",
    "precip_weighing":"DP1.00044.001",
    "precip_tipping":"DP1.00045.001",
    "precip_old_retired":"DP1.00006.001",
}
RELEASE="RELEASE-2026"

def require(ok:bool,why:str)->None:
    if not ok:raise ValueError("NEON_MACRO_TEMPORAL_SOURCE_STOP: "+why)

def _month(d:date)->str:
    return f"{d.year:04d}-{d.month:02d}"

def _summary(values:list[int|float])->dict:
    if not values:
        return {"n":0}
    v=sorted(values)
    n=len(v)
    return {"n":n,"min":min(v),"median":median(v),"mean":mean(v),"max":max(v)}

def weather_release_months(site:dict)->dict[str,set[str]]:
    """Use exactly named published release months, never unversioned months."""
    products=site.get("dataProducts")
    require(isinstance(products,list),"site has no official weather product entries")
    result={x:set() for x in PRODUCTS.values()}
    for product in products:
        if not isinstance(product,dict):
            continue
        code=str(product.get("dataProductCode") or "")
        if code not in result:
            continue
        rel=product.get("availableReleases")
        if not isinstance(rel,list):
            continue
        for row in rel:
            if not isinstance(row,dict) or row.get("release")!=RELEASE:
                continue
            months=row.get("availableMonths")
            if not isinstance(months,list):
                raise ValueError("Published release months malformed")
            result[code].update(str(m) for m in months if isinstance(m,str)
                                and len(m)==7 and m[4]=="-")
    return result

def bout_start_gap(unit:dict)->int:
    dates_a=unit.get("capture_dates_A")
    dates_b=unit.get("capture_dates_B")
    require(isinstance(dates_a,tuple) and isinstance(dates_b,tuple)
            and len(dates_a)==len(dates_b)==3
            and all(isinstance(x,date) for x in dates_a+dates_b),
            "original three original capture dates missing")
    require(len(set(dates_a))==3 and len(set(dates_b))==3,
            "source three-day event has duplicated dates")
    gap=(min(dates_b)-min(dates_a)).days
    require(0<gap<400,"original between-season gap invalid")
    return gap

def temporal_climate_source_audit(
    exact_two:list[dict], strict_three:list[dict],
    source_sites:list[dict],*,expected_two=158,expected_three=58,
)->dict:
    require(len(exact_two)==expected_two and len(strict_three)==expected_three,
            "original exactly-two/three-plus source cohorts drifted")
    original={u["site"] for u in exact_two+strict_three}
    lookup={str(row.get("siteCode") or ""):row
            for row in source_sites if isinstance(row,dict) and row.get("siteCode") in original}
    require(set(lookup)==original,"official metadata missing original source physical site")
    geo=site_metadata_index(list(lookup.values()))
    avail={s:weather_release_months(lookup[s]) for s in sorted(original)}
    two_keys={(u["site"],tuple(u["site_plot"]),u["season_ordinal"]) for u in exact_two}
    three_keys={(u["site"],tuple(u["site_plot"]),u["season_ordinal"]) for u in strict_three}
    require(len(two_keys)==len(exact_two) and len(three_keys)==len(strict_three)
            and not(two_keys & three_keys),"original seasonal pair groups not disjoint")

    def cohort(units:list[dict])->dict:
        gaps=[]
        pairs=[]
        bysite=defaultdict(list)
        transitions=Counter()
        starts=Counter()
        sites_with_no_period_variation=set()
        for u in units:
            g=bout_start_gap(u)
            site=u["site"]
            q=u["season_ordinal"]
            require(isinstance(q,int) and not isinstance(q,bool),
                    "original time ordinal malformed")
            dates=tuple(u["capture_dates_A"])+tuple(u["capture_dates_B"])
            months=frozenset(_month(d) for d in dates)
            gaps.append(g)
            bysite[site].append(g)
            transitions[str(q%4)]+=1
            starts[str(min(u["capture_dates_A"]).year)]+=1
            pairs.append((site,months))
        supported_sites={s for s,z in bysite.items() if len(z)>=2 and len(set(z))>=2}
        broad_sites={s for s,z in bysite.items() if len(z)>=2 and max(z)-min(z)>=30}
        within_site_range=[max(z)-min(z) for z in bysite.values() if len(z)>=2]
        weather={}
        for name,code in PRODUCTS.items():
            eligible=[(site,mos) for site,mos in pairs if mos<=avail[site][code]]
            weather[name]={
                "code":code,
                "source_pair_complete_month_availability":len(eligible),
                "source_pair_fraction":len(eligible)/len(pairs) if pairs else None,
                "source_physical_sites_with_at_least_one_complete_pair":len({s for s,_ in eligible}),
                "source_pair_availability_is_not_climate_measurement":True,
            }
        precodes=[PRODUCTS[x] for x in ("precip_weighing","precip_tipping","precip_old_retired")]
        precip_any=[(site,mos) for site,mos in pairs
                    if any(mos<=avail[site][code] for code in precodes)]
        overlap=[(site,mos) for site,mos in pairs
                 if mos<=avail[site][PRODUCTS["single_air_temperature"]]
                 and any(mos<=avail[site][code] for code in precodes)]
        return {
            "pairs":len(units),
            "physical_sites":len(bysite),
            "ecological_domains":len({geo[s]["domain"] for s in bysite}),
            "calendar_gap_days_source_only":_summary(gaps),
            "original_start_year_counts":dict(sorted(starts.items())),
            "season_transition_q_mod4_counts":dict(sorted(transitions.items())),
            "sites_with_at_least_two_pairs_and_nonconstant_lag":len(supported_sites),
            "sites_with_at_least_two_pairs_and_30day_plus_lag_range":len(broad_sites),
            "within_site_gap_range_days_for_sites_with_two_plus_pairs":_summary(within_site_range),
            "source_weather_month_coverage":weather,
            "any_single_consistent_precip_product_months_pairs":len(precip_any),
            "both_air_temperature_and_a_single_consistent_precip_product_pairs":len(overlap),
            "sites_with_air_temperature_and_consistent_precip_pairs":len({s for s,_ in overlap}),
            "no_daily_temperature_or_precipitation_value_downloaded":True,
            "actual_original_captures_dates_not_exported":True,
        }
    two=cohort(exact_two)
    three=cohort(strict_three)
    require(two["pairs"]+three["pairs"]==216 and two["physical_sites"]==30 and three["physical_sites"]==14,
            "original 216 source pairs/30/14 site source support changed")
    lag_gate={
        "min_informative_original_two_genus_pairs":100,
        "min_sites_with_two_plus_distinct_lags":15,
        "min_sites_with_lag_range_30plus_days":8,
        "min_distinct_transition_categories":3,
        "two_genus_original_pairs":two["pairs"],
        "source_sites_with_distinct_lag":two["sites_with_at_least_two_pairs_and_nonconstant_lag"],
        "source_sites_with_30plus_day_lag_range":two["sites_with_at_least_two_pairs_and_30day_plus_lag_range"],
        "original_transition_categories":sum(n>0 for n in two["season_transition_q_mod4_counts"].values()),
        "no_effect_opened":True,
    }
    # Exact-null informative count must be checked by separate original
    # effect replay: this source-only check cannot infer that 150 source
    # units are all nondegenerate, even though a prior receipt says 150.
    lag_gate["source_only_non_effect_prerequisites_pass"]=(
        two["sites_with_at_least_two_pairs_and_nonconstant_lag"]>=15
        and two["sites_with_at_least_two_pairs_and_30day_plus_lag_range"]>=8
        and lag_gate["original_transition_categories"]>=3
    )
    weather_gate={
        "temperature_and_one_consistent_precip_source_min_original_pairs":100,
        "minimum_independent_physical_sites":20,
        "source_pair_temperature_and_precip_coverage":two["both_air_temperature_and_a_single_consistent_precip_product_pairs"],
        "source_physical_site_weather_coverage":two["sites_with_air_temperature_and_consistent_precip_pairs"],
        "weather_availability_sufficient_to_plan_external_original_month_download":(
            two["both_air_temperature_and_a_single_consistent_precip_product_pairs"]>=100
            and two["sites_with_air_temperature_and_consistent_precip_pairs"]>=20
        ),
        "availability_not_quality_control_or_actual_site_grid_weather":True,
    }
    return {
        "schema":"neon.macro.elapsed_time_weather_original_source.v1",
        "status":"SOURCE_ONLY_LAG_AND_TOWER_WEATHER_AVAILABILITY_AUDITED",
        "original_source_window":"RELEASE-2026 2015-04..2026-09",
        "exactly_two_genera_source":two,
        "original_three_plus_genera_source":three,
        "lag_effect_source_precheck":lag_gate,
        "tower_weather_release_month_availability_gate":weather_gate,
        "scientific_scope":{
            "source_original_exactly_two_pairs":158,
            "source_original_three_plus_pairs":58,
            "total_original_2plus_pairs":216,
            "original_source_identification_and_effort_unchanged":True,
            "old_primary_effect_or_new_exact_two_R_Z_refitted":False,
            "source_site_capture_dates_lat_lon_site_ID_animal_IDs_exported":False,
            "product_availability_is_not_captured_microhabitat":True,
            "weather_months_do_not_imply_QC_pass_or_causal_exposure":True,
            "new_climate_by_R_or_gap_by_R_effect_computed":False,
            "original_density_generality_5of8_failure_unchanged":True,
        },
    }

def run()->dict:
    strict,two,source=original_sources_for_two_genus()
    raw=_request_json(NEON_SITES)
    items=raw.get("data")
    require(isinstance(items,list),"NEON published site list unavailable")
    needed={u["site"] for u in strict+two}
    subset=[z for z in items if isinstance(z,dict) and z.get("siteCode") in needed]
    report=temporal_climate_source_audit(two,strict,subset)
    report["source_provenance"]={
        **source,
        "official_NEON_sites_availability_release":RELEASE,
        "source_rebuilt_2plus_original_216_pairs":True,
        "no_source_location_or_animal_identity_exported":True,
    }
    return report

def main()->int:
    try:
        r=run()
        code=0
    except Exception as e:
        r={"schema":"neon.macro.elapsed_time_weather_original_source.v1",
           "status":"STOP_ORIGINAL_SOURCE_OR_RELEASE_WEATHER_SCHEMA",
           "error_class":type(e).__name__,
           "old_3plus_and_new_2_genus_spatial_effects_unchanged":True,
           "source_identifiers_suppressed":True}
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(r,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
