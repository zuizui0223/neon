#!/usr/bin/env python3
"""Effect-blind MOSA author-calendar source audit.

Compare checksum-verified original MN TOE roster with checksum-verified
author encounter-matrix TOE roster AND the authors' actual 363×3-night
capture-occasion dates. Unlike the earlier conservative "three MN capture
days within one calendar month" screen, this matches primary occasion dates
directly, including month-crossing bouts and nights with zero MN captures.

Still NO MNA, spatial W/B, home ranges, animal interactions or effect slopes.
Does not split re-used toe codes, reclassify species NA, or invent 32 animals.
"""
from __future__ import annotations

import csv
import io
import json
from collections import Counter,defaultdict
from datetime import datetime,timedelta,date
from pathlib import Path

from analysis.audit_mosa_zenodo_source_schema_v1 import (
    API, RECORD_ID, _get,select_datafile,validate_source_bytes,PublishedSourceError,
)
from analysis.audit_mosa_encounter_toe_reconciliation_v1 import (
    _validated_download,author_matrix_species_tags,
)
from analysis.audit_mosa_effect_blind_structure_v1 import (
    published_field_map,parse_all_dates,
)

OUT=Path("build/mosa_author_occasion_mask_v1.json")
TIMEFILE="C_primary_secondary_time_variables_3consecutive_m2.csv"
FROZEN_TOTAL=49216
FROZEN_MN=45433
FROZEN_MN_CODES=19818
FROZEN_AUTHOR_MN_CODES=19678
FROZEN_AUTHOR_NA_ROWS=158
FROZEN_N_OCCASIONS=363
FROZEN_N_AUTHOR_DAYS=1089
FROZEN_MISSING_CODES=140


def validated_author_days(rows:list[dict], *,expected_sessions:int|None=FROZEN_N_OCCASIONS)->dict:
    by_primary=defaultdict(list)
    date_primary=defaultdict(set)
    for r in rows:
        primary=str(r.get("prim_capt") or "").strip()
        secondary=str(r.get("sec_capt") or "").strip()
        dtext=str(r.get("date") or "").strip()
        if not primary.isdecimal() or secondary not in ("1","2","3"):
            raise ValueError("invalid published primary or secondary occasion ID")
        try:
            d=datetime.strptime(dtext,"%d/%m/%Y").date()
        except ValueError as e:
            raise ValueError("unparseable published author capture date") from e
        if not 1994<=d.year<=2023:
            raise ValueError("published date outside archive's 1994-2023 years")
        by_primary[primary].append((int(secondary),d))
        date_primary[d].add(primary)
    if any(len(g)!=1 for g in date_primary.values()):
        raise ValueError("one author date assigned to different primary occasions")
    if not by_primary:
        raise ValueError("empty author time-table")
    for primary,pairs in by_primary.items():
        if len(pairs)!=3 or {k for k,_ in pairs}!={1,2,3}:
            raise ValueError("primary occasion not exactly three distinct nights")
        days=[d for _k,d in sorted(pairs)]
        if days[1]!=days[0]+timedelta(days=1) or days[2]!=days[1]+timedelta(days=1):
            raise ValueError("published primary occasion is not three consecutive dates")
    if expected_sessions is not None and len(by_primary)!=expected_sessions:
        raise ValueError("original authored 363 primary occasion count drifted")
    days=set(date_primary)
    if expected_sessions is not None and len(days)!=FROZEN_N_AUTHOR_DAYS:
        raise ValueError("original 1089 author trap-nights drifted")
    return {
        "primary_sessions":len(by_primary),
        "secondary_nights":len(days),
        "earliest_date":min(days).isoformat(),
        "latest_date":max(days).isoformat(),
        "primary_occasions_crossing_calendar_month":sum(
            len({(d.year,d.month) for _k,d in pairs})>1
            for pairs in by_primary.values()
        ),
        "all_primary_occasions_exactly_three_consecutive_nights":True,
        "_author_days":days,
    }


def classify_missing_by_author_days(
    records:list[dict],fields:list[str],
    matrix_rows:list[tuple[str,str]],author_days:set[date],
    *,expected_original_MN:int|None=FROZEN_MN
)->dict:
    f=published_field_map(fields)
    cal=parse_all_dates([str(r.get(f["date"]) or "") for r in records])
    by_toe=defaultdict(list)
    full_species=Counter()
    for r in records:
        s=str(r.get(f["species"]) or "").strip().upper()
        full_species[s]+=1
        if s!="MN":continue
        toe=str(r.get(f["tag"]) or "").strip()
        if not toe:raise PublishedSourceError("MN capture with blank published TOE code")
        d=cal[str(r.get(f["date"]) or "").strip()]
        x=str(r.get(f["x"]) or "").strip()
        y=str(r.get(f["y"]) or "").strip().upper()
        try:valid_station=(1<=int(x)<=30 and len(y)==1 and y in "ABCDEFGHIJ")
        except (ValueError,TypeError):valid_station=False
        flagged=bool(str(r.get("FLAGS") or "").strip())
        by_toe[toe].append((d,valid_station,flagged))
    n_mn=sum(map(len,by_toe.values()))
    if expected_original_MN is not None and n_mn!=expected_original_MN:
        raise ValueError("source 45433 published MN record count drift")
    raw_mn=set(by_toe)
    author_mn=[str(t).strip() for s,t in matrix_rows
               if str(s).strip().upper()=="MN" and str(t).strip()]
    author_mn_set=set(author_mn)
    if author_mn_set-raw_mn:
        raise ValueError("published author MN tag absent from original raw source")
    missing=raw_mn-author_mn_set
    author_na={str(t).strip() for s,t in matrix_rows
               if str(s).strip().upper() in ("NA","N/A","UNKNOWN","")
               and str(t).strip()}
    flags=Counter()
    any_dates=set(); any_valid=set();twice=set();off_days=set()
    missing_captures_on_author_days=0
    missing_captures_valid_on_author_days=0
    for toe in missing:
        records=by_toe[toe]
        on_date=[(d,good,flag) for d,good,flag in records if d in author_days]
        on_valid=[d for d,good,_flag in on_date if good]
        missing_captures_on_author_days+=len(on_date)
        missing_captures_valid_on_author_days+=len(on_valid)
        if on_date:any_dates.add(toe)
        if on_valid:any_valid.add(toe)
        if len(set(on_valid))>=2:twice.add(toe)
        if not on_date:off_days.add(toe)
        flags["single_capture_record" if len(records)==1 else "multiple_capture_records"]+=1
        flags["any_flag" if any(x[2] for x in records) else "no_flag"]+=1
        flags["species_NA_matrix_overlap" if toe in author_na else "no_author_NA_row"]+=1
    return {
        "schema":"neon.mosa_author_occasion_mask_structural.v1",
        "source_MN_capture_records":n_mn,
        "raw_MN_unique_TOE":len(raw_mn),
        "author_MN_unique_TOE":len(author_mn_set),
        "raw_MN_missing_from_author_MN":len(missing),
        "missing_exclusively_off_author_retained_dates":len(off_days),
        "missing_with_any_capture_on_author_retained_dates":len(any_dates),
        "missing_with_valid_station_capture_on_author_dates":len(any_valid),
        "missing_with_two_or_more_distinct_author_dates":len(twice),
        "missing_MN_capture_rows_on_author_dates":missing_captures_on_author_days,
        "missing_MN_capture_rows_valid_station_on_author_dates":
            missing_captures_valid_on_author_days,
        "missing_also_in_author_NA":len(missing&author_na),
        "missing_tag_record_flags":dict(sorted(flags.items())),
        "all_omissions_explained_by_dates":len(any_dates)==0,
        "species_NA_reassigned":False,
        "unknown_32_published_MN_individuals_gap":19850-len(raw_mn),
        "publication_individual_count_reconciled":False,
        "no_per_tag_values_emitted":True,
        "MNA_spatial_W_B_density_effects_opened":False,
    }


def run():
    meta=json.loads(_get(API).decode("utf-8"))
    if int(meta.get("id",-1))!=RECORD_ID:
        raise PublishedSourceError("original MOSA Zenodo record version changed")
    by_name={str(f.get("key") or ""):f for f in meta.get("files",[])}
    if TIMEFILE not in by_name:
        raise PublishedSourceError("missing author 363 three-night primary session calendar")
    rawfile=select_datafile(meta)
    raw=_validated_download(rawfile)
    valid=validate_source_bytes(raw,rawfile)
    delim={"COMMA":",","SEMICOLON":";","TAB":"\t"}[valid["delimiter_type"]]
    rd=csv.DictReader(io.StringIO(raw.decode(valid["text_encoding"])),delimiter=delim)
    records=list(rd)
    if len(records)!=FROZEN_TOTAL:raise PublishedSourceError("raw MOSA row count drift")

    t=_validated_download(by_name[TIMEFILE])
    head=t[:1000].lower()
    if b"<!doctype html" in head or b"<html" in head:
        raise PublishedSourceError("author time file returned HTML")
    session_reader=csv.DictReader(io.StringIO(t.decode("utf-8-sig")),delimiter=";")
    rows=list(session_reader)
    expected_headers={"date","prim_capt","sec_capt","all_capt","time_interval","time_interval2"}
    if set(session_reader.fieldnames or [])!=expected_headers:
        raise PublishedSourceError("author time file original six-column schema drift")
    date_report=validated_author_days(rows)
    author_days=date_report.pop("_author_days")
    matrix,files=author_matrix_species_tags(meta)
    classification=classify_missing_by_author_days(
        records,valid["column_headers"],matrix,author_days)
    if (classification["raw_MN_unique_TOE"]!=FROZEN_MN_CODES or
        classification["author_MN_unique_TOE"]!=FROZEN_AUTHOR_MN_CODES or
        classification["raw_MN_missing_from_author_MN"]!=FROZEN_MISSING_CODES):
        raise PublishedSourceError("historical 140 code discrepancy drift")
    na_n=sum(str(sp).strip().upper()=="NA" for sp,_ in matrix)
    if na_n!=FROZEN_AUTHOR_NA_ROWS:
        raise PublishedSourceError("frozen author species-NA count drift")

    return {
        "schema":"neon.mosa_author_occasion_mask_audit.v1",
        "status":"AUTHOR_OFFICIAL_OCCASION_MASK_VALIDATED_IDENTITY_HOLD",
        "source":"Zenodo 10049811 official original capture and author matrices+time variables",
        "publication":"Leirs et al., Scientific Data 2023, DOI 10.1038/s41597-023-02700-3",
        "original_MD5":valid["verified_checksum"],
        "time_variables_MD5":by_name[TIMEFILE]["checksum"],
        "author_matrices_MD5":[f["MD5"] for f in files],
        "author_session_schedule":date_report,
        "missing_identity_diagnostics":classification,
        "comparison_is_better_than_capture_month_screen":True,
        "date_mask_sufficient_to_reconcile_19850_vs_19818":False,
        "authors_complete_preprocessing_equivalence_verified":False,
        "MNA_W_B_or_density_effects_authorized":False,
        "interpretation":(
            "Real author 363 three-consecutive-night occasions replace the "
            "conservative derived 182 months for omission provenance only. "
            "A raw capture on an author-listed day is a reason to investigate "
            "other processing stages, not proof of a missed unique animal."
        )
    }


if __name__=="__main__":
    try:r=run()
    except (PublishedSourceError,RuntimeError,ValueError,OSError,UnicodeError) as e:
        r={"schema":"neon.mosa_author_occasion_mask_audit.v1",
           "status":"STOP_AUTHORED_SOURCE_OR_IDENTITY_MAPPING",
           "diagnostic":str(e)[:600],
           "MNA_W_B_or_density_effects_authorized":False}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(r,indent=2,sort_keys=True))
    if r["status"]!="AUTHOR_OFFICIAL_OCCASION_MASK_VALIDATED_IDENTITY_HOLD":
        raise SystemExit(3)
