#!/usr/bin/env python3
"""Read authors' checksum-verified MOSA RMarkdown ID processing, effects sealed.

The publication reports 19,850 M. natalensis individuals versus 19,818
verbatim stripped TOE strings (MD5-verified original). This audit inspects
the AUTHORS' supplied processing/source schema for reproducible identity
corrections. It neither splits tags nor constructs MNA, W/B or density slopes.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from analysis.audit_mosa_zenodo_source_schema_v1 import (
    API, RECORD_ID, _get, PublishedSourceError,
)

OUT=Path("build/mosa_published_identity_processing_v1.json")
PREFERRED=(
    "2_markdown Processing data.Rmd",
    "3_markdown Densities and survival analyses.Rmd",
)
MATCH=re.compile(
    r"\b(toe|toe.id|toecode|individual|unique|duplicat|split|prefix|"
    r"reuse|correction|recaptur|encounter|n_distinct|group_by|MNA|alive)\b",
    re.IGNORECASE,
)

def inspect_lines(text:str,*,max_lines=65):
    entries=[]
    lines=text.splitlines()
    for i,line in enumerate(lines):
        if not MATCH.search(line):continue
        s=line.strip()
        if not s:continue
        # Avoid emitting tag-level values; RMarkdown code/explanatory comments
        # are read-only public methodological material.
        entries.append({
            "line":i+1,
            "snippet":s[:200],
            "trimmed":len(s)>200,
        })
    return {"total_lines":len(lines),"matching_lines":len(entries),
            "excerpts":entries[:max_lines]}

def run():
    meta=json.loads(_get(API).decode("utf-8"))
    if int(meta.get("id",-1))!=RECORD_ID:
        raise PublishedSourceError("Unexpected original MOSA record identity")
    by_name={str(f.get("key") or ""):f for f in meta.get("files",[])}
    inspected={}
    for key in PREFERRED:
        file=by_name.get(key)
        if file is None:
            raise PublishedSourceError("Published MOSA processing Rmd unavailable: "+key)
        url=str((file.get("links") or {}).get("self") or "")
        if not url.startswith("https://"):
            raise PublishedSourceError("MOSA RMarkdown file lacks published HTTPS source")
        raw=_get(url)
        checksum=str(file.get("checksum") or "").lower()
        size=file.get("size")
        if len(raw)!=size:
            raise PublishedSourceError("Published identity script bytes mismatch: "+key)
        if ":" not in checksum or checksum.split(":",1)[0] not in ("md5","sha256"):
            raise PublishedSourceError("RMarkdown checksum schema invalid: "+key)
        alg,expected=checksum.split(":",1)
        if hashlib.new(alg,raw).hexdigest()!=expected:
            raise PublishedSourceError("RMarkdown identity script digest differs: "+key)
        text=raw.decode("utf-8-sig",errors="replace")
        inspected[key]={
            "byte_count":len(raw),
            "published_checksum_verified":True,
            "sha256":hashlib.sha256(raw).hexdigest(),
            "source_text_read_for_individual_identity_only":True,
            **inspect_lines(text),
        }
    encounter_files=[]
    for f in meta.get("files",[]):
        key=str(f.get("key") or "")
        if key.startswith("C_primary_secondary_capture_") and key.lower().endswith(".csv"):
            encounter_files.append({
                "file":key,
                "size":f.get("size"),
                "checksum":f.get("checksum"),
                "not_opened":True,
            })
    if len(encounter_files)<2:
        raise PublishedSourceError("No published MOSA derived encounter matrix for reconciliation")
    return {
        "schema":"neon.external_mosa_author_identity_script_audit.v1",
        "status":"AUTHOR_CORRECTION_SCRIPTS_VERIFIED_IDENTITY_RECONCILIATION_PENDING",
        "publication":"Leirs et al. Scientific Data (2023) 10:798",
        "zenodo_record":RECORD_ID,
        "raw_dataset_MN_TOE_distinct":19818,
        "published_MN_individuals":19850,
        "difference":32,
        "source_scripts":inspected,
        "published_encounter_matrices":encounter_files,
        "MNA_W_B_spatial_effects_opened":False,
        "no_individual_identity_reassignment":True,
        "next_gate":"Reconcile unique MARKED animals using the author's own processing code and precomputed encounter-matrix identity columns before opening MNA or spatial responses."
    }

if __name__=="__main__":
    try:r=run()
    except (PublishedSourceError,RuntimeError,ValueError,OSError) as e:
        r={"schema":"neon.external_mosa_author_identity_script_audit.v1",
           "status":"STOP_AUTHOR_PROCESSING_SOURCE_UNVERIFIED",
           "diagnostic":str(e)[:500],"MNA_W_B_spatial_effects_opened":False}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps(r,indent=2,sort_keys=True))
    if r["status"]!="AUTHOR_CORRECTION_SCRIPTS_VERIFIED_IDENTITY_RECONCILIATION_PENDING":
        raise SystemExit(3)
