#!/usr/bin/env python3
"""Read authors' exact published MOSA capture-session time-table schema.

Goal: determine whether the five raw Mastomys TOE codes absent from the authors'
MN encounter matrix despite being in a *capture-day inferred* 3-night month
might be explained by different true 3-consecutive trapping occasions.

Only published source metadata and methods are opened; no animal location, MNA,
W/B or ecological effects. All downloaded files are checksum verified.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

from analysis.audit_mosa_zenodo_source_schema_v1 import (
    API, RECORD_ID, _get, PublishedSourceError,
)
from analysis.audit_mosa_encounter_toe_reconciliation_v1 import _validated_download

OUT = Path("build/mosa_author_capture_occasion_time_schema_v1.json")
TIMEFILE = "C_primary_secondary_time_variables_3consecutive_m2.csv"
RMD = "2_markdown Processing data.Rmd"
EXPECT_MATRIX_ID_GAP = 32


def parse_time_table(raw: bytes) -> dict:
    head=raw[:1024].strip().lower()
    if b"<html" in head or b"<!doctype html" in head or b"validating..." in head:
        raise ValueError("HTML document received in place of authors' time CSV")
    try:
        text=raw.decode("utf-8-sig")
        encoding="utf-8-sig"
    except UnicodeDecodeError:
        text=raw.decode("cp1252")
        encoding="cp1252"
    first=text.splitlines()[0] if text.splitlines() else ""
    choices=[]
    for sep in (",",";","\t"):
        headers=next(csv.reader([first],delimiter=sep),[])
        if len(headers)>1 and len(set(headers))==len(headers) and all(
            h and len(h)<128 for h in headers
        ):
            choices.append((sep,headers))
    if len(choices)!=1:
        raise ValueError("author time-variable CSV delimiter not unambiguous")
    sep,columns=choices[0]
    reader=csv.DictReader(io.StringIO(text),delimiter=sep)
    rows=[]
    ragged=0
    for row in reader:
        if None in row:ragged+=1
        rows.append(row)
    if ragged:
        raise ValueError("ragged author time-variable CSV rows")
    if not rows:
        raise ValueError("empty author time-variable data")
    sample=[]
    for row in rows[:6]:
        sample.append({field:str(row.get(field) or "")[:80] for field in columns[:12]})
    return {
        "encoding":encoding,
        "delimiter":"TAB" if sep=="\t" else "SEMICOLON" if sep==";" else "COMMA",
        "record_count":len(rows),
        "columns":columns,
        "distinct_nonblank_by_column":{
            field:len({str(r.get(field) or "").strip() for r in rows
                       if str(r.get(field) or "").strip()})
            for field in columns
        },
        "missing_by_column":{
            field:sum(not str(r.get(field) or "").strip() for r in rows)
            for field in columns
        },
        "preview":sample,
        "animal_TOE_ID_not_parsed":True,
        "ecological_density_or_spatial_effect_not_opened":True,
    }


def source_method_slice(text: str, *, start_line: int=170, end_line: int=305):
    lines=text.splitlines()
    return [{"line":i+1,"text":lines[i][:360]}
            for i in range(max(0,start_line-1),min(end_line,len(lines)))]


def run():
    meta=json.loads(_get(API).decode("utf-8"))
    if int(meta.get("id",-1))!=RECORD_ID:
        raise PublishedSourceError("MOSA original Zenodo version drifted")
    names={str(f.get("key") or ""):f for f in meta.get("files",[])}
    if TIMEFILE not in names or RMD not in names:
        raise PublishedSourceError("Published author occasion data or method script missing")
    outputs={}
    for name in (TIMEFILE,RMD):
        f=names[name]
        raw=_validated_download(f)
        outputs[name]={
            "name":name,"length":len(raw),
            "checksum":str(f.get("checksum") or "").lower(),
            "validated_checksum":True,
            "bytes_sha256":hashlib.sha256(raw).hexdigest(),
            "raw":raw,
        }
    time_data=parse_time_table(outputs[TIMEFILE]["raw"])
    method=outputs[RMD]["raw"].decode("utf-8-sig",errors="replace")
    return {
        "schema":"neon.external_mosa_author_occasion_time_schema.v1",
        "status":"EFFECT_BLIND_AUTHOR_SESSION_SCHEMA_OPEN_NO_CAPTURE_EFFECTS",
        "source":"Zenodo 10049811 published author occasion time table, MD5-verified",
        "time_source_md5":outputs[TIMEFILE]["checksum"],
        "processing_code_md5":outputs[RMD]["checksum"],
        "published_time_table":time_data,
        "exact_author_processing_lines_170_to_305":source_method_slice(method),
        "author_preprocessing_lines_1_to_169":source_method_slice(
            method,start_line=1,end_line=169
        ),
        "MOSA_raw_MN_TOE_count":19818,
        "publication_MN_individual_count":19850,
        "published_count_gap_unresolved":True,
        "identity_reassignment_performed":False,
        "primary_occasion_filter_reconstructed":False,
        "MNA_W_B_and_density_effects_opened":False,
        "why":"The original five exceptional missing TOE codes require reconciliation with actual authors' date/occasion mask, not only months with three capture-bearing dates.",
    }


if __name__=="__main__":
    try: result=run()
    except (PublishedSourceError,RuntimeError,ValueError,OSError,UnicodeError) as e:
        result={
            "schema":"neon.external_mosa_author_occasion_time_schema.v1",
            "status":"STOP_AUTHOR_TIME_SOURCE_OR_FORMAT",
            "diagnostic":str(e)[:500],
            "MNA_W_B_and_density_effects_opened":False,
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        k:v for k,v in result.items()
        if k not in ("exact_author_processing_lines_170_to_305", "author_preprocessing_lines_1_to_169")
    },indent=2,ensure_ascii=False,sort_keys=True))
    if result["status"]!="EFFECT_BLIND_AUTHOR_SESSION_SCHEMA_OPEN_NO_CAPTURE_EFFECTS":
        raise SystemExit(3)
