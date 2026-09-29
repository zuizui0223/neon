from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]+","_",str(name).strip().lower()).strip("_")


IDENTITY_NAMES={
    "id","tag","tag_id","tagid","individual","individual_id","individualid",
    "animal","animal_id","animalid","record_id","recordid",
}
SPECIES_NAMES={
    "species","species_name","species_code","speciescode","spcode","taxon",
    "taxon_name","scientific_name","scientificname","valid_name","validname",
}
SEX_NAMES={"sex","gender"}
SITE_NAMES={"site","site_id","siteid","location","location_id","locationid","habitat"}
WEB_NAMES={"web","web_id","webid","grid","grid_id","gridid","plot","plot_id","plotid"}
TRAP_NAMES={"trap","trap_id","trapid","stake","stake_id","stakeid","station","station_id","stationid"}
NIGHT_NAMES={"night","night_id","nightid","capture_night","trap_night","recapture_night","day"}
DATE_NAMES={"date","capture_date","sample_date","year","month","season"}


def classify_column(column: str) -> set[str]:
    name=_norm(column)
    out=set()
    if name in IDENTITY_NAMES:
        out.add("identity")
    if name in SPECIES_NAMES:
        out.add("species")
    if name in SEX_NAMES:
        out.add("sex")
    if name in SITE_NAMES:
        out.add("site")
    if name in WEB_NAMES:
        out.add("web")
    if name in TRAP_NAMES:
        out.add("trap")
    if name in NIGHT_NAMES:
        out.add("night")
    if name in DATE_NAMES:
        out.add("date")
    return out


def detect_delimiter(sample: str) -> str:
    try:
        dialect=csv.Sniffer().sniff(sample,delimiters="\t,;|")
        return dialect.delimiter
    except csv.Error:
        tabs=sample.count("\t")
        commas=sample.count(",")
        return "\t" if tabs>=commas else ","


def audit_file(path: Path) -> dict:
    raw=path.read_bytes()
    if not raw:
        raise RuntimeError("source file is empty")

    text=raw.decode("utf-8-sig",errors="replace")
    delimiter=detect_delimiter(text[:65536])
    reader=csv.reader(text.splitlines(),delimiter=delimiter)

    try:
        header=[str(x).strip() for x in next(reader)]
    except StopIteration:
        raise RuntimeError("source file has no rows")

    structural_columns={key:[] for key in (
        "identity","sex","species","site","web","trap","night","date"
    )}
    for col in header:
        for key in classify_column(col):
            structural_columns[key].append(col)

    row_count=0
    malformed_rows=0
    for row in reader:
        if not row:
            continue
        row_count+=1
        if len(row)!=len(header):
            malformed_rows+=1

    example_columns=sorted(set(
        structural_columns["site"]
        + structural_columns["web"]
        + structural_columns["trap"]
        + structural_columns["night"]
        + structural_columns["date"]
    ))
    examples={}
    for col in example_columns:
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

    required_presence={
        key:bool(cols)
        for key,cols in structural_columns.items()
    }
    required_for_crossscale=("identity","sex","species","site","web","trap","night","date")
    missing=[key for key in required_for_crossscale if not required_presence[key]]

    return {
        "schema":"neon.sevilleta_heteromyid_crossscale.source_schema_audit.v2",
        "audit_revision":"correct exact-token column classification; valid_name is species, not identity",
        "source_file":path.name,
        "size_bytes":len(raw),
        "sha256":hashlib.sha256(raw).hexdigest(),
        "detected_delimiter":repr(delimiter),
        "column_count":len(header),
        "columns":header,
        "data_row_count":row_count,
        "malformed_row_count":malformed_rows,
        "structural_columns":structural_columns,
        "structural_examples":examples,
        "required_presence":required_presence,
        "missing_required_structural_fields":missing,
        "source_adequacy_for_next_estimability_design":not missing,
        "identity_column_present":required_presence["identity"],
        "sex_specific_effects_inspected":False,
        "movement_distances_computed":False,
        "packing_effects_computed":False,
        "ecological_effect_models_fit":0,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    out=audit_file(args.input)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
