from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


REQUIRED_COLUMNS=[
    "Recyear","Season","RecMonth","Recday","TrapDay",
    "Watershed","Line","Sta","Species","Sex",
    "Status","ToeClip","HairClip","REarTag","LEarTag",
]

EXAMPLE_COLUMNS=[
    "TrapDay","Sta","Status","ToeClip","HairClip","REarTag","LEarTag",
]


def audit_file(path: Path) -> dict:
    raw=path.read_bytes()
    if not raw:
        raise RuntimeError("empty Konza CSM012 source")

    text=raw.decode("utf-8-sig",errors="replace")
    reader=csv.DictReader(text.splitlines())
    columns=list(reader.fieldnames or [])
    missing=[name for name in REQUIRED_COLUMNS if name not in columns]

    row_count=0
    malformed=0
    examples={name:[] for name in EXAMPLE_COLUMNS}
    seen={name:set() for name in EXAMPLE_COLUMNS}

    for row in reader:
        row_count+=1
        if None in row:
            malformed+=1
        for name in EXAMPLE_COLUMNS:
            value=str(row.get(name,"")).strip()
            if value and value not in seen[name] and len(examples[name])<15:
                seen[name].add(value)
                examples[name].append(value)

    return {
        "schema":"neon.konza_heteromyid_crossscale.source_schema_audit.v1",
        "source_file":path.name,
        "size_bytes":len(raw),
        "sha256":hashlib.sha256(raw).hexdigest(),
        "column_count":len(columns),
        "columns":columns,
        "data_row_count":row_count,
        "malformed_row_count":malformed,
        "required_columns":REQUIRED_COLUMNS,
        "missing_required_columns":missing,
        "mark_columns":["ToeClip","HairClip","REarTag","LEarTag"],
        "non_stratified_structural_examples":examples,
        "source_adequacy_for_estimability_design":not missing and row_count>0 and malformed==0,
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
