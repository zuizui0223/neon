#!/usr/bin/env python3
"""Descriptive seed disappearance, including nights with no video event record.

RETROSPECTIVE original source audit, not a new animal causal effect. Original
291-row source GO is STILL FAILED because 3 nonblank keyless records exist.
Only 288 source-keyed station-night observations constitute this separate
source-defined descriptive population. No seed loss claimed animal caused.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from datetime import datetime,timezone
from math import isfinite
from pathlib import Path
import json

from analysis.audit_neon_figshare_2026_foraging_station_effort_ID_source_v1 import (
    load_five,original_key,token
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_figshare_2026_seed_loss_no_video_v1.json"
PROTOCOL="docs/NEON_FIGSHARE_2026_SEED_LOSS_WITHOUT_VIDEO_FROZEN_DESCRIPTIVE_20261121.md"
KEYS=("Grid","Site","Session","Night")
SEED_FIELDS=("WP.seeds.set","WP.seeds.left","RO.seeds.set","RO.seeds.left")
MIN_COMPLETE_EACH=100

def require(ok,label):
    if not ok:
        raise ValueError("NEON_FIGSHARE_2026_SEED_LOSS_STOP_"+label)

def parse_seed_count(source):
    """Require finite, nonnegative INTEGER number of offered/remaining seeds."""
    x=str(source or "").strip()
    if x.upper() in ("","NA","NAN","NULL","NONE","N/A"):
        return None
    try:v=float(x)
    except ValueError:
        return None
    require(isfinite(v) and v>=0,"NEGATIVE_OR_NONFINITE_SEED_COUNT")
    require(v.is_integer(),"NONINTEGER_SEED_COUNT_OR_UNIT_MISMATCH")
    return int(v)

def descriptive(rows,events):
    """Produce outcomes ONLY if both source strata pass pre-set QA."""
    require(len(rows)==291 and len(events)==3243,
            "ORIGINAL_291_3243_SOURCE_DRIFT")
    eventkeys=set()
    for e in events:
        k=original_key(e,KEYS)
        require(k is not None,"ORIGINAL_FORAGING_EVENT_KEY_MISSING")
        eventkeys.add(k)
    require(len(eventkeys)==136,"FROZEN_136_ORIGINAL_VIDEO_KEYS_DRIFT")
    matched={}
    footerlike=[]
    for i,s in enumerate(rows):
        k=original_key(s,KEYS)
        if not k:
            fields=sorted(f for f,v in s.items()
                          if f not in KEYS and isinstance(v,str) and v.strip())
            footerlike.append({"source_one_based_row_number":i+1,
                               "nonkey_original_nonblank_field_names":fields})
            continue
        require(k not in matched,"ORIGINAL_DUPLICATE_STATION_NIGHT_KEY")
        matched[k]=s
    require(len(matched)==288 and len(footerlike)==3
            and sorted(x["source_one_based_row_number"] for x in footerlike)==[
                289,290,291],"FROZEN_288_SOURCE_3_KEYLESS_RECORD_DRIFT")
    require(all(k in matched for k in eventkeys),
            "ORIGINAL_VIDEO_EVENT_WITHOUT_STATION_KEY")
    source_counts=Counter()
    valid=defaultdict(list)
    invalid=Counter()
    for key,row in matched.items():
        group=("recorded_camera_event" if key in eventkeys
               else "no_recorded_camera_event")
        source_counts["all_288_keyed_station_nights"]+=1
        source_counts[group+"_total"]=source_counts[group+"_total"]+1
        if not (token(row.get("Night.set")) and
                token(row.get("Morning.check"))):
            invalid[group+"_missing_setup_or_morning_check"]+=1
            continue
        counts=[parse_seed_count(row.get(f)) for f in SEED_FIELDS]
        if any(z is None for z in counts):
            invalid[group+"_missing_or_nonnumeric_seed_count"]+=1
            continue
        wp_set,wp_left,ro_set,ro_left=counts
        if wp_left>wp_set or ro_left>ro_set:
            invalid[group+"_original_remaining_greater_than_offered"]+=1
            continue
        valid[group].append((wp_set,wp_left,ro_set,ro_left))
    # Any physically inconsistent count invalidates ecological interpretation
    # before computing a descriptive seed-disappearance aggregate.
    report={
        "schema":"neon.figshare_2026_seed_disappearance_camera_event_gap.v1",
        "original_figshare_article_id":28207769,
        "original_version":2,
        "original_total_source_station_nights_including_keyless":291,
        "original_unique_valid_station_night_keys":len(matched),
        "three_nonblank_keyless_source_rows_NOT_RECODED_AS_STATIONS":footerlike,
        "original_source_frozen_all_291_station_row_GO_remains_FAILED":True,
        "source_station_night_video_event_class_counts":dict(sorted(source_counts.items())),
        "original_station_source_quality_exclusions":dict(sorted(invalid.items())),
        "numeric_complete_station_nights_by_video_event_class":
            {g:len(v) for g,v in sorted(valid.items())},
        "no_original_animal_ID_or_species_or_site_or_date_exported":True,
        "no_animals_inferred_from_missing_seeds_or_no_video":True,
        "no_natural_food_biomass_or_learning_estimated":True,
        "post_result_descriptive_only_NOT_new_confirmatory_ecology":True,
        "previous_2026_paper_seed_missing_analysis_PRIOR_ART":True,
        "one_NEON_Draft_SUBMISSION_HOLD":True,
        "protocol":PROTOCOL
    }
    gate=(
        invalid["recorded_camera_event_original_remaining_greater_than_offered"]==0
        and invalid["no_recorded_camera_event_original_remaining_greater_than_offered"]==0
        and len(valid["recorded_camera_event"])>=MIN_COMPLETE_EACH
        and len(valid["no_recorded_camera_event"])>=MIN_COMPLETE_EACH
    )
    if not gate:
        report["status"]="SOURCE_STOP_SEED_COUNT_QUALITY_OR_STRATUM_SUPPORT"
        report["seed_disappearance_effect_or_descriptive_numerators"]=None
        return report
    # Exploratory report from all pre-fixed source-eligible original station
    # nights, not individual seed/video events (avoid pseudoreplication).
    results={}
    for group in ("recorded_camera_event","no_recorded_camera_event"):
        arr=valid[group]
        disappearing_wp=sum(x[0]-x[1] for x in arr)
        disappearing_ro=sum(x[2]-x[3] for x in arr)
        results[group]={
            "original_complete_source_station_nights":len(arr),
            "source_nights_with_any_seed_missing":sum(
                (a>b or c>d) for a,b,c,d in arr
            ),
            "original_WP_seeds_offered":sum(z[0] for z in arr),
            "original_WP_seeds_missing":disappearing_wp,
            "original_RO_seeds_offered":sum(z[2] for z in arr),
            "original_RO_seeds_missing":disappearing_ro,
            "original_both_types_seeds_missing":disappearing_wp+disappearing_ro,
            "possible_animal_cause_versus_nonanimal_loss_UNIDENTIFIED":True
        }
        results[group]["fraction_source_nights_any_seed_missing"]=(
            results[group]["source_nights_with_any_seed_missing"]/len(arr))
    tot=sum(x["original_both_types_seeds_missing"] for x in results.values())
    results["fraction_of_all_source_missing_seed_counts_on_nights_without_recorded_video_event"]=(
        results["no_recorded_camera_event"]["original_both_types_seeds_missing"]/tot
        if tot else None
    )
    report["status"]="RETROSPECTIVE_STATION_SOURCE_SEED_DISAPPEARANCE_DESCRIPTIVE_ONLY"
    report["seed_disappearance_effect_or_descriptive_numerators"]=results
    return report

def run():
    tab,integrity,md=load_five()
    obj=descriptive(tab["All Station Nights.csv"],
                    tab["All Foraging Clean.csv"])
    obj["original_published_source_exact_MD5_byte_verified"]=True
    obj["original_five_source_SHA_receipt"]=integrity
    obj["original_provider_metadata_SHA256"]=md
    obj["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    return obj

def main():
    try:record=run();code=0
    except Exception as err:
        record={
            "schema":"neon.figshare_2026_seed_disappearance_camera_event_gap.v1",
            "status":"SOURCE_STOP_ORIGINAL_CSV_OR_INVALID_SEED_COUNTS",
            "error_type":type(err).__name__,
            "reason":str(err)[:160],
            "no_seed_loss_effect_or_animal_causation_claimed":True,
            "original_strict_station_source_STOP_unchanged":True
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n")
    print(json.dumps(record,sort_keys=True,indent=2))
    return code

if __name__=="__main__":
    raise SystemExit(main())
