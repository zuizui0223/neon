#!/usr/bin/env python3
"""Original prairie-vole logger and trapping TEMPORAL OPPORTUNITY source only.

All files original provider MD5 verified. Reads collar assignment dates and
calendar dates from sensor/trap metadata, NEVER dyad pairs or contact outcomes.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import date,timedelta,datetime,timezone
from pathlib import Path
from io import StringIO
from math import comb
import csv,json

from analysis.neon_prairie_vole_verified_raw_schema_v1 import get_original

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_prairie_vole_original_contact_effort_gate_20261115.json"
MIN_ACTIVE_IN_BOTH_DAYS=4
MIN_ADJACENT_DAY_WINDOWS=3
STAGE="PINNED_SENSORS_CSV"

def source_rows(name):
    b=get_original(name)
    reader=csv.DictReader(StringIO(b.decode("utf-8-sig")))
    return list(reader)

def parse_iso(v):
    try:return date.fromisoformat(v.strip())
    except(ValueError,AttributeError):
        raise ValueError("SOURCE_COLLAR_INTERVAL_NOT_ISO") from None

def parse_us(v):
    try:return datetime.strptime(v.strip(),"%m/%d/%y").date()
    except(ValueError,AttributeError):
        raise ValueError("SOURCE_TRAP_DATE_NOT_MM_DD_YY") from None

def gate():
    global STAGE
    collar=source_rows("collar_ids.csv")
    STAGE="COLLAR_ASSIGNMENT_INTERVALS"
    if len(collar)!=38:raise ValueError("SOURCE_38_COLLAR_ASSIGNMENTS_CHANGED")
    episodes=[]
    invalid_earlier_removal=0
    same_day_removal=0
    unique_tags=set();unique_collars=set()
    for x in collar:
        tag=(x.get("tag") or "").strip()
        device=(x.get("collar") or "").strip()
        if not tag or not device:raise ValueError("MISSING_COLLAR_TAG_CROSSWALK")
        start=parse_iso(x.get("date_on"))
        end=parse_iso(x.get("date_off"))
        if start>end:
            invalid_earlier_removal+=1
            continue
        if start==end:
            same_day_removal+=1
        episodes.append((tag,device,start,end))
        unique_tags.add(tag);unique_collars.add(device)
    if invalid_earlier_removal:
        # This exact precommitted integrity constraint FAILED before
        # opening animal dyad contacts. Report the full immutable original
        # 38-row source QC failure, do not drop invalid source subjects
        # and continue to a favorable biological network result.
        return {
            "schema":"neon.prairie_vole_contact_calendar_opportunity.v1",
            "status":"STOP_ORIGINAL_COLLAR_INTERVALS_SOURCE_INTEGRITY",
            "source_provider_original_MD5_verified":True,
            "original_collar_source_rows":len(collar),
            "invalid_original_reverse_date_intervals":invalid_earlier_removal,
            "original_same_day_on_off_intervals":same_day_removal,
            "remaining_source_row_counts_not_promoted_to_paired_exposure":True,
            "zero_proximity_dyad_contact_or_trapping_outcomes_scored":True,
            "no_collar_tag_identity_or_original_dates_exported":True,
            "precommitted_source_original_interval_gate_not_relaxed":True,
            "no_original_NEON_Portal_Finland_Structural_effect_changed":True,
        }
    collisions=0
    for i,(tag,c,st,en) in enumerate(episodes):
        for tag2,c2,st2,en2 in episodes[i+1:]:
            if max(st,st2)>=min(en,en2):continue
            if c==c2 and tag!=tag2:collisions+=1
            if tag==tag2 and c!=c2:collisions+=1

    STAGE="TRAP_SAMPLED_CALENDAR_DAYS"
    traps=source_rows("full_voles_trap.csv")
    if len(traps)!=4454:raise ValueError("SOURCE_4454_TRAP_ROWS_CHANGED")
    trap_days=Counter(parse_us(x.get("date")) for x in traps)

    STAGE="PROXIMITY_SENSOR_CALENDAR_DAYS_ONLY"
    events=source_rows("prox_full_noduplicates.csv")
    if len(events)!=50741:raise ValueError("SOURCE_50741_SENSOR_ROWS_CHANGED")
    sensed_days=Counter(parse_iso(x.get("date")) for x in events)
    STAGE="ORIGINAL_CALENDAR_RISKSET"
    from_day=min(x[2] for x in episodes)
    to_day=max(x[3] for x in episodes)
    active_by_day={}
    invalid_concurrent_collar_days=0
    d=from_day
    while d<=to_day:
        active={(tag,device) for tag,device,st,en in episodes if st<=d<en}
        if len(active)!=len({tag for tag,device in active}):
            invalid_concurrent_collar_days+=1
        active_by_day[d]=active
        d+=timedelta(days=1)
    n=0;present=0;qualifying=0;riskset_dyads=0
    source_months=defaultdict(Counter)
    for d in sorted(active_by_day):
        active=active_by_day[d]
        if len(active)>=2:
            n+=1
            source_months[d.strftime("%Y-%m")]["calendar_active_2plus_collars"]+=1
        if sensed_days[d]:
            source_months[d.strftime("%Y-%m")]["sensor_event_rows"]+=sensed_days[d]
        if trap_days[d]:
            source_months[d.strftime("%Y-%m")]["trapping_capture_rows"]+=trap_days[d]
        if d+timedelta(days=1) not in active_by_day:continue
        shared=active&active_by_day[d+timedelta(days=1)]
        if len(shared)>=MIN_ACTIVE_IN_BOTH_DAYS:
            present+=1
            source_months[d.strftime("%Y-%m")]["candidate_2day_4collar_spans"]+=1
            riskset_dyads+=comb(len(shared),2)
            if sensed_days[d] and sensed_days[d+timedelta(days=1)]:
                qualifying+=1
                source_months[d.strftime("%Y-%m")]["candidate_2day_4collar_source_days_with_events"]+=1
    go=(qualifying>=MIN_ADJACENT_DAY_WINDOWS
        and invalid_concurrent_collar_days==0
        and collisions==0)
    return {
        "schema":"neon.prairie_vole_contact_calendar_opportunity.v1",
        "status":("PUBLISHED_PRAIRIE_VOLE_SENSOR_TIME_SUPPORT_SOURCE_GO_NOT_DYAD_EFFECT"
                  if go else "STOP_PUBLISHED_PRAIRIE_VOLE_SENSOR_SOURCE_CALENDAR_SUPPORT"),
        "verified_original_sources":{
            "source_project":"Figshare 228462",
            "file_count":3,
            "all_exact_provider_MD5_and_bytes_checked":True,
            "original_collar_assignment_rows":len(episodes),
            "distinct_source_collar_IDs":len(unique_collars),
            "distinct_source_animal_tag_IDs":len(unique_tags),
            "original_raw_sensor_event_rows":len(events),
            "original_raw_trap_capture_rows":len(traps),
        },
        "calendar_opportunity":{
            "collar_device_concurrent_assignment_conflicts":collisions,
            "days_with_inconsistent_same_animal_multiple_collars":invalid_concurrent_collar_days,
            "days_with_at_least_two_assigned_collar_tags":n,
            "original_adjacent_day_both_active_at_least_four_collar_tags":present,
            "source_adjacent_day_four_active_tags_and_sensor_events_each_day":qualifying,
            "potential_two_day_exposure_dyad_riskset_opportunities":riskset_dyads,
            "source_month_summary_no_individuals":{
                month:dict(sorted(c.items())) for month,c in sorted(source_months.items())
            },
        },
        "predeclared_single_population_source_gate":{
            "min_consecutive_day_windows":MIN_ADJACENT_DAY_WINDOWS,
            "min_same_animal_and_collar_active_in_both_days":MIN_ACTIVE_IN_BOTH_DAYS,
            "collar_off_day_excluded":True,
            "sensor_events_per_day_not_per_collar_function_test":True,
            "source_seasonal_distribution_cannot_verify_longitudinal_occupancy":True,
            "events_not_contact_free_day_cannot_be_animal_absence":True,
        },
        "ecological_limits":{
            "this_stage_does_not_read_sensed_dyad_IDs_or_contact_value":True,
            "same_period_animal_pair_repeated_contacts_not_estimated":True,
            "collar_active_dates_not_equal_device_confirmed_working":True,
            "original_trap_sampling_effort_not_reconstructed":True,
            "published_2025_network_MRQAP_R2_0_02_is_prior_art":True,
            "one_enclosed_original_population_only":True,
            "old_NEON_Portal_Finland_Structural_effects_unchanged":True
        },
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    global STAGE
    try:res=gate();code=0
    except Exception as exc:
        res={"schema":"neon.prairie_vole_contact_calendar_opportunity.v1",
             "status":"STOP_ORIGINAL_SOURCE_COLLAR_OR_SENSOR_DATE_PARSE",
             "stage":STAGE,"error_class":type(exc).__name__,
             "source_failure_code":str(exc),
             "no_proximity_partner_effect_opened":True}
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(res,indent=2,sort_keys=True))
    return code
if __name__=="__main__":raise SystemExit(main())
