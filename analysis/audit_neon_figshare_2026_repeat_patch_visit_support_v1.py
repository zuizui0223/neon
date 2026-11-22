#!/usr/bin/env python3
"""No-outcome feasibility of within-animal return visits to seed patches.

Pinned original Figshare 2026 camera, station-night and capture rows. The new
source-only test uses exact (Grid,Site,Session,Night,Visit.ID) composites,
original PIT, original Date and Time.start source formats, not seed finding
outcomes, choice, resource quantities, or learning/competition effects.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import json,re

from analysis.audit_neon_figshare_2026_foraging_station_effort_ID_source_v1 import (
    load_five,original_key,original_day,original_tag,token,numerical
)
from analysis.audit_neon_figshare_2026_station_event_capture_source_v2 import (
    corrected_source_only,
)
from analysis.reconcile_neon_figshare_2026_station_summaries_v1 import reconcile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_figshare_2026_repeat_patch_visit_source_v1.json"
PROTOCOL="docs/NEON_FIGSHARE_2026_PRIOR_PATCH_VISIT_SOURCE_GATE_20261122.md"
STATION=("Grid","Site","Session","Night")
VISIT=(*STATION,"Visit.ID")
MIN_UNAMBIGUOUS=100
MIN_PIT_REVISIT=15
MIN_PATCH_RETURN_PITS=8
MIN_PATCH_RETURN_GRIDS=3
MIN_PATCH_REPEATED_RESOURCE=50
MIN_ALTERNATIVES=20
MIN_CONSISTENT=.80
MIN_CLOCK_PARSE=.80

def require(x,label):
    if not x:raise ValueError("SOURCE_REPEAT_PATCH_STOP_"+label)

def clock_type(value):
    """Time formatting evidence, *not* biological time of day classification."""
    t=token(value)
    if t is None:return "MISSING"
    t=t.strip()
    if re.fullmatch(r"\d{4}-\d\d-\d\d[T ](?:[01]?\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?",t):
        return "FULL_ISO_DATETIME"
    if re.fullmatch(r"(?:0?[1-9]|1[0-2]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)? *(?:[AaPp][Mm])",t):
        return "TIME_12H_AMPM"
    if re.fullmatch(r"(?:[01]?\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?",t):
        return "TIME_24H"
    if re.fullmatch(r"\d?\.\d+",t):
        return "NUMERIC_EXCEL_FRACTION_UNVERIFIED"
    return "UNPARSED_OR_AMBIGUOUS"

def is_parseable_clock(kind):
    return kind in {"TIME_24H","TIME_12H_AMPM","FULL_ISO_DATETIME"}

def count_source_support(events,station_rows):
    """Can test pure fabricated data; original-data size gates checked in run."""
    stations={}
    station_alts=defaultdict(set)
    for row in station_rows:
        k=original_key(row,STATION)
        require(k is not None and k not in stations,
                "DUPLICATE_OR_MISSING_SOURCE_STATION")
        stations[k]=row
        station_alts[(k[0],k[2],k[3])].add(k[1])
    groups=defaultdict(list)
    for row in events:
        key=original_key(row,VISIT)
        require(key is not None,"MISSING_ORIGINAL_VISIT_ID_OR_PATCH_KEY")
        require(key[:4] in stations,"VISIT_SOURCE_PATCH_NOT_IN_STATIONS")
        groups[key].append(row)
    source=Counter();clock=Counter()
    clean=[]
    all_original_pits=set()
    for key,rows in groups.items():
        source["original_unique_station_night_visitID_composites"]+=1
        if len(rows)>1:
            source["source_visitIDs_with_multiple_interaction_rows"]+=1
            source["source_extra_seed_interaction_rows_beyond_unique_visitIDs"]+=len(rows)-1
        tags={original_tag(r.get("PIT")) for r in rows}
        days={original_day(r.get("Date")) for r in rows}
        times={token(r.get("Time.start")) for r in rows}
        good_tag=(len(tags)==1 and None not in tags)
        good_day=(len(days)==1 and None not in days)
        good_time=(len(times)==1 and None not in times)
        kind=clock_type(next(iter(times)) if good_time else None)
        clock[kind if good_time else "MISSING_OR_INCONSISTENT"]+=1
        if good_tag:
            tag=next(iter(tags))
            all_original_pits.add(tag)
            source["source_visit_composites_with_unambiguous_PIT"]+=1
            source["source_PIT_visit_composites_with_consistent_PIT_Date_Time.start"]+=int(
                good_day and good_time)
            source["source_PIT_visit_composites_with_parseable_start_clock"]+=int(
                good_day and good_time and is_parseable_clock(kind))
        if not(good_tag and good_day and good_time and is_parseable_clock(kind)):
            source["source_visit_composites_NOT_eligible_for_temporal_return_order"]+=1
            if not good_tag:source["source_visit_composites_PIT_missing_or_conflict"]+=1
            if not good_day:source["source_visit_composites_Date_missing_or_conflict"]+=1
            if not good_time:source["source_visit_composites_start_time_missing_or_conflict"]+=1
            if good_time and not is_parseable_clock(kind):
                source["source_visit_composites_clock_format_not_understood"]+=1
            continue
        tag=next(iter(tags));day=next(iter(days))
        site_date=original_day(stations[key[:4]].get("Date"))
        strict_equal=(site_date is not None and site_date==day)
        any_seed_numeric=any(
            numerical(r.get("WP.available.OBS")) or numerical(r.get("RO.available.OBS"))
            for r in rows
        )
        source["source_clean_PIT_date_clock_visit_composites"]+=1
        source["source_clean_visit_exact_station_Date_concordant"]+=int(strict_equal)
        source["source_clean_visit_with_numeric_observed_seed_field"]+=int(any_seed_numeric)
        clean.append({
            "key":key,"pit":tag,"day":day,"grid":key[0],"site":key[1],
            "station_night":key[:4],
            "resource_recorded":any_seed_numeric,"source_date_concordant":strict_equal
        })
    by_pit=defaultdict(list)
    by_pit_patch=defaultdict(list)
    for row in clean:
        by_pit[row["pit"]].append(row)
        by_pit_patch[(row["pit"],row["grid"],row["site"])].append(row)
    repeated_pits={
        p for p,records in by_pit.items()
        if len(records)>=2 and len({v["station_night"] for v in records})>=2
    }
    patch_pits=set();repeat_grids=set()
    return_records=0;return_with_resources=0;return_date_concordant=0
    return_distinct_days=set()
    # Select later visits only, not multiple seed-interaction rows same visit.
    for (p,grid,site),records in by_pit_patch.items():
        days=sorted({v["day"] for v in records})
        if len(days)<2:continue
        patch_pits.add(p);repeat_grids.add(grid)
        first=days[0]
        for v in records:
            if v["day"]<=first:continue
            return_records+=1
            return_distinct_days.add(v["day"])
            return_with_resources+=int(v["resource_recorded"])
            return_date_concordant+=int(v["source_date_concordant"])
    alts=sum(len(v)>=2 for v in station_alts.values())
    source["source_unique_original_PITs_with_valid_visit_composites"]=len(by_pit)
    source["source_literal_PITs_across_two_or_more_distinct_station_nights"]=len(repeated_pits)
    source["source_distinct_PITs_revisiting_exact_same_GRID_Site_on_later_original_day"]=len(patch_pits)
    source["source_distinct_GRID_with_cross_day_same_PIT_patch_revisits"]=len(repeat_grids)
    source["source_return_visit_composites_later_than_first_original_day"]=return_records
    source["source_return_visit_composites_with_numeric_observed_seed_availability"]=return_with_resources
    source["source_return_visit_composites_with_original_station_event_date_equal"]=return_date_concordant
    source["source_unique_calendar_dates_with_source_return_visits"]=len(return_distinct_days)
    source["source_grid_session_night_occasions_with_two_or_more_station_sites"]=alts
    source["all_original_station_grids_with_valid_station_night_records"]=len({k[0] for k in stations})
    source["all_original_station_nights_with_complete_key"]=len(stations)
    original_visits=sum(v for v in (len(rows) for rows in groups.values()))
    require(original_visits==len(events),"ORIGINAL_SOURCE_VISIT_INTERACTION_ROW_ACCOUNTING")
    n_tag=source["source_visit_composites_with_unambiguous_PIT"]
    n_meta=source["source_PIT_visit_composites_with_consistent_PIT_Date_Time.start"]
    n_clock=source["source_PIT_visit_composites_with_parseable_start_clock"]
    checks={
        "at_least_100_single_PIT_valid_Date_parseable_Time_start_visit_composites":
            len(clean)>=MIN_UNAMBIGUOUS,
        "at_least_15_original_PITs_with_two_separate_station_night_visit_composites":
            len(repeated_pits)>=MIN_PIT_REVISIT,
        "at_least_8_PITs_with_exact_labeled_patch_revisits_across_dates":
            len(patch_pits)>=MIN_PATCH_RETURN_PITS,
        "repeated_labeled_patch_PITs_in_at_least_3_independent_field_grids":
            len(repeat_grids)>=MIN_PATCH_RETURN_GRIDS,
        "at_least_50_later_source_return_visits_with_original_numeric_seed_metadata":
            return_with_resources>=MIN_PATCH_REPEATED_RESOURCE,
        "at_least_20_grid_session_night_source_occasions_with_alternative_stations":
            alts>=MIN_ALTERNATIVES,
        "source_PIT_visit_date_time_fields_consistent_in_at_least_80_percent":
            n_tag>0 and n_meta/n_tag>=MIN_CONSISTENT,
        "source_PIT_date_time_consistent_visits_clock_parseable_in_at_least_80_percent":
            n_meta>0 and n_clock/n_meta>=MIN_CLOCK_PARSE
    }
    return {
        "source_structural_counts":dict(sorted(source.items())),
        "original_Time_start_format_source_category_counts":
            dict(sorted(clock.items())),
        "source_PIT_visit_date_time_consistency_ratio":n_meta/n_tag if n_tag else None,
        "source_PIT_visit_parseable_clock_ratio":n_clock/n_meta if n_meta else None,
        "source_repeat_patch_eligibility_checks":checks,
        "source_repeat_patch_all_checks_GO":all(checks.values()),
        "source_eligible_PITs_within_grids_not_released":True,
        "original_Time.start_full_values_NOT_exported":True
    }

def run():
    tables,hashes,meta=load_five()
    verified=corrected_source_only(tables,hashes,meta)
    require(verified["status"]==
        "CORRECTED_SOURCE_JOIN_GO_NOT_DETECTOR_OPERATION_OR_BIOLOGICAL_EFFECT",
        "PRIOR_CORRECTED_288_3_SOURCE_V2_GO_DRIFT")
    stations=tables["All Station Nights.csv"][:-3]
    raw=count_source_support(tables["All Foraging Clean.csv"],stations)
    return {
        "schema":"neon.figshare_2026_repeat_patch_within_PIT_source_support.v1",
        "status":("SOURCE_REPEAT_PATCH_SUPPORT_GO_NO_BEHAVIORAL_EFFECT"
                  if raw["source_repeat_patch_all_checks_GO"] else
                  "SOURCE_REPEAT_PATCH_SUPPORT_STOP_NO_LEARNING_ESTIMATE"),
        "source_original_article_id":28207769,
        "source_original_article_version":2,
        "original_five_file_publisher_MD5_sha_bytes_reverified":True,
        "prior_source_v2_9of9_numerical_source_GO_reverified":True,
        "prior_288_original_station_nights_plus_3_footers_verified":True,
        "original_source_metadata_sha256":meta,
        **raw,
        "not_known_independent_camera_up_time_or_natural_food_biomass":True,
        "repeated_SITE_ID_literal_keys_not_validated_as_unchanging_physical_patches":True,
        "revisit_occurrence_not_experimental_learning_or_memory":True,
        "source_opportunity_not_niche_or_PIT_individual_selection_probability":True,
        "original_2026_article_resource_personality_seed_finding_findings_prior_art":True,
        "no_original_Seed_Found_Time_searching_or_Seed_disposition_outcomes_opened":True,
        "original_NEON_Portal_Finland_density_results_unchanged":True,
        "single_NEON_ecological_paper_Draft_SUBMISSION_HOLD":True,
        "source_protocol":PROTOCOL,
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    try:
        result=run()
        code=0  # scientific source STOP should be explicit in archived JSON.
    except Exception as exc:
        result={
            "schema":"neon.figshare_2026_repeat_patch_within_PIT_source_support.v1",
            "status":"SOURCE_STOP_ORIGINAL_FORMAT_OR_REPRODUCIBILITY",
            "error_type":type(exc).__name__,
            "reason":str(exc)[:160],
            "no_original_behaviour_or_resource_effect_opened":True
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,sort_keys=True,indent=2))
    return code

if __name__=="__main__":
    raise SystemExit(main())
