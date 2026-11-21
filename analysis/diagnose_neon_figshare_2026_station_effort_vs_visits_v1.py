#!/usr/bin/env python3
"""Inspect original Figshare 2026 station camera opportunity vs observed visits.

Original frozen 291-row source gate REMAINS STOP (three nonempty keyless
records). Only metadata fields and exact source keys are read, not animal IDs,
species, seed amounts or foraging outcomes. This is neither a validated
camera-effort denominator nor an ecological effect.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import json

from analysis.audit_neon_figshare_2026_foraging_station_effort_ID_source_v1 import (
    load_five,original_key,original_day,token,numerical
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_figshare_2026_camera_opportunity_vs_visits_source_v1.json"
PROTOCOL="docs/NEON_FIGSHARE_2026_CAMERA_OPPORTUNITY_VS_VISITS_DESIGN_20261121.md"
KEYS=("Grid","Site","Session","Night")
META=("Date","Night.set","Morning.check","WP.seeds.set","RO.seeds.set")

def source_only_table(data):
    rows=data["All Station Nights.csv"]
    events=data["All Foraging Clean.csv"]
    if len(rows)!=291 or len(events)!=3243:
        raise ValueError("ORIGINAL_SOURCE_291_3243_SOURCE_CARDINALITY_DRIFT")
    events_by_key=Counter()
    for ev in events:
        key=original_key(ev,KEYS)
        if not key:
            raise ValueError("ORIGINAL_FORAGING_EVENT_MISSING_SOURCE_KEY")
        events_by_key[key]+=1
    groups=defaultdict(Counter)
    complete=set()
    malformed=[]
    for idx,row in enumerate(rows):
        key=original_key(row,KEYS)
        if not key:
            fields=sorted(f for f,v in row.items() if f not in KEYS and
                          isinstance(v,str) and v.strip())
            malformed.append({
                "original_one_based_source_CSV_row_number_after_header":idx+1,
                "names_of_nonempty_nonkey_original_columns_ONLY":fields,
                "other_nonempty_source_column_count":len(fields)
            })
            continue
        if key in complete:
            raise ValueError("DUPLICATE_ORIGINAL_COMPLETE_STATION_NIGHT_KEY")
        complete.add(key)
        visited=(key in events_by_key)
        group="at_least_one_observed_video_event" if visited else "no_record_in_all_foraging_events"
        stats=groups[group]
        stats["number_of_original_station_nights"]+=1
        stats["original_Date_parseable"]+=int(original_day(row.get("Date")) is not None)
        n=token(row.get("Night.set")) is not None
        m=token(row.get("Morning.check")) is not None
        stats["original_Night_set_nonmissing"]+=int(n)
        stats["original_Morning_check_nonmissing"]+=int(m)
        stats["both_original_setup_and_morning_check_nonmissing"]+=int(n and m)
        stats["both_original_seed_set_columns_numeric"]+=int(
            numerical(row.get("WP.seeds.set")) and
            numerical(row.get("RO.seeds.set"))
        )
        stats["station_source_rows_with_no_parsable_Date"]+=int(
            original_day(row.get("Date")) is None
        )
    if len(complete)!=288 or len(malformed)!=3 or len(events_by_key)!=136 or not (
        all(key in complete for key in events_by_key)
    ):
        raise ValueError("ORIGINAL_SOURCE_288_3_136_SUPPORT_DRIFT")
    if Counter(z["other_nonempty_source_column_count"] for z in malformed)!={2:2,4:1}:
        raise ValueError("ORIGINAL_KEYLESS_NONBLANK_RECORD_TYPE_DRIFT")
    data_out={name:dict(sorted(value.items())) for name,value in groups.items()}
    with_visit=data_out.get("at_least_one_observed_video_event",{})
    without=data_out.get("no_record_in_all_foraging_events",{})
    complete_nonvisit=without.get("both_original_setup_and_morning_check_nonmissing",0)
    original_Date_only_video=(
        with_visit.get("original_Date_parseable",0)==with_visit.get("number_of_original_station_nights",0)
        and without.get("original_Date_parseable",0)==0
    )
    return {
        "schema":"neon.figshare2026_original_camera_opportunity_versus_visits_source.v1",
        "status":"SOURCE_METADATA_DIAGNOSTIC_ORIGINAL_291_ROW_STRICT_STOP_RETAINED",
        "source_only_station_night_categories":data_out,
        "three_original_keyless_nonblank_source_record_types":malformed,
        "original_complete_source_station_night_keys":len(complete),
        "unique_keyed_station_nights_with_foraging_events":len(events_by_key),
        "keyed_station_nights_without_foraging_event":len(complete)-len(events_by_key),
        "source_Date_perfectly_conditional_on_observed_event_metadata":original_Date_only_video,
        "nonvisit_station_night_rows_with_both_set_check_nonmissing":complete_nonvisit,
        "has_at_least_100_no_event_station_nights_with_set_check_nonmissing":
            complete_nonvisit>=100,
        "setup_and_morning_check_nonmissing_NOT_verified_Camera_operability":True,
        "three_original_keyless_nonblank_rows_not_dropped_from_frozen_GO":True,
        "source_original_291_row_full_key_GO_remains_FAILED":True,
        "no_unobserved_camera_event_equated_with_true_absence":True,
        "no_original_PIT_species_seed_amounts_or_behavior_values_exported":True,
        "no_original_resource_preference_or_learning_effect_calculated":True,
        "one_NEON_ecology_Draft_SUBMISSION_HOLD":True,
    }

def main():
    try:
        data,sha,meta=load_five()
        result=source_only_table(data)
        result["original_provider_5_file_byte_MD5_verified"]=True
        result["original_figshare_article_id"]=28207769
        result["original_source_metadata_sha256"]=meta
        result["original_source_code_paths"]=PROTOCOL
        result["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
        status=0
    except Exception as exc:
        result={
            "schema":"neon.figshare2026_original_camera_opportunity_versus_visits_source.v1",
            "status":"SOURCE_DIAGNOSTIC_STOP",
            "error_type":type(exc).__name__,
            "error_code":str(exc)[:160],
            "no_raw_mammal_effect_calculated":True
        }
        status=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True,indent=2))
    return status

if __name__=="__main__":
    raise SystemExit(main())
