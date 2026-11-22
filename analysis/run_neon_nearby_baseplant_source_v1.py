#!/usr/bin/env python3
"""Real NEON distributed base-plant plot source versus fixed mammal bouts.

Official DP1.10058.001 RELEASE-2026 source-only. Plant cover plots with
same plotID may be approximately 150m offset from mammal trap grids.
No response, genus-by-trap regression, or detection effect computed.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import json,os,re

from analysis.run_neon_habitat_source_link_v1 import (
    reconstruct,_request_json,TOKEN_ENV,digest
)
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    QUERY_URL,_download_many
)
from analysis.neon_field_plant_source_support_v1 import (
    parse_1m2_source,plant_source_events,summarize_nearby_plant_bouts
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_baseplot_cover_time_source_20261028.json"
PRODUCT="DP1.10058.001"
RELEASE="RELEASE-2026"
START="2015-04"
END="2025-12"
MAX_FILES=700
MAX_BYTES=450_000_000
STAGE="ORIGINAL_MAMMAL_RECONSTRUCTION"
STAGES={"ORIGINAL_MAMMAL_RECONSTRUCTION","PLANT_OFFICIAL_MANIFEST",
        "PLANT_SOURCE_MD5_DOWNLOAD","PLANT_PLOT_TIME_CROSSWALK"}

def plant_manifest(payload,sites):
    releases=[b for b in payload.get("data",{}).get("releases",[])
              if isinstance(b,dict) and b.get("release")==RELEASE]
    if len(releases)!=1:
        raise ValueError("Expected one official RELEASE-2026")
    files={}
    for pack in releases[0].get("packages",[]):
        if not isinstance(pack,dict) or pack.get("packageType")!="basic":continue
        site=pack.get("siteCode");month=pack.get("month")
        if site not in sites or not isinstance(month,str):continue
        for row in pack.get("files",[]):
            name=str(row.get("name") or "")
            if "div_1m2data" not in name.lower() or not name.endswith(".csv"):
                continue
            size=row.get("size");md5=str(row.get("md5") or "").lower()
            url=str(row.get("url") or "")
            if not (type(size) is int and size>=0 and
                    re.fullmatch("[0-9a-f]{32}",md5) and url.startswith("https://")):
                raise ValueError("Plant provider source metadata lacks MD5 or size")
            data={"site":site,"month":month,"name":name,
                  "url":url,"size":size,"md5":md5}
            key=(site,month,name)
            if key in files and files[key]!=data:
                raise ValueError("Conflicting repeated plant source file")
            files[key]=data
    return [files[k] for k in sorted(files)]

def run():
    global STAGE
    token=os.environ.get(TOKEN_ENV,"").strip()
    if not token:
        raise ValueError("Original source authorization missing")
    units,plots,sites,names,mammal=reconstruct(token)
    if (len(units),len(plots),len(sites))!=(58,30,14):
        raise ValueError("Frozen mammal 58/30/14 source changed")
    STAGE="PLANT_OFFICIAL_MANIFEST"
    queried=_request_json(QUERY_URL,token=token,body={
        "productCode":PRODUCT,"siteCodes":sorted(sites),
        "startDateMonth":START,"endDateMonth":END,
        "release":RELEASE,"package":"basic","includeProvisional":False
    })
    files=plant_manifest(queried,sites)
    selected_bytes=sum(r["size"] for r in files)
    if not files or len(files)>MAX_FILES or selected_bytes>MAX_BYTES:
        return {
            "schema":"neon.independent_base_plant_cover.source_only.v1",
            "status":"STOP_PLANT_SOURCE_MISSING_OR_FIXED_BUDGET",
            "published_selected_source_files":len(files),
            "published_selected_source_bytes":selected_bytes,
            "predeclared_max_files":MAX_FILES,
            "predeclared_max_bytes":MAX_BYTES,
            "mammal_response_or_plant_cover_effect_opened":False,
        }
    STAGE="PLANT_SOURCE_MD5_DOWNLOAD"
    verified=[]
    for row,raw in zip(files,_download_many(files,token,max_workers=6)):
        parsed,count=parse_1m2_source(raw)
        verified.append((row["site"],parsed,count))
    if len(verified)!=len(files):
        raise RuntimeError("Provider-verified plant source file count drifted")
    STAGE="PLANT_PLOT_TIME_CROSSWALK"
    byplot,count=plant_source_events(verified,plots)
    report=summarize_nearby_plant_bouts(units,byplot)
    return {
        "schema":"neon.independent_base_plant_cover.source_only.v1",
        "status":("SOURCE_BASE_PLANT_NEARBY_TIME_MATCH_GO_NOT_TRAP_HABITAT"
            if report["nearby_base_plot_numeric_cover_source_GO"]
            else "STOP_BASE_PLANT_TIME_COVERAGE_NOT_HABITAT_EFFECT"),
        "plant_source_product":PRODUCT,
        "plant_source_RELEASE":RELEASE,
        "original_mammal_source_cohort":mammal,
        "provider_verified_plant_files":len(verified),
        "published_plant_source_bytes":selected_bytes,
        "plant_source_record_counts":count,
        "matched_plant_field_bout_support":report,
        "official_plant_manifest_digest":digest(queried),
        "source_plant_1m2_data_only_no_100m2_imputation":True,
        "sampling_programme_independent_but_plot_grid_offset":True,
        "source_plant_cover_values_not_used_in_mammal_ecological_fit":True,
        "old_14site_and_30site_capture_location_Z_unchanged":True,
        "old_trap_operability_density_and_weather_failures_unchanged":True,
        "site_plot_individual_animal_dates_and_percent_cover_not_exported":True,
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
    }

def main():
    global STAGE
    try:
        result=run();code=0
    except Exception as exc:
        result={
            "schema":"neon.independent_base_plant_cover.source_only.v1",
            "status":"STOP_ORIGINAL_PLANT_SOURCE_OR_SCHEMA",
            "failure_stage":STAGE if STAGE in STAGES else "UNKNOWN_SOURCE_PHASE",
            "error_class":type(exc).__name__,
            "original_mammal_Z_or_cover_effect_unopened":True,
            "private_source_plant_site_plot_dates_not_exported":True,
        };code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
