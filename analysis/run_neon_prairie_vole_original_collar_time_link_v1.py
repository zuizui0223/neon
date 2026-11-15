#!/usr/bin/env python3
"""Time-resolve recycled ProxLogs collar numbers onto original vole tags.

Source QA ONLY: no contact-effect statistic, network edge estimates,
per-animal identity export or assumption of no contact when collars silent.
Uses original fixed 2024 Figshare article/file IDs, sizes, published MD5s.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib,json,re

from analysis.run_neon_prairie_vole_figshare_identity_preflight_v1 import (
    FROZEN_ORIGINAL_MD5,FIELDS,ORIGINAL_ROWS,PIN,BASE,
    fetch_json,check_filename_file,parse,time_date,ident,source_bytes
)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_prairie_vole_original_collar_time_join_20261115.json"
SOURCE_MIN_RELINK_RATE=0.8
SOURCE_MIN_COLLARED_TAGS_WITH_TRAP=12
SOURCE_MIN_SHARED_CALENDAR_DAYS=5
STAGE="ORIGINAL_FROZEN_MD5_FILES"

def must(condition, label):
    if not condition:raise ValueError("FROZEN_COLLAR_MAPPING_SOURCE_STOP_"+label)

def mask_format(value):
    s=str(value or "").strip()
    if not s:return "EMPTY"
    s=s[:60]
    return "".join("9" if ch.isdigit() else "A" if ch.isalpha()
                   else ch for ch in s)

def collar_source_episodes(rows):
    episodes=defaultdict(list)
    invalid=Counter()
    for row in rows:
        tag=ident(row["tag"]);device=ident(row["collar"])
        start=time_date(row["date_on"]);end=time_date(row["date_off"])
        if not tag or not device or start is None or end is None or end<start:
            invalid["date_or_id_invalid"]+=1
            continue
        episodes[device].append((start,end,tag))
    conflicts=0
    for device,items in episodes.items():
        items.sort()
        for k,a in enumerate(items):
            for b in items[k+1:]:
                if a[1]>=b[0] and b[1]>=a[0] and a[2]!=b[2]:
                    conflicts+=1
    return episodes,dict(invalid),conflicts

def unique_device_assignment(episodes,device,day):
    if day is None:return None,"bad_event_date"
    xs=episodes.get(ident(device),[])
    tags={tag for start,end,tag in xs if start<=day<=end}
    if not xs:return None,"device_unrecorded"
    if not tags:return None,"device_outside_date"
    if len(tags)>1:return None,"date_multiple_different_tags"
    return next(iter(tags)),"unique"

def run():
    global STAGE
    records={name:parse(name,source_bytes(name)) for name in FROZEN_ORIGINAL_MD5}
    collars=records["collar_ids.csv"]
    logger=records["prox_full_noduplicates.csv"]
    trap=records["full_voles_trap.csv"]
    global_tags=records["global_ids.csv"]
    trap_net=records["rfid_trap_network_data_method.csv"]
    STAGE="VERIFY_ORIGINAL_COLLAR_EPISODES"
    episodes,invalid,overlaps=collar_source_episodes(collars)
    must(not invalid and sum(map(len,episodes.values()))==38,
         "ORIGINAL_COLLAR_EPISODE_ID_AND_DATE")
    STAGE="EVENTWISE_COLLAR_TO_ANIMAL_DATE_JOIN"
    counters=Counter()
    parsed_event_days=set()
    parsed_trap_days=set()
    source_tags={ident(r["tag"]) for r in trap if ident(r["tag"])}
    global_dict={}
    for r in global_tags:
        tag=ident(r["tag"])
        sex=ident(r["sex"]).upper()
        if tag in global_dict and global_dict[tag]!=sex:
            raise ValueError("ORIGINAL_TAG_CONFLICTING_SEX")
        global_dict[tag]=sex
    collar_tags={tag for vals in episodes.values() for _,_,tag in vals}
    tagsex=Counter(global_dict.get(tag,"UNKNOWN") for tag in collar_tags)
    collar_tags_in_trapping=collar_tags&source_tags
    enclosures=defaultdict(set)
    for row in trap:
        tag=ident(row["tag"]);enclosure=ident(row["enclosure"])
        if tag in collar_tags and enclosure:
            enclosures[tag].add(enclosure)
        day=time_date(row["date"])
        if day is not None:parsed_trap_days.add(day)
    for r in logger:
        counters["original_logger_source_events"]+=1
        day=time_date(r["date"])
        if day is not None:parsed_event_days.add(day)
        a,code_a=unique_device_assignment(episodes,r["c1"],day)
        b,code_b=unique_device_assignment(episodes,r["c2"],day)
        counters["source_event_endpoint_1_"+code_a]+=1
        counters["source_event_endpoint_2_"+code_b]+=1
        if code_a=="unique" and code_b=="unique":
            counters["events_with_both_original_devices_unambiguous_animal_tags"]+=1
            counters["same_tag_assigned_to_both_device_endpoints"]+=int(a==b)
            counters["events_both_animals_have_original_trap_tags"]+=int(
                a in source_tags and b in source_tags)
            counters["events_both_animals_have_sex_metadata"]+=int(
                global_dict.get(a,"").upper() in ("M","F") and
                global_dict.get(b,"").upper() in ("M","F"))
            if day in parsed_trap_days:
                counters["events_on_days_with_any_live_trapping_record"]+=1
    STAGE="ORIGINAL_TIMESTAMP_FORMAT_DIAGNOSTIC"
    formats={
      "logger_datetime":dict(Counter(mask_format(r["datetime"]) for r in logger).most_common(12)),
      "trap_network_TimeStart":dict(Counter(mask_format(r["TimeStart"]) for r in trap_net).most_common(12)),
      "trap_network_TimeStop":dict(Counter(mask_format(r["TimeStop"]) for r in trap_net).most_common(12)),
    }
    source_days_overlap=len(parsed_event_days&parsed_trap_days)
    unique_rate=counters["events_with_both_original_devices_unambiguous_animal_tags"]/len(logger)
    go=(unique_rate>=SOURCE_MIN_RELINK_RATE and
        len(collar_tags_in_trapping)>=SOURCE_MIN_COLLARED_TAGS_WITH_TRAP and
        source_days_overlap>=SOURCE_MIN_SHARED_CALENDAR_DAYS and
        counters["events_both_animals_have_sex_metadata"]>0)
    return {
        "schema":"neon.prairie_vole_original_collar_time_recycled_ID_linkage.v1",
        "status":"PRAIRIE_VOLE_EVENTWISE_ORIGINAL_COLLAR_TAG_TIME_SOURCE_GO_NOT_CONTACT_EFFECT"
                 if go else "STOP_FROZEN_PRAIRIE_VOLE_ID_TIME_SOURCE_BREADTH",
        "source":{
            "published_paper_doi":"10.1093/jmammal/gyaf032",
            "figshare_public_project":228462,
            "public_original_six_files_MD5_and_size_verified":True,
            "source_38_recorded_collar_episodes":sum(map(len,episodes.values())),
            "original_distinct_collar_device_IDs":len(episodes),
            "distinct_original_animal_tags_with_a_deployed_collar":len(collar_tags),
            "original_collar_episodes_with_overlapping_different_animals_same_device":overlaps,
            "published_global_sex_metadata_for_collared_tags":dict(sorted(tagsex.items())),
            "number_collared_tags_also_ever_in_original_live_trapping_source":len(collar_tags_in_trapping),
            "collared_tags_with_multiple_recorded_enclosures":sum(len(z)>1 for z in enclosures.values()),
            "logger_source_rows":len(logger),
            "calendar_days_with_any_valid_logger_date":len(parsed_event_days),
            "calendar_days_with_any_valid_trapping_date":len(parsed_trap_days),
            "calendar_days_with_at_least_one_logger_and_one_trap_record":source_days_overlap,
            "recycled_collar_events_one_to_one_ID_source_counts":dict(sorted(counters.items())),
            "fraction_original_logger_rows_both_endpoints_time_resolved":unique_rate,
            "original_unparsed_timestamp_patterns_anonymous":formats,
        },
        "source_rule_locked":{
            "minimum_fraction_original_logger_events_unique_tag_pair":SOURCE_MIN_RELINK_RATE,
            "minimum_original_collared_tag_IDs_also_in_trap_source":SOURCE_MIN_COLLARED_TAGS_WITH_TRAP,
            "minimum_calendar_days_with_recorded_both_observation_types":SOURCE_MIN_SHARED_CALENDAR_DAYS,
            "source_thresholds_do_NOT_authorize_contact_effect":True,
        },
        "limits":{
            "overlap_of_ANY_event_days_does_not_prove_simultaneous_dyad_recording":True,
            "same_day_trap_and_logger_does_not_prove_a_logger_was_recording_all_day":True,
            "one_broken_or_memory_full_logger_is_not_an_absence":True,
            "individual_closest_partner_may_be_biological_or_device_bias":True,
            "no_collected_animal_location_values_or_raw_identifiers_exported":True,
            "no_contact_dyad_positive_or_null_effect_estimated":True,
            "published_2025_matrix_QAP_R2_prior_art_unchanged":True,
            "NEON_Portal_Finland_Structural_claims_unmodified":True,
            "one_integrated_mammal_manuscript_submission_HOLD":True,
        },
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    global STAGE
    try:
        result=run();exit_code=0
    except Exception as e:
        result={
          "schema":"neon.prairie_vole_original_collar_time_recycled_ID_linkage.v1",
          "status":"STOP_ORIGINAL_PRAIRIE_VOLE_COLLAR_DATE_SOURCE_IMPLEMENTATION",
          "phase":STAGE,
          "error_class":type(e).__name__,
          "animal_source_identifiers_and_contact_events_not_exported":True,
          "no_old_mammal_biological_response_reopened":True,
        }
        exit_code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    return exit_code

if __name__=="__main__":
    raise SystemExit(main())
