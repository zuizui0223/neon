#!/usr/bin/env python3
"""Original TREAT category codebook ONLY, no vole behavioral outcomes."""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timezone
from hashlib import md5
from io import StringIO
from pathlib import Path
import csv,json

from analysis.audit_neon_figshare_2023_original_csv_schema_v1 import (
    FILES,inventory_source,bounded_original,original_header_and_row_count,require
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_figshare_2023_treatment_ontology_v1.json"

def audit_source_categories():
    hrefs,metadata_sha=inventory_source()
    fid=38217891
    name,size,orig_md5=FILES[fid]
    raw=bounded_original(hrefs[fid],size)
    require(md5(raw).hexdigest()==orig_md5,
            "TREATMENT_SOURCE_MD5_DRIFT")
    head=original_header_and_row_count(raw,name)
    require(head["original_row_count"]==603,
            "ORIGINAL_603_SOURCE_RECORD_DRIFT")
    rd=csv.DictReader(StringIO(raw.decode("utf-8-sig"),newline=""))
    counts=Counter();grids=defaultdict(set)
    sessions=defaultdict(set);sites=defaultdict(set)
    missing_treat=0
    original_SITE_ID_codes=Counter()
    original_PRED_PRES_codes=Counter()
    for record in rd:
        tr=(record["TREAT"] or "").strip()
        if not tr:
            missing_treat+=1
            continue
        grid=(record["GRID"] or "").strip()
        ses=(record["SESSION"] or "").strip()
        site=(record["SITE_ID"] or "").strip()
        counts[tr]+=1
        original_SITE_ID_codes[site]+=1
        original_PRED_PRES_codes[(record.get("PRED_PRES") or "").strip()]+=1
        if grid:grids[tr].add(grid)
        if ses:sessions[tr].add(ses)
        if grid and site:sites[tr].add((grid,site))
    return {
        "schema":"neon.figshare_2023_original_vole_treatment_source_categories.v1",
        "status":"SOURCE_TREATMENT_ORIGINAL_LEVELS_VERIFIED_NOT_RISK_CODING_IDENTIFIED",
        "original_article_id":21512436,
        "original_source_file_id":fid,
        "original_published_file_MD5_verified":orig_md5,
        "original_provider_meta_SHA256":metadata_sha,
        "original_row_count":head["original_row_count"],
        "literal_uninterpreted_TREAT_category_row_counts":dict(sorted(counts.items())),
        "source_TREAT_category_count":len(counts),
        "TREAT_category_meanings_from_original_published_methods":{
            "EVN":"even-aged forest shelterwood",
            "REF":"reference unlogged forest",
            "TWO":"two-stage shelterwood forest"
        },
        "TREAT_is_not_safe_vs_risky_cover_experiment":True,
        "SITE_ID_literal_source_category_counts_only":dict(sorted(original_SITE_ID_codes.items())),
        "PRED_PRES_literal_source_category_counts_only":dict(sorted(original_PRED_PRES_codes.items())),
        "SITE_ID_and_PRED_PRES_risk_semantics_NOT_INFERRED":True,
        "original_missing_TREAT_source_rows":missing_treat,
        "number_of_original_GRIDs_per_TREAT_label":{
            z:len(grids[z]) for z in sorted(counts)},
        "number_of_original_SESSIONs_per_TREAT_label":{
            z:len(sessions[z]) for z in sorted(counts)},
        "original_grid_site_keys_per_TREAT_label":{
            z:len(sites[z]) for z in sorted(counts)},
        "published_two_paired_risk_conditions_not_silently_equated_with_three_source_TREAT_labels":True,
        "no_PIT_or_grid_site_labels_exported":True,
        "no_seed_consumption_selection_personality_or_risk_effects_opened":True,
        "source_categories_not_independent_field_sites":True,
        "further_treatment_mapping_requires_original_published_codebook":True,
        "one_NEON_ecology_paper_Draft_SUBMISSION_HOLD":True,
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
    }

def main():
    try:
        r=audit_source_categories();status=0
    except Exception as exc:
        r={"schema":"neon.figshare_2023_original_vole_treatment_source_categories.v1",
           "status":"SOURCE_STOP_CATEGORIES_NOT_VERIFIED",
           "error_type":type(exc).__name__,
           "reason":str(exc)[:160],
           "no_behavioral_outcomes_estimated":True}
        status=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps(r,indent=2,sort_keys=True))
    return status

if __name__=="__main__":
    raise SystemExit(main())
