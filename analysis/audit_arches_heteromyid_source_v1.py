from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+","_",str(value).strip().lower()).strip("_")


SETS={
    "identity":{
        "id","tag","tag_id","tagid","animal_id","animalid",
        "individual_id","individualid","ear_tag","eartag","mark",
    },
    "sex":{"sex","gender"},
    "species":{
        "species","species_code","speciescode","spcode","taxon",
        "scientific_name","scientificname","sp",
    },
    "trap":{
        "trap","trap_id","trapid","station","station_id","stationid",
        "trap_station","trapstation","stake","stake_id","stakeid",
    },
    "night":{"night","night_id","nightid","trap_night","capture_night"},
    "session":{
        "session","session_id","sessionid","trapping_session","trappingsession",
        "period","occasion","occasion_id","occasionid",
    },
    "date":{"date","capture_date","capturedate","sample_date","sampledate"},
    "year":{"year"},
    "month":{"month"},
    "day":{"day"},
    "x":{
        "x","utm_x","utmx","easting","east","longitude","lon","long",
        "station_x","trap_x",
    },
    "y":{
        "y","utm_y","utmy","northing","north","latitude","lat",
        "station_y","trap_y",
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
        return ","


def audit_one(path: Path, site_label: str) -> dict:
    raw=path.read_bytes()
    if not raw:
        raise RuntimeError(f"empty source: {path}")
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
    example_keys=("trap","night","session","date","year","month","day")
    examples={}
    for key in example_keys:
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

    required={
        "identity":bool(structural["identity"]),
        "sex":bool(structural["sex"]),
        "species":bool(structural["species"]),
        "trap":bool(structural["trap"]),
        "temporal_night_or_date":bool(
            structural["night"]
            or structural["date"]
            or (structural["year"] and structural["month"] and structural["day"])
        ),
    }
    return {
        "site_context":site_label,
        "source_file":path.name,
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
        "adequate_for_estimability_design":all(required.values()),
    }


def audit(salt: Path, willow: Path) -> dict:
    sources=[
        audit_one(salt,"Salt Valley"),
        audit_one(willow,"Willow Flats"),
    ]
    return {
        "schema":"neon.arches_heteromyid_crossscale.source_schema_audit.v1",
        "dataset_doi":"10.5061/dryad.pv608",
        "sources":sources,
        "both_site_files_structurally_adequate":all(
            row["adequate_for_estimability_design"] for row in sources
        ),
        "site_context_count":2,
        "dipodomys_ordii_future_effect_excluded":True,
        "species_specific_counts_inspected":False,
        "sex_specific_counts_inspected":False,
        "movement_distances_computed":False,
        "packing_effects_computed":False,
        "ecological_effect_models_fit":0,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--salt",type=Path,required=True)
    parser.add_argument("--willow",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    out=audit(args.salt,args.willow)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
