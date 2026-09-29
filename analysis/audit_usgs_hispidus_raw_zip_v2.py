from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path


def _classify_columns(columns: list[str]) -> dict[str,list[str]]:
    out={
        "identity":[],
        "sex":[],
        "species":[],
        "capture_time":[],
        "trap_or_station":[],
        "latitude":[],
        "longitude":[],
        "site_or_plot":[],
    }
    for col in columns:
        n=re.sub(r"[^a-z0-9]+","_",str(col).lower()).strip("_")
        if re.search(r"(^|_)(tag|pit|ear_tag|ear_tag_1|ear_tag_2|animal_id|individual_id|unique_id|mark_id|id)($|_)",n):
            out["identity"].append(col)
        if n in {"sex","gender"} or n.endswith("_sex"):
            out["sex"].append(col)
        if re.search(r"(^|_)(species|species_code|taxon|scientific_name|sp)($|_)",n):
            out["species"].append(col)
        if re.search(r"(^|_)(date|datetime|time|occasion|session|night|day|year|month)($|_)",n):
            out["capture_time"].append(col)
        if re.search(r"(^|_)(trap|trap_id|station|stake|grid_cell|capture_location|trap_station)($|_)",n):
            out["trap_or_station"].append(col)
        if re.search(r"(^|_)(lat|latitude)($|_)",n):
            out["latitude"].append(col)
        if re.search(r"(^|_)(lon|long|longitude)($|_)",n):
            out["longitude"].append(col)
        if re.search(r"(^|_)(site|plot|grid|location|colony)($|_)",n):
            out["site_or_plot"].append(col)
    return out


def _audit_text(name: str, raw: bytes) -> dict:
    text=raw.decode("utf-8-sig",errors="replace")
    try:
        delim=csv.Sniffer().sniff(text[:65536],delimiters=",\t;|").delimiter
    except csv.Error:
        delim=","
    reader=csv.reader(text.splitlines(),delimiter=delim)
    try:
        columns=[str(x).strip() for x in next(reader)]
    except StopIteration:
        columns=[]
    row_count=0
    malformed=0
    for row in reader:
        if not row:
            continue
        row_count+=1
        if len(row)!=len(columns):
            malformed+=1
    structural=_classify_columns(columns)
    has_spatial=bool(
        structural["trap_or_station"]
        or (structural["latitude"] and structural["longitude"])
    )
    adequate=bool(
        structural["identity"]
        and structural["sex"]
        and structural["species"]
        and structural["capture_time"]
        and has_spatial
    )
    return {
        "archive_member":name,
        "size_bytes":len(raw),
        "sha256":hashlib.sha256(raw).hexdigest(),
        "delimiter":repr(delim),
        "column_count":len(columns),
        "columns":columns,
        "data_row_count":row_count,
        "malformed_row_count":malformed,
        "structural_columns":structural,
        "has_spatial_capture_field":has_spatial,
        "structurally_adequate_for_estimability_design":adequate,
    }


def audit_zip(path: Path) -> dict:
    raw_zip=path.read_bytes()
    if not raw_zip:
        raise RuntimeError("empty raw-data ZIP")
    records=[]
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as zf:
        members=sorted(
            info.filename
            for info in zf.infolist()
            if not info.is_dir()
        )
        for member in members:
            lower=member.lower()
            if not lower.endswith((".csv",".txt",".tsv")):
                records.append({
                    "archive_member":member,
                    "audited_as_text":False,
                })
                continue
            data=zf.read(member)
            record=_audit_text(member,data)
            record["audited_as_text"]=True
            records.append(record)

    adequate=[
        row["archive_member"] for row in records
        if row.get("structurally_adequate_for_estimability_design")
    ]
    return {
        "schema":"neon.usgs_hispidus_source_audit.raw_zip.v2",
        "archive_name":path.name,
        "archive_size_bytes":len(raw_zip),
        "archive_md5":hashlib.md5(raw_zip).hexdigest(),
        "archive_sha256":hashlib.sha256(raw_zip).hexdigest(),
        "members":records,
        "structurally_adequate_members":adequate,
        "source_adequacy_for_estimability_design":bool(adequate),
        "species_specific_counts_inspected":False,
        "sex_specific_counts_inspected":False,
        "movement_distances_computed":False,
        "packing_effects_computed":False,
        "ecological_effect_models_fit":0,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--zip",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    out=audit_zip(args.zip)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
