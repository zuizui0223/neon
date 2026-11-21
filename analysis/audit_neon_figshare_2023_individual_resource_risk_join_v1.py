#!/usr/bin/env python3
"""Original Figshare 2023 field vole foraging resource/risk/PIT SOURCE ONLY.

All raw CSV bytes/provider md5 are checked again. Read structural identifiers
and availability fields only; no seed-selection, consumption, treatment response,
personality coefficients, social encounter or learning effect is estimated.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timezone
from hashlib import md5,sha256
from io import StringIO
from math import isfinite
from pathlib import Path
import csv,json

from analysis.audit_neon_figshare_2023_original_csv_schema_v1 import (
    FILES, inventory_source, bounded_original, original_header_and_row_count,
    require,
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_figshare_2023_individual_resource_risk_source_v1.json"
PROTOCOL="docs/NEON_FIGSHARE_2023_PIT_RESOURCE_RISK_SOURCE_JOIN_GATE_20261121.md"
EXPECTED_ROWS={
    "2018 Vole Seed Data.csv":603,
    "Vole BLUPS.csv":1069,
    "Vole Personality Data.csv":3712,
}
MISSING={"","NA","NAN","NULL","N/A","UNK","UNKNOWN"}
MIN_VALID_COMBINED_PIT=8
MIN_VALID_JOINED_EVENTS=30
MIN_GRIDS=3
MIN_PATCHES=10
MIN_TREAT_CATEGORIES=2
MIN_SESSIONS=2
MIN_BOTH_RESOURCE=30

def pid(value):
    text=(value or "").strip()
    return text if text.upper() not in MISSING else None

def original_number_available(text):
    s=(text or "").strip()
    if s.upper() in MISSING:
        return False
    try:val=float(s)
    except (ValueError,TypeError):
        return False
    return isfinite(val) and val>=0

def validate_original_sources():
    links,metadata_sha=inventory_source()
    tables={}
    integrity={}
    for fid,(name,size,original_md5) in FILES.items():
        raw=bounded_original(links[fid],size)
        require(md5(raw).hexdigest()==original_md5,"ORIGINAL_MD5_CHANGED")
        checked=original_header_and_row_count(raw,name)
        require(checked["original_row_count"]==EXPECTED_ROWS[name],
                "ORIGINAL_PUBLISHED_ROW_COUNT_CHANGED")
        try:s=raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise ValueError("NEON_FIGSHARE_2023_ORIGINAL_STOP_SOURCE_UTF8") from None
        csv_rows=list(csv.DictReader(StringIO(s,newline="")))
        require(len(csv_rows)==EXPECTED_ROWS[name],"SOURCE_ROW_COUNT_DRIFT")
        tables[name]=csv_rows
        integrity[name]={
            "original_file_id":fid,
            "original_MD5":original_md5,
            "original_SHA256":sha256(raw).hexdigest(),
            "published_row_count":EXPECTED_ROWS[name],
            "original_nonnumeric_unlabeled_first_BLUPS_source_column_excluded":
                name=="Vole BLUPS.csv",
        }
    return tables,integrity,metadata_sha

def source_only_join(tables,integrity,meta_sha):
    seed=tables["2018 Vole Seed Data.csv"]
    blups=tables["Vole BLUPS.csv"]
    personality=tables["Vole Personality Data.csv"]
    # Explicitly ignore source BLUPS unnamed first CSV column.
    blup_ids=Counter(pid(r.get("PIT")) for r in blups if pid(r.get("PIT")))
    pers_ids=Counter(pid(r.get("PIT")) for r in personality if pid(r.get("PIT")))
    support=Counter()
    valid_grids=set();valid_patches=set();valid_treat=set()
    valid_sessions=set();valid_id=set()
    shared_blup=set();shared_pers=set();shared_both=set()
    eligible_matched_rows=0
    category_support=Counter()
    original_event_tags=set()
    for row in seed:
        support["source_original_2018_event_rows"]+=1
        tag=pid(row.get("PIT"))
        session=(row.get("SESSION") or "").strip()
        grid=(row.get("GRID") or "").strip()
        patch=(row.get("SITE_ID") or "").strip()
        treatment=(row.get("TREAT") or "").strip()
        resource=original_number_available(row.get("WP")) and (
            original_number_available(row.get("BF"))
        )
        if tag:
            support["original_2018_event_rows_with_source_PIT"]+=1
            original_event_tags.add(tag)
        else:
            support["event_rows_without_valid_PIT"]+=1
        if resource:
            support["original_event_rows_with_numeric_both_WP_BF"]+=1
        else:
            support["original_event_rows_without_numeric_both_WP_BF"]+=1
        has_structural=bool(tag and session and grid and patch and treatment)
        if not has_structural:
            support["event_rows_missing_any_original_join_or_category"]+=1
            continue
        support["event_rows_with_all_structural_id_category_keys"]+=1
        category_support["original_paired_station_treatment_source"]+=1
        if not resource:
            continue
        support["eligible_source_event_ID_patch_treat_two_resources"]+=1
        valid_grids.add(grid)
        valid_patches.add((grid,patch))
        valid_treat.add(treatment)
        valid_sessions.add(session)
        valid_id.add(tag)
        if tag in blup_ids:
            shared_blup.add(tag)
            support["eligible_events_with_matching_original_BLUPS_PIT"]+=1
        if tag in pers_ids:
            shared_pers.add(tag)
            support["eligible_events_with_matching_original_personality_PIT"]+=1
        if tag in blup_ids and tag in pers_ids:
            shared_both.add(tag)
            eligible_matched_rows+=1
    gates={
      "original_three_CSVs_and_603_1069_3712_rows_reverified":
          len(seed)==603 and len(blups)==1069 and len(personality)==3712,
      "at_least_8_exact_PITs_in_all_three_sources":len(shared_both)>=MIN_VALID_COMBINED_PIT,
      "at_least_30_matching_risk_patch_seed_event_rows":
          eligible_matched_rows>=MIN_VALID_JOINED_EVENTS,
      "at_least_3_original_field_grids":len(valid_grids)>=MIN_GRIDS,
      "at_least_10_original_grid_site_keys":len(valid_patches)>=MIN_PATCHES,
      "at_least_2_original_risk_treatment_source_categories":
          len(valid_treat)>=MIN_TREAT_CATEGORIES,
      "at_least_2_original_session_categories":len(valid_sessions)>=MIN_SESSIONS,
      "at_least_30_resource_numeric_source_events":
          support["eligible_source_event_ID_patch_treat_two_resources"]>=MIN_BOTH_RESOURCE,
    }
    return {
      "schema":"neon.figshare2023_pit_resource_risk_linkage_source.v1",
      "status":("SOURCE_JOIN_GO_ORIGINAL_BAITED_FORAGING_OBSERVATIONS_NOT_ECOLOGY"
                if all(gates.values()) else
                "SOURCE_JOIN_STOP_ID_PATCH_SEED_OR_RISK_SUPPORT"),
      "original_article_id":21512436,
      "original_article_version":1,
      "original_meta_SHA256":meta_sha,
      "original_files":integrity,
      "source_event_support_counts":dict(sorted(support.items())),
      "original_nonempty_2018_event_PIT_count":len(original_event_tags),
      "eligible_original_source_PIT_count":len(valid_id),
      "eligible_original_BLUPS_PIT_overlap_count":len(shared_blup),
      "eligible_original_personality_PIT_overlap_count":len(shared_pers),
      "eligible_exact_PIT_intersection_all_three_source_count":len(shared_both),
      "eligible_complete_event_rows_with_original_PIT_in_all_three":
          eligible_matched_rows,
      "eligible_original_source_grid_count":len(valid_grids),
      "eligible_original_grid_SITE_ID_key_count":len(valid_patches),
      "eligible_original_TREAT_levels_count":len(valid_treat),
      "eligible_original_SESSION_levels_count":len(valid_sessions),
      "original_BLUPS_PITs_with_multiple_source_rows":
          sum(c>1 for c in blup_ids.values()),
      "original_personality_PITs_with_multiple_source_rows":
          sum(c>1 for c in pers_ids.values()),
      "original_ID_exact_only_without_alias_or_numeric_conversion":True,
      "no_original_PIT_GRID_SITE_ID_values_exported":True,
      "source_admission_tests":gates,
      "biological_limits":{
          "no_resource_effect_or_seed_use_proportion_computed":True,
          "no_TREAT_group_selection_or_p_value_computed":True,
          "no_true_mammal_habitat_or_home_range_observed":True,
          "no independent_trap_vs_camera_capture_probability_calibrated":True,
          "no_camera_operable_time_or_absence_exposure_denominators":True,
          "no_learning_reward_reversal_or_dynamic_memory_measured":True,
          "no species_competitor_removal_in_original_cover_risk_manipulation":True,
          "original_article_published_personality_and_risk_effects_PRIOR_ART":True,
          "source_only_not_behavioral_estimate_not_cross_system_replicate":True,
          "ONE_NEON_unified_ecology_paper_DRAFT_SUBMISSION_HOLD":True,
      },
      "protocol":PROTOCOL,
      "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    try:
        t,integrity,meta=validate_original_sources()
        result=source_only_join(t,integrity,meta)
        # A source-level gate STOP is not a source network/parse failure.
        status=0
    except Exception as exc:
        result={
            "schema":"neon.figshare2023_pit_resource_risk_linkage_source.v1",
            "status":"SOURCE_STOP_ORIGINAL_FILES_OR_PIT_COHORT_NOT_VALIDATED",
            "error_type":type(exc).__name__,
            "stop_reason":str(exc)[:160],
            "no_seed_risk_or_personality_response_calculated":True
        }
        status=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    return status

if __name__=="__main__":
    raise SystemExit(main())
