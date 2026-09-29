from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROW_RE=re.compile(
    r"^\s*(?P<trap>[A-J](?:10|[1-9]))\s+"
    r"D\.\s*ordii\s+"
    r"(?P<sex>\S+)\s+"
    r"(?P<age>adult|subadult|juvenile)\b",
    re.I,
)
BURROW_RE=re.compile(
    r"^\s*(?P<id>\d+)\s+"
    r"(?P<age>ad|sa)\s+"
    r"(?P<sex>\S+)\s+",
    re.I,
)


def symbol_class(value: str) -> str | None:
    token=str(value).strip()
    if token in {"♂","♂"}:
        return "M"
    if token in {"♀","♀"}:
        return "F"
    # Some PDF extractors emit male/female symbol plus variation selector.
    base=token.replace("︎","").replace("️","")
    if base=="♂":
        return "M"
    if base=="♀":
        return "F"
    return None


def audit_layout_text(path: Path) -> dict:
    text=path.read_text(encoding="utf-8",errors="replace")
    appendix2=[]
    appendix4=[]
    current=None

    for raw in text.splitlines():
        line=raw.rstrip("\n")
        stripped=line.strip()
        if stripped.startswith("Appendix 2"):
            current="appendix2"
        elif stripped.startswith("Appendix 3"):
            if current=="appendix2":
                current=None
        elif stripped.startswith("Appendix 4"):
            current="appendix4"
        elif stripped.startswith("Appendix 5"):
            if current=="appendix4":
                current=None

        if current=="appendix2":
            m=ROW_RE.match(line)
            if m:
                appendix2.append({
                    "trap":m.group("trap"),
                    "sex_token":m.group("sex"),
                    "sex_class":symbol_class(m.group("sex")),
                    "age":m.group("age").lower(),
                    "line":stripped,
                })
        elif current=="appendix4":
            m=BURROW_RE.match(line)
            if m:
                appendix4.append({
                    "id":m.group("id"),
                    "sex_token":m.group("sex"),
                    "sex_class":symbol_class(m.group("sex")),
                    "age":m.group("age").lower(),
                    "line":stripped,
                })

    def summary(rows):
        return {
            "row_count":len(rows),
            "male_symbol_rows":sum(r["sex_class"]=="M" for r in rows),
            "female_symbol_rows":sum(r["sex_class"]=="F" for r in rows),
            "unparsed_sex_rows":sum(r["sex_class"] is None for r in rows),
            "unique_sex_tokens":sorted({r["sex_token"] for r in rows}),
            "example_lines":[r["line"] for r in rows[:12]],
        }

    a2=summary(appendix2)
    a4=summary(appendix4)
    usable=(
        a2["male_symbol_rows"]>0
        and a2["female_symbol_rows"]>0
        and a4["male_symbol_rows"]>0
        and a4["female_symbol_rows"]>0
    )

    return {
        "schema":"neon.auburn_dordii_crossscale_case.pdf_sex_symbol_audit.v1",
        "appendix2":a2,
        "appendix4":a4,
        "direct_sex_symbol_extraction_usable":usable,
        "sex_specific_effects_inspected":False,
        "packing_effects_inspected":False,
        "burrow_use_effects_inspected":False,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--layout-text",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    out=audit_layout_text(args.layout_text)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
