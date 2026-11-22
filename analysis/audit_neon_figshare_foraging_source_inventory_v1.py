#!/usr/bin/env python3
"""Source metadata only: original Figshare rodent RFID/seed resource datasets.

No raw data file requests, animal traits, seed choice, foraging responses,
learning models, capture-space claims, or individual/patch coordinates.
"""
from __future__ import annotations
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
import json,re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_figshare_foraging_source_inventory_v1.json"
ORIGINAL_SOURCES={
    21512436:{
        "role":"primary_2023_RFID_camera_seed_amount",
        "title_keyword":"Predation risk and personality",
        "landing":"https://doi.org/10.6084/m9.figshare.21512436",
        "original_paper_doi":"10.1002/ecs2.4377"
    },
    28207769:{
        "role":"secondary_2026_seed_finding_inventory_ONLY",
        "title_keyword":"Intraspecific and environmental variation",
        "landing":"https://doi.org/10.6084/m9.figshare.28207769",
        "original_paper_doi":"10.1002/ecy.70312"
    }
}
ENDPOINT="https://api.figshare.com/v2/articles"
META_MAX=1_000_000
MAX_SOURCE_FILES=50
PROTOCOL="docs/NEON_INDEPENDENT_FORAGING_RFID_SEED_SOURCE_GATE_20261121.md"

def gate(ok,why):
    if not ok:
        raise ValueError("NEON_FIGSHARE_SOURCE_STOP_"+why)

def validate_download_href(url):
    if not isinstance(url,str) or not url or len(url)>1024:
        return False
    p=urlsplit(url)
    return (
        p.scheme=="https" and p.username is None and p.password is None
        and p.hostname in {
            "figshare.com", "ndownloader.figshare.com","api.figshare.com",
            "s3-eu-west-1.amazonaws.com","ndownloader.figshare.com"
        }
        and not p.fragment
    )

def audit_article_meta(payload,expected_id,raw_digest=None):
    """Audit provider-level source inventory without biological content."""
    gate(isinstance(payload,dict),"ARTICLE_METADATA_NOT_OBJECT")
    gate(payload.get("id")==expected_id,"UNEXPECTED_ARTICLE_ID")
    source=ORIGINAL_SOURCES[expected_id]
    title=payload.get("title")
    gate(isinstance(title,str) and source["title_keyword"].lower() in title.lower(),
         "TITLE_ID_PROVENANCE_MISMATCH")
    doi=payload.get("doi") or ""
    gate(isinstance(doi,str),"SOURCE_DOI_NOT_STRING")
    gate(str(expected_id) in doi or not doi,"SOURCE_DOI_ARTICLE_ID_MISMATCH")
    fs=payload.get("files")
    gate(isinstance(fs,list) and 0<len(fs)<=MAX_SOURCE_FILES,
         "ORIGINAL_SOURCE_FILE_INVENTORY_EMPTY_OR_TOO_LARGE")
    names=set();ids=set();files=[]
    for f in fs:
        gate(isinstance(f,dict),"ORIGINAL_FILE_META_NOT_OBJECT")
        fid=f.get("id")
        name=f.get("name")
        size=f.get("size")
        gate(isinstance(fid,int) and fid>0 and fid not in ids,
             "ORIGINAL_DUPLICATE_OR_INVALID_FILE_ID")
        gate(isinstance(name,str) and 0<len(name)<=256 and
             "/" not in name and "\\" not in name and name not in names,
             "ORIGINAL_DUPLICATE_OR_UNSAFE_FILENAME")
        gate(isinstance(size,int) and size>=0,"ORIGINAL_INVALID_FILE_SIZE")
        ids.add(fid);names.add(name)
        md5=f.get("computed_md5") or f.get("supplied_md5") or f.get("md5")
        gate(md5 is None or (isinstance(md5,str) and
                             re.fullmatch(r"[0-9a-fA-F]{32}",md5) is not None),
             "ORIGINAL_INVALID_MD5_METADATA")
        href=f.get("download_url")
        if href is not None:
            gate(validate_download_href(href),"NONFIGSHARE_UNSAFE_PROVIDER_URL")
        files.append({
            "provider_file_id":fid,
            "original_filename":name,
            "published_size_bytes":size,
            "published_md5_if_any":md5 or "",
            "has_provider_https_download_href":bool(href),
            "original_file_suffix":(name.rsplit(".",1)[-1].lower() if "." in name else ""),
            # No URL itself: source ID + exact official metadata needed for Stage B.
        })
    return {
        "schema":"neon.public_figshare_foraging_original_metadata_inventory.v1",
        "status":"PROVIDER_FILE_INVENTORY_GO_METADATA_ONLY",
        "role":source["role"],
        "original_figshare_article_id":expected_id,
        "source_landing":source["landing"],
        "article_title_from_provider":title,
        "article_doi_from_provider":doi,
        "original_peer_reviewed_paper_doi":source["original_paper_doi"],
        "article_version_from_provider":payload.get("version"),
        "published_date_from_provider":payload.get("published_date"),
        "provider_meta_json_sha256":raw_digest,
        "original_file_count":len(files),
        "original_file_inventory":files,
        "maximum_original_file_size":max(f["published_size_bytes"] for f in files),
        "no_raw_biological_files_downloaded":True,
        "no_original_animal_ID_or_seed_response_observed":True,
        "not_a_proof_usable_joined_RFID_resource_patch_data":True,
        "not_an_independent_Neon_recurrence_replication":True,
    }

def get_meta(article_id):
    req=Request(f"{ENDPOINT}/{article_id}",headers={
        "Accept":"application/json",
        "User-Agent":"NEON-original-public-figshare-source-inventory/1.0"
    })
    try:
        with urlopen(req,timeout=35) as response:
            gate(getattr(response,"status",200)==200,"PROVIDER_METADATA_HTTP_STATUS")
            raw=response.read(META_MAX+1)
    except HTTPError as e:
        raise ValueError("NEON_FIGSHARE_SOURCE_STOP_HTTP_"+str(e.code)) from e
    except (URLError,TimeoutError) as e:
        raise ValueError("NEON_FIGSHARE_SOURCE_STOP_API_NETWORK_UNAVAILABLE") from e
    gate(0<len(raw)<=META_MAX,"PROVIDER_METADATA_MISSING_OR_OVERSIZED")
    gate(raw.lstrip().startswith(b"{"),"PROVIDER_RETURNED_HTML_OR_NOT_JSON")
    try:
        js=json.loads(raw)
    except (ValueError,UnicodeDecodeError):
        raise ValueError("NEON_FIGSHARE_SOURCE_STOP_INVALID_PROVIDER_JSON") from None
    return audit_article_meta(js,article_id,sha256(raw).hexdigest())

def run():
    results={}
    for ident in ORIGINAL_SOURCES:
        try:
            results[str(ident)]=get_meta(ident)
        except Exception as exc:
            results[str(ident)]={
                "status":"SOURCE_STOP_PROVIDER_METADATA_OR_IDENTIFICATION",
                "article_id":ident,"role":ORIGINAL_SOURCES[ident]["role"],
                "reason_code":str(exc)[:160],
                "no_original_biological_rows_opened":True
            }
    return {
        "schema":"neon.public_original_figshare_foraging_candidate_inventory.v1",
        "status":(
            "PRIMARY_PROVIDER_METADATA_GO" if
            results["21512436"]["status"]=="PROVIDER_FILE_INVENTORY_GO_METADATA_ONLY"
            else "PRIMARY_PROVIDER_METADATA_STOP"),
        "original_sources":results,
        "candidate_order_locked_before_metadata_fetch":True,
        "first_selected_article_ID":21512436,
        "secondary_dataset_inventory_only_not_fallback_outcome":True,
        "no_rfid_camera_seed_choice_or_individual_data_opened":True,
        "no_NEON_Portal_Finland_Structural_original_effects_recomputed":True,
        "one_unified_NEON_manuscript_DRAFT_SUBMISSION_HOLD":True,
        "protocol":PROTOCOL,
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
    }

def main():
    result=run()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    # Metadata network STOP is a recorded source decision, not a false biology GO.
    return 0

if __name__=="__main__":
    raise SystemExit(main())
