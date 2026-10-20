#!/usr/bin/env python3
"""Five exact, source-named NEON mammal grid-anchor CHM GeoTIFF pixel pilot.

The biological motivation is within-plot *environmental source coverage*.
This file does NOT join genus/individual capture patterns with CHM heights,
fit habitat or detection effects, or change previously corrected positive
seasonal lineage recurrence. Every plot remains in the original 30/14 set.

Download 2015–2025 latest advertised RELEASE-2026 CHM tiles using the
NEON monthly source URL; verify declared provider byte-size/CRC32C/MD5
against actual downloaded bytes before reading 1-m rasters. Raw plot IDs,
anchor coordinates, tile URLs and individual heights are private RAM only.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import math
import os
from pathlib import Path
from statistics import median
from urllib.parse import urlparse
import json

from analysis.run_neon_habitat_source_link_v1 import (
    reconstruct, location_query, _request_json, BASE, TOKEN_ENV, digest,
)
from analysis.neon_habitat_location_link_v1 import ANCHORS
from analysis.neon_e5_chm_pilot_v1 import (
    PRODUCT, RELEASE, latest_month_before_cutoff, inspect_reference_pixel,
)
from analysis.neon_chm_monthly_source_v2 import monthly_chm_manifest, download_monthly_tile
from analysis.run_neon_e5_chm_pilot_v1 import explicit_epsg
from analysis.audit_neon_lineage_environmental_source_coverage_v1 import (
    GEO_LOCATION_ISSUE_GRIDS,
)
from analysis.neon_five_anchor_chm_source_v1 import (
    aggregate_five_anchor_height_support,
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_five_anchor_chm_source_v1.json"
FROZEN_E5=ROOT/"results/neon_e5_chm_reference_pixels_receipt_20261020.json"
MAX_DOWNLOAD_BYTES=280_000_000


def require(ok,reason):
    if not ok:
        raise RuntimeError("ORIGINAL_SOURCE_FIVE_ANCHOR_STOP: "+reason)


def run():
    token=os.environ.get(TOKEN_ENV,"").strip()
    if not token:raise RuntimeError("original NEON RELEASE-2026 data credential unavailable")
    e5=json.loads(FROZEN_E5.read_text(encoding="utf-8"))
    require(
        e5["status"]=="ACTUAL_REFERENCE_PIXELS_READ_NOT_TRAP_HABITAT_EVIDENCE"
        and e5["valid_reference_pixels"]==30
        and e5["sites_with_valid_reference_pixel"]==14
        and e5["valid_reference_height_m_summary"]["zero_values"]==19
        and e5["fixed_original_plots"]==30,
        "original E5 real raster source result unavailable",
    )
    units,cohort,sites,names,source=reconstruct(token)
    require((len(units),len(cohort),len(sites))==(58,30,14),
            "fixed seasonal source 58/30/14 cohort changed")
    require(all(len(names.get(key,set()))==1 for key in cohort),
            "original fixed cohort plot namedLocation must be unique")
    require(tuple(ANCHORS)==("A1","A10","J1","J10","E5"),
            "original source five anchor names changed")

    location_jobs=[
        (key,anchor,next(iter(names[key]))+"."+anchor)
        for key in sorted(cohort) for anchor in ANCHORS
    ]
    anchors={}
    location_errors=Counter()
    response_digests=[]
    with ThreadPoolExecutor(max_workers=4) as ex:
        for key,anchor,loc,error,raw_sha in ex.map(
            lambda job: location_query(job,token),location_jobs
        ):
            if error:
                location_errors["SOURCE_LOCATION_QUERY_OR_PARSE_FAILED"]+=1
            else:
                anchors[(key,anchor)]=loc
                response_digests.append(raw_sha)

    meta=_request_json(BASE+"products/"+PRODUCT+"?release="+RELEASE,token=token)
    entries=meta.get("data",{}).get("siteCodes",[])
    if not isinstance(entries,list):raise ValueError("CHM source site availability schema")
    bysite={item["siteCode"]:item for item in entries}
    choices={
        site:latest_month_before_cutoff(
            bysite.get(site,{}).get("availableMonths",[])
        ) for site in sites
    }
    source_years=Counter()
    manifests={}
    manifest_errors=Counter()
    manifest_hashes=[]
    for site in sorted(sites):
        month=choices[site]
        if month is None:
            manifest_errors["SITE_NO_RELEASED_ACQUISITION_MONTH"]+=1
            manifests[site]=[]
            continue
        source_years[month[:4]]+=1
        try:
            urls=[
                url for url in bysite[site].get("availableDataUrls",[])
                if urlparse(url).path.rstrip("/").endswith("/"+month)
            ]
            if len(urls)!=1 or urlparse(urls[0]).hostname!="data.neonscience.org":
                raise ValueError("SOURCE_MONTHLY_URL_MISSING_OR_AMBIGUOUS")
            payload=_request_json(urls[0],token=token)
            manifest_hashes.append(digest(payload))
            manifests[site]=monthly_chm_manifest(payload,site,month)
        except Exception as exc:
            # Only a class of failure, never source URL or site identity.
            manifest_errors["SITE_RELEASED_MONTH_MANIFEST_ERROR"]+=1
            manifests[site]=[]

    requests={}
    unique_tiles={}
    for key in sorted(cohort):
        for anchor in ANCHORS:
            loc=anchors.get((key,anchor))
            req=(key,anchor)
            if loc is None:
                requests[req]={
                    "status":"SOURCE_ANCHOR_UNAVAILABLE",
                    "loc":None,"tile_id":None,
                }
                continue
            epsg=explicit_epsg(loc)
            if epsg is None:
                requests[req]={
                    "status":"SOURCE_DATUM_UNSUPPORTED",
                    "loc":loc,"tile_id":None,
                }
                continue
            site=key[0]
            if site not in manifests or not manifests[site]:
                requests[req]={
                    "status":"RELEASED_SITE_MANIFEST_UNAVAILABLE",
                    "loc":loc,"tile_id":None,
                }
                continue
            x,y=loc["xy"]
            tile_x=1000*math.floor(x/1000)
            tile_y=1000*math.floor(y/1000)
            options=[
                item for item in manifests[site]
                if item["tile_easting"]==tile_x and item["tile_northing"]==tile_y
            ]
            if len(options)!=1:
                requests[req]={
                    "status":("NO_RELEASED_TILE_AT_ANCHOR" if not options
                              else "MULTIPLE_TILES_AT_ANCHOR"),
                    "loc":loc,"tile_id":None,
                }
                continue
            tile=options[0]
            ident=(tile["site"],tile["month"],tile["name"])
            unique_tiles[ident]=tile
            requests[req]={
                "status":"TILE_SELECTED","loc":loc,
                "tile_id":ident,"source_epsg":epsg,
            }

    bytes_selected=sum(meta["size"] for meta in unique_tiles.values())
    if bytes_selected>MAX_DOWNLOAD_BYTES:
        raise ValueError("Original source pilot CHM download byte cap exceeded")

    raster_by_tile={}
    tile_SHA=[]
    tile_checksum_categories=Counter()
    download_errors=Counter()
    def download_one(row):
        tid,tile=row
        try:
            original_bytes=download_monthly_tile(tile,token)
            return tid,original_bytes,None
        except Exception as e:
            return tid,None,type(e).__name__

    with ThreadPoolExecutor(max_workers=4) as ex:
        for ident,raw,error in ex.map(
            download_one,sorted(unique_tiles.items())
        ):
            if error:
                download_errors["CHM_TILE_DOWNLOAD_OR_CHECKSUM_FAILED"]+=1
            else:
                raster_by_tile[ident]=raw
                tile_SHA.append(hashlib.sha256(raw).hexdigest())
                tile_checksum_categories[unique_tiles[ident]["checksum_kind"]]+=1

    rows=[]
    raster_failures=Counter()
    for (key,anchor),obj in sorted(requests.items()):
        loc=obj["loc"]
        state=obj["status"]
        height=None
        if state=="TILE_SELECTED":
            if obj["tile_id"] not in raster_by_tile:
                state="CHM_TILE_FAILED_PROVIDER_CHECK"
            else:
                try:
                    pixel=inspect_reference_pixel(
                        raster_by_tile[obj["tile_id"]],
                        *loc["xy"],obj["source_epsg"],
                        loc["uncertainty_m"],
                    )
                    state=pixel["status"]
                    if state=="VALID_REFERENCE_PIXEL":
                        height=pixel["height_m"]
                except Exception as exc:
                    raster_failures["RASTER_VALIDATION_OR_READ_ERROR"]+=1
                    state="RASTER_VALIDATION_OR_READ_ERROR"
        rows.append({
            "plot_key":key,"anchor":anchor,"status":state,
            "height_m":height,
            "uncertainty_known":(
                loc is not None and loc["uncertainty_m"] is not None
            ),
            "historically_flagged_grid":key[1] in GEO_LOCATION_ISSUE_GRIDS,
        })

    result=aggregate_five_anchor_height_support(rows,expected_plots=30)
    # Mandatory self-consistency of the original E5: current source and
    # raster files must not be silently changed by the five-point pilot.
    require(
        result["valid_E5_reference_anchors"]==30
        and result["zero_E5_reference_heights"]==19,
        "old source E5 pixel coverage/heights drifted",
    )
    require(
        result["plots_with_published_geolocation_issue"]==
        4,
        "original flagged physical-grid denominator changed",
    )
    return {
        **result,
        "schema":"neon.CHMRaster.five_named_anchor_source.pilot.v1",
        "status":"FIVE_NAMED_CHM_REFERENCE_ANCHORS_AUDITED_NOT_HABITAT_EFFECT",
        "retrieved_UTC":datetime.now(timezone.utc).isoformat(),
        "original_source":source,
        "frozen_58_unit_30_plot_14_site_cohort_reproduced":True,
        "earlier_E5_30_valid_19_zero_reproduced":True,
        "raster_acquisition_site_year_counts":dict(sorted(source_years.items())),
        "source_monthly_URL_selection":"unchanged official advertised month in latest 2015–2025 per site",
        "source_sites_with_suppressed_month_manifest":sum(
            site not in manifests or not manifests[site] for site in sites
        ),
        "source_monthly_manifest_error_class_counts":dict(manifest_errors),
        "source_monthly_manifest_digest_set_SHA256":digest(sorted(manifest_hashes)),
        "source_current_anchor_coordinate_digest_set_SHA256":digest(sorted(response_digests)),
        "current_anchor_location_errors":dict(location_errors),
        "unique_selected_CHM_tiles":len(unique_tiles),
        "unique_provider_size_and_checksum_verified_CHM_tiles":len(raster_by_tile),
        "source_selected_tiles_total_bytes":bytes_selected,
        "provider_checksum_types":dict(tile_checksum_categories),
        "source_verified_tile_SHA256_set_digest":digest(sorted(tile_SHA)),
        "CHM_tile_download_error_categories":dict(download_errors),
        "CHM_raster_read_error_categories":dict(raster_failures),
        "source_effect_scope":{
            "only_five_literal_station_anchors_evaluated":True,
            "all_100_station_locations_verified":False,
            "current_named_locations_are_not_historical_capture_date_crosswalk":True,
            "no_plant_ground_shrub_cover_from_zero_CHM":True,
            "no_genus_trap_recurrence_or_habitat_regression_computed":True,
            "no_source_plot_coords_or_individual_heights_exported":True,
            "original_corrected_genus_spatial_recurrence_unchanged":True,
            "original_density_genus_generality":"FAILED_5_OF_8",
            "MOSA_W_B_effects":"SEALED",
        },
    }


def main()->int:
    try:
        data=run()
    except Exception as exc:
        data={
            "schema":"neon.CHMRaster.five_named_anchor_source.pilot.v1",
            "status":"STOP_FIVE_ANCHOR_CHM_SOURCE_OR_ORIGINAL_COHORT",
            "error_class":type(exc).__name__,
            "raster_or_habitat_ecological_effect_computed":False,
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(data,indent=2,sort_keys=True))
    return 3 if data["status"].startswith("STOP_") else 0


if __name__=="__main__":
    raise SystemExit(main())
