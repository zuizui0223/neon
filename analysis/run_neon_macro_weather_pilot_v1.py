#!/usr/bin/env python3
"""Two-product, one original trapping-month, source-only NEON tower weather QA.

Only the earliest source-sorted original exact-two-genus pairing with
verified RELEASE-2026 monthly availability in *both* fixed products is
eligible for this first schema/data-integrity probe. This is not a
climate–mammal regression, nor precipitation method substitution.

Private original source event date, site, plot, UTM coordinates, tag and
taxon names stay in RAM. Output summarizes instrument table column
schemas, provider MD5/size integrity and quality/finite row support ONLY.
"""
from __future__ import annotations

import csv, io, hashlib, json, os
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from analysis.run_multiscale_density_estimability_release2026_v3 import (
    _request_json,_download_one,QUERY_URL,TOKEN_ENV,
)
from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.run_neon_macro_temporal_weather_source_v1 import (
    NEON_SITES, weather_release_months,PRODUCTS,
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_macro_tower_weather_first_month_qc_pilot_v1.json"
RELEASE="RELEASE-2026"
PRODUCT_TABLE={
    "single_air_temperature":("DP1.00002.001","SAAT_30min"),
    "precip_tipping":("DP1.00045.001","TIPPRE_30min"),
}
MAX_SINGLE_FILE_BYTES=15000000

def need(ok:bool,reason:str)->None:
    if not ok:raise ValueError("NEON_ATMOSPHERIC_SOURCE_QA_STOP: "+reason)


def eligible_first_original_pair(
    two:list[dict],site_rows:list[dict]
)->tuple[str,str]:
    """Returns private site, first original trapping-month; no Z inspected."""
    indexed={row.get("siteCode"):row for row in site_rows if isinstance(row,dict)}
    for u in sorted(two,key=lambda z:(z["site"],tuple(z["site_plot"]),z["season_ordinal"])):
        meta=indexed.get(u["site"])
        if not meta:continue
        availability=weather_release_months(meta)
        mos={x.isoformat()[:7] for x in u["capture_dates_A"]+u["capture_dates_B"]}
        if mos <= availability[PRODUCT_TABLE["single_air_temperature"][0]] and mos <= availability[PRODUCT_TABLE["precip_tipping"][0]]:
            return u["site"], min(mos)
    raise ValueError("No original exact-two site/month has both fixed weather products")


def _month_manifest(payload:dict,product:str,site:str,month:str,tablename:str)->dict:
    root=payload.get("data")
    need(isinstance(root,dict),"data query release response missing")
    releases=root.get("releases")
    need(isinstance(releases,list),"unexpected release query format")
    blocks=[x for x in releases if isinstance(x,dict) and x.get("release")==RELEASE]
    need(len(blocks)==1,"expected original RELEASE-2026 block")
    options=[]
    for pkg in blocks[0].get("packages",[]):
        if not isinstance(pkg,dict) or pkg.get("packageType")!="basic" or pkg.get("siteCode")!=site or pkg.get("month")!=month:
            continue
        for row in pkg.get("files",[]):
            if not isinstance(row,dict):continue
            name=str(row.get("name") or "")
            if not name.endswith(".csv") or tablename not in name:continue
            url=str(row.get("url") or "")
            md5=str(row.get("md5") or "").lower()
            size=row.get("size")
            if not url.startswith("https://") or len(md5)!=32 or not isinstance(size,int) or isinstance(size,bool) or size<=0:
                raise ValueError("NEON provider weather file digest or size missing")
            if size>MAX_SINGLE_FILE_BYTES:
                raise ValueError("30min weather source file exceeds safe pilot byte cap")
            options.append({
                "site":site,"month":month,"name":name,
                "url":url,"md5":md5,"size":size,
            })
    need(bool(options),"Published month does not contain required 30min table")
    options.sort(key=lambda x:x["name"])
    return options[0]


def table_qa(raw:bytes,tablekind:str)->dict:
    if len(raw)>MAX_SINGLE_FILE_BYTES or len(raw)<=10:
        raise ValueError("Pilot source bytes empty or too large")
    text=raw.decode("utf-8-sig")
    reader=csv.DictReader(io.StringIO(text))
    cols=list(reader.fieldnames or [])
    need(bool(cols),"No instrument table columns")
    def by_norm(c):
        return "".join(ch.lower() for ch in c if ch.isalnum())
    allowed={
        "single_air_temperature":{"tempsinglemean","tempmean"},
        "precip_tipping":{"precipbulk","preciptot","preciptotal"},
    }
    candidates=[c for c in cols if by_norm(c) in allowed[tablekind]]
    # Broader allowed source patterns are listed as QA, not silently
    # treated as a different physically compatible variable.
    qc=[c for c in cols if ("finalqf" in by_norm(c) or by_norm(c).endswith("qf"))]
    rowcount=0
    finite=Counter()
    quality_flag=Counter()
    for row in reader:
        rowcount+=1
        for col in candidates:
            value=str(row.get(col) or "").strip()
            if not value:continue
            try:
                num=float(value)
            except ValueError:continue
            if num==num and abs(num)<1e12:
                finite[col]+=1
        for col in qc:
            if "finalqf" in by_norm(col):
                label=str(row.get(col) or "").strip()
                quality_flag[label if label in {"0","1"} else "MISSING_OR_OTHER"]+=1
    need(rowcount>=100,"No credible 30-minute instrument data support")
    return {
        "rows":rowcount,
        "field_count":len(cols),
        "has_start_and_end_time_schema":(
            any(by_norm(c)=="startdatetime" for c in cols)
            and any(by_norm(c)=="enddatetime" for c in cols)
        ),
        "primary_variable_candidates_detected":sorted(candidates),
        "finite_numeric_rows_by_candidate":dict(sorted(finite.items())),
        "n_final_quality_flag_columns":sum("finalqf" in by_norm(c) for c in qc),
        "summarized_final_quality_flag_counts":dict(sorted(quality_flag.items())),
        "primary_physical_measurement_column_semantics_checked":bool(candidates),
        "no_original_capture_dates_or_site_ids_exported":True,
        "no_ecological_effect_fitted":True,
    }


def run()->dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    need(bool(token),"original NEON API credential unavailable")
    original_strict,two,cohort=original_sources_for_two_genus()
    need((len(original_strict),len(two))==(58,158),"original source population drift")
    source=_request_json(NEON_SITES).get("data")
    need(isinstance(source,list),"official weather-month location availability missing")
    site,month=eligible_first_original_pair(two,source)
    output={}
    for name,(prod,tab) in PRODUCT_TABLE.items():
        request=_request_json(QUERY_URL,token=token,body={
            "productCode":prod,"siteCodes":[site],
            "startDateMonth":month,"endDateMonth":month,
            "release":RELEASE,"package":"basic","includeProvisional":False,
        })
        record=_month_manifest(request,prod,site,month,tab)
        contents=_download_one(record,token)
        output[name]={
            "product_code":prod,
            "selected_interval":"30min",
            "source_MD5_and_byte_count_verified":True,
            "provider_selected_source_file_size_bytes":record["size"],
            "table":table_qa(contents,name),
        }
    return {
        "schema":"neon.macro.tower_weather_first_original_month_QA.v1",
        "status":"SOURCE_ONLY_ORIGINAL_NEON_TEMPERATURE_AND_TIPPING_30MIN_QA",
        "source_cohort_frozen_3plus":len(original_strict),
        "source_cohort_frozen_exact_two":len(two),
        "source_probe_is_only_first_eligible_original_source_month":True,
        "query_cohort_selection_outcome_blind":True,
        "source_release":RELEASE,
        "monthly_product_QA":output,
        "no_other_weather_month_or_site_assumed_QC_passed":True,
        "no_meteorology_value_or_mammal_identity_exported":True,
        "no_climate_mammal_Z_regression_fit":True,
        "weather_tower_not_mammal_grid_microhabitat":True,
        "older_precipitation_methods_never_merged":True,
        "no_raw_original_files_or_neon_api_urls_exported":True,
    }


def main()->int:
    try:
        report=run()
        code=0
    except Exception as e:
        report={
            "schema":"neon.macro.tower_weather_first_original_month_QA.v1",
            "status":"STOP_WEATHER_PROVIDER_30MIN_SCHEMA_OR_ACCESS",
            "error_class":type(e).__name__,
            "private_source_exception_or_site_ids_suppressed":True,
            "no_weather_effect_estimated":True,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
