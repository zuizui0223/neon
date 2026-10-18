#!/usr/bin/env python3
"""Inventory verified RELEASE-2026 small-mammal DNA barcode table schemas.

Pre-effect SOURCE AUDIT ONLY. It may download one early and one late
checksum-verified file per published table to inspect column names and
structure, but NEVER exports any sampleID, tagID, sequence, individual
taxon label, BOLD identification, animal location, W/B or ecological slope.

This phase does NOT claim barcode coverage or identity validation. It
precedes a separately specified source-only sample-key linkage gate.
"""
from __future__ import annotations

import csv
import io
import json
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from analysis.run_multiscale_density_estimability_release2026_v3 import (
    _download_many, _inventory, _request_json, _site_codes,
    PRODUCT as TRAP_PRODUCT, RELEASE, TOKEN_ENV, QUERY_URL,
)
from analysis.audit_multiscale_density_mnka_variation_v1 import USER_AGENT

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/neon_barcode_schema_inventory_v1.json"
BARCODE_PRODUCT = "DP1.10076.001"
START = "2015-04"
END = "2023-11"
BOLD_TABLES = (
    "mam_BOLDcollectionData",
    "mam_BOLDspecimenDetails",
    "mam_BOLDtaxonomy",
    "mam_BOLDvoucherInfo",
)
OPTIONAL_TABLES = ("mam_barcodingqa",)
TABLES = BOLD_TABLES + OPTIONAL_TABLES


def classify_file(name: str) -> str | None:
    if not str(name).lower().endswith(".csv"):
        return None
    for table in TABLES:
        if table.casefold() in str(name).casefold():
            return table
    return None


def parse_schema(raw: bytes) -> dict:
    text = raw.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(text))
    header = next(reader, [])
    if not header or len(header) != len(set(header)):
        raise RuntimeError("barcode CSV has empty or duplicate header")
    if any(not x.strip() for x in header):
        raise RuntimeError("barcode CSV contains an unnamed field")
    # Count records in *sampled* source files only; no observation content.
    nrows = 0
    for row in reader:
        if len(row) != len(header):
            raise RuntimeError("barcode CSV ragged file")
        nrows += 1
    return {
        "columns": header,
        "n_columns": len(header),
        "sampled_file_data_rows": nrows,
        "possible_sample_link_fields": sorted(
            x for x in header
            if any(k in x.casefold() for k in
                   ("sampleid","samplecode","voucherid","specimenid","processid","recordid"))
        ),
        "no_sample_values_exported": True,
    }


def extract_inventory(payload: dict) -> list[dict]:
    # Reuse the exact release-aware canonical NEON inventory parser.
    files = _inventory(payload)
    return [row for row in files if classify_file(row["name"]) is not None]


def choose_schema_files(files: list[dict]) -> list[dict]:
    """First and last versioned months for each published table.

    Endpoints are chosen from metadata, never biological barcode outcomes.
    """
    by_table = defaultdict(list)
    for z in files:
        table = classify_file(z["name"])
        if table:
            by_table[table].append(z)
    selected = []
    for table, rows in sorted(by_table.items()):
        rows = sorted(rows, key=lambda v: (v["month"],v["site"],v["name"]))
        selected.append(rows[0])
        if rows[-1]["name"] != rows[0]["name"]:
            selected.append(rows[-1])
    return selected


def run() -> dict:
    token = os.environ.get(TOKEN_ENV,"").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN required for original release")
    if RELEASE != "RELEASE-2026":
        raise RuntimeError("not source-frozen NEON release")

    # Product metadata is public. API query requires existing account token.
    product_json = _request_json(
        f"https://data.neonscience.org/api/v0/products/{BARCODE_PRODUCT}"
    )
    sites = _site_codes(product_json)
    payload = _request_json(
        QUERY_URL, token=token,
        body={
            "productCode": BARCODE_PRODUCT,
            "siteCodes": sites,
            "startDateMonth":START,
            "endDateMonth":END,
            "release":RELEASE,
            "package":"basic",
            "includeProvisional":False,
        },
    )
    files = extract_inventory(payload)
    by_table = defaultdict(list)
    for item in files:
        table = classify_file(item["name"])
        if table is not None:
            by_table[table].append(item)
    # Require published four tables: do not infer absence if API is incomplete.
    missing = sorted(set(BOLD_TABLES)-set(by_table))
    if missing:
        raise RuntimeError(f"four canonical BOLD tables not in immutable source: {missing}")

    sampled = choose_schema_files(files)
    raw_samples = _download_many(sampled,token,max_workers=4)
    by_table_schema = defaultdict(list)
    for meta,raw in zip(sampled,raw_samples):
        # _download_many ensures every file matches the published MD5 + size.
        table = classify_file(meta["name"])
        out = parse_schema(raw)
        out["source_site"]=meta["site"]
        out["source_year_month"]=meta["month"]
        out["source_checksum_MD5"]=meta["md5"]
        out["source_file_size"]=meta["size"]
        by_table_schema[table].append(out)

    table_summary={}
    for table in TABLES:
        rows = by_table.get(table,[])
        months = sorted({z["month"] for z in rows})
        table_summary[table]={
            "source_files":len(rows),
            "source_sites":len({z["site"] for z in rows}),
            "earliest_month":months[0] if months else None,
            "latest_month":months[-1] if months else None,
            "sampled_schema":by_table_schema.get(table,[]),
        }
    # A schema can change between the first and last files. Track this
    # rather than silently using the first matching column name.
    drift = {
        t: len({tuple(r["columns"]) for r in data["sampled_schema"]})>1
        for t,data in table_summary.items()
    }
    return {
        "schema":"neon.barcode_release2026_source_schema.v1",
        "status":"BARCODE_SOURCE_SCHEMA_VERIFIED_NO_BIOLOGICAL_MATCHES",
        "release":RELEASE,
        "barcode_product":BARCODE_PRODUCT,
        "trap_product_for_future_link":TRAP_PRODUCT,
        "fixed_query_start":START,
        "fixed_query_end":END,
        "published_product_metadata_site_count":len(sites),
        "inventory_validated_MD5_and_file_size":True,
        "release_files_by_table":table_summary,
        "first_last_header_drift":drift,
        "inventory_unique_files":len(files),
        "sampled_files_verified":len(sampled),
        "all_source_headers_recorded_as_original":True,
        "earSampleID_to_barcode_link_proven":False,
        "barcode_taxonomic_determinations_read":False,
        "barcode_sample_to_animal_matches_calculated":False,
        "capture_sample_IDs_or_individual_IDs_exported":False,
        "W_B_or_MNKA_space_effect_opened":False,
        "original_8genus_generalization":"FAILED_5_OF_8",
        "new_Peromyscus_directional_replication":"NOT_REPLICATED_IMPRECISE",
        "full_five_genus_confirmation":"NOT_ESTIMABLE",
        "MOSA_spatial_effects":"SEALED",
        "next_gate":"Identify unambiguous earSampleID and BOLD-voucher key from verified table schemas, then implement source-only join with barcode selection bias and taxonomy quality checks before opening any ecological effects.",
    }


def main() -> int:
    try:
        out=run()
    except Exception as exc:
        out={
            "schema":"neon.barcode_release2026_source_schema.v1",
            "status":"STOP_BARCODE_SOURCE_OR_SCHEMA_GATE",
            "diagnostic":str(exc)[:850],
            "barcode_taxonomic_determinations_read":False,
            "W_B_or_MNKA_space_effect_opened":False,
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0 if out["status"]=="BARCODE_SOURCE_SCHEMA_VERIFIED_NO_BIOLOGICAL_MATCHES" else 3


if __name__=="__main__":
    raise SystemExit(main())
