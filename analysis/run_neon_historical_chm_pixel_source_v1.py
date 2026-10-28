#!/usr/bin/env python3
"""Actual source-verified 2013-2025 AOP CHM near original mammal capture days.

No mammal capture response/Z or genus habitat effect is opened. All raw
sites, named locations, dates, UTM, per-trap heights are transient in RAM.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import hashlib
import json
import math
import os
from pathlib import Path
from urllib.parse import urlparse

from analysis.run_neon_habitat_source_link_v1 import (
    BASE,TOKEN_ENV,reconstruct,_request_json,digest
)
from analysis.run_neon_3000_chm_source_v1 import (
    fetch_rest_station,sample_chm_tile,require
)
from analysis.neon_graphql_dated_station_source_v1 import (
    validate_history_projection,summarize_full_station_dated_coverage
)
from analysis.neon_dated_station_location_v1 import station_labels_10x10
from analysis.audit_neon_lineage_environmental_source_coverage_v1 import (
    GEO_LOCATION_ISSUE_GRIDS
)
from analysis.neon_chm_monthly_source_v2 import (
    monthly_chm_manifest,download_monthly_tile
)
from analysis.neon_historical_chm_source_support_v1 import (
    frozen_selected_month_days,source_month_manifest_support,
    summarize_actual_historical_pixels
)
from analysis.run_neon_aop_historical_flight_month_v1 import (
    audit_flight_month_availability,MONTH_RE,PRODUCT,RELEASE
)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_historical_chm_actual_pixel_source_v1.json"
SOURCE_MONTH=ROOT/"results/neon_aop_multiyear_month_coverage_receipt_20261028.json"
SOURCE_LOCATION=ROOT/"results/neon_3000_rest_historical_source_receipt_20261028.json"
MAX_TILE_BYTES=350_000_000
PHASE="PRECHECK_FROZEN_HISTORICAL_SOURCE"
PHASES={
    "PRECHECK_FROZEN_HISTORICAL_SOURCE","ORIGINAL_MAMMAL_SOURCE",
    "FROZEN_SOURCE_FLIGHT_MONTHS","ORIGINAL_REST_NAMED_STATIONS",
    "ORIGINAL_CAPTURE_DATE_LOCATIONS","PUBLISHED_MONTHLY_AOP_MANIFESTS",
    "SELECT_HISTORICAL_STATION_TILES","VERIFY_PROVIDER_TIFF_BYTES",
    "SAMPLE_HISTORICAL_CHM_STATIONS","AGGREGATE_HISTORICAL_SOURCE_COVERAGE"
}

def _phase(text):
    global PHASE
    if text not in PHASES:raise AssertionError("Unrecognized source phase")
    PHASE=text

def run():
    token=os.environ.get(TOKEN_ENV,"").strip()
    require(bool(token),"NEON authorized source token unavailable")
    prev=json.loads(SOURCE_MONTH.read_text())
    geo=json.loads(SOURCE_LOCATION.read_text())
    require(prev["status"]=="MULTIYEAR_OFFICIAL_AOP_MONTH_AVAILABILITY_AUDITED_NOT_HABITAT_EFFECT"
        and prev["total_unique_site_flight_month_pairs"]==97
        and prev["pairs_all_six_days_within_12_months"]==36
        and prev["pairs_all_six_days_within_3_months"]==22
        and prev["pairs_all_six_days_within_12_months_only_not_later_acquisition"]==18
        and geo["status"]=="FULL_100_STATION_CAPTURE_DATE_SOURCE_GO"
        and geo["historically_projected_valid_attempts"]==34800,
        "Frozen 28 Oct independent metadata/source receipts changed")
    _phase("ORIGINAL_MAMMAL_SOURCE")
    units,plots,sites,names,original_source=reconstruct(token)
    require((len(units),len(plots),len(sites))==(58,30,14)
            and all(len(names.get(p,set()))==1 for p in plots),
            "Original RELEASE-2026 mammal source population drift")
    _phase("FROZEN_SOURCE_FLIGHT_MONTHS")
    meta=_request_json(BASE+"products/"+PRODUCT+"?release="+RELEASE,token=token)
    rows=meta.get("data",{}).get("siteCodes",[])
    require(isinstance(rows,list),"Original published AOP source site list invalid")
    bysite={r["siteCode"]:r for r in rows
            if isinstance(r,dict) and isinstance(r.get("siteCode"),str)}
    site_months={
        s:sorted({m for m in bysite.get(s,{}).get("availableMonths",[])
                  if isinstance(m,str) and MONTH_RE.fullmatch(m)})
        for s in sites
    }
    check=audit_flight_month_availability(units,site_months)
    for field,expected in (
        ("total_unique_site_flight_month_pairs",97),
        ("pairs_all_six_days_within_12_months",36),
        ("pairs_all_six_days_within_3_months",22),
        ("pairs_all_six_days_within_12_months_only_not_later_acquisition",18),
        ("original_distinct_plot_day_keys",339)):
        require(check[field]==expected,"Historical AOP metadata source changed")
    days,pairs=frozen_selected_month_days(units,site_months)
    stations=station_labels_10x10()
    require(len(stations)==100,"Mammal trap roster changed")
    jobs=[
        ((site,plot,station),next(iter(names[(site,plot)]))+"."+station)
        for site,plot in sorted(plots) for station in stations
    ]
    require(len(jobs)==3000 and len({n for key,n in jobs})==3000,
            "Private original named mammal stations drifted")
    _phase("ORIGINAL_REST_NAMED_STATIONS")
    documents={};history_sha=[]
    with ThreadPoolExecutor(max_workers=8) as pool:
        for key,doc,sha,err in pool.map(
            lambda j:fetch_rest_station(j,token),jobs
        ):
            if doc is not None: documents[key]=doc
            if sha is not None:history_sha.append(sha)
    require(len(documents)==3000,"Original canonical REST 3000 stations incomplete")
    flagged={(s,p) for s,p in plots if p in GEO_LOCATION_ISSUE_GRIDS}
    require(len(flagged)==4,"Four original geolocation issue grids changed")
    _phase("ORIGINAL_CAPTURE_DATE_LOCATIONS")
    base=summarize_full_station_dated_coverage(units,documents,
        historically_flagged_plots=flagged)
    require(base["status"]=="FULL_100_STATION_CAPTURE_DATE_SOURCE_GO"
            and base["historically_projected_valid_attempts"]==34800,
            "Original all-station capture dates not preserved")

    # Only original days temporally within the preselected 12-month window
    # may enter actual AOP raster sampling. All 58 pairs remain denominators.
    selected_days={
        key:(month,lag) for key,(month,lag) in days.items()
        if month is not None and lag is not None and abs(lag)<=12
    }
    selected_months={(plot[0],month) for (plot,day),(month,lag) in days.items() if month}
    _phase("PUBLISHED_MONTHLY_AOP_MANIFESTS")
    manifests={};mh=[];errors=Counter()
    for site,month in sorted(selected_months):
        links=[
            url for url in bysite.get(site,{}).get("availableDataUrls",[])
            if urlparse(url).hostname=="data.neonscience.org"
            and urlparse(url).path.rstrip("/").endswith("/"+month)
        ]
        if len(links)!=1:
            manifests[(site,month)]=None
            errors["NO_UNIQUE_ORIGINAL_RELEASE_MONTH_URL"]+=1
            continue
        try:
            payload=_request_json(links[0],token=token)
            manifests[(site,month)]=monthly_chm_manifest(payload,site,month)
            mh.append(digest(payload))
        except Exception:
            manifests[(site,month)]=None
            errors["ORIGINAL_MONTH_CHM_MANIFEST_RETRIEVAL_INVALID"]+=1
    manifests_summary=source_month_manifest_support(units,site_months,manifests)
    require(manifests_summary["original_pairs_with_closest_AOP_month_abs_lag12"]==36,
            "Source months not same 36 original close pairs")

    # For every selected date, source coordinates and uncertainty are
    # computed from actual date-effective REST histories in RAM.
    _phase("SELECT_HISTORICAL_STATION_TILES")
    chosen_tiles={}
    points_by_tile=defaultdict(list)
    missing=Counter()
    day_selected_valid_count={key:0 for key in selected_days}
    unique_targets=0
    for (plot,day),(month,lag) in sorted(selected_days.items()):
        site=plot[0]
        source_rows=[]
        for station in stations:
            key=(site,plot[1],station)
            detail=validate_history_projection(documents[key],day)
            source_rows.append((key,detail))
        direct=[d["direct_source_uncertainty_m"] for key,d in source_rows
                if d["direct_source_uncertainty_m"] is not None]
        require(bool(direct),"Original one-monument-source uncertainty changed")
        maxu=max(direct)
        manifest=manifests.get((site,month))
        for (s,p,station),detail in source_rows:
            unique_targets+=1
            if not manifest:
                missing["MISSING_OFFICIAL_MONTHLY_CHM_MANIFEST"]+=1
                continue
            x,y=detail["xy"]
            tx=1000*math.floor(x/1000);ty=1000*math.floor(y/1000)
            options=[r for r in manifest
                     if r["tile_easting"]==tx and r["tile_northing"]==ty]
            if len(options)!=1:
                missing["NO_SINGLE_OFFICIAL_CHM_TILE_AT_STATION"]+=1
                continue
            tile=options[0]
            tid=(tile["site"],tile["month"],tile["name"])
            if tid in chosen_tiles and chosen_tiles[tid]!=tile:
                raise ValueError("Official duplicate tile metadata differs")
            chosen_tiles[tid]=tile
            u=detail["direct_source_uncertainty_m"]
            adjusted=(float(u)+1 if u is not None else float(maxu)+3)
            points_by_tile[tid].append(
                ((plot,day,station),x,y,detail["utm_epsg"],adjusted)
            )
    nbytes=sum(t["size"] for t in chosen_tiles.values())
    total_source_rows=len(selected_days)*100
    require(unique_targets==total_source_rows,"Historical day station denominator changed")

    # Protect against unbounded historic AOP downloads; no alternate
    # month selection or selective source-site subset after results.
    if nbytes>MAX_TILE_BYTES:
        return {
            "schema":"neon.macro.historical_CHM_true_pixels_source.v1",
            "status":"STOP_ORIGINAL_HISTORICAL_CHM_TILE_DOWNLOAD_BUDGET",
            "source_manifest":manifests_summary,
            "metadata_month_source":check,
            "estimated_original_unique_bytes":nbytes,
            "frozen_byte_budget":MAX_TILE_BYTES,
            "source_selection_not_revised":True,
            "no_genus_habitat_or_detection_effect":True,
        }

    _phase("VERIFY_PROVIDER_TIFF_BYTES")
    downloaded={};raster_sha=[];raster_errors=Counter()
    def one(x):
        tid,tile=x
        try: return tid,download_monthly_tile(tile,token),None
        except Exception: return tid,None,"CHM_DOWNLOAD_OR_CHECKSUM_ERROR"
    with ThreadPoolExecutor(max_workers=4) as pool:
        for tid,raw,error in pool.map(one,sorted(chosen_tiles.items())):
            if raw is not None:
                downloaded[tid]=raw
                raster_sha.append(hashlib.sha256(raw).hexdigest())
            else:
                raster_errors[error]+=1
    _phase("SAMPLE_HISTORICAL_CHM_STATIONS")
    observed={};pixel_status=Counter()
    uncertainty_range_nonzero=0
    uncertainty_clipped=0
    for tid,items in points_by_tile.items():
        if tid not in downloaded:
            for private_key,*_ in items:
                observed[private_key]={"status":"CHM_TILE_NOT_CHECKSUM_VALID"}
            continue
        try:
            observed.update(sample_chm_tile(downloaded[tid],items))
        except Exception:
            for private_key,*_ in items:
                observed[private_key]={"status":"CHM_TILE_RASTER_READ_INVALID"}
    for (plot,day,station),row in observed.items():
        status=row["status"];pixel_status[status]+=1
        if status=="VALID_REFERENCE_PIXEL":
            day_selected_valid_count[(plot,day)]+=1
            if row.get("uncertainty_window_clipped"):
                uncertainty_clipped+=1
            if row.get("window_min") is not None and row.get("window_max") is not None:
                uncertainty_range_nonzero+=int(row["window_max"]>row["window_min"])
    pixel_status["NO_UNIQUE_ORIGINAL_TILE_AT_LOCATION"]=sum(missing.values())
    require(sum(pixel_status.values())==total_source_rows,
            "Original station×day selected source denominator drifted")
    _phase("AGGREGATE_HISTORICAL_SOURCE_COVERAGE")
    actual=summarize_actual_historical_pixels(units,site_months,day_selected_valid_count)
    within12=actual.get("within12_actually_qualified_pairs",0)
    distinct_sites=actual["qualified_physical_sites_by_class"]["within12"]
    distinct_plots=actual["qualified_original_plots_by_class"]["within12"]
    source_go=within12>=20 and distinct_sites>=8 and distinct_plots>=12
    return {
        "schema":"neon.macro.historical_CHM_true_pixels_source.v1",
        "status":("HISTORIC_CHM_SOURCE_SUPPORT_GO_NOT_BIOLOGICAL_EFFECT"
                  if source_go else "STOP_HISTORIC_CHM_SOURCE_SUPPORT_NOT_GENUS_EFFECT"),
        "original_RECAPTURE_source":original_source,
        "original_historical_REST_positions":"FULL_100_STATION_CAPTURE_DATE_SOURCE_GO",
        "verified_original_58_pairs_30_plots_14_sites":True,
        "original_geolocation_issue_grids_retained":4,
        "recorded_capture_month_metadata_selection":check,
        "historical_monthly_manifest_source":manifests_summary,
        "manifest_errors_by_class":dict(errors),
        "manifest_response_sha256_set":digest(sorted(mh)),
        "actual_historical_CHM_1m_pixel_support":actual,
        "source_day_stations_in_selected_12month_window":total_source_rows,
        "actual_1m_pixel_status_counts":dict(sorted(pixel_status.items())),
        "unique_source_selected_CHM_tiles":len(chosen_tiles),
        "provider_checksum_size_verified_tiles":len(downloaded),
        "estimated_selected_unique_raster_bytes":nbytes,
        "download_error_counts":dict(sorted(raster_errors.items())),
        "raster_response_SHA256_set":digest(sorted(raster_sha)),
        "location_history_response_SHA256_set":digest(sorted(history_sha)),
        "uncertainty_window_nonzero_height_range_station_days":uncertainty_range_nonzero,
        "uncertainty_window_clipped_source_station_days":uncertainty_clipped,
        "predeclared_source_minimum_pairs":20,
        "predeclared_source_minimum_physical_sites":8,
        "predeclared_source_minimum_plots":12,
        "actual_source_go_not_ecological_go":source_go,
        "source_retrieved_utc":datetime.now(timezone.utc).isoformat(),
        "no_private_site_plot_trap_day_coordinates_or_heights_exported":True,
        "AOP_acquisition_month_not_exact_flight_day":True,
        "AOP_CHM_not_ground_shrub_or_rodent_detection":True,
        "genus_or_recapture_response_not_recomputed":True,
        "original_spatial_recurrence_z_and_failed_other_gates_unchanged":True,
        "habitat_vs_catchability_mechanism_not_identified":True,
    }

def main():
    global PHASE
    try:
        result=run()
        code=0 # A scientific source STOP after valid checks is still recorded.
    except Exception as exc:
        result={
            "schema":"neon.macro.historical_CHM_true_pixels_source.v1",
            "status":"STOP_SOURCE_INFRASTRUCTURE_OR_ORIGINAL_COHORT",
            "failure_stage":PHASE if PHASE in PHASES else "UNKNOWN_PHASE",
            "error_class":type(exc).__name__,
            "no_original_animal_station_geolocation_dates_or_tile_urls_exported":True,
            "original_neon_spatial_ecological_results_not_refitted":True,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
