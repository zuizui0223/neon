#!/usr/bin/env python3
"""Source-only diagnosis after original Figshare 2026 station-key STOP.

Reads ONLY original MD5-pinned source identity/calendar keys. Does not access
species outcomes, seed finding, consumption, temporal effects or behavioral
response values. NEVER exports original site, grid, PIT, station or timestamps.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import json

from analysis.audit_neon_figshare_2026_foraging_station_effort_ID_source_v1 import (
    load_five, token, original_day, original_key
)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_figshare_2026_station_key_source_diagnosis_v1.json"
FIELDS=("Grid","Site","Session","Night")

def source_key_census(rows):
    miss=Counter();seen=Counter();dates=Counter();vary=defaultdict(set)
    original_keyless_source_record_other_field_presence=Counter()
    for row in rows:
        for field in FIELDS:
            if token(row.get(field)) is None:
                miss[field]+=1
            else:
                vary[field].add(token(row.get(field)))
        k=original_key(row,FIELDS)
        if k:
            seen[k]+=1
            dates["rows_with_complete_station_night_key"]+=1
            if original_day(row.get("Date")) is not None:
                dates["complete_key_rows_with_parseable_Date"]+=1
        else:
            dates["rows_with_missing_some_station_night_key"]+=1
            other_populated=sum(bool((val or "").strip()) for field,val in row.items()
                                if field not in FIELDS)
            original_keyless_source_record_other_field_presence[other_populated]+=1
        if original_day(row.get("Date")) is not None:
            dates["total_rows_with_parseable_Date"]+=1
    return {
        "source_original_rows":len(rows),
        "number_of_missing_original_values_per_key_component":dict(sorted(miss.items())),
        "source_unique_literal_value_count_per_key_component":
            {field:len(vary[field]) for field in FIELDS},
        "source_distinct_complete_station_night_keys":len(seen),
        "keyless_original_rows_other_fields_nonempty_count_histogram":
            dict(sorted(original_keyless_source_record_other_field_presence.items())),
        "complete_station_night_key_collision_row_count":
            sum(n-1 for n in seen.values() if n>1),
        "original_header_and_date_source_census":dict(sorted(dates.items())),
    },seen

def run():
    tables,files,metadata=load_five()
    st,available=source_key_census(tables["All Station Nights.csv"])
    ev,events=source_key_census(tables["All Foraging Clean.csv"])
    return {
        "schema":"neon.figshare2026_station_night_original_missing_key_diagnostic.v1",
        "status":"ORIGINAL_KEYS_ONLY_DIAGNOSED_AFTER_FROZEN_SOURCE_STOP",
        "original_figshare_article_id":28207769,
        "original_version":2,
        "original_MD5_and_five_file_byte_sources_reverified":True,
        "source_metadata_sha256":metadata,
        "station_night_source_keys":st,
        "foraging_event_source_keys":ev,
        "distinct_complete_original_foraging_keys_also_in_station_nights":
            sum(k in available for k in events),
        "original_source_labels_and_PITs_not_exported":True,
        "no_original_resource_outcome_or_TREAT_effect_opened":True,
        "no_change_to_frozen_original_zero_missing_station_key_gate":True,
        "no_2023_data_or_biological_estimate_opened":True,
        "one_NEON_ecology_Draft_SUBMISSION_HOLD":True,
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
    }

def main():
    try:res=run();code=0
    except Exception as e:
        res={"schema":"neon.figshare2026_station_night_original_missing_key_diagnostic.v1",
             "status":"SOURCE_DIAGNOSIS_STOP",
             "error":type(e).__name__,
             "error_code":str(e)[:140],"no_biological_effect_computed":True}
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print(json.dumps(res,indent=2,sort_keys=True))
    return code
if __name__=="__main__":
    raise SystemExit(main())
