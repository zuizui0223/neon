#!/usr/bin/env python3
"""Published 2025 prairie-vole direct-ProxLogs and trapping source HEADER gate.

Read Figshare project article metadata and exact provider MD5-verified public
file bytes. Never output any individual animal IDs or observed dyad counts.
Untrusted raw data does not authorize fitting an outcome or promoting an
already-published network comparison into new ecological evidence.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timezone
from io import StringIO
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request,urlopen
import csv,hashlib,json

PROJECT_ID=228462
BASE="https://api.figshare.com/v2"
PIN={
  "collar_ids.csv":(27855279,50635479,1550),
  "proxlog_summary.csv":(27855339,50636031,2378),
  "full_voles_trap.csv":(27855354,50636346,185698),
  "prox_full_noduplicates.csv":(27855393,50636655,1973533),
  "rfid_trap_network_data_method.csv":(27855438,50636994,93557),
  "collar_success_long.csv":(27855444,50637150,862),
  "collar_success_adj.csv":(27855459,50637243,117),
  "global_ids.csv":(27855462,50637252,7174),
  "JoM_analyses.R":(27855516,50637315,23005),
}
META_MAX=600000
OUT=Path(__file__).resolve().parents[1]/"build/neon_prairie_vole_logger_figshare_file_headers_20261115.json"
PHASE="PUBLIC_ORIGINAL_ARTICLE_METADATA"
STAGES={"PUBLIC_ORIGINAL_ARTICLE_METADATA","ORIGINAL_FILE_MD5_VERIFICATION","CSV_FILE_HEADER_AUDIT"}

def fetch_json(uri):
    if not uri.startswith(BASE+"/articles/"):
        raise ValueError("Unrecognized public original article API")
    req=Request(uri,headers={"Accept":"application/json","User-Agent":"NEON-open-reproducibility-source/1"})
    with urlopen(req,timeout=60) as resp:
        data=resp.read(META_MAX+1)
    if len(data)>META_MAX:raise ValueError("Figshare article response too large")
    return json.loads(data.decode("utf-8"))

def check_filename_file(url,expected_id,maxbytes):
    urlp=urlparse(url)
    if urlp.scheme!="https" or urlp.hostname not in (
        "api.figshare.com","ndownloader.figshare.com","figshare.com"
    ):
        raise ValueError("File not on original Figshare public download host")
    if not (str(expected_id) in urlp.path):
        raise ValueError("Provider file ID not in official download path")
    request=Request(url,headers={"User-Agent":"NEON-mammal-public-source-reanalysis/1"})
    with urlopen(request,timeout=110) as resp:
        data=resp.read(maxbytes+1)
    if len(data)>maxbytes:raise ValueError("Original file exceeds frozen file size")
    return data

def csv_headers_and_nrows(raw):
    try:s=raw.decode("utf-8-sig")
    except UnicodeDecodeError as ex:raise ValueError("Public CSV source is not UTF-8") from ex
    headerline=s.splitlines()[0] if s.splitlines() else ""
    delimiters=[",","\t",";"]
    d=max(delimiters,key=headerline.count)
    if headerline.count(d)<1:raise ValueError("Unknown published CSV separator")
    reader=csv.reader(StringIO(s),delimiter=d)
    header=next(reader,[])
    if len(header)<2 or len(set(header))!=len(header):
        raise ValueError("Original CSV missing/duplicate headers")
    n=0
    for row in reader:
        if not row or all(not x.strip() for x in row):
            continue
        if len(row)!=len(header):
            raise ValueError("Original public CSV ragged row schema")
        n+=1
    return header,n,d

def run():
    global PHASE
    allfiles=[]
    for name,(article,file_id,bytesize) in PIN.items():
        x=fetch_json(f"{BASE}/articles/{article}")
        if x.get("id")!=article or not isinstance(x.get("files"),list):
            raise ValueError("Original published article identity drift")
        original=[f for f in x["files"] if f.get("id")==file_id and f.get("name")==name]
        if len(original)!=1:
            raise ValueError("Original name/ID Figshare correspondence drift")
        f=original[0]
        if f.get("size")!=bytesize or f.get("is_link_only") is True:
            raise ValueError("Original published immutable source size drift")
        check_md5=f.get("computed_md5") or f.get("supplied_md5")
        if not isinstance(check_md5,str) or len(check_md5)!=32:
            raise ValueError("Original provider MD5 missing")
        if f.get("supplied_md5") and f.get("computed_md5"):
            if f["supplied_md5"].lower()!=f["computed_md5"].lower():
                raise ValueError("Original public provider MD5 disagreements")
        allfiles.append((name,article,file_id,bytesize,check_md5,f.get("download_url")))
    PHASE="ORIGINAL_FILE_MD5_VERIFICATION"
    summary=[]
    for name,article,file_id,bytesize,md5,uri in allfiles:
        if not isinstance(uri,str):raise ValueError("Original provider download link missing")
        data=check_filename_file(uri,file_id,bytesize)
        if len(data)!=bytesize or hashlib.md5(data).hexdigest()!=md5.lower():
            raise ValueError("Original Figshare file MD5/size disagree")
        entry={
            "file_name":name,
            "original_article_id":article,
            "original_file_id":file_id,
            "bytes":len(data),
            "original_md5":md5.lower(),
            "provider_MD5_and_bytes_verified":True
        }
        if name.lower().endswith(".csv"):
            PHASE="CSV_FILE_HEADER_AUDIT"
            headers,rows,sep=csv_headers_and_nrows(data)
            entry.update({
                "source_header_fields":headers,
                "source_table_rows":rows,
                "delimiter":{",":"comma","\t":"tab",";":"semicolon"}[sep]
            })
        else:
            entry["source_format"]="R source code (original authors)"
        summary.append(entry)
        PHASE="ORIGINAL_FILE_MD5_VERIFICATION"
    return {
        "schema":"neon.prairie_vole_direct_logger_trap_original_file_header_gate.v1",
        "status":"PUBLIC_ORIGINAL_PRAIRIE_VOLE_9_FILES_VERIFIED_HEADERS_ONLY",
        "paper_doi":"10.1093/jmammal/gyaf032",
        "public_project":PROJECT_ID,
        "public_articles":len(PIN),
        "public_original_files":len(summary),
        "public_original_source_bytes":sum(x["bytes"] for x in summary),
        "files":summary,
        "source_eligibility":{
            "provider_MD5_and_exact_size_all_9_files":True,
            "any_original_animal_ID_values_recorded_in_receipt":False,
            "any_observed_proximity_event_values_in_receipt":False,
            "original_published_proximity_vs_trap_R2_not_recomputed":True,
            "paired_animal_ID_crosswalk_established":False,
            "at_risk_dyad_sampling_frame_established":False,
            "matched_logger_running_exposure_established":False,
            "actual_new_biological_contact_comparison_authorized":False
        },
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    global PHASE
    try:
        result=run();exit_code=0
    except Exception as e:
        result={
            "schema":"neon.prairie_vole_direct_logger_trap_original_file_header_gate.v1",
            "status":"STOP_PRAIRIE_VOLE_FIGSHARE_ORIGINAL_FILE_SOURCE_VERIFICATION",
            "failed_stage":PHASE if PHASE in STAGES else "UNKNOWN",
            "error_class":type(e).__name__,
            "raw_animal_ID_or_proximity_outcomes_not_exported":True,
            "no_old_NEON_Portal_Finland_Structural_results_opened":True
        }
        exit_code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    return exit_code

if __name__=="__main__":
    raise SystemExit(main())
