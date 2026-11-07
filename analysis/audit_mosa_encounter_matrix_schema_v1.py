#!/usr/bin/env python3
"""MOSA authors' original encounter-matrix structural reconciliation only.

Inspect both separately published checksum-locked C_primary_secondary_capture
CSV archives and the authors' RMarkdown transformation. Count encounter
matrix rows / ID columns, but do NOT compute capture metrics, any MNA model,
spatial W/B or ecology slopes.

Research question: why 19,818 verbatim corrected source TOE strings versus
19,850 MN 'unique individuals' stated in Leirs et al. (2023)?
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

from analysis.audit_mosa_zenodo_source_schema_v1 import (
    API,RECORD_ID,_get,PublishedSourceError,
)

OUT=Path("build/mosa_author_encounter_identity_schema_v1.json")
FILES=(
    "C_primary_secondary_capture_3consecutive_o_1_10000b.csv",
    "C_primary_secondary_capture_3consecutive_o_10000-20000b.csv",
)

def parse_encounter_headers(raw:bytes) -> dict:
    try:text=raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text=raw.decode("cp1252")
    head=text.splitlines()[0] if text else ""
    possible=[]
    for sep in (",",";","\t"):
        line=next(csv.reader([head],delimiter=sep),[])
        if len(line)>=2:possible.append((sep,line))
    if len(possible)!=1:raise PublishedSourceError("ambiguous encounter matrix CSV delimiter")
    sep,headers=possible[0]
    n=0
    lengths=Counter()
    first_ids=set()
    duplicates=0
    blank=0
    for row in csv.reader(io.StringIO(text),delimiter=sep):
        if n==0 and row==headers:
            n+=1
            continue
        if n==0:raise PublishedSourceError("encounter header mismatch")
        n+=1
        lengths[len(row)]+=1
        if not row or not row[0].strip():blank+=1
        else:
            key=row[0].strip()
            if key in first_ids:duplicates+=1
            else:first_ids.add(key)
    n-=1
    if not n:raise PublishedSourceError("empty encounter matrix")
    if len(lengths)>1 or list(lengths)!=[len(headers)]:
        raise PublishedSourceError("ragged author encounter matrix row format")
    return {
        "rows":n,"columns":len(headers),
        "delimiter":"SEMICOLON" if sep==";" else "TAB" if sep=="\t" else "COMMA",
        "first_column_unique":duplicates==0 and blank==0,
        "first_column_duplicate_rows":duplicates,
        "first_column_blank_rows":blank,
        "first_column_distinct_nonblank":len(first_ids),
        "first_field_header":headers[0][:100],
        "first_eight_column_headers":[s[:80] for s in headers[:8]],
        "numbered_primary_columns_after_ID":len(headers)-1,
        "contains_spatial_coordinates":False,
        "effects_or_MNA_calculated":False,
    }


def run()->dict:
    meta=json.loads(_get(API).decode("utf-8"))
    if int(meta.get("id",-1))!=RECORD_ID:
        raise PublishedSourceError("Zenodo MOSA record drift")
    by_name={str(r.get("key") or ""):r for r in meta.get("files",[])}
    results={}
    for name in FILES:
        f=by_name.get(name)
        if f is None:
            raise PublishedSourceError("author original encounter matrix absent: "+name)
        url=str((f.get("links") or {}).get("self") or "")
        if not url.startswith("https://"):
            raise PublishedSourceError("author encounter matrix lacks HTTPS")
        raw=_get(url)
        if len(raw)!=int(f.get("size") or -1):
            raise PublishedSourceError("encounter matrix published size mismatch")
        checksum=str(f.get("checksum") or "").strip().lower()
        if ":" not in checksum:raise PublishedSourceError("published matrix has no checksum")
        alg,want=checksum.split(":",1)
        if alg not in ("md5","sha256") or hashlib.new(alg,raw).hexdigest()!=want:
            raise PublishedSourceError("encounter matrix MD5 mismatch")
        result=parse_encounter_headers(raw)
        result["source_file_md5"]=checksum
        result["published_bytes"]=len(raw)
        results[name]=result
    overall=sum(x["rows"] for x in results.values())
    return {
        "schema":"neon.external_mosa_author_encounter_identity_schema.v1",
        "status":"AUTHOR_CAPTURE_MATRIX_STRUCTURE_VERIFIED_NOT_INDIVIDUAL_ID_RESOLVED",
        "source":"Zenodo 10049811 original version, MD5 verified",
        "matrix_parts":results,
        "combined_matrix_rows":overall,
        "raw_MN_TOE_string_uniques":19818,
        "publication_MN_unique_individual_claim":19850,
        "matrix_rows_minus_published_MN_claim":overall-19850,
        "identity_mapping_to_original_TOE":False,
        "no_identity_split_or_merge":True,
        "MNA_W_B_and_ecological_slopes_opened":False,
        "further_gate":"Check author encounter matrices' first column and RMarkdown preprocessing to determine exactly which identities rows represent and whether they can reconcile the 19850 published MN individuals without introducing post-outcome repairs.",
    }


if __name__=="__main__":
    try:r=run()
    except (PublishedSourceError,RuntimeError,ValueError,OSError) as e:
        r={"schema":"neon.external_mosa_author_encounter_identity_schema.v1",
           "status":"STOP_AUTHOR_ENCOUNTER_SOURCE_OR_SCHEMA_ERROR",
           "diagnostic":str(e)[:500],
           "MNA_W_B_and_ecological_slopes_opened":False}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps(r,indent=2,sort_keys=True))
    if r["status"]!="AUTHOR_CAPTURE_MATRIX_STRUCTURE_VERIFIED_NOT_INDIVIDUAL_ID_RESOLVED":
        raise SystemExit(3)
