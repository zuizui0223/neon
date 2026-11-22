#!/usr/bin/env python3
"""Original regional NOAA weather CSV HEADER inspection after schema STOP.

Only immutable Git SHA, provider CSV header, byte size and declared station
metadata are accessed. NEVER read or print original numerical precipitation.
"""
from __future__ import annotations
import csv,json
from datetime import datetime,timezone
from io import StringIO
from pathlib import Path

from analysis.audit_portal_2022_regional_rain_context_v1 import (
    ORIGINAL_SOURCES,pinned_bytes,SOURCE_COMMIT
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_portal_region_rain_schema_diagnosis_20261121.json"

def run():
    report={}
    for name,(path,sha,station,cap) in ORIGINAL_SOURCES.items():
        original=pinned_bytes(path,sha,cap)
        first=original.split(b"\n",1)[0].decode("utf-8-sig").strip("\r")
        cols=next(csv.reader(StringIO(first)))
        report[name]={
            "path":path,
            "source_hash_verified":sha,
            "original_byte_size":len(original),
            "header_field_names":cols,
            "source_header_count":len(cols),
            "has_exact_lowercase_required_columns":
                {"year","month","day","station","prcp"}.issubset(set(cols)),
            "no_rainfall_rows_or_values_read":True
        }
    return {
        "schema":"neon.portal_regional_rain_original_header_audit.v1",
        "status":"SOURCE_SCHEMA_DIAGNOSIS_AFTER_CAP_AND_HEADER_STOPS",
        "source_commit":SOURCE_COMMIT,
        "sources":report,
        "no_regional_rainfall_values_calculated":True,
        "previous_2020_25_rodent_or_plant_response_unread":True,
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    try:r=run();exitcode=0
    except Exception as e:
        r={"schema":"neon.portal_regional_rain_original_header_audit.v1",
           "status":"STOP_ORIGINAL_HEADER_SOURCE","failure":str(e)[:140],
           "no_rainfall_value_read":True}
        exitcode=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    print(json.dumps(r,sort_keys=True,indent=2))
    return exitcode

if __name__=="__main__":
    raise SystemExit(main())
