#!/usr/bin/env python3
"""Independent original Portal regional NOAA GHCN-Daily rain context.

Post-result environmental context, never replaces failed Portal site gauge
or regresses on open rodent/plant effects. Both files and years prespecified.
"""
from __future__ import annotations
from collections import Counter
from datetime import date,datetime,timezone
from hashlib import sha1,sha256
from io import StringIO
from math import isfinite
from pathlib import Path
from urllib.request import Request,urlopen
import csv,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_portal_2022_regional_rain_20261121.json"
SOURCE_COMMIT="afd75933249ae60f3a5e9dab00b354f219e5e045"
SOURCE_BASE="https://raw.githubusercontent.com/weecology/PortalData/"+SOURCE_COMMIT+"/"
ORIGINAL_SOURCES={
    "Rodeo":("Weather/Rodeo_regional_weather.csv",
             "dcbcd3f7e414a51ff74d31b17891f8e0593506fc","USC00026716",60_000_000),
    "SanSimon":("Weather/Sansimon_regional_weather.csv",
                "0f905f95d788378e3415a1482e4abfa73a2ea3b6","US1AZCH0005",30_000_000),
}
YEARS=(2021,2022,2023,2024)
SEASON_MONTHS=(7,8,9)
EXPECTED_DAYS=92
MIN_COVERAGE=.9
PROTOCOL="docs/NEON_PORTAL_2022_REGIONAL_RAIN_CONTEXT_POSTRESULT_20261121.md"

def require(ok,label):
    if not ok:
        raise ValueError("PORTAL_REGIONAL_RAIN_STOP_"+label)

def pinned_bytes(path,sha,cap):
    request=Request(SOURCE_BASE+path,
        headers={"User-Agent":"NEON-Portal-regional-source/1","Accept":"text/csv"})
    with urlopen(request,timeout=90) as response:
        require(response.status==200,"ORIGINAL_HTTP_STATUS")
        data=response.read(cap+1)
    require(0<len(data)<=cap,"BOUNDED_ORIGINAL_SIZE")
    require(not data[:256].lstrip().lower().startswith((b"<!doctype",b"<html",b"{")),
            "HTML_OR_JSON_NOT_CSV")
    blob_sha=sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    require(blob_sha==sha,"ORIGINAL_GIT_BLOB_SHA_DRIFT")
    return data

def parse_original_station(raw, expected_station):
    try:s=raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("PORTAL_REGIONAL_RAIN_STOP_NONUTF8_ORIGINAL") from None
    rd=csv.DictReader(StringIO(s))
    h=rd.fieldnames or []
    require(len(h)==len(set(h)) and
            {"year","month","day","station","prcp"}.issubset(h),
            "ORIGINAL_DAILY_RAIN_SCHEMA")
    d={y:{} for y in YEARS}
    rejected=Counter()
    for row in rd:
        require(None not in row and all(v is not None for v in row.values()),
                "ORIGINAL_CSV_RAGGED_ROWS")
        try:y=int(row["year"]);m=int(row["month"]);day=int(row["day"])
        except (TypeError,ValueError):
            rejected["unparseable_calendar_row"]+=1
            continue
        if y not in YEARS or m not in SEASON_MONTHS:continue
        try:dayobj=date(y,m,day)
        except ValueError:
            raise ValueError("PORTAL_REGIONAL_RAIN_STOP_BAD_TARGET_CALENDAR") from None
        require(row["station"].strip()==expected_station,
                "WRONG_OR_MULTIPLE_GHCN_STATIONS")
        daystr=row.get("date","")
        if daystr.strip():
            require(daystr.strip()==dayobj.isoformat(),"GHCN_DATE_ROW_CONFLICT")
        value_text=(row["prcp"] or "").strip()
        value=None
        if value_text and value_text.lower() not in ("na","nan","null"):
            try:v=float(value_text)
            except ValueError:
                rejected["non_numeric_rain"]+=1
            else:
                require(isfinite(v) and v>=0,"INVALID_OR_NEGATIVE_RAIN")
                value=v
        if dayobj in d[y]:
            require(d[y][dayobj]==value,"CONFLICTING_DAY_RAIN_DUPLICATE")
        d[y][dayobj]=value
    summary={}
    for y in YEARS:
        n=sum(val is not None for val in d[y].values())
        summary[str(y)]={
            "source_date_rows":len(d[y]),
            "days_with_valid_precipitation":n,
            "valid_92day_fraction":n/EXPECTED_DAYS,
            "90pct_valid_days_pass":n/EXPECTED_DAYS>=MIN_COVERAGE,
        }
    eligible=all(summary[str(y)]["90pct_valid_days_pass"] for y in YEARS)
    return d,{
        "per_year":summary,
        "original_data_eligible_all_four_years":eligible,
        "skipped_or_non_numeric_flags":dict(sorted(rejected.items())),
    }

def changes(totals):
    out={}
    for y in YEARS[:-1]:
        d=totals[y+1]-totals[y]
        out[f"{y}_to_{y+1}"]={"signed_mm":d,"absolute_mm":abs(d)}
    pivot=out["2022_to_2023"]["absolute_mm"]
    return {
        "all_three_precommitted_differences":out,
        "2022_to_2023_absolute_difference_rank":
            1+sum(v["absolute_mm"]>pivot for v in out.values()),
        "no_significance_claim_from_only_three_transitions":True,
    }

def station_report(name,metadata):
    path,sha,station,cap=metadata
    raw=pinned_bytes(path,sha,cap)
    report={
        "original_file":path,"original_Git_blob_SHA_verified":sha,
        "original_sha256":sha256(raw).hexdigest(),
        "original_bytes":len(raw),"original_station_id":station,
        "not_colocated_with_Portal_20ha_experiment":True,
    }
    try:
        d,valid=parse_original_station(raw,station)
    except ValueError as error:
        if str(error)=="PORTAL_REGIONAL_RAIN_STOP_ORIGINAL_DAILY_RAIN_SCHEMA":
            # Rodeo original is a Wunderground PWS hourly file with
            # 'stationid', 'hour', 'preciptotal', not frozen daily GHCN
            # 'station' and 'prcp'. Never sum preciptotal as daily PRCP.
            report["status"]="REGIONAL_SOURCE_SCHEMA_STOP_HOURLY_PWS_NOT_DAILY_GHCN"
            report["source_QC"]={"original_daily_prcp_schema_present":False}
            report["observed_monsoon_rain_mm_by_year"]=None
            report["year_changes"]=None
            return report
        raise
    report["source_QC"]=valid
    if valid["original_data_eligible_all_four_years"]:
        annual={y:sum(z for z in d[y].values() if z is not None)
                for y in YEARS}
        report["status"]="REGIONAL_SOURCE_QUALITY_GO_CONTEXT_ONLY"
        report["observed_monsoon_rain_mm_by_year"]={
            str(y):annual[y] for y in YEARS}
        report["year_changes"]=changes(annual)
    else:
        report["status"]="REGIONAL_SOURCE_QUALITY_STOP_NO_RAIN_TOTALS"
        report["observed_monsoon_rain_mm_by_year"]=None
        report["year_changes"]=None
    return report

def run():
    results={}
    for name,metadata in ORIGINAL_SOURCES.items():
        results[name]=station_report(name,metadata)
    good=[k for k,v in results.items() if v["status"]=="REGIONAL_SOURCE_QUALITY_GO_CONTEXT_ONLY"]
    status=("REGIONAL_RAIN_CONTEXT_TWO_STATIONS_GO" if len(good)==2 else
            "REGIONAL_RAIN_CONTEXT_ONE_STATION_GO" if len(good)==1 else
            "REGIONAL_RAIN_SOURCE_QUALITY_STOP")
    return {
        "schema":"neon.portal_2022_regional_precipitation_postresult_context.v1",
        "status":status,
        "source_original_PortalData_Git_commit":SOURCE_COMMIT,
        "fixed_years":list(YEARS),"monsoon_months":list(SEASON_MONTHS),
        "original_station_results":results,
        "source_eligible_stations":good,
        "no_substitute_for_original_failed_on_site_hourly_rain":True,
        "no_original_mammal_plant_or_NDVI_values_loaded":True,
        "only_regional_context_not_competition_mechanism":True,
        "posterior_2022_rodent_result_known_before_weather_test":True,
        "one_NEON_draft_submission_HOLD":True,
        "protocol":PROTOCOL,
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    try:receipt=run();exitcode=0
    except Exception as e:
        receipt={
            "schema":"neon.portal_2022_regional_precipitation_postresult_context.v1",
            "status":"STOP_ORIGINAL_REGION_FILES_OR_SCHEMA",
            "failure_class":type(e).__name__,
            "failure_code":str(e)[:140],
            "no_original_mammal_effects_or_rainfall_totals_reported":True
        }
        exitcode=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print(json.dumps(receipt,sort_keys=True,indent=2))
    return exitcode

if __name__=="__main__":
    raise SystemExit(main())
