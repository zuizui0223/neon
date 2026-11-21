#!/usr/bin/env python3
"""Inspect original NEON RELEASE-2026 categorical fate codebook ONLY.

The main NEON loader's _inventory intentionally excludes metadata files.
This script queries original release package metadata without changing any
mammal biological cohort, downloads at most one source-validated static
categoricalCodes_10072 CSV, and extracts ONLY original 'fate' variable's
public documented controlled categories. Does NOT download animal rows,
open day2/3 reencounter responses, or reinterpret missing fate.
"""
from __future__ import annotations
import csv,io,json,os,re
from pathlib import Path

from analysis.run_multiscale_density_estimability_release2026_v3 import (
    _request_json,_download_one,_site_codes,
    PRODUCT_URL,QUERY_URL,TOKEN_ENV,PRODUCT,RELEASE,START,END,
)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_fate_official_categorical_codes_20261028.json"

def need(ok:bool,reason:str):
    if not ok:raise ValueError("NEON_RELEASE_FATE_CODEBOOK_SOURCE_STOP: "+reason)

def safe_controlled(label:str)->str:
    """Controlled-category metadata only, never identifiers or free text."""
    s=" ".join(str(label or "").split())
    if len(s)>90 or not re.fullmatch(r"[A-Za-z][A-Za-z0-9 ();,.'/_-]*",s):
        return "WITHHELD_NONCONTROLLED_CODE"
    # Do not display possible site, date, plot, animal, metadata provenance.
    if re.search(r"\d{3,}|(?:site|person|tagid|nightuid|plotid)",s,re.I):
        return "WITHHELD_NONCONTROLLED_CODE"
    return s

def run()->dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    need(bool(token),"original source permission absent")
    need((PRODUCT,RELEASE,START,END)==("DP1.10072.001","RELEASE-2026","2015-04","2026-09"),
         "original mammal release changed")
    sites=_site_codes(_request_json(PRODUCT_URL))
    query=_request_json(QUERY_URL,token=token,body={
        "productCode":PRODUCT,"siteCodes":sites,
        "startDateMonth":START,"endDateMonth":END,
        "release":RELEASE,"package":"basic","includeProvisional":False,
    })
    blocks=[b for b in query.get("data",{}).get("releases",[])
            if isinstance(b,dict) and b.get("release")==RELEASE]
    need(len(blocks)==1,"original official release packages unavailable")
    matches={}
    meta_table_types={}
    for pkg in blocks[0].get("packages",[]):
        if not isinstance(pkg,dict) or pkg.get("packageType")!="basic":continue
        for x in pkg.get("files",[]):
            if not isinstance(x,dict):continue
            name=str(x.get("name") or "")
            if "categoricalcodes_10072" in name.lower() and name.lower().endswith(".csv"):
                md5=str(x.get("md5") or "").lower()
                size=x.get("size")
                url=str(x.get("url") or "")
                need(len(md5)==32 and len(url)>5 and url.startswith("https://")
                     and isinstance(size,int) and not isinstance(size,bool)
                     and 0<size<=5000000,
                     "original controlled-code metadata source file lacking digest/size")
                key=(md5,size)
                matches[key]={"md5":md5,"size":size,"url":url,"name":name}
            elif "variables_10072" in name.lower():
                meta_table_types["variables_10072_present"] = True
    if not matches:
        return {
            "schema":"neon.macro.official_fate_categorical_metadata.v1",
            "status":"STOP_CATEGORICAL_CODEBOOK_NOT_IN_ORIGINAL_RELEASE_QUERY",
            "source_release":RELEASE,
            "official_same_release_metadata_inventory_scanned":True,
            "no_fate_category_invented":True,
            "original_firstnight_615_fate_results_not_reclassified":True,
            "animal_outcome_records_never_accessed":True,
        }
    # If multiple source codebooks are advertised, do NOT pick one that
    # gives a favorable biological interpretation. STOP until versioned.
    need(len(matches)==1,
         "more than one checksum-distinct categorical codebook in original release")
    row=next(iter(matches.values()))
    raw=_download_one(row,token)
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    fields=list(reader.fieldnames or [])
    need(bool(fields),"original controlled-code CSV has no schema")
    # field names depend on official NEON metadata version; whitelist broad
    # literal names, fail if ambiguity makes fate rows uninterpretable.
    candidates=[c for c in fields if c.lower() in
                {"fieldname","field","variable","variablename","field_name"}]
    if len(candidates)!=1:
        return {
            "schema":"neon.macro.official_fate_categorical_metadata.v1",
            "status":"STOP_OFFICIAL_CODEBOOK_FIELD_SCHEMA_UNRECOGNIZED",
            "csv_field_count":len(fields),
            "controlled_variable_field_match_count":len(candidates),
            "source_MD5_verified":True,
            "source_released_category_not_inferred":True,
            "original_fate_reencounter_effect_sealed":True,
        }
    var=candidates[0]
    selected=[rec for rec in reader if str(rec.get(var) or "").strip().lower()=="fate"]
    if not selected:
        return {
            "schema":"neon.macro.official_fate_categorical_metadata.v1",
            "status":"STOP_ORIGINAL_CATEGORICAL_FILE_HAS_NO_FATE_ROWS",
            "metadata_variable_column_recognized":True,
            "source_MD5_verified":True,
            "cannot_assume_blank_implies_released":True,
            "old_reencounter_results_unchanged":True,
        }
    # Original categorical CSV may have code/value vs category/description
    # columns. Surface only bounded controlled labels (no unknown text).
    allowed=set(candidates+[c for c in fields if c.lower() in {
        "code","category","value","description","codevalue","codedvalue",
        "displayvalue","categorycode","categoryname","categorydescription"}])
    fate_values=[]
    for rec in selected:
        fate_values.append({
            col:safe_controlled(rec.get(col,"")) for col in sorted(allowed)
            if col!=var
        })
    return {
        "schema":"neon.macro.official_fate_categorical_metadata.v1",
        "status":"ORIGINAL_OFFICIAL_FATE_CATEGORICAL_ROWS_VERIFIED",
        "source_release":RELEASE,
        "source_official_provider_MD5_and_file_size_verified":True,
        "number_of_provider_categorical_fate_rows":len(fate_values),
        "safe_fate_public_controlled_codes":fate_values,
        "pre_2017_and_2017plus_meanings_may_differ":True,
        "blank_fate_does_not_automatically_establish_live_release":True,
        "no_original_capture_rows_or_day2_3_reencounter_outcomes_opened":True,
        "no_source_site_dates_station_tag_genus_identifiers_exported":True,
    }

def main()->int:
    try:
        out=run();code=0
    except Exception as e:
        out={
            "schema":"neon.macro.official_fate_categorical_metadata.v1",
            "status":"STOP_OFFICIAL_FATE_CODEBOOK_INVARIANT",
            "error_class":type(e).__name__,
            "source_exception_and_identifiers_suppressed":True,
            "new_released_genus_reencounter_effect_not_opened":True,
        };code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return code
if __name__=="__main__":
    raise SystemExit(main())
