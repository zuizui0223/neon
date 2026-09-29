from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


CATEGORIES={
    "identity":(
        "tag","tagid","tag_id","individual","individualid","individual_id",
        "animal","animalid","animal_id","id","rfid","pit","pitid","pit_id",
        "ear","eartag","ear_tag","mark","markid","mark_id",
    ),
    "sex":("sex","gender"),
    "species":("species","spcode","speciescode","species_code","taxon"),
    "site":("site","location","habitat","plot"),
    "web":("web","webid","web_id","grid","gridid","grid_id"),
    "trap":("trap","trapno","trap_no","trapnumber","trap_number","stake","station"),
    "night":("night","trapnight","trap_night","captureday","capture_day","trapday","trap_day","day"),
    "date":("date","year","month","season","sampledate","sample_date"),
    "recap":("recap","recapture","status","fate"),
}


def norm(value: object) -> str:
    return re.sub(r"[^a-z0-9]+","",str(value or "").strip().lower())


def classify(columns: list[str]) -> dict[str,list[str]]:
    out={key:[] for key in CATEGORIES}
    normalized={key:{norm(x) for x in vals} for key,vals in CATEGORIES.items()}
    for col in columns:
        nc=norm(col)
        for key,names in normalized.items():
            if nc in names:
                out[key].append(col)
    return out


def detect_delimiter(text: str) -> str:
    try:
        return csv.Sniffer().sniff(text[:65536],delimiters=",\t;|").delimiter
    except csv.Error:
        return ","


def audit(path: Path) -> dict:
    raw=path.read_bytes()
    if not raw:
        raise RuntimeError("empty Sevilleta raw source")
    text=raw.decode("utf-8-sig",errors="replace")
    delim=detect_delimiter(text)
    reader=csv.reader(text.splitlines(),delimiter=delim)
    try:
        columns=[str(x).strip() for x in next(reader)]
    except StopIteration:
        raise RuntimeError("no rows")

    row_count=0
    malformed=0
    for row in reader:
        if not row:
            continue
        row_count+=1
        if len(row)!=len(columns):
            malformed+=1

    structural=classify(columns)
    examples={}
    # Only non-biological structural coding examples. Do not summarize
    # species/sex/identity values at source-audit stage.
    for key in ("site","web","trap","night","date","recap"):
        for col in structural[key]:
            vals=[]
            seen=set()
            for row in csv.DictReader(text.splitlines(),delimiter=delim):
                val=str(row.get(col,"")).strip()
                if val and val not in seen:
                    seen.add(val)
                    vals.append(val)
                    if len(vals)>=15:
                        break
            examples[col]=vals

    required={
        "identity":bool(structural["identity"]),
        "sex":bool(structural["sex"]),
        "species":bool(structural["species"]),
        "site":bool(structural["site"]),
        "web":bool(structural["web"]),
        "trap":bool(structural["trap"]),
        "night_or_recapture_structure":bool(structural["night"] or structural["recap"]),
        "date_context":bool(structural["date"]),
    }
    return {
        "schema":"neon.sevilleta_heteromyid_crossscale.raw_source_schema_audit.v3",
        "source_file":path.name,
        "size_bytes":len(raw),
        "sha1":hashlib.sha1(raw).hexdigest(),
        "sha256":hashlib.sha256(raw).hexdigest(),
        "delimiter":repr(delim),
        "column_count":len(columns),
        "columns":columns,
        "data_row_count":row_count,
        "malformed_row_count":malformed,
        "structural_columns":structural,
        "non_biological_structural_examples":examples,
        "required_presence":required,
        "source_adequacy_for_estimability_design":all(required.values()) and malformed==0,
        "species_specific_counts_inspected":False,
        "sex_specific_counts_inspected":False,
        "movement_distances_computed":False,
        "packing_effects_computed":False,
        "ecological_effect_models_fit":0,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    out=audit(args.input)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
