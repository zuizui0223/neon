#!/usr/bin/env python3
"""Real 2026 Zenodo independent camera-vs-NEON original mammal source audit.

This measures whether externally obtained cameras co-occur IN SPACE AND
TIME with original live trapping. Not a habitat-vs-detection effect.
No original mammal ecological response or genus-space Z is calculated.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import urllib.request
import urllib.error
from urllib.parse import quote
from pyproj import Transformer

from analysis.run_neon_habitat_source_link_v1 import (
    BASE,TOKEN_ENV,reconstruct,_request_json,digest
)
from analysis.neon_graphql_dated_station_source_v1 import validate_history_projection
from analysis.neon_dated_station_location_v1 import station_labels_10x10
from analysis.neon_camera_independent_source_gate_v1 import (
    parse_deployments,parse_camera_sequences,
    candidate_e5_pairs,exact_station_camera_sources,
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_zenodo_camera_independent_source_gate_v1.json"
SOURCE_DOI="10.5281/zenodo.20826511"
PIN={
    "camera_trap_deployments.csv":"82537cdf0a586fa14c9a8b6afd7be470",
    "camera_trap_sequences.csv":"7531a5b9fb3848ef33e162d5206a6f43",
    "subproject_descriptions.csv":"be1502427995886ef1c64c10410d1ee2",
}
MAX_CAMERA_SOURCE_BYTES=9_000_000
PHASE="ZENODO_CAMERA_SOURCE_RETRIEVAL"
PHASES={
    "ZENODO_CAMERA_SOURCE_RETRIEVAL",
    "VERIFY_INDEPENDENT_CAMERA_CSVS",
    "RECONSTRUCT_FROZEN_NEON_SEASON_PAIRS",
    "VERIFY_30_ORIGINAL_E5_SOURCE_HISTORIES",
    "INDEPENDENT_CAMERA_SPACETIME_PREFLIGHT",
    "VERIFY_ORIGINAL_100_STATIONS_AT_NEARBY_CAMERA_PLOTS",
    "AGGREGATE_INDEPENDENT_GENUS_CAMERA_SOURCE_SUPPORT",
}

def must(ok,why):
    if not ok:raise ValueError("Independent camera original source STOP: "+why)

def get_pinned_camera_file(name):
    """The source is public; accept bytes only at the original published MD5."""
    if name not in PIN:
        raise ValueError("Original camera source file not pinned")
    url="https://zenodo.org/records/20826511/files/"+quote(name,safe="")+"?download=1"
    req=urllib.request.Request(url,headers={"User-Agent":"NEON-source-verification/1.0"})
    with urllib.request.urlopen(req,timeout=150) as resp:
        raw=resp.read(MAX_CAMERA_SOURCE_BYTES+1)
    if len(raw)>MAX_CAMERA_SOURCE_BYTES or hashlib.md5(raw).hexdigest()!=PIN[name]:
        raise ValueError("Camera source size/published MD5 mismatch")
    return raw

def location_docs(jobs,token,*,workers=8):
    def read_one(job):
        key,full=job
        url=BASE+"locations/"+quote(full,safe="")+"?history=true"
        result=_request_json(url,token=token)
        doc=result.get("data")
        must(isinstance(doc,dict) and doc.get("locationName")==full
             and isinstance(doc.get("locationHistory"),list)
             and doc["locationHistory"],"Official NEON source station history")
        return key,doc,digest(result)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(read_one,jobs))

def to_latlon(detail,cache):
    epsg=detail["utm_epsg"]
    if epsg not in cache:
        cache[epsg]=Transformer.from_crs(epsg,4326,always_xy=True)
    x,y=detail["xy"]
    lon,lat=cache[epsg].transform(x,y)
    return lat,lon

def run():
    global PHASE
    token=os.environ.get(TOKEN_ENV,"").strip()
    must(bool(token),"Existing NEON release source authorization unavailable")

    raw={};bytecounts={}
    for name in PIN:
        payload=get_pinned_camera_file(name)
        raw[name]=payload
        bytecounts[name]=len(payload)
    PHASE="VERIFY_INDEPENDENT_CAMERA_CSVS"
    camera_deployments,cam_diag=parse_deployments(raw["camera_trap_deployments.csv"])
    camera_genus=parse_camera_sequences(raw["camera_trap_sequences.csv"],camera_deployments)
    must(len(camera_deployments)>0 and
         cam_diag["source_deployment_rows"]==len(camera_deployments),
         "Published original camera deployments invalid")

    PHASE="RECONSTRUCT_FROZEN_NEON_SEASON_PAIRS"
    units,plots,sites,names,mammal=reconstruct(token)
    must((len(units),len(plots),len(sites))==(58,30,14)
         and all(len(names.get(p,set()))==1 for p in plots),
         "Frozen 58-pair 30-grid 14-site mammal original cohort drifted")
    days_byplot=defaultdict(set)
    for u in units:
        days_byplot[tuple(u["site_plot"])].update(
            tuple(u["capture_dates_A"])+tuple(u["capture_dates_B"])
        )
    must(sum(len(days) for days in days_byplot.values())==339,
         "Original 339 distinct plot-day keys changed")

    PHASE="VERIFY_30_ORIGINAL_E5_SOURCE_HISTORIES"
    jobs=[
        ((site,plot),next(iter(names[(site,plot)]))+".E5")
        for site,plot in sorted(plots)
    ]
    e5=location_docs(jobs,token)
    must(len(e5)==30,"Original E5 source documents incomplete")
    crs_cache={}
    coords_e5={}
    E5_sha=[]
    for plot,doc,sha in e5:
        at_days=[validate_history_projection(doc,day)
                 for day in sorted(days_byplot[plot])]
        original={(d["utm_epsg"],d["xy"]) for d in at_days}
        must(len(original)==1,"Historical E5 moved; cannot infer a stable source grid centre")
        coords_e5[plot]=to_latlon(at_days[0],crs_cache)
        E5_sha.append(sha)

    PHASE="INDEPENDENT_CAMERA_SPACETIME_PREFLIGHT"
    spatial,prospective=candidate_e5_pairs(
        units,coords_e5,camera_deployments
    )

    PHASE="VERIFY_ORIGINAL_100_STATIONS_AT_NEARBY_CAMERA_PLOTS"
    selected_plots=set(prospective)
    station_locs={}
    station_hashes=[]
    # This is a factual direct-station test, not a fabricated 10m grid.
    for plot in sorted(selected_plots):
        site,grid=plot
        original_name=next(iter(names[plot]))
        station_jobs=[
            ((site,grid,station),original_name+"."+station)
            for station in station_labels_10x10()
        ]
        actual=location_docs(station_jobs,token)
        latlons=[]
        for key,doc,sha in actual:
            detail=[validate_history_projection(doc,day)
                    for day in sorted(days_byplot[plot])]
            must(len({(d["utm_epsg"],d["xy"]) for d in detail})==1,
                 "Original station location changes over capture dates")
            latlons.append(to_latlon(detail[0],crs_cache))
            station_hashes.append(sha)
        must(len(latlons)==100,"Exact 100 source station coordinates missing")
        station_locs[plot]=latlons
    PHASE="AGGREGATE_INDEPENDENT_GENUS_CAMERA_SOURCE_SUPPORT"
    exact=exact_station_camera_sources(
        units,station_locs,camera_deployments,prospective,
        camera_genus["small_rodent_genus_by_deployment_day"]
    )
    independent_hardware_source=bool(
        spatial["camera_plot_links_E5_250m_with_capture_day_overlap"]
    )
    strict=exact["strict_source_20pair_8site_12plot_two_genus_GO"]
    return {
        "schema":"neon.macro.camera_independent_detection_original_source.v1",
        "status":(
            "CAMERA_SOURCE_STRICT_TWO_SEASON_RODENT_GENUS_SPACETIME_GO_NOT_EFFECT"
            if strict else
            "STOP_INDEPENDENT_CAMERA_SAME_STATION_TWO_SEASON_SOURCE_SUPPORT"
        ),
        "source":{
            "doi":SOURCE_DOI,
            "published_year":2026,
            "camera_deployment_period":"2015-2022 original external survey",
            "camera_source_published_MD5_verified_three_csvs":True,
            "original_source_downloaded_total_bytes":sum(bytecounts.values()),
            "source_bytes_by_file":dict(sorted(bytecounts.items())),
            "camera_original_deployments":cam_diag,
            "camera_original_sequence_count_by_category":camera_genus["census"],
            "known_target_small_rodent_camera_genus_richness":camera_genus["small_rodent_genus_richness"],
            "camera_deployments_with_genus_identified_small_rodents":camera_genus["camera_deployments_with_target_rodent_genus"],
        },
        "original_neon_source":{
            "mammal_release":"RELEASE-2026",
            "original_fixed_mammal_pairs":len(units),
            "original_fixed_mammal_grids":len(plots),
            "original_physical_sites":len(sites),
            "distinct_plot_capture_dates":sum(len(x) for x in days_byplot.values()),
            "source_30_E5_location_hashes_digest":digest(sorted(E5_sha)),
            "exact_station_history_documents_checked_after_spacetime_prefilter":len(station_hashes),
            "exact_station_history_sha256_set_digest":digest(sorted(station_hashes)),
            "original_mammal_source_reproduced":mammal,
        },
        "camera_E5_proximity_screen":spatial,
        "camera_exact_station_and_genus_source":exact,
        "fixed_source_thresholds":{
            "prefilter_E5_radius_m":250,
            "actual_station_proximity_radius_m":20,
            "min_pair_seasons":20,
            "min_physical_sites":8,
            "min_original_grids":12,
            "genus_identification":"at least two recurring Cricetidae/Heteromyidae/Dipodidae/Muridae camera genus labels in both trapping seasons",
        },
        "scientific_boundary":{
            "camera_is_a_different_observation_hardware_from_sherman_traps":True,
            "camera_and_live_trap_detection_errors_not_assumed_independent":True,
            "single_short_camera_campaign_cannot_demonstrate_adjacent_season_recurrence":True,
            "camera_mammal_genus_detections_not_detection_corrected_true_space_use":True,
            "camera_genus_unidentified_small_mammal_not_treated_as_genus":True,
            "original_mammal_genus_station_response_not_read_or_refitted":True,
            "existing_positive_capture_space_R_and_all_failed_density_weather_operability_gates_unchanged":True,
            "no_animal_ID_site_grid_trap_station_camera_coordinates_raw_photos_or_dates_exported":True,
            "single_macro_ecology_paper_remains_SUBMISSION_HOLD":True,
            "next_if_stop":"Seek pre-specified independent multi-season paired rodent cameras+live traps at exact stations, or a prospective new source; do not reinterpret camera survey as capture-space validation",
        },
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
    }

def main():
    global PHASE
    try:
        result=run()
        code=0  # Scientific STOP is a valid data/source endpoint.
    except Exception as exc:
        result={
            "schema":"neon.macro.camera_independent_detection_original_source.v1",
            "status":"STOP_INDEPENDENT_CAMERA_SOURCE_INFRASTRUCTURE_OR_SCHEMA",
            "failed_source_stage":PHASE if PHASE in PHASES else "UNKNOWN_SOURCE_STAGE",
            "error_class":type(exc).__name__,
            "camera_or_neon_source_identifiers_coordinates_dates_not_exported":True,
            "no_old_animal_ecological_response_opened":True,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
