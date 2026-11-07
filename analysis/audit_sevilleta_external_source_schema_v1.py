#!/usr/bin/env python3
"""Effect-blind independent Sevilleta LTER rodent source-byte discovery.

Newsome (2016) SEV8 archive knb-lter-sev.8.297972 / DOI:
10.6073/pasta/142d2a1c7a1a6397fb56a47b5817bf1d, mirrored at UNM.
Metadata describes eight sites, three trap webs/site, three consecutive
nights, 145 web stakes and 148 traps/web (1989–2015 source version).

This audit accesses a previously identified exact public raw TXT link,
refuses bot/HTML, checks row schema and records its checksum for later
source-version locking. It NEVER calculates coordinates, abundance MNA,
within-animal W, among-animal B, or density effects.

The radial trapping web is NOT interchangeable with NEON's 10×10 grid.
A 10m square-lattice assumption would be scientifically incorrect.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

OUT=Path("build/sevilleta_SEV8_source_schema_v1.json")
URL=("https://digitalrepository.unm.edu/cgi/viewcontent.cgi?"
     "article=1280&context=lter_sev_data&filename=3&type=additional")
PACKAGE="knb-lter-sev.8.297972"
DOI="10.6073/pasta/142d2a1c7a1a6397fb56a47b5817bf1d"


def inspect_sev8_bytes(raw: bytes,*,minimum_bytes:int=100000)->dict:
    if len(raw)<minimum_bytes:
        raise ValueError("Sevilleta source unexpectedly short or incomplete")
    head=raw[:4096].lstrip().lower()
    if any(x in head for x in (
        b"<!doctype html", b"<html", b"captcha",
        b"cloudflare",b"<title>validating",b"within.website"
    )):
        raise ValueError("HTML verification page is not a scientific data table")
    try:text=raw.decode("utf-8-sig");encoding="utf-8-sig"
    except UnicodeDecodeError:
        text=raw.decode("cp1252");encoding="cp1252"
    if "\x00" in text:
        raise ValueError("NUL byte in putative SEV8 source")
    # Only the header and shape; the original data rows are not disclosed.
    candidates=[]
    first=text.splitlines()[0] if text.splitlines() else ""
    for delim,label in (("\t","TAB"),(",","COMMA"),(";","SEMICOLON")):
        header=next(csv.reader([first],delimiter=delim),[])
        if len(header)>=6 and all(h.strip() and "<" not in h and ">" not in h for h in header):
            candidates.append((delim,label,header))
    if len(candidates)!=1:
        raise ValueError("Sevilleta capture table delimiter/header ambiguous")
    delimiter,label,headers=candidates[0]
    reader=csv.reader(io.StringIO(text),delimiter=delimiter)
    if next(reader,None)!=headers:
        raise ValueError("Sevilleta table header not reproducible")
    n=0
    incomplete=0
    for row in reader:
        if not any(c.strip() for c in row):
            continue
        n+=1
        if len(row)!=len(headers):
            incomplete+=1
    if incomplete:raise ValueError(f"ragged table records: {incomplete}")
    if not n:raise ValueError("No Sevilleta trapping observations")
    return {
        "schema":"neon.SEV8_external_source_byte_schema.v1",
        "status":"UNPINNED_PUBLISHED_MIRROR_BYTES_PARSEABLE_SCHEMA_ONLY",
        "source_bytes":len(raw),
        "source_SHA256":hashlib.sha256(raw).hexdigest(),
        "distinct_source_sha256_bytes":64,
        "record_encoding":encoding,
        "delimiter":label,
        "headers":headers,
        "header_count":len(headers),
        "row_count":n,
        "raw_source_MD5_published_independently_verified":False,
        "tag_semantics_unverified":True,
        "stake_spatial_geometry_unverified":True,
        "three_night_within_individual_support_unverified":True,
        "individual_W_B_opened":False,
        "genus_MNA_or_density_effect_opened":False,
        "independent_biological_confirmation":False,
        "interpretation":"A table parsed from the versioned UNM mirror is not yet an official EDI byte-checksum validation or a supported repeated-animal response cohort."
    }


def run()->dict:
    req=urllib.request.Request(
        URL,headers={"User-Agent":"NEON-independent-Sevilleta-schema/1.0",
                     "Accept":"text/plain,text/tab-separated-values,*/*"},
    )
    with urllib.request.urlopen(req,timeout=150) as response:
        body=response.read()
    result=inspect_sev8_bytes(body)
    result["source_dataset"]=PACKAGE
    result["source_DOI"]=DOI
    result["source_URL"]=URL
    result["reported_metadata_design"]={
        "sites":8,"webs_per_site":3,
        "web_spokes":12,"stations_per_web":145,
        "traps_per_web":148,
        "sampling":"three consecutive nights in spring and fall",
        "geometry":"radial webs; NOT rectangular NEON lattice"
    }
    return result


if __name__=="__main__":
    try:r=run()
    except (RuntimeError,ValueError,UnicodeError,urllib.error.URLError,TimeoutError) as exc:
        r={
            "schema":"neon.SEV8_external_source_byte_schema.v1",
            "status":"STOP_SEV8_SOURCE_BYTES_OR_SCHEMA_UNVERIFIED",
            "source_DOI":DOI,
            "diagnostic":str(exc)[:400],
            "individual_W_B_opened":False,
            "genus_MNA_or_density_effect_opened":False
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps(r,indent=2,sort_keys=True))
    if r["status"]!="UNPINNED_PUBLISHED_MIRROR_BYTES_PARSEABLE_SCHEMA_ONLY":
        raise SystemExit(3)
