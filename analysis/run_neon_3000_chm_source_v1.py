#!/usr/bin/env python3
"""Source-only 3000-station CHM raster sampling plus capture-month temporal QA.

Uses canonical NEON REST station histories and checksum-verified RELEASE-2026
AOP CHM tiles. This is NOT a genus, habitat, catchability, movement, density,
or recurrence ecological effect fit. All private identity/location fields
stay in process memory; aggregate-only artifact.
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
import time
import urllib.error
from urllib.parse import quote,urlparse

import numpy as np
from rasterio.io import MemoryFile
from rasterio.windows import Window

from analysis.run_neon_habitat_source_link_v1 import (
    reconstruct,_request_json,BASE,TOKEN_ENV,digest
)
from analysis.neon_dated_station_location_v1 import station_labels_10x10
from analysis.neon_graphql_dated_station_source_v1 import (
    validate_history_projection,summarize_full_station_dated_coverage
)
from analysis.audit_neon_lineage_environmental_source_coverage_v1 import GEO_LOCATION_ISSUE_GRIDS
from analysis.neon_e5_chm_pilot_v1 import (
    PRODUCT,RELEASE,latest_month_before_cutoff
)
from analysis.neon_chm_monthly_source_v2 import monthly_chm_manifest,download_monthly_tile
from analysis.neon_3000_chm_source_qa_v1 import (
    STATIONS,original_month_source_alignment,aggregate_full_station_chm,
    protected_five_anchor_replay,VALID
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_3000_chm_source_20261028.json"
FIVE=ROOT/"results/neon_five_anchor_chm_source_receipt_20261020.json"
MAX_TILE_BYTES=280_000_000
STAGE="FROZEN_OLD_FIVE_ANCHOR_RECEIPT"
VALID_STAGES={
    "FROZEN_OLD_FIVE_ANCHOR_RECEIPT","ORIGINAL_RECAPTURE_SOURCE",
    "REST_FULL_STATION_HISTORIES","VALIDATE_ORIGINAL_SOURCE_DATES",
    "AOP_RELEASE_MONTHS","AOP_CHM_TILE_MANIFEST","AOP_TILE_DOWNLOAD",
    "CANOPY_RASTER_PERSISTED_SOURCE_CHECK","AGGREGATE_SOURCE_HABITAT_COVERAGE"
}

def require(value,reason):
    if not value:
        raise RuntimeError("NEON_3000_CHM_SOURCE_STOP: "+reason)


def fetch_rest_station(job,token):
    """Privacy-preserving REST original history with bounded transport retries."""
    key, name=job
    url=BASE+"locations/"+quote(name,safe="")+"?history=true"
    for attempt in range(4):
        try:
            raw=_request_json(url,token=token)
            d=raw.get("data") if isinstance(raw,dict) else None
            require(isinstance(d,dict) and d.get("locationName")==name,
                    "Original official REST station identity mismatch")
            h=d.get("locationHistory")
            if not isinstance(h,list) or not h or any(not isinstance(r,dict) for r in h):
                return key,None,None,"SOURCE_HISTORY_MISSING"
            return key,d,digest(raw),None
        except urllib.error.HTTPError as exc:
            if exc.code in (400,404):
                return key,None,None,"SOURCE_STATION_NAME_NOT_FOUND"
            if exc.code in (429,500,502,503,504) and attempt<3:
                time.sleep(2**attempt)
                continue
            raise RuntimeError("Official REST station HTTP transport failed") from None
        except (urllib.error.URLError,TimeoutError,OSError):
            if attempt<3:
                time.sleep(2**attempt)
                continue
            raise RuntimeError("Official REST station transient exhausted") from None
    raise RuntimeError("Official REST retry count exhausted")


def sample_chm_tile(raw, items, *, expected_source_tif=True):
    """Sample original projected named points from ONE verified tile in RAM.

    items is a private sequence of (station_key,x,y,EPSG,assumed_U).
    No coordinate/height output may be serialized except aggregated statistics.
    """
    results={}
    with MemoryFile(raw) as mem,mem.open() as ds:
        if ds.count!=1 or ds.crs is None or any(abs(abs(v)-1)>1e-6 for v in ds.res):
            return {key:{"status":"CHM_SOURCE_RASTER_SCHEMA_INVALID"} for key,*_ in items}
        if expected_source_tif and (ds.width!=1000 or ds.height!=1000):
            return {key:{"status":"CHM_TILE_NOT_1000_PIXEL_SQUARE"} for key,*_ in items}
        if abs(ds.transform.b)>1e-8 or abs(ds.transform.d)>1e-8:
            return {key:{"status":"CHM_SOURCE_RASTER_ROTATED"} for key,*_ in items}
        actual_epsg=ds.crs.to_epsg()
        for key,x,y,epsg,u in items:
            if actual_epsg!=epsg:
                results[key]={"status":"STATION_TO_RASTER_CRS_MISMATCH"}
                continue
            if not math.isfinite(x) or not math.isfinite(y):
                results[key]={"status":"NONFINITE_SOURCE_STATION"}
                continue
            row,col=ds.index(x,y)
            if not (0<=row<ds.height and 0<=col<ds.width):
                results[key]={"status":"SOURCE_STATION_OUTSIDE_NAMED_TILE"}
                continue
            pixel=ds.read(1,window=Window(col,row,1,1),masked=True)
            if np.ma.is_masked(pixel[0,0]) or not math.isfinite(float(pixel[0,0])):
                results[key]={"status":"CHM_PIXEL_MASKED"}
                continue
            height=float(pixel[0,0])
            if u is None or not math.isfinite(u) or u<0 or u>50:
                results[key]={"status":"STATION_UNCERTAINTY_NOT_QUALIFIED"}
                continue
            n=max(1,math.ceil(float(u)+math.sqrt(.5)))
            left=max(0,col-n); right=min(ds.width,col+n+1)
            top=max(0,row-n); bottom=min(ds.height,row+n+1)
            w=ds.read(1,window=Window(left,top,right-left,bottom-top),masked=True)
            masked=np.ma.getmaskarray(w)|(~np.isfinite(w.data))
            candidates=w.data[~masked]
            clipped=(left!=col-n or top!=row-n or right!=col+n+1 or bottom!=row+n+1)
            results[key]={
                "status":VALID,"height_m":height,"uncertainty_window_clipped":clipped,
                "uncertainty_window_valid_fraction":float(candidates.size/w.size),
                "window_min":float(candidates.min()) if candidates.size else None,
                "window_max":float(candidates.max()) if candidates.size else None,
            }
    return results


def run():
    global STAGE
    token=os.environ.get(TOKEN_ENV,"").strip()
    require(bool(token),"Original source token missing")
    old=json.loads(FIVE.read_text(encoding="utf-8"))
    require(old["status"]=="FIVE_NAMED_CHM_REFERENCE_ANCHORS_AUDITED_NOT_HABITAT_EFFECT"
            and old["valid_anchors"]==150
            and old["valid_zero_canopy_anchors"]==93
            and old["zero_E5_reference_heights"]==19
            and old["plots_with_nonzero_five_anchor_canopy_range"]==14
            and old["original_plots"]==30,
            "Frozen published 150-point CHM source did not match")
    STAGE="ORIGINAL_RECAPTURE_SOURCE"
    units,cohort,sites,names,captured_source=reconstruct(token)
    require((len(units),len(cohort),len(sites))==(58,30,14)
            and all(len(names.get(key,set()))==1 for key in cohort),
            "Original 58/30/14 mammal source changed")
    require(tuple(STATIONS)==tuple(station_labels_10x10()),
            "Canonical original 100 station roster changed")
    jobs=[
        ((site,plot,station),next(iter(names[(site,plot)]))+"."+station)
        for site,plot in sorted(cohort) for station in STATIONS
    ]
    require(len(jobs)==3000 and len({n for _,n in jobs})==3000,
            "Original 3000 station labels not unique")

    STAGE="REST_FULL_STATION_HISTORIES"
    documents={};rest_sha=[];rest_error=Counter()
    with ThreadPoolExecutor(max_workers=8) as pool:
        for key,doc,sha,error in pool.map(lambda item:fetch_rest_station(item,token),jobs):
            documents[key]=doc
            if sha is not None:rest_sha.append(sha)
            if error is not None:rest_error[error]+=1
    require(len(documents)==3000 and len(rest_sha)==3000,
            "Original REST-only 3000 source histories no longer complete")
    flagged={(s,p) for s,p in cohort if p in GEO_LOCATION_ISSUE_GRIDS}
    require(len(flagged)==4,"Original flagged geolocation issue grids changed")

    STAGE="VALIDATE_ORIGINAL_SOURCE_DATES"
    historical=summarize_full_station_dated_coverage(
        units,documents,expected_pairs=58,expected_sites=14,
        expected_plots=30,min_pairs=40,min_sites=8,min_plots=20,
        historically_flagged_plots=flagged,
    )
    require(historical["status"]=="FULL_100_STATION_CAPTURE_DATE_SOURCE_GO"
            and historical["historically_projected_valid_attempts"]==34800
            and historical["fixed_original_station_date_attempts"]==34800,
            "Previously approved original source date coverage drifted")
    byplotdates=defaultdict(set)
    for u in units:
        plot=tuple(u["site_plot"])
        byplotdates[plot].update(tuple(u["capture_dates_A"])+tuple(u["capture_dates_B"]))
    require(sum(len(x) for x in byplotdates.values())==339,
            "Original 339 distinct plot-date opportunities changed")
    locations={}
    for key,doc in documents.items():
        plot=key[:2]
        records=[validate_history_projection(doc,d) for d in sorted(byplotdates[plot])]
        point=records[0]
        if any(r["xy"]!=point["xy"] or r["utm_epsg"]!=point["utm_epsg"]
               for r in records[1:]):
            raise RuntimeError("Station historical location shifted, cannot assign one CHM pixel")
        locations[key]=point
    byplotdirect=defaultdict(list)
    for key,loc in locations.items():
        u=loc["direct_source_uncertainty_m"]
        if u is not None:byplotdirect[key[:2]].append(u)
    require(len(byplotdirect)==30 and all(x for x in byplotdirect.values()),
            "No monument uncertainty in one or more source plots")
    assumed_U={
        key:loc["direct_source_uncertainty_m"]+1
        if loc["direct_source_uncertainty_m"] is not None
        else max(byplotdirect[key[:2]])+3
        for key,loc in locations.items()
    }

    STAGE="AOP_RELEASE_MONTHS"
    metadata=_request_json(BASE+"products/"+PRODUCT+"?release="+RELEASE,token=token)
    allsite=metadata.get("data",{}).get("siteCodes",[])
    require(isinstance(allsite,list),"Original AOP product metadata missing siteCodes")
    bysite={r["siteCode"]:r for r in allsite if isinstance(r,dict) and r.get("siteCode")}
    months={
        s:latest_month_before_cutoff(bysite.get(s,{}).get("availableMonths",[]))
        for s in sites
    }
    temporal=original_month_source_alignment(units,months)
    require(temporal["acquisition_year_site_counts"]==
            old["raster_acquisition_site_year_counts"]
            and temporal["site_flight_month_available"]==14,
            "Published original 14-site CHM acquisition month selection drifted")

    STAGE="AOP_CHM_TILE_MANIFEST"
    manifests={}
    manifest_sha=[]
    manifest_errors=Counter()
    for site in sorted(sites):
        m=months[site]
        try:
            siteurls=[
                url for url in bysite[site].get("availableDataUrls",[])
                if urlparse(url).hostname=="data.neonscience.org"
                and urlparse(url).path.rstrip("/").endswith("/"+m)
            ]
            require(len(siteurls)==1,"CHM monthly endpoint ambiguous")
            response=_request_json(siteurls[0],token=token)
            manifests[site]=monthly_chm_manifest(response,site,m)
            manifest_sha.append(digest(response))
        except Exception:
            manifests[site]=[]
            manifest_errors["CHM_SITE_MANIFEST_MISSING_OR_INVALID"]+=1

    selected={}
    station_tile={}
    preliminary={}
    for key,loc in sorted(locations.items()):
        site=key[0];x,y=loc["xy"]
        x0=math.floor(x/1000)*1000;y0=math.floor(y/1000)*1000
        options=[r for r in manifests.get(site,[]) if
                 r["tile_easting"]==x0 and r["tile_northing"]==y0]
        if len(options)!=1:
            preliminary[key]="CHM_NO_SINGLE_RELEASED_TILE_FOR_NAMED_STATION"
            continue
        tile=options[0]
        identity=(tile["site"],tile["month"],tile["name"])
        selected[identity]=tile
        station_tile[key]=identity
    total_bytes=sum(t["size"] for t in selected.values())
    require(total_bytes<=MAX_TILE_BYTES,
            "Frozen maximum 280 MB raster source budget exceeded")

    STAGE="AOP_TILE_DOWNLOAD"
    raster_bytes={}
    raster_sha=[]
    downloaded_checks=Counter()
    tile_errors=Counter()
    def download_one(item):
        tid,tile=item
        try:
            raw=download_monthly_tile(tile,token)
            return tid,raw,None
        except Exception as exc:
            return tid,None,type(exc).__name__
    with ThreadPoolExecutor(max_workers=4) as pool:
        for tid,raw,error in pool.map(download_one,sorted(selected.items())):
            if error:
                tile_errors["PROVIDER_CHM_SIZE_CHECKSUM_OR_TRANSPORT_ERROR"]+=1
            else:
                raster_bytes[tid]=raw
                raster_sha.append(hashlib.sha256(raw).hexdigest())
                downloaded_checks[selected[tid]["checksum_kind"]]+=1

    STAGE="CANOPY_RASTER_PERSISTED_SOURCE_CHECK"
    bytile=defaultdict(list)
    for key,ident in station_tile.items():
        loc=locations[key]
        bytile[ident].append((
            key,loc["xy"][0],loc["xy"][1],loc["utm_epsg"],assumed_U[key]
        ))
    pixelresults={}
    tile_read_errors=Counter()
    for tid,points in bytile.items():
        if tid not in raster_bytes:
            for key,*_ in points:
                pixelresults[key]={"status":"TILE_SOURCE_NOT_VERIFIED"}
            continue
        try:
            pixelresults.update(sample_chm_tile(raster_bytes[tid],points))
        except Exception:
            tile_read_errors["RASTER_DECODE_ERROR"]+=1
            for key,*_ in points:
                pixelresults[key]={"status":"CHM_RASTER_FAILED_TO_DECODE"}
    rows=[]
    for key in sorted(locations):
        row=pixelresults.get(key,{"status":preliminary.get(key,"CHM_NO_PIXEL_RESULT")})
        rows.append({
            "plot_key":key[:2],"station":key[2],"status":row["status"],
            "height_m":row.get("height_m"),
            "historically_flagged_plot":key[:2] in flagged,
        })
    replay=protected_five_anchor_replay(rows)
    require(replay["all_original_five_anchor_pixels_valid"]
            and replay["five_named_anchor_pixels_valid"]==150
            and replay["five_anchor_zero_pixels"]==93
            and replay["E5_zero_pixels"]==19
            and replay["plots_five_anchor_positive_canopy_range"]==14,
            "Previously reported real five-anchor canopy values not reproduced")

    STAGE="AGGREGATE_SOURCE_HABITAT_COVERAGE"
    summary=aggregate_full_station_chm(rows)
    windowvalid=[
        r for r in pixelresults.values()
        if r["status"]==VALID and r["window_min"] is not None
    ]
    return {
        "schema":"neon.macro.full100_chm_month_source_qa.v1",
        "status":"FULL_3000_STATION_CHM_SOURCE_AUDITED_NO_ECOLOGICAL_EFFECT",
        "original_captured_population":captured_source,
        "original_58_30_14_geographical_cohort_unchanged":True,
        "dated_REST_history_source_verified":historical["source_date_and_geographic_coverage_gate_passed"],
        "historically_date_valid_station_attempts":historical["historically_projected_valid_attempts"],
        "original_station_location_source_digest_set_sha256":digest(sorted(rest_sha)),
        "temporal_source_alignment":temporal,
        "canopy_source_coverage":summary,
        "previous_five_anchor_replay":replay,
        "CHM_monthly_manifest_digest_set":digest(sorted(manifest_sha)),
        "CHM_monthly_manifest_error_categories":dict(manifest_errors),
        "selected_source_unique_tiles":len(selected),
        "selected_source_tile_bytes":total_bytes,
        "provider_size_and_checksum_verified_tiles":len(raster_bytes),
        "provider_checksum_kinds":dict(downloaded_checks),
        "raster_download_error_categories":dict(tile_errors),
        "raster_read_error_categories":dict(tile_read_errors),
        "raster_local_sha256_digest_set":digest(sorted(raster_sha)),
        "uncertainty_window_station_pixels_valid":len(windowvalid),
        "uncertainty_window_clipped_at_tile_edge":sum(r["uncertainty_window_clipped"] for r in windowvalid),
        "uncertainty_window_zero_center_but_positive_neighborhood":sum(
            r["height_m"]==0 and r["window_max"]>0 for r in windowvalid),
        "uncertainty_window_positive_range":sum(
            r["window_max"]>r["window_min"] for r in windowvalid),
        "geoNEON_adjusted_uncertainty_is_assumed_not_confidence_bound":True,
        "source_acquisition_is_calendar_month_not_exact_flight_day":True,
        "source_coordinates_and_raster_data_or_heights_not_exported":True,
        "ecological_limits":{
            "canopy_height_does_not_measure_understory_shrub_ground_cover":True,
            "contemporaneous_vegetation_habitat_not_established_by_month_matching":True,
            "historical_2015_2026_capture_habitat_not_inferred_from_latest_2022_2024_AOP":True,
            "genus_specific_detection_not_identified":True,
            "genus_habitat_selection_or_recurrence_effect_not_fitted":True,
            "original_density_generality_5_of_8_failure_unchanged":True,
            "original_mammal_capture_space_recurrence_unchanged":True,
            "old_operability_18_of_158_and_temperature_79_of_80_STOP_unchanged":True,
            "old_graphql_vs_rest_equivalence_STOP_unchanged":True,
            "next":"Use source-year-appropriate environment plus independent detection/effort before a future held-out ecological mechanism test",
        },
        "source_retrieved_utc":datetime.now(timezone.utc).isoformat(),
    }


def main():
    global STAGE
    try:
        out=run()
        status=0
    except Exception as exc:
        out={
            "schema":"neon.macro.full100_chm_month_source_qa.v1",
            "status":"STOP_FULL_3000_CHM_SOURCE_OR_REPLAY",
            "safe_failure_stage":STAGE if STAGE in VALID_STAGES else "UNKNOWN_STAGE",
            "error_class":type(exc).__name__,
            "source_private_animal_station_site_dates_coordinates_urls_or_heights_exported":False,
            "old_positive_or_negative_ecological_endpoints_unchanged":True,
        }
        status=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return status


if __name__=="__main__":
    raise SystemExit(main())
