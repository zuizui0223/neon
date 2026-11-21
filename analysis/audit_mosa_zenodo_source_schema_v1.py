#!/usr/bin/env python3
"""Effect-blind source-byte and schema validation for independent MOSA rodents.

Dataset: Leirs et al. 2023 Scientific Data, 29 years of monthly 3-night
trapping in Morogoro, Tanzania. Zenodo record 10049811, CC-BY.

NO W/B, abundance trends/slopes, territoriality, site-level density, or
individual geographic positions are calculated. This first step asks whether
the 49,216-capture raw CSV is genuinely accessible, checksum-valid, and has
the fields needed for later *separately frozen* structural estimability.
Reject bot-challenge HTML as scientific data (see Borneo false-green audit).
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import os
import http.client
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/mosa_external_schema_v1.json"
RECORD_ID=10049811
API=f"https://zenodo.org/api/records/{RECORD_ID}"
DATASET_DOI="10.5281/zenodo.10049811"
EXPECTED_FILENAME="mosa_Feb2023_Flags.csv"
# Immutable Zenodo version 10049811 inventory, pinned before raw ecological
# capture occasions or any spatial or abundance response are inspected.
EXPECTED_PUBLISHED_BYTES=2849668
EXPECTED_PUBLISHED_MD5="12c04902947b91922c3f6c98760ecb54"
EXPECTED_PUBLISHED_CAPTURE_RECORDS=49216
AGENT="neon-ecology-independent-MOSA-byte-schema/1.0"


class PublishedSourceError(RuntimeError):
    pass


def _get(url:str)->bytes:
    """Retry transient Zenodo transport only; checksum validation stays downstream.

    401/403 and unsupported responses are NOT retried or silently replaced.
    """
    req=urllib.request.Request(
        url,headers={"User-Agent":AGENT,"Accept":"application/json, text/csv, */*"}
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=150) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt==2:
                raise
        except (http.client.IncompleteRead, ConnectionResetError, TimeoutError,
                urllib.error.URLError):
            if attempt==2:
                raise
        time.sleep(1.5*(attempt+1))
    raise AssertionError("unexpected Zenodo retry terminal state")


def select_datafile(meta:dict)->dict:
    if not isinstance(meta,dict) or not isinstance(meta.get("files"),list):
        raise PublishedSourceError("Zenodo record has no verifiable file inventory")
    candidates=[
        f for f in meta["files"]
        if str(f.get("key") or "").lower()==EXPECTED_FILENAME.lower()
    ]
    if not candidates:
        candidates=[
            f for f in meta["files"]
            if (str(f.get("key") or "").lower().endswith(".csv") and
                "mosa" in str(f.get("key") or "").lower() and
                "flag" in str(f.get("key") or "").lower())
        ]
    if len(candidates)!=1:
        raise PublishedSourceError(
            "Expected one raw MOSA capture CSV; candidates="+str(len(candidates)))
    f=candidates[0]
    if f.get("size")!=EXPECTED_PUBLISHED_BYTES or str(f.get("checksum") or "").lower()!=(
        "md5:"+EXPECTED_PUBLISHED_MD5):
        raise PublishedSourceError(
            "MOSA fixed original Zenodo bytes/digest changed; revalidate before any effects")
    url=(f.get("links") or {}).get("self") or (f.get("links") or {}).get("content")
    if not isinstance(url,str) or not url.startswith("https://"):
        raise PublishedSourceError("Zenodo file has no secure download URL")
    return f


def validate_source_bytes(raw:bytes,file:dict)->dict:
    name=str(file.get("key") or "")
    head=raw[:3072].lstrip().lower()
    if any(k in head for k in (
        b"<!doctype html",b"<html",b"<title>validating",
        b"cloudflare",b"captcha",b"within.website")):
        raise PublishedSourceError("HTML challenge instead of scientific capture CSV")
    size=file.get("size")
    if isinstance(size,bool) or not isinstance(size,int) or size<1000:
        raise PublishedSourceError("Missing valid positive Zenodo source file size")
    if len(raw)!=size:
        raise PublishedSourceError(f"Source size mismatch, got {len(raw)} expected {size}")
    declared=str(file.get("checksum") or "").lower().strip()
    if ":" not in declared:
        raise PublishedSourceError("Zenodo capture file is missing published checksum")
    algorithm,want=declared.split(":",1)
    if algorithm not in ("md5","sha256"):
        raise PublishedSourceError("Unsupported published checksum algorithm")
    actual=hashlib.new(algorithm,raw).hexdigest()
    if actual!=want:
        raise PublishedSourceError("MOSA file checksum mismatch")
    # The archived field notebook CSV may use a legacy text encoding.
    # Decoding fallback never changes the checksum-verified source bytes.
    encoding="utf-8-sig"
    try:
        text=raw.decode(encoding)
    except UnicodeDecodeError:
        encoding="cp1252"
        try:
            text=raw.decode(encoding)
        except UnicodeDecodeError:
            # Fallback for older Latin-1 CMR exports containing cp1252-
            # undefined bytes. Published checksum and source CSV structure
            # remain mandatory, so this cannot silently accept arbitrary HTML.
            encoding="latin-1"
            text=raw.decode(encoding)
    if chr(0) in text or chr(0xfffd) in text:
        raise PublishedSourceError("Binary or replacement characters in capture CSV")
    # Legacy Excel/European field-data exports sometimes use semicolon or
    # tab-delimited files even when the published extension is .csv.
    # Select ONLY by the outcome-blind header schema, before reading rows.
    delimiters=(",", ";", chr(9))
    choices=[]
    header_text=text.splitlines()[0] if text.splitlines() else ""
    for sep in delimiters:
        try:
            fields0=next(csv.reader([header_text],delimiter=sep))
        except (csv.Error, StopIteration):
            continue
        if 6<=len(fields0)<=200 and all(
            name and "<" not in name and ">" not in name for name in fields0
        ):
            choices.append((sep,fields0))
    if len(choices)!=1:
        raise PublishedSourceError(
            "Invalid/ambiguous capture CSV header delimiters; candidate counts="
            +str(len(choices))
        )
    delimiter=choices[0][0]
    reader=csv.DictReader(io.StringIO(text),delimiter=delimiter)
    fields=list(reader.fieldnames or [])
    count=0
    invalid_rows=0
    for row in reader:
        count+=1
        if None in row: invalid_rows+=1
    if count<1000 or invalid_rows:
        raise PublishedSourceError(f"implausible source rows={count}, ragged={invalid_rows}")
    # Do not silently accept a structurally plausible but incomplete or
    # wrong-version MOSA extract when the published 2023 source should
    # contain exactly 49,216 capture rows.
    if name.lower()==EXPECTED_FILENAME.lower() and count!=EXPECTED_PUBLISHED_CAPTURE_RECORDS:
        raise PublishedSourceError(
            f"Original MOSA capture rows differ from published {EXPECTED_PUBLISHED_CAPTURE_RECORDS}: {count}")
    return {
        "file_name":name,
        "verified_checksum":declared,
        "verified_byte_count":len(raw),
        "raw_capture_records":count,
        "text_encoding":encoding,
        "delimiter_type":("TAB" if delimiter==chr(9) else "SEMICOLON" if delimiter==";" else "COMMA"),
        "column_headers":fields,
        "csv_field_count":len(fields),
        "all_csv_rows_structurally_well_formed":True,
        "schema_field_names_only":True,
    }


def run()->dict:
    metadata=json.loads(_get(API).decode("utf-8"))
    if int(metadata.get("id",-1))!=RECORD_ID:
        raise PublishedSourceError("Zenodo record identity drift")
    file=select_datafile(metadata)
    raw=_get(str((file.get("links") or {}).get("self") or
                 (file.get("links") or {}).get("content")))
    validated=validate_source_bytes(raw,file)
    return {
        "schema":"neon.external_mosa_source_schema_v1",
        "status":"ACCESS_AND_PUBLISHED_CHECKSUM_PASS_SCHEMA_ONLY",
        "dataset_record":RECORD_ID,
        "doi":DATASET_DOI,
        "dataset_title":metadata.get("metadata",{}).get("title"),
        "published_license":"CC-BY (reported by Leirs et al., 2023)",
        "file":validated,
        "expected_protocol":{
            "primary_occasions":"monthly",
            "secondary_occasions":"3 consecutive trap nights",
            "lattice":"30x10 stations with 10m spacing",
            "study_sites":1,
            "source_years":"March 1994 to February 2023",
        },
        "individual_and_date_fields_mapped":False,
        "three_night_repeat_support_tested":False,
        "MNA_or_MNKA_opened":False,
        "space_use_W_B_or_density_slopes_opened":False,
        "NEON_mammal_genera_generalization_claimed":False,
        "next_gate":"Declare exact individual, station, species, month and night column mapping and capture status before using any ecological outcomes; one-site MOSA cannot reproduce multi-genus or multi-site significance tests."
    }


if __name__=="__main__":
    try:
        result=run()
    except (PublishedSourceError,urllib.error.URLError,ValueError,RuntimeError,TimeoutError) as e:
        result={
            "schema":"neon.external_mosa_source_schema_v1",
            "status":"STOP_MOSA_SOURCE_BYTES_OR_SCHEMA_NOT_VERIFIED",
            "diagnostic":str(e)[:500],
            "space_use_W_B_or_density_slopes_opened":False,
            "biological_replication_claimed":False,
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    if result["status"]!="ACCESS_AND_PUBLISHED_CHECKSUM_PASS_SCHEMA_ONLY":
        raise SystemExit(3)
