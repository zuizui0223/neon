#!/usr/bin/env python3
"""Original Portal hourly weather and Landsat8 monsoon SOURCE-only QC.

Never accesses rodent species, plant quadrat abundance, nor previous effects.
Validates immutable provider raw Git blob, outputs only year×source coverage.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from datetime import date
from hashlib import sha1, sha256
from io import StringIO
from math import isfinite
from pathlib import Path
from urllib.request import Request, urlopen
import csv
import json

SOURCE_COMMIT = "afd75933249ae60f3a5e9dab00b354f219e5e045"
SOURCE = {
    "Weather/Portal_weather.csv": ("bc9d999db496b55e04281c1317a98b3ff3304eed",150_000_000),
    "NDVI/ndvi.csv": ("0a55a926712210ee786660517a1ae12285bb6303",1_000_000),
}
YEARS = (2021,2022,2023,2024)
MONSOON_MONTHS = (7,8,9)
EXPECTED_HOURLY = 2208
MIN_VALID_PRECIP = .90
MIN_VALID_SAT_IMAGES = 2
MAX_CLOUD = 30.
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_portal_environment_2022_source_only_20261121.json"
SOURCE_REPO="weecology/PortalData"
PROTOCOL="docs/NEON_PORTAL_2022_ENVIRONMENT_POSTRESULT_DESIGN_20261121.md"

def require(test,code):
    if not test:
        raise ValueError("PORTAL_ENV_SOURCE_STOP_"+code)

def get_pinned_raw(path):
    expected,max_bytes=SOURCE[path]
    url=f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_COMMIT}/{path}"
    request=Request(url,headers={"User-Agent":"NEON-source-integrity/1","Accept":"text/csv"})
    with urlopen(request,timeout=120) as handle:
        require(handle.status==200,"SOURCE_HTTP_STATUS")
        data=handle.read(max_bytes+1)
    require(0<len(data)<=max_bytes,"SOURCE_SIZE_CAP_OR_EMPTY")
    header=data[:512].lstrip().lower()
    require(not any(header.startswith(w) for w in (b"<html",b"<!doctype",b"{",b"pk\x03\x04")),
            "SOURCE_HTML_OR_WRONG_FORMAT")
    actual=sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    require(actual==expected,"ORIGINAL_GIT_BLOB_SHA_MISMATCH")
    return data

def iter_csv(raw,required):
    try:
        data=raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("PORTAL_ENV_SOURCE_STOP_NONUTF8_ORIGINAL") from None
    reader=csv.DictReader(StringIO(data))
    cols=reader.fieldnames or []
    require(len(cols)==len(set(cols)) and set(required).issubset(cols),
            "REQUIRED_HEADER_OR_DUPLICATE_COLUMN")
    for row in reader:
        require(None not in row and all(val is not None for val in row.values()),
                "SOURCE_RAGGED_ROW")
        yield row

def year_month_day(row):
    try:
        y=int(row["year"]);m=int(row["month"]);d=int(row["day"])
        day=date(y,m,d)
    except (ValueError,TypeError):
        return None
    return day

def weather_support(raw):
    """Counts coverage but returns private numeric values to downstream runner."""
    samples={y:{} for y in YEARS}
    parse_errors=Counter()
    raw_hour_entries=0
    for row in iter_csv(raw,("year","month","day","hour","precipitation")):
        try:
            year=int(row["year"])
        except (ValueError,TypeError):
            continue
        if year not in YEARS:
            continue
        try:
            month=int(row["month"])
        except (ValueError,TypeError):
            parse_errors["invalid_month"]+=1
            continue
        if month not in MONSOON_MONTHS:
            continue
        d=year_month_day(row)
        require(d is not None,"INVALID_YEAR_MONTH_DAY_IN_TARGET_WINDOW")
        try:
            hr=int(row["hour"])
        except (TypeError,ValueError):
            raise ValueError("PORTAL_ENV_SOURCE_STOP_HOUR_FIELD_NOT_INTEGER") from None
        require(0<=hr<=23,"HOUR_OUTSIDE_0_23")
        raw_hour_entries+=1
        text=(row["precipitation"] or "").strip()
        value=None
        if text and text.lower() not in ("na","nan","null"):
            try:
                value=float(text)
            except ValueError:
                parse_errors["non_numeric_precipitation"]+=1
            else:
                require(isfinite(value) and value>=0,"NEGATIVE_OR_NONFINITE_RAIN")
        key=(month,d.day,hr)
        old=samples[year].get(key,"UNSEEN")
        if old!="UNSEEN":
            require(old==value,"CONFLICTING_DUPLICATE_HOURLY_RAIN")
        samples[year][key]=value
    coverage={}
    for year in YEARS:
        n_valid=sum(q is not None for q in samples[year].values())
        require(len(samples[year])<=EXPECTED_HOURLY,"EXCESS_MONSOON_HOURS")
        coverage[str(year)]={
            "observed_distinct_hour_slots":len(samples[year]),
            "hours_with_valid_nonnegative_rain":n_valid,
            "total_expected_hour_slots":EXPECTED_HOURLY,
            "valid_fraction":n_valid/EXPECTED_HOURLY,
            "90pct_hours_threshold_passed":n_valid/EXPECTED_HOURLY>=MIN_VALID_PRECIP,
        }
    return samples,{
        "per_year":coverage,
        "raw_target_monsoon_hour_entries":raw_hour_entries,
        "parse_flag_counts":dict(parse_errors),
        "all_years_rain_quality_pass":all(
            coverage[str(y)]["90pct_hours_threshold_passed"] for y in YEARS)
    }

def ndvi_support(raw):
    """Fixed Landsat8-only, USGS, cloud<=30%; no sensor correction."""
    selected={y:[] for y in YEARS}
    counts=defaultdict(Counter)
    for row in iter_csv(raw,("date","sensor","source","ndvi","cloud_cover")):
        stamp=(row["date"] or "").strip()
        try:
            d=date.fromisoformat(stamp)
        except ValueError:
            continue
        year=d.year
        if year not in YEARS or d.month not in MONSOON_MONTHS:
            continue
        counts[year]["all_monsoon_provider_rows"]+=1
        if (row["sensor"] or "").strip()!="Landsat8" or (
             row["source"] or "").strip()!="USGS":
            counts[year]["excluded_other_sensor_or_provider"]+=1
            continue
        counts[year]["Landsat8_original_rows"]+=1
        try:
            cloud=float(row["cloud_cover"])
            value=float(row["ndvi"])
        except (TypeError,ValueError):
            counts[year]["missing_ndvi_or_cloud"]+=1
            continue
        if not (isfinite(cloud) and isfinite(value)):
            counts[year]["missing_ndvi_or_cloud"]+=1
            continue
        require(0<=cloud<=100 and -1<=value<=1,
                "IMPOSSIBLE_NDVI_OR_CLOUD_RANGE")
        if cloud>MAX_CLOUD:
            counts[year]["cloud_over_30pct"]+=1
            continue
        counts[year]["Landsat8_clear_numeric_images"]+=1
        selected[year].append(value)
    info={}
    for y in YEARS:
        n=len(selected[y])
        info[str(y)]={
            **dict(counts[y]),
            "valid_monsoon_Landsat8_images":n,
            "minimum_two_Landsat8_images_pass":n>=MIN_VALID_SAT_IMAGES,
        }
    return selected,{
        "per_year":info,
        "all_years_Landsat8_source_gate_pass":all(
            len(selected[y])>=MIN_VALID_SAT_IMAGES for y in YEARS),
        "original_source_radius_about_1000m_not_plot_specific":True,
    }

def verify_sources():
    raw={}
    receipts={}
    for path,(sha,limit) in SOURCE.items():
        source=get_pinned_raw(path)
        raw[path]=source
        receipts[path]={
            "original_git_blob_sha":sha,
            "source_byte_length":len(source),
            "raw_bytes_SHA256":sha256(source).hexdigest(),
        }
    precip,weather_qc=weather_support(raw["Weather/Portal_weather.csv"])
    greenery,ndvi_qc=ndvi_support(raw["NDVI/ndvi.csv"])
    return precip,greenery,{
        "schema":"neon.portal_site_climate_postresult_source.v1",
        "source":{
            "original_repository":SOURCE_REPO,
            "original_git_commit":SOURCE_COMMIT,
            "checksum_verification":"both original Git blob SHA-1 reproduced",
            "files":receipts
        },
        "fixed_source_rules":{
            "years":list(YEARS),
            "monsoon_months":list(MONSOON_MONTHS),
            "precip_historical_expected_hours_per_year":EXPECTED_HOURLY,
            "required_precip_valid_hour_fraction":MIN_VALID_PRECIP,
            "ndvi_sensor":"Landsat8","ndvi_provider":"USGS",
            "maximum_ndvi_cloud_percent":MAX_CLOUD,
            "minimum_clear_NDVI_images_per_year":MIN_VALID_SAT_IMAGES,
        },
        "weather_source_coverage":weather_qc,
        "satellite_source_coverage":ndvi_qc,
        "rain_gate_pass":weather_qc["all_years_rain_quality_pass"],
        "ndvi_gate_pass":ndvi_qc["all_years_Landsat8_source_gate_pass"],
        "all_environment_gates_pass":(
            weather_qc["all_years_rain_quality_pass"] and
            ndvi_qc["all_years_Landsat8_source_gate_pass"]
        ),
        "no_climate_or_ndvi_means_sums_or_differences_reported":True,
        "no_original_rodent_or_plant_abundance_or_mammal_outcome_read":True,
        "post_result_context_only_not_independent_confirmatory_test":True,
        "protocol":PROTOCOL,
    }

def main():
    try:
        _,_,receipt=verify_sources()
        receipt["status"]=("ENV_SOURCE_GO_NO_NUMERIC_CLIMATE_EFFECT"
                           if receipt["all_environment_gates_pass"] else
                           "ENV_SOURCE_PARTIAL_OR_STOP_NO_CLIMATE_VALUES")
        code=0
    except Exception as exc:
        receipt={
            "schema":"neon.portal_site_climate_postresult_source.v1",
            "status":"SOURCE_STOP_SOURCE_OR_FORMAT_NOT_BIOLOGICAL_RESULT",
            "error_type":type(exc).__name__,
            "stop_reason":str(exc)[:130],
            "no_precipitation_NDVI_or_rodent_effect_reported":True
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print(json.dumps(receipt,sort_keys=True,indent=2))
    return code

if __name__=="__main__":
    raise SystemExit(main())
