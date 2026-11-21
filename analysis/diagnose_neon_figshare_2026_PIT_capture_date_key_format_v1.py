#!/usr/bin/env python3
"""Source-only original 2026 Figshare PIT/grid/year and calendar format diagnosis.

Original strict source admission remains STOP. No recoding individual IDs,
no time shifts and no foraging/seed/predator biological outcomes.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import json,re

from analysis.audit_neon_figshare_2026_foraging_station_effort_ID_source_v1 import (
    load_five,original_tag,token,original_day,original_key
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_figshare_2026_PIT_capture_and_date_key_diagnostic_20261121.json"

def diagnostic():
    data,integrity,meta=load_five()
    capt=data["2016-2023 Capture Data.csv"]
    events=data["All Foraging Clean.csv"]
    stations=data["All Station Nights.csv"]
    c=Counter();unique_pit=set();unique_grid=set();year_labels=Counter()
    capture_tuples=set();capture_tag_grid=set()
    for row in capt:
        tag=original_tag(row.get("PIT"))
        grid=token(row.get("GRID"))
        yr=token(row.get("YEAR"))
        day=original_day(row.get("DATE"))
        c["original_source_capture_rows"]+=1
        c["capture_rows_with_literal_PIT"]+=int(bool(tag))
        c["capture_rows_with_literal_GRID"]+=int(bool(grid))
        c["capture_rows_with_literal_YEAR"]+=int(bool(yr))
        c["capture_rows_with_parsable_DATE"]+=int(day is not None)
        if tag:unique_pit.add(tag)
        if grid:unique_grid.add(grid)
        if tag and grid:capture_tag_grid.add((tag,grid))
        if yr:
            if re.fullmatch(r"\d{4}",yr):
                year_labels["four_digits"]+=1
                if tag and grid:capture_tuples.add((tag,grid,int(yr)))
            elif re.fullmatch(r"\d{4}\.0+",yr):
                year_labels["four_digits_dot_zeros"]+=1
            elif re.fullmatch(r"\d+",yr):
                year_labels["other_numeric_digit_length"]+=1
            else:
                year_labels["other_or_non_integer_year_source"]+=1
        else:
            year_labels["missing_year"]+=1
        if yr and day:
            c["original_capture_DATE_and_YEAR_literal_text_equal"]+=int(
                yr==str(day.year))
    ep=set();eg=set();ept=set();eptg=set()
    event_count=Counter();event_year_parse=Counter()
    for row in events:
        tag=original_tag(row.get("PIT"))
        grid=token(row.get("Grid"))
        day=original_day(row.get("Date"))
        event_count["original_event_rows"]+=1
        if tag:ep.add(tag)
        if grid:eg.add(grid)
        if tag and grid:
            eptg.add((tag,grid))
            event_count["event_rows_with_exact_PIT_and_GRID"]+=1
            event_count["original_event_rows_exact_capture_PIT_GRID_match"]+=int(
                (tag,grid) in capture_tag_grid)
        if tag:
            event_count["original_event_rows_exact_capture_PIT_only_match"]+=int(
                tag in unique_pit)
        if tag and grid and day:
            ept.add((tag,grid,day.year))
            event_count["original_event_rows_exact_capture_PIT_GRID_year_match"]+=int(
                (tag,grid,day.year) in capture_tuples)
        if day:
            event_year_parse[str(day.year)]+=1
    station_index={}
    for row in stations:
        key=original_key(row,("Grid","Site","Session","Night"))
        if key:station_index[key]=row
    day_diffs=Counter()
    for row in events:
        key=original_key(row,("Grid","Site","Session","Night"))
        if not key or key not in station_index:continue
        da=original_day(row.get("Date"))
        db=original_day(station_index[key].get("Date"))
        if not da or not db:
            day_diffs["at_least_one_original_date_unparsable"]+=1
            continue
        delta=(da-db).days
        day_diffs[str(delta) if abs(delta)<=3 else "original_dates_more_than_3_days_apart"]+=1
    return {
      "schema":"neon.figshare2026_original_PIT_grid_year_calendar_key_diagnostic.v1",
      "status":"AFTER_SOURCE_STOP_IDENTIFICATION_AND_DATE_FORMAT_ONLY_NO_SOURCE_GO",
      "original_figshare_article_id":28207769,
      "version":2,"source_original_md5_and_metadata_reverified":True,
      "original_capture_field_presence_source_counts":dict(sorted(c.items())),
      "original_capture_year_literal_format_counts":dict(sorted(year_labels.items())),
      "unique_original_capture_literal_PIT_count":len(unique_pit),
      "unique_original_capture_literal_GRID_count":len(unique_grid),
      "distinct_original_capture_PIT_GRID_keys":len(capture_tag_grid),
      "distinct_capture_PIT_GRID_four_digit_YEAR_keys":len(capture_tuples),
      "unique_original_foraging_literal_PIT_count":len(ep),
      "unique_original_foraging_literal_Grid_count":len(eg),
      "distinct_exact_PIT_overlap_across_capture_and_foraging_source":len(ep&unique_pit),
      "distinct_exact_GRID_overlap_across_capture_and_foraging_source":len(eg&unique_grid),
      "distinct_exact_PIT_GRID_overlap_across_sources":len(eptg&capture_tag_grid),
      "original_foraging_event_capture_exact_match_counts":dict(sorted(event_count.items())),
      "original_foraging_rows_by_parsed_calendar_year":dict(sorted(event_year_parse.items())),
      "original_foraging_minus_station_night_date_difference_days_histogram":
          dict(sorted(day_diffs.items())),
      "no_individual_identifiers_or_exact_sites_or_calendar_dates_exported":True,
      "no_original_source_key_normalization_to_get_favorable_match":True,
      "original_frozen_all_station_nights_required_source_GO_still_FAILED":True,
      "no_original_seed_finding_choice_or_animal_trait_effect_calculated":True,
      "one_NEON_Draft_SUBMISSION_HOLD":True,
      "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    try:
        val=diagnostic();code=0
    except Exception as exc:
        val={"schema":"neon.figshare2026_original_PIT_grid_year_calendar_key_diagnostic.v1",
             "status":"DIAGNOSTIC_SOURCE_STOP","error":type(exc).__name__,
             "reason":str(exc)[:140],"no_effect_calculated":True}
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(val,sort_keys=True,indent=2)+"\n")
    print(json.dumps(val,sort_keys=True,indent=2))
    return code
if __name__=="__main__":
    raise SystemExit(main())
