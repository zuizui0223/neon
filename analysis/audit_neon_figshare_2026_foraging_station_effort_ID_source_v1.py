#!/usr/bin/env python3
"""Effect-blind source bridge: 2026 Figshare foraging x station nights x PIT capture.

No foraging response, animal species preference, risk treatment, movement,
learning or seed-amount effects. Exact Figshare IDs/MD5 provider pinned.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from datetime import datetime,timezone,date
from hashlib import sha256,md5
from io import StringIO
from math import isfinite
from pathlib import Path
from urllib.request import Request,urlopen
import csv,json

from analysis.audit_neon_figshare_2026_original_foraging_schema_v1 import (
    SOURCE_FILES, ARTICLE, VERSION, validate_provider_info, original_csv_structure
)
from analysis.audit_neon_figshare_2023_original_csv_schema_v1 import (
    bounded_original
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_figshare_2026_station_night_foraging_id_source_v1.json"
PROTOCOL="docs/NEON_FIGSHARE_2026_STATION_NIGHT_ID_SEED_SOURCE_GATE_20261121.md"
REQUIRED_STATION=100
REQUIRED_MATCHED_EVENTS=100
REQUIRED_GRID=3
REQUIRED_IDENTIFIED_EVENTS=30
REQUIRED_SEED_STATIONS=60
REQUIRED_SEED_EVENTS=30
REQUIRED_DATE_RATIO=.50
MISSING=frozenset({"","NA","NAN","NULL","N/A","UNK","UNKNOWN","NO PIT"})
PHASE="FETCH_PINNED_2026_FIGSHARE_ORIGINALS"

def require(ok,label):
    if not ok:
        raise ValueError("NEON_FIGSHARE_2026_BRIDGE_STOP_"+label)

def original_tag(v):
    tag=str(v or "").strip()
    return tag if tag.upper() not in MISSING else None

def token(v):
    s=str(v or "").strip()
    return s if s and s.upper() not in MISSING else None

def numerical(v):
    s=token(v)
    if s is None:
        return False
    try:n=float(s)
    except (ValueError,TypeError):
        return False
    return isfinite(n) and n>=0

def original_day(v):
    s=token(v)
    if s is None:
        return None
    for fmt in ("%Y-%m-%d","%m/%d/%Y","%m/%d/%y",
                "%Y/%m/%d","%m-%d-%Y"):
        try:return datetime.strptime(s,fmt).date()
        except (ValueError,TypeError):pass
    return None

def original_key(row,headers):
    fields=(token(row.get(k)) for k in headers)
    parts=tuple(fields)
    return parts if all(parts) else None

def load_five():
    global PHASE
    with urlopen(Request(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                         headers={"Accept":"application/json",
                                  "User-Agent":"NEON-original-source-six-keys/1"}),
                 timeout=40) as handle:
        meta_raw=handle.read(1_000_001)
    require(0<len(meta_raw)<=1_000_000 and meta_raw.lstrip().startswith(b"{"),
            "ORIGINAL_PROVIDER_META_NOT_JSON")
    meta=json.loads(meta_raw)
    original_urls=validate_provider_info(meta)
    result={}
    hashes={}
    PHASE="ORIGINAL_MD5_AND_CSV_SYNTAX"
    for fid,(name,size,original_md5) in SOURCE_FILES.items():
        raw=bounded_original(original_urls[fid],size)
        require(md5(raw).hexdigest()==original_md5,"PUBLISHED_FILE_MD5_CHANGE")
        shape=original_csv_structure(raw)
        try:s=raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise ValueError("NEON_FIGSHARE_2026_BRIDGE_STOP_UTF8") from None
        tab=list(csv.DictReader(StringIO(s,newline="")))
        require(len(tab)==shape["original_rows"],
                "SOURCE_ROWS_DRIFT")
        result[name]=tab
        hashes[name]={
            "original_provider_file_id":fid,
            "MD5_verified":original_md5,
            "original_SHA256":sha256(raw).hexdigest(),
            "verified_original_rows":len(tab),
        }
    return result,hashes,sha256(meta_raw).hexdigest()

def tally_structural(data,hashes,metadata_digest):
    """Only source identifiers, calendar and availability, not outcome fields."""
    global PHASE
    PHASE="ORIGINAL_STATION_NIGHT_LINK"
    capt=data["2016-2023 Capture Data.csv"]
    alls=data["All Foraging Clean.csv"]
    stations=data["All Station Nights.csv"]
    mouse=data["Mouse Foraging Data Clean.csv"]
    vole=data["Vole Foraging Data Clean.csv"]
    require((len(capt),len(alls),len(stations),len(mouse),len(vole))==
            (11614,3243,291,883,951),
            "ORIGINAL_FIVE_ROW_COUNT_DRIFT")
    station_keys={}
    source_station=Counter()
    for rec in stations:
        k=original_key(rec,("Grid","Site","Session","Night"))
        require(k is not None,"ORIGINAL_STATION_NIGHT_KEY_MISSING")
        require(k not in station_keys,"DUPLICATE_ORIGINAL_STATION_NIGHT_KEY")
        station_keys[k]=rec
        source_station["original_station_night_rows"]+=1
        if original_day(rec.get("Date")) is not None:
            source_station["station_nights_valid_date"]+=1
        if numerical(rec.get("WP.seeds.set")) and numerical(rec.get("RO.seeds.set")):
            source_station["original_station_nights_both_seed_set_numeric"]+=1
        else:
            source_station["source_station_nights_missing_a_numeric_seed_set_field"]+=1
    PHASE="ORIGINAL_PIT_GRID_YEAR_CAPTURES_SOURCE"
    captures=set()
    source_capt=Counter()
    for rec in capt:
        tag=original_tag(rec.get("PIT"))
        grid=token(rec.get("GRID"))
        yy=token(rec.get("YEAR"))
        if not (tag and grid and yy):
            source_capt["captures_missing_any_original_ID_grid_year"]+=1
            continue
        try:y=int(yy)
        except ValueError:
            source_capt["captures_invalid_year"]+=1
            continue
        d=original_day(rec.get("DATE"))
        if d and d.year!=y:
            source_capt["original_capture_date_year_conflict"]+=1
            continue
        captures.add((tag,grid,y))
        source_capt["source_capture_rows_with_exact_PIT_grid_year"]+=1
    PHASE="ORIGINAL_FORAGING_EVENT_STATION_NIGHT_RESOURCE_METADATA"
    source_all=Counter()
    matched_grids=set()
    matched_stations=set()
    valid_pits=set()
    event_key_census=Counter()
    for rec in alls:
        k=original_key(rec,("Grid","Site","Session","Night"))
        if k is None:
            source_all["events_missing_original_station_night_key"]+=1
            continue
        if k not in station_keys:
            source_all["event_rows_without_exact_original_station_night"]+=1
            continue
        source_all["event_rows_with_exact_original_station_night"]+=1
        matched_grids.add(k[0])
        matched_stations.add(k)
        d=original_day(rec.get("Date"))
        sd=original_day(station_keys[k].get("Date"))
        if d and sd:
            source_all["event_and_station_night_dates_both_parseable"]+=1
            if d==sd:
                source_all["original_event_and_station_night_exact_date_match"]+=1
            else:
                source_all["original_event_and_station_night_DATE_CONFLICT"]+=1
        tag=original_tag(rec.get("PIT"))
        if tag:
            valid_pits.add(tag)
            source_all["station_matched_event_rows_with_original_PIT"]+=1
            if d and (tag,k[0],d.year) in captures:
                source_all["event_rows_with_exact_PIT_GRID_YEAR_capture_source_match"]+=1
        if numerical(rec.get("WP.available.OBS")) or numerical(rec.get("RO.available.OBS")):
            source_all["station_matched_events_with_at_least_one_numeric_observed_seed_amount"]+=1
        ev=token(rec.get("Visit.ID"))
        if ev:
            event_key_census[(*k,ev)]+=1
    def view_stat(records):
        unique=set()
        eligible=0
        overlapping=0
        for rec in records:
            k=original_key(rec,("Grid","Site","Session","Night"))
            vid=token(rec.get("Visit.ID"))
            if k and vid:
                key=(*k,vid)
                unique.add(key)
                eligible+=1
                if key in event_key_census:
                    overlapping+=1
        return {
            "original_rows":len(records),
            "rows_with_complete_original_grid_site_session_night_visit_ID":eligible,
            "unique_original_view_event_keys":len(unique),
            "rows_with_exact_key_in_all_foraging_source":overlapping,
            "not_an_additional_independent_dataset":True,
        }
    date_denom=source_all["event_and_station_night_dates_both_parseable"]
    good_ratio=(source_all["original_event_and_station_night_exact_date_match"]/
                date_denom if date_denom else 0)
    checks={
        "at_least_100_unique_valid_dated_original_station_nights":
            source_station["station_nights_valid_date"]>=REQUIRED_STATION,
        "at_least_100_exact_station_night_matched_events":
            source_all["event_rows_with_exact_original_station_night"]>=REQUIRED_MATCHED_EVENTS,
        "matched_events_in_at_least_3_original_grids":
            len(matched_grids)>=REQUIRED_GRID,
        "at_least_30_exact_PIT_grid_year_linked_capture_and_foraging_events":
            source_all["event_rows_with_exact_PIT_GRID_YEAR_capture_source_match"]>=REQUIRED_IDENTIFIED_EVENTS,
        "at_least_60_original_station_nights_numeric_two_seed_set_fields":
            source_station["original_station_nights_both_seed_set_numeric"]>=REQUIRED_SEED_STATIONS,
        "at_least_30_station_matched_events_one_numeric_observed_seed_field":
            source_all["station_matched_events_with_at_least_one_numeric_observed_seed_amount"]>=REQUIRED_SEED_EVENTS,
        "at_least_half_parseable_events_match_original_station_calendar_date":
            date_denom>0 and good_ratio>=REQUIRED_DATE_RATIO,
        "mouse_and_vole_views_both_have_exact_original_all_foraging_keys":
            (view_stat(mouse)["rows_with_exact_key_in_all_foraging_source"]>0
             and view_stat(vole)["rows_with_exact_key_in_all_foraging_source"]>0),
    }
    return {
        "schema":"neon.figshare_2026_capture_foraging_station_night_original_link.v1",
        "status":("SOURCE_JOIN_GO_NOT_DETECTOR_CALIBRATION_OR_ECOLOGICAL_EFFECT"
                  if all(checks.values()) else
                  "SOURCE_JOIN_STOP_MATCHED_EFFORT_ID_OR_RESOURCE_COVERAGE"),
        "original_figshare_article_id":ARTICLE,
        "original_version":VERSION,
        "original_article_metadata_sha256":metadata_digest,
        "original_five_file_sha_receipts":hashes,
        "source_station_night_census":dict(sorted(source_station.items())),
        "source_capture_identification_census":dict(sorted(source_capt.items())),
        "source_foraging_station_ID_seed_census":dict(sorted(source_all.items())),
        "distinct_original_stations_with_matched_foraging_records":len(matched_stations),
        "original_grids_with_matched_foraging_records":len(matched_grids),
        "distinct_original_PITs_in_matched_foraging_events":len(valid_pits),
        "full_foraging_rows_with_repeated_station_key_and_VisitID":
            sum(v-1 for v in event_key_census.values() if v>1),
        "mouse_view_source_overlap":view_stat(mouse),
        "vole_view_source_overlap":view_stat(vole),
        "original_foraging_station_date_consistency_rate":good_ratio,
        "original_source_admission_checks":checks,
        "no_original_PIT_Grid_Site_Date_seed_amount_or_camera_response_exported":True,
        "no_seed_found_consumed_dispersed_choice_or_foraging_time_measured":True,
        "no_original_taxon_or_pit_response_model_fitted":True,
        "not_continuous_operable_camera_night_time_or_detection_probability":True,
        "same_field_forest_as_2023_study_2018_PIT_overlap_unchecked":True,
        "no_NEON_Portal_Finland_Structural_effect_recomputed":True,
        "one_NEON_Draft_SUBMISSION_HOLD":True,
        "protocol":PROTOCOL,
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
    }

def main():
    global PHASE
    try:
        tables,hashed,meta=load_five()
        out=tally_structural(tables,hashed,meta)
        code=0
    except Exception as exc:
        out={"schema":"neon.figshare_2026_capture_foraging_station_night_original_link.v1",
             "status":"SOURCE_STOP_ORIGINAL_FILE_OR_SCHEMA",
             "source_phase":PHASE,"error_type":type(exc).__name__,
             "reason_code":str(exc)[:160],
             "no_raw_or_effect_imputation":True}
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps(out,sort_keys=True,indent=2))
    return code

if __name__=="__main__":
    raise SystemExit(main())
