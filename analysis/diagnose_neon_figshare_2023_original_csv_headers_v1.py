#!/usr/bin/env python3
"""Effect-blind original Figshare CSV HEADER diagnosis after empty label STOP.

Retrieves exact previously locked 3 CSV bytes and original provider MD5.
Prints only original column header names and empty/duplicate positions.
No raw animal tag, seed availability, risk, visit or choice values.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timezone
from hashlib import md5,sha256
from io import StringIO
from pathlib import Path
import csv,json

from analysis.audit_neon_figshare_2023_original_csv_schema_v1 import (
    FILES, inventory_source, bounded_original, require
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_figshare_2023_original_header_diagnosis_v1.json"

def diagnose():
    hrefs,meta_hash=inventory_source()
    diagnosed={}
    for fid,(name,size,expected_md5) in FILES.items():
        raw=bounded_original(hrefs[fid],size)
        require(md5(raw).hexdigest()==expected_md5,
                "DIAG_ORIGINAL_PROVIDER_MD5_MISMATCH")
        decoded=raw.decode("utf-8-sig")
        parser=csv.reader(StringIO(decoded,newline=""))
        try:
            header=next(parser)
        except StopIteration:
            raise ValueError("NEON_FIGSHARE_DIAG_EMPTY_ORIGINAL_CSV") from None
        blanks=[i for i,h in enumerate(header) if not h.strip()]
        repeated=[x for x,n in Counter(header).items() if n>1 and x.strip()]
        # Diagnostics limited to schema: one pass with row WIDTH counts only.
        width=Counter()
        for row in parser:
            width[len(row)]+=1
        diagnosed[name]={
            "source_original_file_id":fid,
            "provider_original_md5_verified":expected_md5,
            "original_sha256":sha256(raw).hexdigest(),
            "original_bytes":size,
            "raw_header_labels":header,
            "header_count":len(header),
            "zero_based_empty_header_positions":blanks,
            "repeated_nonempty_headers":repeated,
            "original_csv_row_width_histogram":dict(sorted(width.items())),
            "original_source_event_values_not_exported":True,
        }
    return {
        "schema":"neon.figshare_2023_original_CSV_header_only_diagnosis.v1",
        "status":"SOURCE_HEADER_DIAGNOSIS_NOT_ECOLOGICAL_EFFECT",
        "original_article_id":21512436,
        "original_version":1,
        "original_provider_metadata_sha256":meta_hash,
        "source_schemas":diagnosed,
        "no_behavior_animal_seed_risk_response_values_logged":True,
        "next_contract_requires_structural_schema_rule_before_join":True,
        "unified_NEON_paper_SUBMISSION_HOLD":True,
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
    }

def main():
    try:outcome=diagnose();code=0
    except Exception as exc:
        outcome={"schema":"neon.figshare_2023_original_CSV_header_only_diagnosis.v1",
                 "status":"SOURCE_SCHEMA_DIAGNOSIS_STOP",
                 "error_type":type(exc).__name__,
                 "stop_reason":str(exc)[:140],
                 "no_original_biological_response_reported":True}
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(outcome,indent=2,sort_keys=True)+"\n")
    print(json.dumps(outcome,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
