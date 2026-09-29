from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


STRUCTURAL_PATTERNS={
    "identity":re.compile(r"(tag|individual|animal|id)",re.I),
    "sex":re.compile(r"sex",re.I),
    "species":re.compile(r"(species|spcode|taxon)",re.I),
    "site":re.compile(r"(site|location|habitat)",re.I),
    "web":re.compile(r"(web|grid|plot)",re.I),
    "trap":re.compile(r"(trap|stake|station)",re.I),
    "night":re.compile(r"(night|day|capture.?code|recap)",re.I),
    "date":re.compile(r"(date|year|month|season)",re.I),
}


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
    sample=text[:65536]
    delimiter=detect_delimiter(sample)
    reader=csv.reader(text.splitlines(),delimiter=delimiter)

    try:
        header=[str(x).strip() for x in next(reader)]
    except StopIteration:
        raise RuntimeError("source file has no rows")

    row_count=0
    malformed_rows=0
    structural_columns={
        name:[col for col in header if pattern.search(col)]
        for name,pattern in STRUCTURAL_PATTERNS.items()
    }
    index={col:i for i,col in enumerate(header)}

    # Only structural coding examples are collected; no sex-stratified counts
    # or spatial effect values are computed.
    example_columns=sorted(set(
        structural_columns["site"]
        + structural_columns["web"]
        + structural_columns["night"]
        + structural_columns["date"]
    ))

    for row in reader:
        if not row:
            continue
        row_count+=1
        if len(row)!=len(header):
            malformed_rows+=1
            continue
        # Row-shape validation only. Values are summarized in a separate pass.

    # Re-read with DictReader for deterministic small structural examples.
    examples={}
    dict_reader=csv.DictReader(text.splitlines(),delimiter=delimiter)
    for col in example_columns:
        values=[]
        seen=set()
        for row in dict_reader:
            value=str(row.get(col,"")).strip()
            if value and value not in seen:
                seen.add(value)
                values.append(value)
                if len(values)>=12:
                    break
        examples[col]=values
        dict_reader=csv.DictReader(text.splitlines(),delimiter=delimiter)

    required_presence={
        key:bool(cols)
        for key,cols in structural_columns.items()
    }

    return {
        "schema":"neon.sevilleta_heteromyid_crossscale.source_schema_audit.v1",
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
        "source_adequacy_for_next_estimability_design":all(
            required_presence[key]
            for key in ("identity","sex","species","site","web","trap","night","date")
        ),
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
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
