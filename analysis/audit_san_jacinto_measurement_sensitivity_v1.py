from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import statistics
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def _load(name: str, rel: str):
    path=ROOT/rel
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EFFECT=_load(
    "san_jacinto_effects",
    "analysis/san_jacinto_crossscale_effects_v1.py",
)


def median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    xs=sorted(float(x) for x in values)
    if len(xs)==1:
        return xs[0]
    pos=(len(xs)-1)*q
    lo=int(math.floor(pos))
    hi=int(math.ceil(pos))
    if lo==hi:
        return xs[lo]
    w=pos-lo
    return xs[lo]*(1-w)+xs[hi]*w


def compare_states(first: list[dict], last: list[dict]) -> dict:
    def key(x: dict):
        return (
            x["grid"],x["species"],x["unique_ID"],
            x["bout_id"],x["date"],
        )

    a={key(x):x for x in first}
    b={key(x):x for x in last}
    shared=sorted(set(a)&set(b))
    if len(shared)!=len(a) or len(shared)!=len(b):
        raise RuntimeError(
            f"first/last nightly identity sets differ: "
            f"first={len(a)}, last={len(b)}, shared={len(shared)}"
        )

    by_species=defaultdict(lambda:{
        "nightly_states":0,
        "different_flag":0,
        "distances":[],
        "time_spans":[],
    })
    distances=[]
    time_spans=[]
    changed=0

    for k in shared:
        left=a[k]
        right=b[k]
        species=left["species"]
        rec=by_species[species]
        rec["nightly_states"]+=1

        span=float(right["nocturnal_time"])-float(left["nocturnal_time"])
        if span< -1e-12:
            raise RuntimeError("last nocturnal time precedes first")
        rec["time_spans"].append(span)
        time_spans.append(span)

        x1,y1=EFFECT.flag_xy(left["flag"])
        x2,y2=EFFECT.flag_xy(right["flag"])
        d=math.hypot(x2-x1,y2-y1)
        rec["distances"].append(d)
        distances.append(d)
        if left["flag"]!=right["flag"]:
            changed+=1
            rec["different_flag"]+=1

    species_summary={}
    for species,rec in sorted(by_species.items()):
        n=rec["nightly_states"]
        species_summary[species]={
            "nightly_states":n,
            "first_last_flag_different_count":rec["different_flag"],
            "first_last_flag_different_fraction":(
                rec["different_flag"]/n if n else None
            ),
            "median_first_last_distance_m":median(rec["distances"]),
            "q90_first_last_distance_m":quantile(rec["distances"],0.9),
            "max_first_last_distance_m":max(rec["distances"]) if rec["distances"] else None,
            "median_first_last_time_span_hours":median(rec["time_spans"]),
        }

    n=len(shared)
    return {
        "nightly_states":n,
        "first_last_flag_different_count":changed,
        "first_last_flag_different_fraction":changed/n if n else None,
        "median_first_last_distance_m":median(distances),
        "q90_first_last_distance_m":quantile(distances,0.9),
        "max_first_last_distance_m":max(distances) if distances else None,
        "median_first_last_time_span_hours":median(time_spans),
        "q90_first_last_time_span_hours":quantile(time_spans,0.9),
        "species":species_summary,
    }


def download_rows(source_receipt: dict) -> list[dict]:
    source=next(
        x for x in source_receipt["files"]
        if x["name"]=="year round trap data.csv"
    )
    req=urllib.request.Request(
        source["download_url"],
        headers={"User-Agent":"san-jacinto-postresult-measurement-audit/1.0"},
    )
    with urllib.request.urlopen(req,timeout=180) as response:
        raw=response.read()
    actual=hashlib.sha256(raw).hexdigest()
    if actual!=source["sha256"]:
        raise RuntimeError("source checksum mismatch")
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))


def audit(source_receipt: dict, result: dict) -> dict:
    rows=download_rows(source_receipt)
    first,_=EFFECT.nightly_states_selection(rows,selection="first")
    last,_=EFFECT.nightly_states_selection(rows,selection="last")
    comparison=compare_states(first,last)

    return {
        "schema":"neon.san_jacinto_crossscale.postresult_measurement_sensitivity.v1",
        "date":"2026-09-29",
        "inferential_role":"post_result_explanatory_only",
        "primary_decision":result["primary"]["decision"]["decision"],
        "primary_family_effects":{
            "packing":result["primary"]["packing"]["family"]["effect"],
            "movement":result["primary"]["movement"]["family"]["effect"],
        },
        "last_capture_family_effects":{
            "packing":result["sensitivities"]["last_nightly_capture"]["packing"]["family"]["effect"],
            "movement":result["sensitivities"]["last_nightly_capture"]["movement"]["family"]["effect"],
        },
        "first_last_nightly_state_comparison":comparison,
        "ruling":(
            "The movement endpoint is timing-definition-sensitive: first-versus-last "
            "nightly representative locations can change between captures within a night. "
            "This audit is explanatory only and cannot rescue or redefine the frozen primary decision."
        ),
        "can_change_primary_decision":False,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-receipt",type=Path,required=True)
    parser.add_argument("--result",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()

    out=audit(
        json.loads(args.source_receipt.read_text()),
        json.loads(args.result.read_text()),
    )
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    raise SystemExit(main())
