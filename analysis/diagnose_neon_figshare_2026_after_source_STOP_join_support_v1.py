#!/usr/bin/env python3
"""Counterfactual structural coverage AFTER frozen 2026 Figshare source STOP.

Original 291 station-night records contain three keyless rows with OTHER
nonempty source fields, so the first frozen source gate remains FAILED. The
288 keyed records are used here ONLY to diagnose potential joins, never to
rescue scientific source GO or claim camera operability/detection probability.
No foraging, seed-choice or species-interaction outcomes are opened.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import json

from analysis.audit_neon_figshare_2026_foraging_station_effort_ID_source_v1 import (
    load_five,original_key,original_day,original_tag,token,numerical
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_figshare_2026_after_stop_structural_join_diagnostic_v1.json"
FIELDS=("Grid","Site","Session","Night")

def diagnose():
    data,hashes,md=load_five()
    rawstations=data["All Station Nights.csv"]
    events=data["All Foraging Clean.csv"]
    captures=data["2016-2023 Capture Data.csv"]
    mouse=data["Mouse Foraging Data Clean.csv"]
    vole=data["Vole Foraging Data Clean.csv"]
    if (len(rawstations),len(events),len(captures),len(mouse),len(vole))!=(
            291,3243,11614,883,951):
        raise ValueError("ORIGINAL_FIVE_TABLE_CARDINALITIES_DRIFT")

    valid_stations={}
    source=Counter()
    for row in rawstations:
        k=original_key(row,FIELDS)
        if not k:
            source["unresolved_station_night_rows_MUST_NOT_ENTER_GO"]+=1
            other_fields=sum(bool((v or "").strip()) for field,v in row.items()
                             if field not in FIELDS)
            source["missing_keys_with_other_original_nonempty_cells"]+=int(other_fields>0)
            continue
        if k in valid_stations:
            raise ValueError("DUPLICATE_ORIGINAL_COMPLETE_STATION_NIGHT_KEY")
        valid_stations[k]=row
        source["original_station_night_rows_with_all_4_keys"]+=1
        source["original_keyed_station_nights_with_Date"]+=int(original_day(row.get("Date")) is not None)
        source["original_keyed_station_nights_both_WP_RO_seeds_set_numeric"]+=int(
            numerical(row.get("WP.seeds.set")) and numerical(row.get("RO.seeds.set")))
    if source["unresolved_station_night_rows_MUST_NOT_ENTER_GO"]!=3 or (
        source["missing_keys_with_other_original_nonempty_cells"]!=3
    ):
        raise ValueError("ORIGINAL_KEYLESS_ROW_DIAGNOSTIC_DRIFT")

    cp=set()
    for row in captures:
        tag=original_tag(row.get("PIT"))
        grid=token(row.get("GRID"))
        year=token(row.get("YEAR"))
        if not tag or not grid or not year:continue
        try:y=int(year)
        except ValueError:continue
        d=original_day(row.get("DATE"))
        if d and y!=d.year:continue
        cp.add((tag,grid,y))
    ev=Counter();distinct_grid=set();distinct_keys=set()
    identifiers=set();event_ids=set()
    for row in events:
        k=original_key(row,FIELDS)
        if not k:
            ev["original_event_missing_key"]+=1
            continue
        if k not in valid_stations:
            ev["event_key_not_found_in_original_keyed_station_record"]+=1
            continue
        ev["foraging_rows_exact_matched_original_station_night_key"]+=1
        distinct_grid.add(k[0]);distinct_keys.add(k)
        tag=original_tag(row.get("PIT"))
        d=original_day(row.get("Date"))
        sd=original_day(valid_stations[k].get("Date"))
        if tag:
            identifiers.add(tag)
            ev["source_station_matched_events_with_original_PIT"]+=1
            if d and (tag,k[0],d.year) in cp:
                ev["source_events_with_PIT_GRID_calendar_year_capture_match"]+=1
        if d and sd:
            ev["source_event_and_station_date_both_parseable"]+=1
            ev["original_event_station_date_exact_equal"]+=int(d==sd)
            ev["original_event_station_date_disagree"]+=int(d!=sd)
        if numerical(row.get("WP.available.OBS")) or numerical(row.get("RO.available.OBS")):
            ev["original_matched_event_with_numeric_observed_seed_field"]+=1
        visit=token(row.get("Visit.ID"))
        if visit:
            event_ids.add((*k,visit))
    v={}
    for label,rows in (("mouse",mouse),("vole",vole)):
        complete=0;in_all=0
        unique=set()
        for row in rows:
            k=original_key(row,FIELDS)
            vis=token(row.get("Visit.ID"))
            if not (k and vis):continue
            complete+=1
            z=(*k,vis)
            unique.add(z)
            in_all+=int(z in event_ids)
        v[label]={
            "original_source_rows":len(rows),
            "source_rows_with_complete_original_event_ID":complete,
            "distinct_source_view_event_ID_keys":len(unique),
            "source_view_rows_also_in_original_All_Foraging":in_all,
            "taxon_specific_views_NOT_independent_of_original_All_Foraging":True,
        }
    denom=ev["source_event_and_station_date_both_parseable"]
    return {
        "schema":"neon.figshare2026_after_frozen_station_key_STOP_structural_diagnostic.v1",
        "status":"ORIGINAL_SOURCE_STOP_KEYLESS_ROWS_RETAINED__SUPPORT_DIAGNOSTIC_ONLY",
        "original_figshare_article_id":28207769,
        "original_article_version":2,
        "original_source_MD5_and_five_file_hashes_verified":True,
        "original_provider_metadata_sha256":md,
        "original_total_station_night_rows_unchanged":len(rawstations),
        "source_station_night_diagnostic":dict(sorted(source.items())),
        "source_foraging_to_station_ID_seed_diagnostic":dict(sorted(ev.items())),
        "distinct_valid_complete_original_station_night_keys_with_events":len(distinct_keys),
        "distinct_grids_represented_in_key_matched_events":len(distinct_grid),
        "original_identified_PITs_among_matched_events":len(identifiers),
        "distinct_original_capture_PIT_GRID_year_source_keys":len(cp),
        "event_and_station_exact_date_match_fraction_when_both_dates_parsed":
            ev["original_event_station_date_exact_equal"]/denom if denom else None,
        "original_mouse_and_vole_taxon_view_support":v,
        "original_frozen_all_291_records_full_key_GO_requirement_failed":True,
        "no_offending_source_row_dropped_from_frozen_original_scientific_gate":True,
        "no_original_PIT_GRID_Site_Date_or_seed_quantity_values_exported":True,
        "no_rodent_seed_choice_search_predator_or_personality_effect_estimated":True,
        "no_operable_camera_absence_denominators_confirmed":True,
        "same_original_forest_as_2023_individual_overlap_unchecked":True,
        "not_NEON_or_Portal_independent_spatial_niche_replication":True,
        "one_NEON_Draft_SUBMISSION_HOLD":True,
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
    }

def main():
    try:
        value=diagnose();code=0
    except Exception as exc:
        value={"schema":"neon.figshare2026_after_frozen_station_key_STOP_structural_diagnostic.v1",
               "status":"SOURCE_DIAGNOSTIC_STOP","error_type":type(exc).__name__,
               "reason":str(exc)[:140],"no_biological_effect_or_source_GO":True}
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(value,sort_keys=True,indent=2)+"\n")
    print(json.dumps(value,sort_keys=True,indent=2))
    return code
if __name__=="__main__":
    raise SystemExit(main())
