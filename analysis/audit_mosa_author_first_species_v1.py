#!/usr/bin/env python3
"""Effect-blind MOSA reconciliation of author-first species and normalized TOE IDs.

Leirs et al. (2023) published RMarkdown section 1.3:
  MN = mosa3  # all species; NOT raw MN captures only
  ID = unique(MN$TOE)
  character = rbind(character, ID2[1,4:12])  # first retained record
  ... then keep rows where character$SPECIES == "MN".
That means later MN captures can share a TOE with an encounter-matrix NA row,
without authorization to relabel the initial species or infer a new animal.

Compare original Zenodo MD5-locked raw records with authors' exact 363x3-day
session calendar and published author encounter rows, before ANY MNA, W/B,
space-use distances, animal density slopes or behavioral mechanism inference.

The approved raw data remain on GitHub Actions only; no tag IDs are written to
the receipt. The only output is aggregate counts and explicit unresolved cases.
"""
from __future__ import annotations

import csv
import io
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from analysis.audit_mosa_author_occasion_mask_v1 import (
    TIMEFILE, FROZEN_N_OCCASIONS, FROZEN_TOTAL, FROZEN_MN,
    FROZEN_MN_CODES, FROZEN_AUTHOR_MN_CODES, FROZEN_MISSING_CODES,
    validated_author_days,
)
from analysis.audit_mosa_effect_blind_structure_v1 import (
    published_field_map, parse_all_dates,
)
from analysis.audit_mosa_encounter_toe_reconciliation_v1 import (
    _validated_download, author_matrix_species_tags,
)
from analysis.audit_mosa_zenodo_source_schema_v1 import (
    _get, API, RECORD_ID, select_datafile,
    validate_source_bytes, PublishedSourceError,
)

OUT=Path("build/mosa_author_first_species_v1.json")


def _species(value:object)->str:
    text=str(value or "").strip().upper()
    if text in ("", "NA", "N/A", "UNKNOWN"):
        return "NA"
    if text=="MN":
        return "MN"
    return "OTHER"


def classify_first_species_provenance(
    records:list[dict], fields:list[str],
    matrix_rows:list[tuple[str,str]], author_days:set[date],
    *, expected_raw_mn:int|None=FROZEN_MN,
    expected_author_mn:int|None=FROZEN_AUTHOR_MN_CODES,
    expected_missing:int|None=FROZEN_MISSING_CODES,
)->dict:
    if not author_days:
        raise ValueError("no verified author retained occasion days")
    f=published_field_map(fields)
    days=parse_all_dates([str(row.get(f["date"]) or "").strip() for row in records])

    raw_mn_codes=set()
    count_mn_rows=0
    first_all={}
    first_retained={}
    raw_mn_retained=set()
    species_of_toe=defaultdict(set)
    for row in records:
        toe=str(row.get(f["tag"]) or "").strip()
        sp=_species(row.get(f["species"]))
        day=days[str(row.get(f["date"]) or "").strip()]
        if sp=="MN":
            count_mn_rows+=1
            if not toe:
                raise PublishedSourceError("raw MN capture without TOE ID")
            raw_mn_codes.add(toe)
            if day in author_days:
                raw_mn_retained.add(toe)
        if not toe:
            continue
        species_of_toe[toe].add(sp)
        if toe not in first_all:
            first_all[toe]=sp
        if day in author_days and toe not in first_retained:
            # Source order, as ID2[1,4:12] in the authors' R script.
            first_retained[toe]=sp
    if expected_raw_mn is not None and count_mn_rows!=expected_raw_mn:
        raise PublishedSourceError("frozen source raw MN capture count drift")
    if len(raw_mn_codes)!=FROZEN_MN_CODES and expected_missing is not None:
        raise PublishedSourceError("frozen raw unique MN code count drift")

    author_mn_verbatim=[str(t or "") for sp,t in matrix_rows
                        if _species(sp)=="MN"]
    author_mn=[v.strip() for v in author_mn_verbatim if v.strip()]
    author_mn_codes=set(author_mn)
    if expected_author_mn is not None and len(author_mn_codes)!=expected_author_mn:
        raise PublishedSourceError("published author MN unique TOE roster drift")
    if author_mn_codes-raw_mn_codes:
        raise PublishedSourceError("author MN TOE not present under MN in original")
    matrix_na_codes={
        str(t or "").strip() for sp,t in matrix_rows
        if _species(sp)=="NA" and str(t or "").strip()
    }
    unknown_overlap=author_mn_codes & matrix_na_codes
    missing=raw_mn_codes-author_mn_codes
    if expected_missing is not None and len(missing)!=expected_missing:
        raise PublishedSourceError("frozen 140 missing MN codes drift")

    first_counts=Counter()
    subgroups=Counter()
    first_retained_mn_no_matrix=set()
    for code in missing:
        initial=first_retained.get(code,"NO_RETAINED_RECORD")
        first_counts[initial]+=1
        if code in raw_mn_retained:
            subgroups["missing_with_any_author_date_capture"]+=1
            subgroups["missing_with_MN_date_and_first_retained_NA"]+=(
                initial=="NA")
            subgroups["missing_with_MN_date_and_first_retained_OTHER"]+=(
                initial=="OTHER")
            subgroups["missing_with_MN_date_and_first_retained_MN"]+=(
                initial=="MN")
        if code in matrix_na_codes:
            subgroups["missing_also_in_author_NA"]+=1
        if initial=="MN" and code not in matrix_na_codes:
            first_retained_mn_no_matrix.add(code)
            subgroups["missing_with_first_MN_and_no_author_NA"]+=1
        if initial=="NA" and code in matrix_na_codes:
            subgroups["missing_with_first_NA_and_author_NA"]+=1
        if initial=="OTHER" and code in matrix_na_codes:
            subgroups["missing_with_first_OTHER_and_author_NA"]+=1

    first_author_mn=Counter(first_retained.get(code,"NO_RETAINED_RECORD")
                             for code in author_mn_codes)
    first_author_na=Counter(first_retained.get(code,"NO_RETAINED_RECORD")
                             for code in matrix_na_codes)
    exact_duplicates=sum(x-1 for x in Counter(author_mn_verbatim).values())
    norm_duplicates=len(author_mn)-len(author_mn_codes)
    if norm_duplicates<exact_duplicates:
        raise RuntimeError("unexpected duplicate normalization identity")
    return {
        "schema":"neon.mosa_author_first_retained_species_roster.v1",
        "original_MN_capture_rows":count_mn_rows,
        "original_distinct_MN_TOE":len(raw_mn_codes),
        "author_MN_rows":len(author_mn),
        "author_MN_unique_TOE":len(author_mn_codes),
        "author_MN_exact_duplicate_rows":exact_duplicates,
        "author_MN_normalized_duplicate_rows":norm_duplicates,
        "author_MN_duplicate_rows_created_by_normalization":
            norm_duplicates-exact_duplicates,
        "author_MN_and_NA_label_overlap":len(unknown_overlap),
        "author_NA_TOE_count":len(matrix_na_codes),
        "author_MN_codes_first_retained_as_MN":first_author_mn["MN"],
        "author_MN_codes_first_retained_not_MN":
            len(author_mn_codes)-first_author_mn["MN"],
        "author_MN_first_retained_species_distribution":dict(sorted(first_author_mn.items())),
        "author_NA_first_retained_species_distribution":dict(sorted(first_author_na.items())),
        "raw_MN_codes_absent_author_MN":len(missing),
        "missing_first_retained_species":{
            v:first_counts[v] for v in ("MN","NA","OTHER","NO_RETAINED_RECORD")
        },
        "missing_with_any_author_date_capture":
            subgroups["missing_with_any_author_date_capture"],
        "missing_also_in_author_NA":
            subgroups["missing_also_in_author_NA"],
        "missing_with_first_MN_and_no_author_NA":
            subgroups["missing_with_first_MN_and_no_author_NA"],
        "first_MN_missing_from_author_MN_without_NA_row":
            len(first_retained_mn_no_matrix),
        "missing_code_subgroups":dict(sorted(subgroups.items())),
        "original_MN_TOE_first_raw_species_distribution":dict(sorted(Counter(
            first_all[code] for code in raw_mn_codes).items())),
        "first_retained_species_is_same_as_raw_first_capture":
            sum(first_all.get(code)==first_retained.get(code) for code in raw_mn_codes),
        "first_record_rule_read_from_published_RMarkdown":True,
        "author_exact_manual_date_filter_reimplemented":False,
        "author_RMarkdown_first_species_rule_sufficiently_reconciled":False,
        "source_temporal_order_assumed_as_published_R_dataframe":True,
        "author_correction_of_one_raw_date_not_reenacted":True,
        "author_MN_row_is_not_proven_unique_biological_animal":True,
        "species_NA_reassigned_to_MN":False,
        "individual_ids_disclosed":False,
        "MNA_W_B_density_effects_opened":False,
        "final_19850_versus_19818_gap_resolved":False,
        "interpretation":(
            "Source-order first retained species predicts the classification "
            "potentially used in authors' MN and NA encounter histories. "
            "First-retained-species projections are effect-blind diagnostics; "
            "without fully reproducing manual date deletion, one date "
            "correction and TOE encoding they do not establish one-to-one "
            "animal correspondence or resolve published individual counts."
        ),
    }


def run() -> dict:
    meta=json.loads(_get(API).decode("utf-8"))
    if int(meta.get("id",-1))!=RECORD_ID:
        raise PublishedSourceError("immutable 2023 MOSA Zenodo record changed")
    by_name={str(row.get("key") or ""):row for row in meta.get("files",[])}
    if TIMEFILE not in by_name:
        raise PublishedSourceError("author 363 occasion session schedule missing")
    rawfile=select_datafile(meta)
    raw=_validated_download(rawfile)
    valid=validate_source_bytes(raw,rawfile)
    sep={"SEMICOLON":";","COMMA":",","TAB":"\t"}[valid["delimiter_type"]]
    reader=csv.DictReader(io.StringIO(raw.decode(valid["text_encoding"])),delimiter=sep)
    records=list(reader)
    if len(records)!=FROZEN_TOTAL:
        raise PublishedSourceError("original MOSA capture count drift")
    tb=_validated_download(by_name[TIMEFILE])
    time_reader=csv.DictReader(io.StringIO(tb.decode("utf-8-sig")),delimiter=";")
    time_rows=list(time_reader)
    cal=validated_author_days(time_rows)
    author_days=cal.pop("_author_days")
    author,files=author_matrix_species_tags(meta)
    classification=classify_first_species_provenance(
        records,valid["column_headers"],author,author_days)
    return {
        "schema":"neon.mosa_author_first_species_reconciliation_audit.v1",
        "status":"EFFECT_BLIND_AUTHOR_FIRST_SPECIES_AUDIT_IDENTITY_HOLD",
        "source_original_md5":valid["verified_checksum"],
        "author_time_md5":by_name[TIMEFILE]["checksum"],
        "author_encounter_MD5":[x["MD5"] for x in files],
        "original_author_calendar_nights":len(author_days),
        "author_RMarkdown_rule_source":"Joachimmarien/MOSA, 2_markdown Processing data.Rmd, lines 174-177, 280-300",
        "published_toe_first_capture_species":classification,
        "full_unique_animal_reconciliation":False,
        "MOSA_MNA_W_B_or_density_effect_authorized":False,
        "original_NEON_genus_generality":"FAILED_UNCHANGED",
        "next_gate":"If projected first-retained taxon does not fully match published author row classification, inspect manual date deletions/date correction and original toe code whitespace with checksum-verified author processing; do not infer animal split identities.",
    }


if __name__=="__main__":
    try:
        result=run()
    except (PublishedSourceError,RuntimeError,ValueError,UnicodeError,OSError) as e:
        result={
            "schema":"neon.mosa_author_first_species_reconciliation_audit.v1",
            "status":"STOP_SOURCE_OR_IDENTITY_RECONCILIATION",
            "diagnostic":str(e)[:500],
            "MOSA_MNA_W_B_or_density_effect_authorized":False,
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    if result["status"]!="EFFECT_BLIND_AUTHOR_FIRST_SPECIES_AUDIT_IDENTITY_HOLD":
        raise SystemExit(3)
