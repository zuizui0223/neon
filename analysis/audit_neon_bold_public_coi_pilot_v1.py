#!/usr/bin/env python3
"""Read-only BOLD v5 single NEON Peromyscus sample public-API connectivity.

Only one morphologically identified archival BOLD sample ID is selected,
without W/B or new ecological outcomes. NEVER print/store sample IDs, BOLD
query_id, sequences, specimens, locations or accession numbers.
This is not a genetic species identification or misidentification audit.
"""
from __future__ import annotations

import csv
import io
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

from analysis.audit_neon_barcode_schema_v1 import (
    BARCODE_PRODUCT, START, END, extract_inventory, classify_file
)
from analysis.audit_multiscale_density_mnka_variation_v1 import _taxonomy
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    RELEASE, TOKEN_ENV, QUERY_URL, _request_json, _site_codes, _download_many,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"build/neon_bold_public_coi_pilot_v1.json"
HOST = "https://portal.boldsystems.org"
MAX_RESPONSE_BYTES = 5_000_000


def select_source_candidate(
    chosen_source_metadata: list[dict],
    raw_sources: list[bytes],
    genus_by_taxon: dict[str,str],
) -> tuple[str, dict]:
    """Lexicographic source-ID choice, no ecological/COI result selection."""
    options=[]
    seen=0
    for meta,raw in zip(chosen_source_metadata,raw_sources):
        reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
        fields=set(reader.fieldnames or [])
        if not {"sampleID","taxonID","genus"}.issubset(fields):
            raise RuntimeError("original BOLD taxonomy source field drift")
        for row in reader:
            sample=str(row.get("sampleID") or "").strip()
            taxon=str(row.get("taxonID") or "").strip()
            genus=str(row.get("genus") or "").strip()
            if not sample or sample.upper() in {"NA","N/A","NULL"} or "|" in sample:
                continue
            if genus.casefold()!="peromyscus" or genus_by_taxon.get(taxon)!="Peromyscus":
                continue
            seen+=1
            options.append(sample)
    if not options:
        raise RuntimeError("No Peromyscus archived source sample in preselected first files")
    return sorted(set(options))[0],{
        "candidate_archive_rows":seen,
        "unique_candidate_sampleIDs":len(set(options)),
        "selection_rule":"first source month per site, then lexicographically first distinct Peromyscus sampleID",
        "no_sample_ID_returned_in_receipt":True,
    }


def choose_pilot_files(barcode_inventory: list[dict]) -> list[dict]:
    """First source file per site with BOLD taxonomy, fixed before outcomes."""
    rows=[x for x in barcode_inventory
          if classify_file(x["name"])=="mam_BOLDtaxonomy"]
    by_site=defaultdict(list)
    for row in rows:
        by_site[row["site"]].append(row)
    return [
        sorted(rows,key=lambda x:(x["month"],x["name"]))[0]
        for _site,rows in sorted(by_site.items())
    ]


def public_json(stage: str, path: str, query: dict | None=None) -> dict | list:
    if stage not in {"preprocessor","query","documents"}:
        raise ValueError("unknown BOLD API stage")
    path_part=path + ("?"+urllib.parse.urlencode(query) if query else "")
    url=HOST + path_part
    req=urllib.request.Request(
        url,headers={
            "User-Agent":"neon-source-barcoding-pilot/1.0 (scientific source audit)",
            "Accept":"application/json",
        },method="GET",
    )
    try:
        with urllib.request.urlopen(req,timeout=60) as response:
            actual=response.geturl()
            if not actual.startswith(HOST+"/"):
                raise RuntimeError("untrusted redirect from BOLD host")
            content=response.read(MAX_RESPONSE_BYTES+1)
    except urllib.error.HTTPError as exc:
        # Never expose a URL including a source sampleID/token.
        raise RuntimeError(f"BOLD {stage} API HTTP status {exc.code}") from None
    except (urllib.error.URLError,TimeoutError,OSError) as exc:
        raise RuntimeError(f"BOLD {stage} transport failure: {type(exc).__name__}") from None
    if len(content)>MAX_RESPONSE_BYTES:
        raise RuntimeError(f"BOLD {stage} response exceeds fixed pilot byte cap")
    try:
        result=json.loads(content.decode("utf-8"))
    except (ValueError,UnicodeDecodeError):
        raise RuntimeError(f"BOLD {stage} did not return JSON") from None
    if not isinstance(result,(dict,list)):
        raise RuntimeError(f"BOLD {stage} returned non-document root type")
    return result


def _public_record_summary(data: dict | list, queried_sample: str) -> dict:
    if isinstance(data,list):
        records=data
        root_keys=[]
    else:
        root_keys=sorted(data)[:20]
        records=[]
        for k in ("documents","records","data","results"):
            if isinstance(data.get(k),list):
                records=data[k]
                break
        if not records and any(k in data for k in ("sampleid","processid","nuc")):
            records=[data]
    # Look only at property name shapes and whether the exact source ID is
    # represented; NEVER emit the identifier or any sequence/taxon value.
    string_dump=json.dumps(data,sort_keys=True)
    if len(string_dump)>MAX_RESPONSE_BYTES:
        raise RuntimeError("unexpected oversized JSON after parse")
    sequence_name_count=0
    marker_name_count=0
    def count_key_names(obj,depth=0):
        nonlocal sequence_name_count,marker_name_count
        if depth>16:return
        if isinstance(obj,dict):
            for k,v in obj.items():
                kn=str(k).casefold()
                if kn in {"nuc","nucleotides","sequence","nucleotide_sequence","nucraw"}:
                    sequence_name_count+=1
                if "marker" in kn or "genbank" in kn or "insdc" in kn:
                    marker_name_count+=1
                if isinstance(v,(dict,list)):count_key_names(v,depth+1)
        elif isinstance(obj,list):
            for v in obj[:30]:
                if isinstance(v,(dict,list)):count_key_names(v,depth+1)
    count_key_names(data)
    return {
        "root_metadata_keys":root_keys,
        "parsed_document_count_guess":len(records),
        "exact_query_sample_value_appeared_in_public_record":queried_sample in string_dump,
        "possible_nucleotide_sequence_property_count":sequence_name_count,
        "possible_marker_or_accession_property_count":marker_name_count,
        "no_sequence_or_identification_exported":True,
    }


def run() -> dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    if not token:raise RuntimeError("existing authorized NEON_API_TOKEN required")
    if RELEASE!="RELEASE-2026":raise RuntimeError("release drift")
    genus_by_taxon=_taxonomy()[1]
    product=_request_json(
        f"https://data.neonscience.org/api/v0/products/{BARCODE_PRODUCT}"
    )
    sites=_site_codes(product)
    payload=_request_json(QUERY_URL,token=token,body={
        "productCode":BARCODE_PRODUCT,"siteCodes":sites,
        "startDateMonth":START,"endDateMonth":END,
        "release":RELEASE,"package":"basic","includeProvisional":False,
    })
    manifest=extract_inventory(payload)
    if len(manifest)!=3536:
        raise RuntimeError("original release BOLD manifest different from source-verified receipt")
    source_files=choose_pilot_files(manifest)
    source_bytes=_download_many(source_files,token,max_workers=5)
    sample,choice=select_source_candidate(source_files,source_bytes,genus_by_taxon)

    triplet="ids:sampleid:"+sample
    # Do not output any of the three URLs, their source identifier or query_id.
    prep=public_json("preprocessor","/api/query/preprocessor",{"query":triplet})
    query=public_json("query","/api/query",{"query":triplet,"extent":"full"})
    query_id=query.get("query_id") if isinstance(query,dict) else None
    if not isinstance(query_id,str) or not query_id:
        raise RuntimeError("BOLD v5 query has no valid private ephemeral query_id")
    clean_token=urllib.parse.quote(query_id,safe="")
    docs=public_json("documents",f"/api/documents/{clean_token}/download",
                     {"format":"json"})
    summary=_public_record_summary(docs,sample)
    state=(
        "BOLD_V5_SINGLE_SAMPLE_PUBLIC_RECORD_PROBE_PASS_NOT_SPECIES_VALIDATED"
        if summary["exact_query_sample_value_appeared_in_public_record"]
        else "STOP_BOLD_PUBLIC_RECORD_HAS_NO_EXACT_ARCHIVAL_SAMPLE_MATCH"
    )
    return {
        "schema":"neon.bold_v5_one_sample_readonly_api_probe.v1",
        "status":state,
        "original_neon_release":"RELEASE-2026",
        "NEON_product":BARCODE_PRODUCT,
        "archived_source_taxonomy_files_checked":len(source_files),
        "source_candidate_selection":choice,
        "BOLD_v5_three_stages_completed":True,
        "public_record_shape":summary,
        "preprocessor_result_was_JSON":True,
        "query_result_was_JSON":True,
        "sequence_quality_evaluated":False,
        "species_by_COI_confirmed":False,
        "genetic_error_rate_estimated":False,
        "raw_sample_ID_query_id_sequence_or_taxon_exported":False,
        "W_B_or_crossscale_effects_opened":False,
        "original_8genus_guard":"FAILED_5_OF_8",
        "MOSA_effects":"SEALED",
    }


def main() -> int:
    try:
        out=run()
    except Exception as exc:
        out={
            "schema":"neon.bold_v5_one_sample_readonly_api_probe.v1",
            "status":"STOP_BOLD_PUBLIC_ONE_SAMPLE_PROBE",
            "sanitized_diagnostic":(
                str(exc)[:220] if str(exc).startswith(("BOLD ","No Peromyscus","original","release","existing","untrusted","unexpected"))
                else type(exc).__name__
            ),
            "raw_sample_ID_query_id_sequence_or_taxon_exported":False,
            "W_B_or_crossscale_effects_opened":False,
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0 if out["status"]=="BOLD_V5_SINGLE_SAMPLE_PUBLIC_RECORD_PROBE_PASS_NOT_SPECIES_VALIDATED" else 3

if __name__=="__main__":
    raise SystemExit(main())
