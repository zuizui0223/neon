#!/usr/bin/env python3
"""Verified Figshare vole contact source: timeline STRUCTURE, no pair outcome.

Reads only date string syntax/blankness of seven MD5-pinned CSVs.
Does not inspect dyad IDs, tags, exact event dates, contact rates, biology.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from io import StringIO
import csv,json,re
from analysis.neon_prairie_vole_verified_raw_schema_v1 import PIN,get_original

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_prairie_vole_date_format_source_20261115.json"
DATES={
 "collar_ids.csv":("date_on","date_off"),
 "proxlog_summary.csv":("date","collar on","collar off","collar download"),
 "prox_full_noduplicates.csv":("date","datetime"),
 "full_voles_trap.csv":("date",),
 "rfid_trap_network_data_method.csv":("TimeStart","TimeStop")
}
STAGE="ORIGINAL_DATE_SYNTAX_ONLY"
def date_pattern(value):
    if value is None or not str(value).strip():return "MISSING"
    return re.sub(r"[0-9]","#",str(value).strip())[:64]
def parse_headers(original):
    rows=list(csv.DictReader(StringIO(original.decode("utf-8-sig"))))
    # Time columns in this audit do NOT include R unnamed index fields.
    return rows
def audit():
    global STAGE
    summary={}
    for name,fields in DATES.items():
        raw=get_original(name)
        with StringIO(raw.decode("utf-8-sig")) as h:
            reader=csv.DictReader(h)
            headers=reader.fieldnames or []
            if not set(fields)<=set(headers):
                raise ValueError("DATE_FIELDS_NOT_IN_ORIGINAL_"+name)
            patterns={column:Counter() for column in fields}
            n=0
            for row in reader:
                n+=1
                for column in fields:
                    patterns[column][date_pattern(row.get(column))]+=1
        summary[name]={
            "source_file_id":PIN[name][0],
            "source_MD5_verified":True,
            "source_rows":n,
            "date_time_source_patterns":{
                column:dict(sorted(counter.items()))
                for column,counter in patterns.items()
            },
            "source_event_calendar_values_not_exported":True
        }
    return {
        "schema":"neon.prairie_vole_sensor_and_trap_date_formats.v1",
        "status":"ORIGINAL_PROVIDER_VERIFIED_DATE_SYNTAX_NOT_LOGGER_EFFORT",
        "source":"Figshare project 228462, seven original published CSVs",
        "date_syntax_summary":summary,
        "no_collar_identity_time_join_done":True,
        "no_proximity_pair_or_trap_pair_events_scored":True,
        "source_next_gate":"Choose unambiguous source date parser, verify collar actual operating intervals and same-time trap events before any dyad persistence or contact claim",
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }
def main():
    global STAGE
    try: result=audit();code=0
    except Exception as exc:
        result={
            "schema":"neon.prairie_vole_sensor_and_trap_date_formats.v1",
            "status":"STOP_PUBLISHED_SOURCE_DATE_FORMAT_SCHEMA",
            "failed_stage":STAGE,"source_error_class":type(exc).__name__,
            "source_error_code":str(exc),
            "animal_contact_effects_not_opened":True
        };code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code
if __name__=="__main__":raise SystemExit(main())
