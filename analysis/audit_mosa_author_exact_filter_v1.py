#!/usr/bin/env python3
"""Reconstruct MOSA authors' raw date exclusion and first-species TOE provenance.

Parse the 55 explicit original-unique-date deletions and one date correction
directly from the checksum-verified published 2023 '2_markdown Processing
data.Rmd'. Replay on checksum-verified 49,216 original MOSA capture records.
Compare exact resulting dates with the authors' checksum-verified
363 x 3 = 1,089 primary-secondary occasion schedule, and match the source-
order first-retained-record species labels against the published encounter
matrix. No animal identities exported and no MNA, W/B, NN or density effects.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import re
from collections import Counter
from datetime import date, datetime
from pathlib import Path

from analysis.audit_mosa_zenodo_source_schema_v1 import (
    API, RECORD_ID, _get, select_datafile,validate_source_bytes,
    PublishedSourceError,
)
from analysis.audit_mosa_encounter_toe_reconciliation_v1 import (
    _validated_download,author_matrix_species_tags,
)
from analysis.audit_mosa_author_occasion_mask_v1 import (
    validated_author_days,TIMEFILE,FROZEN_TOTAL,FROZEN_MN_CODES,
    FROZEN_AUTHOR_MN_CODES,FROZEN_MISSING_CODES,git_blob_sha1,
)
from analysis.audit_mosa_effect_blind_structure_v1 import (
    published_field_map,parse_all_dates,
)

OUT=Path("build/mosa_author_exact_filter_v1.json")
PROCESSING="2_markdown Processing data.Rmd"
PUBLISHED_RMD_GIT_BLOB_SHA1="32e51e955a30b74052d5f1654216f846bb8874f9"
EXPECTED_DELETIONS=55
# Identical public authored exclusion command indices checked independently against
# the Zenodo RMarkdown archived source; its whole-file bytes need not match
# a later GitHub text snapshot.
EXPECTED_AUTHOR_REMOVALS=(7, 8, 9, 10, 32, 33, 34, 35, 39, 40, 41, 57, 58, 59, 60, 61, 62, 63, 67, 89, 90, 91, 92, 96, 97, 113, 117, 118, 122, 123, 235, 236, 240, 241, 245, 246, 247, 248, 252, 253, 254, 291, 301, 371, 372, 373, 374, 375, 376, 377, 381, 382, 383, 384, 506)
EXPECTED_CORRECTION_ORIGINAL_DATE_INDEX=469
EXPECTED_CORRECTION_DATE="2004-04-13"


def parse_author_filter_commands(
    source:str, *, expected_deletions:int|None=EXPECTED_DELETIONS,
)->dict:
    token=r'MN=MN\[-\(which\(MN\[,2\]==xx\[(\d+),2\]\)\),\]'
    found=[int(v) for v in re.findall(token,source)]
    if not found:
        raise ValueError("no explicit date deletion commands in published RMarkdown")
    if len(set(found))!=len(found):
        raise ValueError("duplicate author date deletion index")
    if expected_deletions is not None and len(found)!=expected_deletions:
        raise ValueError(f"expected {expected_deletions} published date deletions, got {len(found)}")
    if source.count("MN=MN[-")!=len(found):
        raise ValueError("unrecognized additional author MN date deletion statement")
    correction=re.findall(
        r'MN\[\(which\(MN\[,2\]==xx\[(\d+),2\]\)\),2\]=as.Date\("([0-9-]+)"\)',
        source,
    )
    if len(correction)!=1:
        raise ValueError("published author date correction not exactly one")
    index,new_day=correction[0]
    date.fromisoformat(new_day)
    if int(index) in found:
        raise ValueError("published date correction targets an excluded index")
    return {
        "removed_original_unique_date_indices":sorted(found),
        "corrected_source_date_index":int(index),
        "corrected_to_date":new_day,
        "original_commands_verified":True,
    }


def replay_author_schedule(
    records:list[dict],date_field:str,cmds:dict,
    *,expected_author_days:set[date]|None=None
)->dict:
    if not records:
        raise ValueError("original MOSA source rows empty")
    raw_dates=[str(r.get(date_field) or "").strip() for r in records]
    parsed=parse_all_dates(raw_dates)
    first_seen=list(dict.fromkeys(parsed[value] for value in raw_dates))
    drop_indices=cmds["removed_original_unique_date_indices"]
    target_index=cmds["corrected_source_date_index"]
    if any(i<1 or i>len(first_seen) for i in drop_indices+[target_index]):
        raise ValueError("authored original unique-date index exceeds source calendar")
    dropped={first_seen[i-1] for i in drop_indices}
    corrected_source=first_seen[target_index-1]
    correction=date.fromisoformat(cmds["corrected_to_date"])
    kept=[]
    affected=0
    for row,text in zip(records,raw_dates):
        original=parsed[text]
        if original in dropped:
            continue
        current=dict(row)
        if original==corrected_source:
            current[date_field]=correction.strftime("%d/%m/%Y")
            affected+=1
        kept.append(current)
    retained_days={datetime.strptime(str(r[date_field]),"%d/%m/%Y").date()
                   for r in kept}
    if expected_author_days is not None and retained_days!=expected_author_days:
        raise ValueError(
            "author published dates differ from reexecuted explicit RMarkdown "
            f"filter (missing={len(expected_author_days-retained_days)},"
            f"extra={len(retained_days-expected_author_days)})"
        )
    return {
        "source_unique_dates":len(first_seen),
        "source_raw_capture_records":len(records),
        "removed_source_date_count":len(dropped),
        "source_rows_after_authored_date_deletions":len(kept),
        "date_corrected_capture_rows":affected,
        "dates_after_authored_deletions":len(retained_days),
        "retained_days":retained_days,
        "retained_rows":kept,
        "published_calendar_exact_match":
            expected_author_days is not None and retained_days==expected_author_days,
    }


def first_species_label(value:object)->str:
    if value is None or str(value).strip().upper() in ("","NA","N/A","UNKNOWN"):
        return "NA"
    return str(value).strip().upper()


def source_first_species(
    records:list[dict],tag_field:str,species_field:str,
)->dict[str,str]:
    first={}
    for row in records:
        tag=str(row.get(tag_field) or "").strip()
        if not tag or tag.upper()=="NO_CAPTURE":
            continue
        if tag not in first:
            first[tag]=first_species_label(row.get(species_field))
    return first


def reconcile_labels(
    original:list[dict], retained:list[dict], fields:list[str],
    published_matrix:list[tuple[str,str]]
)->dict:
    f=published_field_map(fields)
    raw_mn={str(r.get(f["tag"]) or "").strip() for r in original
            if first_species_label(r.get(f["species"]))=="MN"}
    raw_mn.discard("")
    if len(raw_mn)!=FROZEN_MN_CODES:
        raise RuntimeError("original raw MN tag roster drift")
    first=source_first_species(retained,f["tag"],f["species"])
    published_mn_raw=[str(t or "") for sp,t in published_matrix
                      if first_species_label(sp)=="MN"]
    published_mn={t.strip() for t in published_mn_raw if t.strip()}
    published_na={str(t or "").strip() for sp,t in published_matrix
                  if first_species_label(sp)=="NA" and str(t or "").strip()}
    if len(published_mn)!=FROZEN_AUTHOR_MN_CODES or len(raw_mn-published_mn)!=FROZEN_MISSING_CODES:
        raise RuntimeError("frozen original/author MN roster drift")
    predicted_mn={tag for tag,sp in first.items() if sp=="MN"}
    predicted_na={tag for tag,sp in first.items() if sp=="NA"}
    missing=raw_mn-published_mn
    actual_species_first=Counter(first.get(t,"NO_RETAINED_RECORD") for t in missing)
    author_label_first=Counter(first.get(t,"NO_RETAINED_RECORD") for t in published_mn)
    whitespace_exact_dups=sum(n-1 for n in Counter(published_mn_raw).values())
    whitespace_normalized_dups=len(published_mn_raw)-len(published_mn)
    return {
        "author_matrix_total_rows":len(published_matrix),
        "raw_MN_unique_TOE":len(raw_mn),
        "author_MN_unique_TOE":len(published_mn),
        "author_NA_unique_TOE":len(published_na),
        "author_MN_raw_exact_duplicate_rows":whitespace_exact_dups,
        "author_MN_whitespace_normalization_collisions":
            whitespace_normalized_dups-whitespace_exact_dups,
        "predicted_first_species_MN_TOE":len(predicted_mn),
        "predicted_first_species_NA_TOE":len(predicted_na),
        "predicted_MN_absent_from_author_MN":len(predicted_mn-published_mn),
        "author_MN_absent_from_predicted_first_MN":len(published_mn-predicted_mn),
        "predicted_NA_absent_from_author_NA":len(predicted_na-published_na),
        "author_NA_absent_from_predicted_first_NA":len(published_na-predicted_na),
        "missing_rawMN_in_authorMN":len(missing),
        "missing_MN_first_retained_species_distribution":
            dict(sorted(actual_species_first.items())),
        "author_MN_first_retained_species_distribution":
            dict(sorted(author_label_first.items())),
        "rawMN_missing_MN_but_predicted_MN":len(missing & predicted_mn),
        "rawMN_missing_MN_but_author_NA":len(missing & published_na),
        "author_MN_label_matches_first_retained_species_exactly":
            not (published_mn-predicted_mn or predicted_mn-published_mn),
        "author_NA_label_matches_first_retained_species_exactly":
            not (published_na-predicted_na or predicted_na-published_na),
        "published_19850_unique_animal_claim_reconciled":False,
        "no_TOE_values_emitted":True,
        "animal_ID_splits_or_species_relabels_performed":False,
        "MNA_W_B_or_density_effects_opened":False,
    }


def run()->dict:
    meta=json.loads(_get(API).decode("utf-8"))
    if int(meta.get("id",-1))!=RECORD_ID:
        raise PublishedSourceError("MOSA author Zenodo version identity changed")
    byname={str(v.get("key") or ""):v for v in meta.get("files",[])}
    if PROCESSING not in byname or TIMEFILE not in byname:
        raise PublishedSourceError("published author processing/date file unavailable")
    original=select_datafile(meta)
    raw=_validated_download(original)
    validated=validate_source_bytes(raw,original)
    sep={"SEMICOLON":";","COMMA":",","TAB":"\t"}[validated["delimiter_type"]]
    reader=csv.DictReader(io.StringIO(raw.decode(validated["text_encoding"])),delimiter=sep)
    original_rows=list(reader)
    if len(original_rows)!=FROZEN_TOTAL:
        raise PublishedSourceError("original raw source row count drift")
    f=published_field_map(validated["column_headers"])

    method_raw=_validated_download(byname[PROCESSING])
    method_sha1=git_blob_sha1(method_raw)
    # The official Zenodo RMarkdown is MD5-verified above. It differs at
    # whole-file byte level from the public GitHub text snapshot, so require
    # literal equivalence of *all effect-blind cleaning commands* instead of
    # treating a formatting/editorial change as a scientific identity drift.
    rmd=method_raw.decode("utf-8-sig",errors="strict")
    commands=parse_author_filter_commands(rmd)
    if (tuple(commands["removed_original_unique_date_indices"])
            != EXPECTED_AUTHOR_REMOVALS
        or commands["corrected_source_date_index"]
            != EXPECTED_CORRECTION_ORIGINAL_DATE_INDEX
        or commands["corrected_to_date"]!=EXPECTED_CORRECTION_DATE):
        raise PublishedSourceError("published date deletion/correction semantics differ from audited source")
    time_raw=_validated_download(byname[TIMEFILE])
    time_reader=csv.DictReader(io.StringIO(time_raw.decode("utf-8-sig")),delimiter=";")
    cal=validated_author_days(list(time_reader))
    authored_days=cal.pop("_author_days")
    schedule=replay_author_schedule(
        original_rows,f["date"],commands,expected_author_days=authored_days)
    author,authorfiles=author_matrix_species_tags(meta)
    identity=reconcile_labels(original_rows,schedule["retained_rows"],
                              validated["column_headers"],author)
    schedule.pop("retained_days")
    schedule.pop("retained_rows")
    return {
        "schema":"neon.mosa_author_exact_RMarkdown_schedule_replay.v1",
        "status":"EXACT_AUTHORED_DATE_MASK_REPRODUCED_IDENTITY_RECONCILIATION_HOLD",
        "source":"Zenodo 10049811 original, 2_markdown Processing data.Rmd, author 363 primary time table and encounter matrices",
        "original_md5":validated["verified_checksum"],
        "processing_script_md5":byname[PROCESSING]["checksum"],
        "processing_script_git_blob_SHA1":method_sha1,
        "original_Zenodo_Rmd_bytes_equal_GitHub_snapshot":
            method_sha1==PUBLISHED_RMD_GIT_BLOB_SHA1,
        "all_55_original_date_deletions_match_GitHub_script":True,
        "original_date_correction_matches_GitHub_script":True,
        "published_occasion_table_md5":byname[TIMEFILE]["checksum"],
        "published_matrix_md5":[a["MD5"] for a in authorfiles],
        "published_original_capture_records":len(original_rows),
        "author_replay_commands":commands,
        "replay_structural":schedule,
        "identity_first_species":identity,
        "MOSA_external_W_B_or_MNA_authorized":False,
        "next_decision":"If author MN and NA labels coincide with exact first-record prediction, map biological TOE reuse/whitespace and clarify published 19850 individuals claim; if not, stop and seek author clarification. Never add 32 invented animals or reassign NA species.",
        "NEON_original_6_of_8_general_guard":"FAILED_UNCHANGED",
    }


if __name__=="__main__":
    try:
        result=run()
    except (PublishedSourceError,RuntimeError,ValueError,UnicodeError,OSError) as exc:
        result={
            "schema":"neon.mosa_author_exact_RMarkdown_schedule_replay.v1",
            "status":"STOP_AUTHOR_EXACT_DATE_OR_MATRIX_PROVENANCE",
            "error":str(exc)[:550],
            "MOSA_W_B_MNA_density_effects_opened":False,
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    if result["status"]!="EXACT_AUTHORED_DATE_MASK_REPRODUCED_IDENTITY_RECONCILIATION_HOLD":
        raise SystemExit(3)
