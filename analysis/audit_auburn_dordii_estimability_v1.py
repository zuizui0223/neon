from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


CAPTURE_START=re.compile(
    r"^(?P<trap>[A-J](?:10|[1-9]))\s+"
    r"(?P<species>D\.\s*ordii|P\.\s*manic(?:ulatus)?|P\.\s*flavescens)\b"
    r"(?P<rest>.*)$"
)
BURROW_START=re.compile(r"^(?P<id>\d+)\s+(?P<age>ad|sa)\b(?P<rest>.*)$")

CONDITION_PATTERN=(
    r"post-lactating,\s*estrus|"
    r"lactating/pregnant|"
    r"post-lactating|"
    r"non-reproductive|"
    r"non-scrotal|"
    r"lactating|"
    r"pregnant|"
    r"scrotal|"
    r"estrus"
)
BURROW_ROW=re.compile(
    rf"^(?P<id>\d+)\s+(?P<age>ad|sa)\s+\?\s+"
    rf"(?P<condition>{CONDITION_PATTERN})\s+"
    r"(?P<weight>\d+)\s+"
    r"(?P<n4>\d+|-)\s+"
    r"(?P<n7>\d+|-)(?:\s|$)",
    re.I,
)


def normalize_condition(value: str) -> str:
    text=" ".join(str(value).lower().replace("?", " ").split())
    text=text.replace(" ,",",")
    return text.strip(" ,")


def infer_sex(*, age: str, condition: str) -> str | None:
    if str(age).lower() not in {"adult","ad"}:
        return None
    cond=normalize_condition(condition)
    if any(
        token in cond
        for token in (
            "estrus",
            "pregnant",
            "lactating",
            "post-lactating",
        )
    ):
        return "F"
    if "scrotal" in cond:
        return "M"
    return None


def _section(text: str, start_marker: str, end_marker: str) -> str:
    start=text.find(start_marker)
    if start<0:
        raise RuntimeError(f"start marker not found: {start_marker}")
    end=text.find(end_marker,start+len(start_marker))
    if end<0:
        raise RuntimeError(f"end marker not found: {end_marker}")
    return text[start:end]


def parse_appendix2(text: str) -> list[dict]:
    section=_section(
        text,
        "Appendix 2.  Captures of small mammals",
        "Appendix 3.  Number of burrows used",
    )
    lines=section.splitlines()
    records=[]
    season=None
    current=None

    def finish():
        nonlocal current
        if current is None:
            return
        records.append(current)
        current=None

    for raw in lines:
        line=" ".join(raw.strip().split())
        if not line:
            continue
        sm=re.fullmatch(r"Summer\s+(2005|2006|2007)",line,re.I)
        if sm:
            finish()
            season=f"Summer {sm.group(1)}"
            continue
        m=CAPTURE_START.match(line)
        if m:
            finish()
            current={
                "season":season,
                "trap_location":m.group("trap"),
                "species":" ".join(m.group("species").replace("."," . ").split())
                    .replace(" . ","."),
                "parts":[m.group("rest").strip()],
            }
            continue
        if current is not None:
            if (
                line.isdigit()
                or line.startswith("Appendix 2 continued")
                or line.startswith("Trap location Species Sex")
                or line in {"X indicates capture","- indicates no capture"}
            ):
                continue
            current["parts"].append(line)
    finish()

    out=[]
    for rec in records:
        if rec["season"] not in {"Summer 2006","Summer 2007"}:
            continue
        species=rec["species"].replace(" ","")
        if species!="D.ordii":
            continue

        body=" ".join(x for x in rec["parts"] if x)
        body=" ".join(body.replace("?"," ").split())
        flags=re.search(r"([X-])\s+([X-])\s+([X-])\s*$",body,re.I)
        if not flags:
            out.append({
                "season":rec["season"],
                "trap_location":rec["trap_location"],
                "parse_ok":False,
                "parse_reason":"missing_three_night_flags",
                "raw_body":body,
            })
            continue

        prefix=body[:flags.start()].strip()
        meta=re.search(
            r"\b(?P<age>adult|subadult|juvenile)\b"
            r"(?P<condition>.*?)"
            r"(?P<weight>\d+)\s+(?P<tag>\d+)\s*$",
            prefix,
            re.I,
        )
        if not meta:
            out.append({
                "season":rec["season"],
                "trap_location":rec["trap_location"],
                "parse_ok":False,
                "parse_reason":"missing_age_weight_tag",
                "raw_body":body,
            })
            continue

        condition=normalize_condition(meta.group("condition"))
        age=meta.group("age").lower()
        sex=infer_sex(age=age,condition=condition)
        out.append({
            "season":rec["season"],
            "trap_location":rec["trap_location"],
            "species":"D. ordii",
            "age":age,
            "condition":condition,
            "sex_inferred":sex,
            "weight_g":int(meta.group("weight")),
            "tag_id":meta.group("tag"),
            "night1":flags.group(1).upper()=="X",
            "night2":flags.group(2).upper()=="X",
            "night3":flags.group(3).upper()=="X",
            "parse_ok":True,
        })
    return out


def parse_appendix4(text: str) -> list[dict]:
    section=_section(
        text,
        "Appendix 4.  Distances between burrows",
        "Appendix 5.  Captures and observations",
    )
    lines=section.splitlines()
    records=[]
    season=None
    current=None

    def finish():
        nonlocal current
        if current is None:
            return
        records.append(current)
        current=None

    for raw in lines:
        line=" ".join(raw.strip().split())
        if not line:
            continue
        sm=re.fullmatch(r"(Summer|Winter)\s+(2006|2007|2008)",line,re.I)
        if sm:
            finish()
            season=f"{sm.group(1).title()} {sm.group(2)}"
            continue
        m=BURROW_START.match(line)
        if m:
            finish()
            current={
                "season":season,
                "parts":[line],
            }
            continue
        if current is not None:
            if (
                line.isdigit()
                or line.startswith("Appendix 4 continued")
                or line.startswith("ID Age Sex Reproductive condition")
                or line.startswith("Number of burrows")
            ):
                continue
            current["parts"].append(line)
    finish()

    out=[]
    for rec in records:
        if rec["season"] not in {"Summer 2006","Summer 2007"}:
            continue
        body=" ".join(rec["parts"])
        body=" ".join(body.split())
        m=BURROW_ROW.match(body)
        if not m:
            out.append({
                "season":rec["season"],
                "parse_ok":False,
                "parse_reason":"header_fields_not_parseable",
                "raw_body":body,
            })
            continue
        condition=normalize_condition(m.group("condition"))
        age=m.group("age").lower()
        sex=infer_sex(age=age,condition=condition)
        n4=None if m.group("n4")=="-" else int(m.group("n4"))
        n7=None if m.group("n7")=="-" else int(m.group("n7"))
        out.append({
            "season":rec["season"],
            "id":m.group("id"),
            "age":age,
            "condition":condition,
            "sex_inferred":sex,
            "weight_g":int(m.group("weight")),
            "burrows_4n":n4,
            "burrows_7n":n7,
            "parse_ok":True,
        })
    return out


def trap_xy(trap_location: str) -> tuple[float,float]:
    m=re.fullmatch(r"([A-J])(10|[1-9])",str(trap_location))
    if not m:
        raise ValueError(f"invalid trap location: {trap_location}")
    row=ord(m.group(1))-ord("A")
    col=int(m.group(2))-1
    return float(col*10),float(row*10)


def summarize_estimability(captures: list[dict], burrows: list[dict]) -> dict:
    seasons={}
    for season in ("Summer 2006","Summer 2007"):
        cap=[
            r for r in captures
            if r.get("season")==season
            and r.get("parse_ok")
            and r.get("age")=="adult"
            and r.get("sex_inferred") in {"M","F"}
            and r.get("tag_id")
        ]
        bur=[
            r for r in burrows
            if r.get("season")==season
            and r.get("parse_ok")
            and r.get("age")=="ad"
            and r.get("sex_inferred") in {"M","F"}
            and r.get("burrows_4n") is not None
        ]

        night_counts=[]
        usable_nights=0
        for night in (1,2,3):
            active=[
                r for r in cap
                if r[f"night{night}"]
            ]
            n_m=sum(r["sex_inferred"]=="M" for r in active)
            n_f=sum(r["sex_inferred"]=="F" for r in active)
            eligible=n_m>=3 and n_f>=3
            usable_nights+=eligible
            night_counts.append({
                "night":night,
                "n_male":n_m,
                "n_female":n_f,
                "eligible_n3":eligible,
            })

        bur_counts={
            sex:sum(r["sex_inferred"]==sex for r in bur)
            for sex in ("M","F")
        }
        cap_by_id={
            r["tag_id"]:r["sex_inferred"]
            for r in cap
        }
        bur_by_id={
            r["id"]:r["sex_inferred"]
            for r in bur
        }
        linked={
            sex:sorted(
                ident for ident in set(cap_by_id)&set(bur_by_id)
                if cap_by_id[ident]==sex
                and bur_by_id[ident]==sex
            )
            for sex in ("M","F")
        }
        sex_conflicts=sorted(
            ident for ident in set(cap_by_id)&set(bur_by_id)
            if cap_by_id[ident]!=bur_by_id[ident]
        )

        packing_pass=usable_nights>=2
        burrow_pass=bur_counts["M"]>=3 and bur_counts["F"]>=3
        linkage_pass=len(linked["M"])>=2 and len(linked["F"])>=2

        seasons[season]={
            "capture_records_sex_diagnostic":len(cap),
            "night_counts":night_counts,
            "usable_nights_n3":usable_nights,
            "burrow_records_sex_diagnostic":len(bur),
            "burrow_counts":{"male":bur_counts["M"],"female":bur_counts["F"]},
            "linked_ids":{
                "male":linked["M"],
                "female":linked["F"],
            },
            "linked_counts":{
                "male":len(linked["M"]),
                "female":len(linked["F"]),
            },
            "linkage_sex_conflicts":sex_conflicts,
            "packing_gate_passed":packing_pass,
            "burrow_gate_passed":burrow_pass,
            "linkage_gate_passed":linkage_pass,
            "season_gate_passed":packing_pass and burrow_pass and linkage_pass,
        }

    passed=all(row["season_gate_passed"] for row in seasons.values())
    return {
        "schema":"neon.auburn_dordii_crossscale_case.estimability.v1",
        "seasons":seasons,
        "gate":{
            "every_summer_must_pass":True,
            "passed":passed,
            "decision":(
                "authorize_auburn_case_effect_lock"
                if passed else
                "stop_auburn_case_not_estimable"
            ),
        },
        "appendix2_total_parsed_records":sum(r.get("parse_ok",False) for r in captures),
        "appendix2_parse_failures":sum(not r.get("parse_ok",False) for r in captures),
        "appendix4_total_parsed_records":sum(r.get("parse_ok",False) for r in burrows),
        "appendix4_parse_failures":sum(not r.get("parse_ok",False) for r in burrows),
        "packing_effects_inspected":False,
        "burrow_use_effects_inspected":False,
        "ecological_effect_models_fit":0,
    }


def run(path: Path) -> dict:
    raw=path.read_bytes()
    text=raw.decode("utf-8-sig",errors="replace")
    captures=parse_appendix2(text)
    burrows=parse_appendix4(text)
    out=summarize_estimability(captures,burrows)
    out.update({
        "source_file":path.name,
        "source_size_bytes":len(raw),
        "source_sha256":hashlib.sha256(raw).hexdigest(),
    })
    return out


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    out=run(args.input)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
