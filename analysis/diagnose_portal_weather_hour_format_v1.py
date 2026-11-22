#!/usr/bin/env python3
"""Effect-blind schema diagnosis of original Portal station 'hour' labels.

Read the pinned original Git blob; do NOT read precipitation numeric values,
model coefficients, vegetation greenness or rodent records.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
import json

from analysis.audit_portal_2022_site_climate_source_v1 import (
    get_pinned_raw,iter_csv,YEARS,MONSOON_MONTHS,SOURCE_COMMIT
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_portal_weather_hour_schema_diag_20261121.json"

def run():
    raw=get_pinned_raw("Weather/Portal_weather.csv")
    counts=Counter()
    byyear=defaultdict(Counter)
    mapping=Counter()
    stats=Counter()
    for row in iter_csv(raw,("year","month","day","hour","timestamp")):
        try:y=int(row["year"]);m=int(row["month"])
        except (ValueError,TypeError):continue
        if y not in YEARS or m not in MONSOON_MONTHS:continue
        label=(row["hour"] or "").strip()
        timestamp=(row["timestamp"] or "").strip()
        counts[label]+=1
        byyear[str(y)][label]+=1
        stats["target_source_rows"]+=1
        # Ordinal timestamp fields are metadata; no precipitation values.
        hh=""
        if " " in timestamp:
            hh=timestamp.split(" ",1)[1].split(":",1)[0]
        if hh.isdigit():
            mapping[(label,hh)]+=1
        else:
            stats["timestamp_hour_unparsed"]+=1
    return {
        "schema":"neon.portal_original_hour_label_format_audit.v1",
        "status":"SOURCE_HOUR_FORMAT_DIAGNOSIS_ONLY",
        "source_original_git_commit":SOURCE_COMMIT,
        "no_precipitation_or_NDVI_numeric_values_read":True,
        "no_mammal_or_plant_effect_read":True,
        "all_unique_hour_labels_and_counts":dict(sorted(counts.items(),
            key=lambda z:(int(z[0]) if z[0].isdigit() else 99999,z[0]))),
        "distinct_hour_labels":len(counts),
        "per_year_unique_label_count":{y:len(c) for y,c in sorted(byyear.items())},
        "source_label_to_timestamp_hour_counts":[
            {"hour_label":label,"timestamp_hour":hh,"source_rows":value}
            for (label,hh),value in sorted(mapping.items(),
                key=lambda z:(int(z[0][0]) if z[0][0].isdigit() else 99999,z[0][1]))
        ],
        "source_census_counts":dict(sorted(stats.items())),
        "this_is_diagnosis_after_two_format_stops_not_a_biological_result":True,
    }

def main():
    try:r=run();code=0
    except Exception as e:
        r={"status":"STOP_SOURCE_DIAGNOSIS","error_class":type(e).__name__,
           "code":str(e)[:120],"no_precipitation_effect_read":True}
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps(r,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
