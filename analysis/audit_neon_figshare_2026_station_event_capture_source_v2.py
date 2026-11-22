#!/usr/bin/env python3
"""Corrected source-only Figshare 2026 station/foraging/capture bridge, v2.

Different version from immutable source v1, which FAILED because it mistook 3
verified original summary rows for nonkeyed station-nights and interpreted
two-digit capture YEAR as a full calendar year. ALL original numeric source
admission thresholds are preserved; no animal seed-use response is opened.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import json
import re

from analysis.audit_neon_figshare_2026_foraging_station_effort_ID_source_v1 import (
    load_five,original_key,original_day,original_tag,token,numerical,
    REQUIRED_STATION,REQUIRED_MATCHED_EVENTS,REQUIRED_GRID,
    REQUIRED_IDENTIFIED_EVENTS,REQUIRED_SEED_STATIONS,REQUIRED_SEED_EVENTS,
    REQUIRED_DATE_RATIO
)
from analysis.reconcile_neon_figshare_2026_station_summaries_v1 import reconcile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_figshare_2026_station_event_capture_source_v2.json"
PROTOCOL="docs/NEON_FIGSHARE_2026_CORRECTED_STATION_SOURCE_V2_20261122.md"
FIVE_COUNTS=(11614,3243,291,883,951)
KEYS=("Grid","Site","Session","Night")

def require(ok,code):
    if not ok:raise ValueError("SOURCE_V2_STOP_"+code)

def source_verified_calendar_year(row):
    """The original capture YEAR codes 16..23 validated by source DATE."""
    txt=token(row.get("YEAR"))
    dt=original_day(row.get("DATE"))
    require(txt is not None and
            re.fullmatch(r"1[6-9]|2[0-3]",txt) is not None,
            "ORIGINAL_CAPTURE_2DIGIT_YEAR_ONTOLOGY_CHANGE")
    require(dt is not None and dt.year==2000+int(txt),
            "ORIGINAL_CAPTURE_YEAR_AND_DATE_NOT_IDENTICAL")
    return dt.year

def corrected_source_only(tables,provenance,metadata_sha):
    named=(
        "2016-2023 Capture Data.csv","All Foraging Clean.csv",
        "All Station Nights.csv","Mouse Foraging Data Clean.csv",
        "Vole Foraging Data Clean.csv"
    )
    require(tuple(len(tables[s]) for s in named)==FIVE_COUNTS,
            "IMMUTABLE_ORIGINAL_FIVE_CSV_ROWS_DRIFT")
    captures,events,station_source,mouse,vole=(tables[s] for s in named)
    # Must verify three original footer records via the independently
    # authored v1 field count audit BEFORE a 288-row station subset exists.
    verified=reconcile(station_source,events)
    require(verified["station_source_rows"]==291 and
            verified["station_nights"]==288 and
            len(verified["verified_tail_summaries"])==3 and
            verified["station_nights_with_event_rows"]==136,
            "ORIGINAL_FOOTER_OR_STATION_ID_QA_CHANGE")
    station_rows=station_source[:-3]
    by_key={}
    site=Counter()
    for row in station_rows:
        key=original_key(row,KEYS)
        require(key is not None and key not in by_key,
                "INCOMPLETE_OR_DUPLICATE_EXPERIMENTAL_STATION")
        by_key[key]=row
        site["original_288_verified_station_nights"]+=1
        site["with_source_parseable_Date"]+=int(original_day(row.get("Date")) is not None)
        site["with_both_numeric_original_WP_RO_offered"]+=int(
            numerical(row.get("WP.seeds.set")) and
            numerical(row.get("RO.seeds.set"))
        )
        site["source_setup_and_morning_fields_both_nonmissing"]+=int(
            token(row.get("Night.set")) is not None and
            token(row.get("Morning.check")) is not None)
    require(len(by_key)==288,"STATION_ROSTER_DIFFERENT_FROM_FOOTER_COHORT")
    capture_source=Counter()
    capture_key=set()
    for row in captures:
        calendar_year=source_verified_calendar_year(row)
        capture_source["all_11614_capture_YEAR_2DIGIT_DATE_verified"]+=1
        pit=original_tag(row.get("PIT"))
        grid=token(row.get("GRID"))
        if pit and grid:
            capture_key.add((pit,grid,calendar_year))
            capture_source["capture_rows_with_original_PIT_GRID_YEAR_verified"]+=1
        else:
            capture_source["capture_rows_missing_PIT_or_GRID"]+=1
    require(capture_source["all_11614_capture_YEAR_2DIGIT_DATE_verified"]==11614,
            "CAPTURE_CALENDAR_FORMAT_INCOMPLETE")
    ev=Counter()
    matched_grid=set()
    matched_stations=set()
    original_pit_tags=set()
    all_event_keys=Counter()
    for row in events:
        key=original_key(row,KEYS)
        require(key is not None and key in by_key,
                "ORIGINAL_FORAGING_EVENT_HAS_NO_EXACT_STATION_NIGHT")
        ev["all_foraging_rows_with_exact_source_station_night"]+=1
        matched_grid.add(key[0])
        matched_stations.add(key)
        dt=original_day(row.get("Date"))
        src=original_day(by_key[key].get("Date"))
        if dt and src:
            ev["event_and_station_dates_both_parseable"]+=1
            ev["source_event_and_station_dates_equal"]+=int(dt==src)
            ev["source_event_and_station_dates_NOT_EQUAL"]+=int(dt!=src)
        else:ev["event_or_station_original_date_missing"]+=1
        pit=original_tag(row.get("PIT"))
        if pit:
            original_pit_tags.add(pit)
            ev["original_foraging_rows_with_literal_PIT"]+=1
            if dt and (pit,key[0],dt.year) in capture_key:
                ev["foraging_rows_exact_capture_PIT_GRID_DATE_YEAR_match"]+=1
        if numerical(row.get("WP.available.OBS")) or numerical(row.get("RO.available.OBS")):
            ev["foraging_rows_at_least_one_numeric_observed_seed_availability"]+=1
        visit=token(row.get("Visit.ID"))
        if visit:
            all_event_keys[(*key,visit)]+=1
    def taxon_view(source_rows):
        valid=0
        overlap=0
        uniques=set()
        for row in source_rows:
            key=original_key(row,KEYS)
            visit=token(row.get("Visit.ID"))
            if key and visit:
                composite=(*key,visit)
                valid+=1
                uniques.add(composite)
                overlap+=int(composite in all_event_keys)
        return {
          "original_view_source_rows":len(source_rows),
          "original_complete_event_identifier_source_rows":valid,
          "original_view_unique_identifiers":len(uniques),
          "rows_existing_in_original_All_Foraging":overlap,
          "overlapping_view_NOT_independent_observation_set":True
        }
    views={"mouse":taxon_view(mouse),"vole":taxon_view(vole)}
    denom=ev["event_and_station_dates_both_parseable"]
    ratio=ev["source_event_and_station_dates_equal"]/denom if denom else 0
    checks={
      "original_288_station_footer_and_summary_validation":True,
      "at_least_100_unique_original_source_dated_station_nights":
          site["with_source_parseable_Date"]>=REQUIRED_STATION,
      "at_least_100_exact_station_night_matched_events":
          ev["all_foraging_rows_with_exact_source_station_night"]>=REQUIRED_MATCHED_EVENTS,
      "matched_events_in_at_least_3_original_grids":
          len(matched_grid)>=REQUIRED_GRID,
      "at_least_30_exact_capture_PIT_GRID_calendar_YEAR_matched_event_rows":
          ev["foraging_rows_exact_capture_PIT_GRID_DATE_YEAR_match"]>=REQUIRED_IDENTIFIED_EVENTS,
      "at_least_60_station_nights_with_both_original_seed_offerings_numeric":
          site["with_both_numeric_original_WP_RO_offered"]>=REQUIRED_SEED_STATIONS,
      "at_least_30_matched_foraging_rows_with_numeric_observed_seed_offer":
          ev["foraging_rows_at_least_one_numeric_observed_seed_availability"]>=REQUIRED_SEED_EVENTS,
      "at_least_half_of_parseable_event_station_dates_exactly_equal":
          denom>0 and ratio>=REQUIRED_DATE_RATIO,
      "mouse_and_vole_taxon_views_each_overlap_combined_source":
          (views["mouse"]["rows_existing_in_original_All_Foraging"]>0
           and views["vole"]["rows_existing_in_original_All_Foraging"]>0)
    }
    return {
      "schema":"neon.figshare2026_original_station_event_capture_SOURCE_v2",
      "status":("CORRECTED_SOURCE_JOIN_GO_NOT_DETECTOR_OPERATION_OR_BIOLOGICAL_EFFECT"
                if all(checks.values()) else
                "CORRECTED_SOURCE_JOIN_STOP_THRESHOLD_OR_SOURCE_SUPPORT"),
      "original_figshare_article_id":28207769,
      "original_figshare_article_version":2,
      "original_publisher_FiveFiles_MD5_SHA256_verified":True,
      "provider_metadata_sha256":metadata_sha,
      "five_original_file_sha_receipts":provenance,
      "historical_v1_all_291_rows_keyed_gate_result":"FAIL_PRESERVED_IN_ORIGINAL_V1",
      "v1_failure_cause":"last_3_verified_arithmetic_summary_rows_not_stations",
      "v1_capture_year_failure_cause":"two_digit_year_16_to_23_matches_2016_to_2023_original_DATE",
      "original_all_station_csv_rows_including_summaries":291,
      "original_verified_experimental_station_night_rows":288,
      "original_verified_summary_rows_not_observations":3,
      "verified_original_summary_types":
          [z["summary_type"] for z in verified["verified_tail_summaries"]],
      "original_station_rows_with_video_event_key":len(matched_stations),
      "original_station_rows_without_video_event_key":288-len(matched_stations),
      "station_source_census":dict(sorted(site.items())),
      "capture_source_identity_census":dict(sorted(capture_source.items())),
      "original_foraging_event_source_census":dict(sorted(ev.items())),
      "grids_with_source_foraging_events":len(matched_grid),
      "distinct_original_source_PITs_not_independent_animal_population":len(original_pit_tags),
      "original_repeated_composite_visit_identifiers":
          sum(n-1 for n in all_event_keys.values() if n>1),
      "mouse_view_is_subset_source":views["mouse"],
      "vole_view_is_subset_source":views["vole"],
      "source_date_exact_equality_ratio":ratio,
      "original_v1_numerical_support_gates_unchanged":True,
      "v2_original_source_only_admission_checks":checks,
      "positive_event_table_NOT_all_cameras_or_all_visits":True,
      "source_setup_morning_dates_NOT_continuous_camera_operability":True,
      "original_source_mismatched_dates_NOT_shifted":True,
      "seed_fate_or_seed_consumption_or_finding_outcomes_NOT_computed":True,
      "no_spatial_occupancy_or_mammal_niche_resource_learning_model":True,
      "same_forest_as_2018_Penobscot_seed_study_NOT_independent_geographic_system":True,
      "original_neon_portal_finland_and_density_results_unchanged":True,
      "one_NEON_ecological_manuscript_Draft_SUBMISSION_HOLD":True,
      "fixed_source_v2_protocol":PROTOCOL,
      "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    try:
        tabs,provenance,meta=load_five()
        result=corrected_source_only(tabs,provenance,meta)
        code=0 if result["status"].startswith("CORRECTED_SOURCE_JOIN_GO") else 3
    except Exception as exc:
        result={"schema":"neon.figshare2026_original_station_event_capture_SOURCE_v2",
                "status":"CORRECTED_SOURCE_STOP_ORIGINAL_5_FILES_OR_RECORD_ONTOLOGY",
                "error_type":type(exc).__name__,
                "stop_code":str(exc)[:180],
                "source_v1_fail_and_evidence_persist":True,
                "no_mammal_effect_or_source_imputation":True}
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,sort_keys=True,indent=2))
    return code

if __name__=="__main__":
    raise SystemExit(main())
