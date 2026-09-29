from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+","_",str(value).strip().lower()).strip("_")


SETS={
    "identity":{
        "id","tag","tag_id","tagid","pit","pit_tag","pittag",
        "ear_tag","eartag","individual","individual_id","individualid",
        "animal_id","animalid","mark","mark_id","markid",
    },
    "sex":{"sex","gender"},
    "species":{
        "species","species_code","speciescode","spcode","taxon",
        "scientific_name","scientificname","species_id","speciesid","sp",
    },
    "site":{
        "site","site_id","siteid","location","location_id","locationid",
        "grid_id","gridid","grid","plot","plot_id","plotid",
    },
    "trap":{
        "trap","trap_id","trapid","station","station_id","stationid",
        "grid_point","gridpoint","point","point_id","pointid",
        "trap_station","trapstation","stake","stake_id","stakeid",
    },
    "night":{
        "night","night_id","nightid","trap_night","capture_night",
        "check","trap_check","trapcheck","visit","visit_id","visitid",
    },
    "occasion":{
        "session","session_id","sessionid","occasion","occasion_id",
        "occasionid","survey","survey_id","surveyid","period",
    },
    "date":{
        "date","capture_date","capturedate","sample_date","sampledate",
        "trapping_date","trappingdate",
    },
    "year":{"year"},
    "month":{"month"},
    "day":{"day"},
    "x":{
        "x","easting","utm_x","utmx","longitude","lon","long",
        "trap_x","grid_x","point_x",
    },
    "y":{
        "y","northing","utm_y","utmy","latitude","lat",
        "trap_y","grid_y","point_y",
    },
}


def classify(columns: list[str]) -> dict[str,list[str]]:
    out={key:[] for key in SETS}
    for column in columns:
        n=norm(column)
        for key,names in SETS.items():
            if n in names:
                out[key].append(column)
    return out


def detect_delimiter(text: str) -> str:
    try:
        return csv.Sniffer().sniff(text[:65536],delimiters=",\t;|").delimiter
    except csv.Error:
        tabs=text[:65536].count("\t")
        commas=text[:65536].count(",")
        return "\t" if tabs>commas else ","


def _decode(raw: bytes) -> str:
    for enc in ("utf-8-sig","utf-8","cp1252","latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8",errors="replace")


def audit_table(name: str, raw: bytes) -> dict:
    text=_decode(raw)
    delimiter=detect_delimiter(text)
    reader=csv.reader(text.splitlines(),delimiter=delimiter)
    try:
        columns=[str(x).strip() for x in next(reader)]
    except StopIteration:
        return {
            "archive_member":name,
            "empty":True,
            "size_bytes":len(raw),
            "sha256":hashlib.sha256(raw).hexdigest(),
        }

    row_count=0
    malformed=0
    for row in reader:
        if not row:
            continue
        row_count+=1
        if len(row)!=len(columns):
            malformed+=1

    structural=classify(columns)
    temporal=bool(
        structural["night"]
        or structural["date"]
        or (structural["year"] and structural["month"] and structural["day"])
    )
    spatial=bool(
        structural["trap"]
        or (structural["x"] and structural["y"])
    )
    required={
        "identity":bool(structural["identity"]),
        "sex":bool(structural["sex"]),
        "species":bool(structural["species"]),
        "site_context":bool(structural["site"]),
        "spatial_capture_location":spatial,
        "temporal_capture_occasion":temporal,
    }

    examples={}
    for key in ("site","trap","night","occasion","date","year","month","day"):
        for col in structural[key]:
            values=[]
            seen=set()
            for row in csv.DictReader(text.splitlines(),delimiter=delimiter):
                value=str(row.get(col,"")).strip()
                if value and value not in seen:
                    seen.add(value)
                    values.append(value)
                    if len(values)>=12:
                        break
            examples[col]=values

    return {
        "archive_member":name,
        "empty":False,
        "size_bytes":len(raw),
        "sha256":hashlib.sha256(raw).hexdigest(),
        "delimiter":repr(delimiter),
        "column_count":len(columns),
        "columns":columns,
        "data_row_count":row_count,
        "malformed_row_count":malformed,
        "structural_columns":structural,
        "structural_examples":examples,
        "required_presence":required,
        "structurally_adequate_capture_table":all(required.values()),
    }


def audit_zip(path: Path) -> dict:
    raw=path.read_bytes()
    if not raw:
        raise RuntimeError("source ZIP is empty")
    if not zipfile.is_zipfile(path):
        raise RuntimeError("source is not a valid ZIP archive")

    members=[]
    tables=[]
    with zipfile.ZipFile(path) as zf:
        for info in sorted(zf.infolist(),key=lambda x:x.filename.lower()):
            if info.is_dir():
                continue
            name=info.filename
            member_raw=zf.read(info)
            members.append({
                "name":name,
                "compressed_size":int(info.compress_size),
                "size":int(info.file_size),
                "sha256":hashlib.sha256(member_raw).hexdigest(),
            })
            lower=name.lower()
            if lower.endswith((".csv",".tsv",".txt")):
                tables.append(audit_table(name,member_raw))

    adequate=[
        row["archive_member"]
        for row in tables
        if row.get("structurally_adequate_capture_table")
    ]

    return {
        "schema":"neon.wyoming_pocketmouse_crossscale.source_schema_audit.v1",
        "dataset_doi":"10.15786/n57k-sz82",
        "source_zip":path.name,
        "source_zip_size_bytes":len(raw),
        "source_zip_sha256":hashlib.sha256(raw).hexdigest(),
        "archive_member_count":len(members),
        "archive_members":members,
        "tabular_member_count":len(tables),
        "tables":tables,
        "adequate_capture_tables":adequate,
        "source_adequacy_for_estimability_design":bool(adequate),
        "dipodomys_ordii_future_effect_excluded":True,
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
    print(json.dumps({
        "source_zip_sha256":out["source_zip_sha256"],
        "archive_member_count":out["archive_member_count"],
        "adequate_capture_tables":out["adequate_capture_tables"],
        "tables":[{
            "archive_member":row["archive_member"],
            "data_row_count":row.get("data_row_count"),
            "columns":row.get("columns"),
            "structural_columns":row.get("structural_columns"),
            "structurally_adequate_capture_table":
                row.get("structurally_adequate_capture_table"),
        } for row in out["tables"]],
        "source_adequacy_for_estimability_design":
            out["source_adequacy_for_estimability_design"],
    },indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
