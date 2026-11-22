#!/usr/bin/env python3
"""Why original MOSA Mastomys toe codes are absent from authors' matrix.

Uses only original Zenodo 2023 checksum-locked data and authored matrix rows.
Checks whether source codes lacking an MN-labelled matrix row are from calendar
months without exactly three consecutive capture dates; also distinguishes
matrix NA species codes that originate in non-MN source taxa.

All analyses are STRUCTURAL provenance checks before any monthly MNA, W/B,
density slope, territorial behaviour or individual identity relabelling.
"""
from __future__ import annotations

import csv
import io
import json
from collections import Counter,defaultdict
from datetime import timedelta
from pathlib import Path

from analysis.audit_mosa_effect_blind_structure_v1 import (
    published_field_map,parse_all_dates,
)
from analysis.audit_mosa_encounter_toe_reconciliation_v1 import (
    _validated_download, author_matrix_species_tags,
)
from analysis.audit_mosa_zenodo_source_schema_v1 import (
    API,RECORD_ID,select_datafile,validate_source_bytes,
    _get,PublishedSourceError,
)

OUT=Path("build/mosa_author_missing_tag_sources_v1.json")
FROZEN_RAW_COUNT=49216
FROZEN_MN_COUNT=45433
FROZEN_RAW_UNIQUE_MN=19818
FROZEN_AUTHOR_MN_UNIQUE=19678
FROZEN_AUTHOR_UNKNOWN_NA=158


def classify_missing_tags(
    records:list[dict],header:list[str],matrix_rows:list[tuple[str,str]],
    *,expected_raw_mn:int|None=FROZEN_MN_COUNT,
)->dict:
    f=published_field_map(header)
    dates=parse_all_dates([str(r.get(f["date"]) or "").strip() for r in records])
    mn_rows=[]
    raw_non_mn=defaultdict(set)
    all_mn_month_days=defaultdict(set)
    for r in records:
        sp=str(r.get(f["species"]) or "").strip().upper()
        toe=str(r.get(f["tag"]) or "").strip()
        if not toe:continue
        if sp!="MN":
            raw_non_mn[toe].add(sp)
            continue
        day=dates.get(str(r.get(f["date"]) or "").strip())
        if day is None:raise ValueError("source MN row lacks valid capture day")
        key=(day.year,day.month)
        # Match existing conservative 3-night spatial support: invalid
        # location cannot establish a valid candidate session.
        try:
            xi=int(str(r.get(f["x"]) or "").strip())
            yi=str(r.get(f["y"]) or "").strip().upper()
            valid_station=(1<=xi<=30 and len(yi)==1 and yi in "ABCDEFGHIJ")
        except (ValueError,TypeError):
            valid_station=False
        if valid_station:
            all_mn_month_days[key].add(day)
        mn_rows.append((toe,day,key,valid_station,bool(str(r.get("FLAGS") or "").strip())))

    if expected_raw_mn is not None and len(mn_rows)!=expected_raw_mn:
        raise ValueError("original checksum-valid source MN row count changed")
    raw_mn_codes={toe for toe,*_ in mn_rows}
    matrix_mn=[str(t).strip() for sp,t in matrix_rows
               if str(sp).strip().upper()=="MN" and str(t).strip()]
    matrix_mn_codes=set(matrix_mn)
    missing=raw_mn_codes-matrix_mn_codes
    if matrix_mn_codes-raw_mn_codes:
        raise ValueError("author MN matrix has tag unknown in raw MN")
    unknown=[str(t).strip() for sp,t in matrix_rows
             if str(sp).strip().upper() in ("NA","N/A","UNKNOWN","")
             and str(t).strip()]
    unknown_set=set(unknown)

    strict_months=set()
    for key,ds in all_mn_month_days.items():
        dates_sorted=sorted(ds)
        if len(dates_sorted)==3 and all(
            dates_sorted[i+1]==dates_sorted[i]+timedelta(days=1)
            for i in (0,1)
        ):
            strict_months.add(key)

    by_tag=defaultdict(list)
    for toe,day,month,good,flag in mn_rows:
        if toe in missing:
            by_tag[toe].append((day,month,good,flag))
    with_strict=set()
    with_twice_strict=set()
    singleton=set()
    flagged=set()
    for toe,rr in by_tag.items():
        if len(rr)==1:singleton.add(toe)
        if any(flag for _day,_m,_good,flag in rr):flagged.add(toe)
        by_month=defaultdict(set)
        for day,month,valid,_flag in rr:
            if valid and month in strict_months:
                by_month[month].add(day)
        if by_month:with_strict.add(toe)
        if any(len(days)>=2 for days in by_month.values()):
            with_twice_strict.add(toe)

    non_mn_tags=set(raw_non_mn)
    return {
        "schema":"neon.MOSA_author_missing_TOE_structural_causes.v1",
        "raw_MN_capture_rows_with_nonblank_TOE":len(mn_rows),
        "raw_MN_unique_TOE":len(raw_mn_codes),
        "matrix_MN_rows":len(matrix_mn),
        "matrix_MN_unique_TOE":len(matrix_mn_codes),
        "matrix_NA_rows":len(unknown),
        "matrix_NA_distinct_TOE":len(unknown_set),
        "raw_MN_missing_from_matrix_MN":len(missing),
        "strict_three_consecutive_day_MN_months":len(strict_months),
        "missing_raw_MN_tags_with_capture_in_strict_three_day_month":
            len(with_strict),
        "missing_raw_MN_tags_with_only_non_strict_month_captures":
            len(missing-with_strict),
        "missing_raw_MN_tags_with_ge2_capture_days_in_strict_three_day_month":
            len(with_twice_strict),
        "missing_raw_MN_tags_with_only_one_capture_record":len(singleton),
        "missing_raw_MN_tags_with_any_nonblank_flags":len(flagged),
        "missing_raw_MN_tags_appearing_under_matrix_NA":
            len(missing&unknown_set),
        "raw_MN_tags_absent_from_matrix_MN_or_NA":
            len(missing-unknown_set),
        "matrix_NA_tag_codes_found_in_raw_nonMN":
            len(unknown_set&non_mn_tags),
        "matrix_NA_tag_codes_found_in_raw_MN":
            len(unknown_set&raw_mn_codes),
        "matrix_NA_tag_codes_absent_from_any_raw_species":
            len(unknown_set-(raw_mn_codes|non_mn_tags)),
        "raw_nonMN_species_of_matrix_NA_TOE":dict(sorted(Counter(
            sp for t in unknown_set&non_mn_tags
            for sp in raw_non_mn[t]).items())),
        "unresolved_19850_vs_19818_unique_individual_difference":
            19850-len(raw_mn_codes),
        "species_NA_code_identity_resolved":False,
        "per_individual_codes_disclosed":False,
        "MNA_or_WB_unsealed":False,
        "causal_omission_reason_proven":False,
        "interpretation":(
            "Author-matrix absence can coincide with lack of strictly complete "
            "three-day months, but that is not proof of authors' exact row "
            "filtering. Species NA cannot be assigned to Mastomys. The published "
            "19850 unique individual claim is not reconciled by these overlaps."
        ),
    }


def run():
    meta=json.loads(_get(API).decode("utf-8"))
    if int(meta.get("id",-1))!=RECORD_ID:
        raise PublishedSourceError("MOSA record version changed")
    source=select_datafile(meta)
    raw=_validated_download(source)
    validated=validate_source_bytes(raw,source)
    sep={"COMMA":",","SEMICOLON":";","TAB":"\t"}[
        validated["delimiter_type"]]
    reader=csv.DictReader(
        io.StringIO(raw.decode(validated["text_encoding"])),delimiter=sep)
    records=list(reader)
    if len(records)!=FROZEN_RAW_COUNT:
        raise PublishedSourceError("frozen original capture row count changed")
    matrix,files=author_matrix_species_tags(meta)
    r=classify_missing_tags(records,list(reader.fieldnames or []),matrix)
    if (r["raw_MN_unique_TOE"]!=FROZEN_RAW_UNIQUE_MN or
        r["matrix_MN_unique_TOE"]!=FROZEN_AUTHOR_MN_UNIQUE or
        r["matrix_NA_rows"]!=FROZEN_AUTHOR_UNKNOWN_NA):
        raise PublishedSourceError("previous checksum-verified roster count drift")
    return {
        "schema":"neon.MOSA_author_missing_TOE_structural_causes.v1",
        "status":"SOURCE_OMISSION_STRUCTURE_RECONCILED_ONLY_IDENTITY_HOLD",
        "source_checksum":validated["verified_checksum"],
        "author_matrix_checksum_parts":[
            {"filename":x["file"],"MD5":x["MD5"]} for x in files],
        "result":r,
        "authors_ID_TOE_crosswalk_verified":False,
        "MNA_WB_or_density_effects_authorized":False,
    }


if __name__=="__main__":
    try:r=run()
    except (PublishedSourceError,RuntimeError,ValueError,OSError) as exc:
        r={"schema":"neon.MOSA_author_missing_TOE_structural_causes.v1",
           "status":"STOP_MOSA_SOURCE_PROVENANCE_DRIFT",
           "error":str(exc)[:400],
           "MNA_WB_or_density_effects_authorized":False}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps(r,indent=2,sort_keys=True))
    if r["status"]!="SOURCE_OMISSION_STRUCTURE_RECONCILED_ONLY_IDENTITY_HOLD":
        raise SystemExit(3)
