#!/usr/bin/env python3
"""Actual published multi-year NEON AOP CHM flight-month support census.

Effect-blind: ONLY the original mammal 58-pair historical capture dates and
official AOP acquisition-month metadata. Never selects a CHM image by
canopy value, taxon identity or old recurrence Z. Month support != raster
tile/vegetation habitat validity.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import date,datetime,timezone
from statistics import median
import json
import os
import re
from pathlib import Path

from analysis.run_neon_habitat_source_link_v1 import (
    reconstruct,_request_json,BASE,TOKEN_ENV,digest
)
from analysis.neon_e5_chm_pilot_v1 import PRODUCT,RELEASE
from analysis.neon_3000_chm_source_qa_v1 import month_gap

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_aop_historical_flight_month_coverage_v1.json"
MONTH_RE=re.compile(r"^(20(?:1[3-9]|2[0-5]))-(0[1-9]|1[0-2])$")


def nearest_flight_month(day:date, published_months:list[str]):
    """Choose nearest calendar MONTH; tie prefers earlier, not future.

    This is a metadata source-availability rule only, not ecological
    image selection, tree-cover inference, or exact acquisition-date matching.
    """
    if not isinstance(day,date):
        raise ValueError("Original capture date required")
    if not isinstance(published_months,(tuple,list)):
        raise ValueError("Official month collection required")
    if any(not isinstance(m,str) or not MONTH_RE.fullmatch(m) for m in published_months):
        raise ValueError("Invalid official publication month")
    choices=sorted(set(published_months))
    if not choices:
        return None,None
    result=min(choices,key=lambda m:(abs(month_gap(day,m)),month_gap(day,m)>0,m))
    return result,month_gap(day,result)


def audit_flight_month_availability(units,site_months,*,expected_pairs=58,
                                    expected_plots=30,expected_sites=14):
    if len(units)!=expected_pairs:
        raise ValueError("Original frozen source pair count drifted")
    plots=set();sites=set();byplotday={};gaps=[];pair3=pair12=pair24=0
    pair3_prior=pair12_prior=0
    same_flight_pair=0
    distinct_selected=set()
    for u in units:
        site=u["site"]
        plot=tuple(u["site_plot"])
        ds=tuple(u["capture_dates_A"])+tuple(u["capture_dates_B"])
        if len(ds)!=6 or len(set(ds))!=6 or plot[0]!=site:
            raise ValueError("Original six-date or plot identity invalid")
        plots.add(plot);sites.add(site)
        chosen=[nearest_flight_month(d,site_months.get(site,[])) for d in ds]
        gg=[g for _,g in chosen]
        gaps.extend(gg)
        for d,select in zip(ds,chosen):
            byplotday[(plot,d)]=select
            if select[0] is not None:distinct_selected.add((plot,select[0]))
        pair3+=int(all(g is not None and abs(g)<=3 for g in gg))
        pair12+=int(all(g is not None and abs(g)<=12 for g in gg))
        pair24+=int(all(g is not None and abs(g)<=24 for g in gg))
        pair3_prior+=int(all(g is not None and -3<=g<=0 for g in gg))
        pair12_prior+=int(all(g is not None and -12<=g<=0 for g in gg))
        same_flight_pair+=int(all(m is not None for m,g in chosen)
                             and len({m for m,g in chosen})==1)
    if len(sites)!=expected_sites or len(plots)!=expected_plots or set(site_months)!=sites:
        raise ValueError("Physical site and plot source mismatch")
    good=[g for g in gaps if g is not None]
    per_site=[len(set(x)) for x in site_months.values()]
    return {
        "schema":"neon.macro.AOP_original_flight_month_source_v1",
        "status":"MULTIYEAR_OFFICIAL_AOP_MONTH_AVAILABILITY_AUDITED_NOT_HABITAT_EFFECT",
        "original_capture_pairs":len(units),
        "original_capture_plots":len(plots),
        "original_physical_sites":len(sites),
        "original_repeated_capture_day_attempts":len(gaps),
        "original_distinct_plot_day_keys":len(byplotday),
        "source_site_months_per_site_summary":{
            "min":min(per_site),"median":median(per_site),"max":max(per_site)
        },
        "sites_with_one_or_more_flight_month":sum(n>0 for n in per_site),
        "total_unique_site_flight_month_pairs":sum(per_site),
        "distinct_plot_selected_month_keys":len(distinct_selected),
        "original_day_attempts_with_any_published_month":len(good),
        "closest_month_abs_lag_3_or_less_day_attempts":sum(abs(g)<=3 for g in good),
        "closest_month_abs_lag_12_or_less_day_attempts":sum(abs(g)<=12 for g in good),
        "closest_month_abs_lag_24_or_less_day_attempts":sum(abs(g)<=24 for g in good),
        "closest_month_earlier_than_capture_day_attempts":sum(g<0 for g in good),
        "closest_month_later_than_capture_day_attempts":sum(g>0 for g in good),
        "closest_month_same_calendar_month_attempts":sum(g==0 for g in good),
        "pairs_all_six_days_within_3_months":pair3,
        "pairs_all_six_days_within_12_months":pair12,
        "pairs_all_six_days_within_24_months":pair24,
        "pairs_all_six_days_within_3_months_only_not_later_acquisition":pair3_prior,
        "pairs_all_six_days_within_12_months_only_not_later_acquisition":pair12_prior,
        "pairs_all_six_days_closest_month_same_single_flight":same_flight_pair,
        "closest_source_month_gap_summary_abs":{
            "min":min(map(abs,good)) if good else None,
            "median":median(map(abs,good)) if good else None,
            "max":max(map(abs,good)) if good else None
        },
        "nearest_month_tie_prefer_prior_acquisition":True,
        "calendar_month_is_not_exact_aerial_flight_date":True,
        "AOP_month_metadata_does_not_prove_tile_coverage_at_mammal_trap":True,
        "no_source_canopy_values_ever_opened":True,
        "original_mammal_genus_space_effects_unchanged":True,
        "true_mammal_habitat_or_genus_detection_not_estimated":True,
        "private_site_plot_day_month_pairs_exported":False,
    }


def run():
    token=os.environ.get(TOKEN_ENV,"").strip()
    if not token:raise RuntimeError("Original NEON source authorization missing")
    units,plots,sites,names,source=reconstruct(token)
    if (len(units),len(plots),len(sites))!=(58,30,14):
        raise RuntimeError("Original mammal cohort source denominator changed")
    meta=_request_json(BASE+"products/"+PRODUCT+"?release="+RELEASE,token=token)
    listing=meta.get("data",{}).get("siteCodes",[])
    if not isinstance(listing,list):
        raise ValueError("Original AOP source product metadata invalid")
    rows={item["siteCode"]:item for item in listing if isinstance(item,dict)
          and isinstance(item.get("siteCode"),str)}
    site_months={
        site:sorted({
            m for m in rows.get(site,{}).get("availableMonths",[])
            if isinstance(m,str) and MONTH_RE.fullmatch(m)
        })
        for site in sites
    }
    out=audit_flight_month_availability(units,site_months)
    out["source_provenance"]={
        "source":"NEON official RELEASE-2026 DP3.30015.001 site availability metadata",
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
        "official_product_metadata_digest":digest(meta),
        "original_mammal_source_verified":source,
        "no_full_CHM_manifest_or_any_pixel_measured_in_this_census":True,
        "not_a_retry_of_failed_GraphQL_v_REST_station_history":True,
        "genus_spatial_Z_not_refitted":True,
    }
    return out


def main():
    try:
        value=run()
        returncode=0
    except Exception as exc:
        value={
            "schema":"neon.macro.AOP_original_flight_month_source_v1",
            "status":"STOP_MULTYEAR_AOP_MONTH_SOURCE_OR_ORIGINAL_COHORT",
            "error_class":type(exc).__name__,
            "site_plot_capture_dates_and_observed_spatial_outcomes_exported":False,
            "original_genus_space_results_unchanged":True,
        }
        returncode=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(value,indent=2,sort_keys=True))
    return returncode

if __name__=="__main__":
    raise SystemExit(main())
