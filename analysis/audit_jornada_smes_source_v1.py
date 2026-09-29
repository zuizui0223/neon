from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+","_",str(value).strip().lower()).strip("_")


COLUMN_SETS={
    "identity":{
        "id","tag","tag_id","tagid","animal_id","animalid","individual_id",
        "individualid","ear_tag","eartag","mark","rodent_id","rodentid",
    },
    "sex":{"sex","gender"},
    "species":{
        "species","species_code","speciescode","spcode","taxon","scientific_name",
        "scientificname","sp","species_id","speciesid",
    },
    "site":{
        "site","site_id","siteid","location","location_id","locationid",
        "study_site","studysite","habitat",
    },
    "web":{
        "web","web_id","webid","grid","grid_id","gridid","plot","plot_id","plotid",
        "trapping_web","trappingweb",
    },
    "trap":{
        "trap","trap_id","trapid","station","station_id","stationid",
        "trap_station","trapstation","stake","stake_id","stakeid",
    },
    "night":{"night","night_id","nightid","trap_night","capture_night","day"},
    "session":{
        "session","session_id","sessionid","period","occasion","occasion_id",
        "occasionid","trapping_session","trappingsession",
    },
    "date":{"date","capture_date","capturedate","sample_date","sampledate"},
    "year":{"year"},
    "month":{"month"},
}


def classify(columns: list[str]) -> dict[str,list[str]]:
    out={key:[] for key in COLUMN_SETS}
    for col in columns:
        n=norm(col)
        for key,names in COLUMN_SETS.items():
            if n in names:
                out[key].append(col)
    return out


def detect_delimiter(text: str) -> str:
    try:
        return csv.Sniffer().sniff(text[:65536],delimiters=",\t;|").delimiter
    except csv.Error:
        return ","


def audit_csv(path: Path) -> dict:
    raw=path.read_bytes()
    if not raw:
        raise RuntimeError(f"empty file: {path}")
    if b"<html" in raw[:5000].lower():
        raise RuntimeError(f"HTML response saved as CSV: {path}")

    text=raw.decode("utf-8-sig",errors="replace")
    delimiter=detect_delimiter(text)
    reader=csv.reader(text.splitlines(),delimiter=delimiter)
    try:
        columns=[str(x).strip() for x in next(reader)]
    except StopIteration:
        raise RuntimeError(f"no rows: {path}")

    row_count=0
    malformed=0
    for row in reader:
        if not row:
            continue
        row_count+=1
        if len(row)!=len(columns):
            malformed+=1

    structural=classify(columns)
    has_time=bool(
        structural["night"]
        or structural["date"]
        or (structural["year"] and structural["month"])
        or structural["session"]
    )
    required={
        "identity":bool(structural["identity"]),
        "sex":bool(structural["sex"]),
        "species":bool(structural["species"]),
        "spatial_context":bool(structural["site"] or structural["web"]),
        "trap":bool(structural["trap"]),
        "time_or_session":has_time,
    }
    return {
        "file_name":path.name,
        "size_bytes":len(raw),
        "sha256":hashlib.sha256(raw).hexdigest(),
        "delimiter":repr(delimiter),
        "data_row_count":row_count,
        "malformed_row_count":malformed,
        "column_count":len(columns),
        "columns":columns,
        "structural_columns":structural,
        "required_presence":required,
        "capture_table_structurally_adequate":all(required.values()),
    }


def audit_directory(directory: Path) -> dict:
    paths=sorted(directory.glob("*.csv"))
    if not paths:
        raise RuntimeError("no CSV files discovered")
    files=[]
    for path in paths:
        try:
            files.append(audit_csv(path))
        except RuntimeError as error:
            files.append({
                "file_name":path.name,
                "audit_error":str(error),
                "capture_table_structurally_adequate":False,
            })
    candidates=[
        row["file_name"] for row in files
        if row.get("capture_table_structurally_adequate")
    ]
    return {
        "schema":"neon.jornada_smes_heteromyid_crossscale.source_schema_audit.v1",
        "source_title":"Rodent data from trapping webs in the long-term Small Mammal Exclusion Study (SMES) at Jornada Basin LTER, 1995-2007",
        "files":files,
        "structurally_adequate_capture_tables":candidates,
        "source_adequacy_for_estimability_design":bool(candidates),
        "previously_inspected_species_future_effect_excluded":[
            "Chaetodipus baileyi",
            "Chaetodipus penicillatus",
            "Dipodomys merriami",
            "Dipodomys ordii",
        ],
        "species_specific_counts_inspected":False,
        "sex_specific_counts_inspected":False,
        "movement_distances_computed":False,
        "packing_effects_computed":False,
        "ecological_effect_models_fit":0,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--directory",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    out=audit_directory(args.directory)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
