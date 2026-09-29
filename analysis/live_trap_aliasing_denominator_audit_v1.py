from __future__ import annotations

# AI assistance disclosure: This file was drafted or refactored with OpenAI ChatGPT (GPT-5.6 Sol, September 2026); it remains under author responsibility and is verified by repository tests/workflows.

import argparse
import csv
import hashlib
import json
import math
import re
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

SPECIES={
    "PEMA":"Peromyscus maniculatus",
    "PEER":"Peromyscus eremicus",
}
FLAGS={f"{r}{c}" for r in "ABCDEFG" for c in range(1,8)}
XY={
    f"{r}{c}":((c-1)*6.25,i*6.25)
    for i,r in enumerate("ABCDEFG")
    for c in range(1,8)
}
URL="https://ndownloader.figshare.com/files/33058799"
SHA256="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"


def clean(x: object) -> str:
    return str(x or "").strip()


def parse_time(x: object) -> float | None:
    m=re.fullmatch(r"(\d{1,2}):(\d{2})",clean(x))
    if not m:
        return None
    h=int(m.group(1)); minute=int(m.group(2))
    if minute>=60:
        return None
    if 7<=h<=11:
        h+=12
    elif h==12:
        h=24
    elif 0<=h<=6:
        h+=24
    else:
        return None
    return h+minute/60


def distance(a: str,b: str) -> float:
    x1,y1=XY[a]; x2,y2=XY[b]
    return math.hypot(x2-x1,y2-y1)


def audit(rows: list[dict], frozen_result: dict) -> dict:
    grouped=defaultdict(list)
    excluded=Counter()

    for idx,row in enumerate(rows):
        sp=clean(row.get("species"))
        if sp not in SPECIES:
            continue
        uid=clean(row.get("unique_ID"))
        grid=clean(row.get("grid"))
        date=clean(row.get("date"))
        flag=clean(row.get("flag")).upper()
        time=parse_time(row.get("time"))

        if not uid:
            excluded["missing_id"]+=1; continue
        if not grid:
            excluded["missing_grid"]+=1; continue
        if not date:
            excluded["missing_date"]+=1; continue
        if flag not in FLAGS:
            excluded["invalid_flag"]+=1; continue
        if time is None:
            excluded["invalid_time"]+=1; continue

        grouped[(sp,grid,uid,date)].append({
            "idx":idx,"flag":flag,"time":time,
        })

    species={}
    for sp,name in SPECIES.items():
        groups=[
            (key,items) for key,items in grouped.items()
            if key[0]==sp
        ]
        total=len(groups)
        repeat=[(k,v) for k,v in groups if len(v)>=2]

        expected=int(frozen_result["species"][sp]["repeat_capture_nights"])
        if len(repeat)!=expected:
            raise RuntimeError(
                f"{sp} repeat nights {len(repeat)} != frozen result {expected}"
            )

        shifted=0
        any_change=0
        by_grid=Counter()
        by_grid_total=Counter()
        by_grid_repeat=Counter()

        for key,items in groups:
            grid=key[1]
            by_grid_total[grid]+=1
            if len(items)<2:
                continue
            by_grid_repeat[grid]+=1
            first=min(items,key=lambda x:(x["time"],x["idx"]))
            last=max(items,key=lambda x:(x["time"],x["idx"]))
            d=distance(first["flag"],last["flag"])
            if first["flag"]!=last["flag"]:
                any_change+=1
            if d>=6.25-1e-12:
                shifted+=1
                by_grid[grid]+=1

        frozen_shift=int(frozen_result["species"][sp]["one_spacing_shift_count"])
        if shifted!=frozen_shift:
            raise RuntimeError(
                f"{sp} shifted nights {shifted} != frozen result {frozen_shift}"
            )

        species[sp]={
            "scientific_name":name,
            "all_valid_individual_nights":total,
            "repeat_capture_individual_nights":len(repeat),
            "repeat_capture_fraction":len(repeat)/total if total else None,
            "one_spacing_shift_observed_nights":shifted,
            "observed_one_spacing_aliasing_lower_bound_fraction_all_nights":(
                shifted/total if total else None
            ),
            "any_flag_change_observed_nights":any_change,
            "observed_any_change_lower_bound_fraction_all_nights":(
                any_change/total if total else None
            ),
            "single_capture_or_unresolved_within_night_count":total-len(repeat),
            "interpretation":(
                "The all-night fractions are observational lower bounds: "
                "single-capture nights cannot reveal first-to-last positional change."
            ),
            "grid_all_nights":dict(sorted(by_grid_total.items())),
            "grid_repeat_nights":dict(sorted(by_grid_repeat.items())),
            "grid_observed_one_spacing_shift_nights":dict(sorted(by_grid.items())),
        }

    return {
        "schema":"neon.live_trap_aliasing.denominator_audit.v1",
        "species":species,
        "primary_result_unchanged":True,
        "inferential_role":"post_result_denominator_context_only",
        "claim":"observed aliasing exposure among all valid individual-nights is a lower bound, not an estimate of latent movement on single-capture nights",
    }


def download() -> list[dict]:
    req=urllib.request.Request(URL,headers={"User-Agent":"live-trap-aliasing-denominator-audit/1.0"})
    with urllib.request.urlopen(req,timeout=180) as response:
        raw=response.read()
    if hashlib.sha256(raw).hexdigest()!=SHA256:
        raise RuntimeError("source checksum mismatch")
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--frozen-result",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()

    result=audit(
        download(),
        json.loads(args.frozen_result.read_text()),
    )
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
