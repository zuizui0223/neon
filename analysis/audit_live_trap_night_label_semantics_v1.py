from __future__ import annotations

# AI assistance disclosure: This audit was drafted with OpenAI ChatGPT
# (GPT-5.6 Sol, September 2026) and is verified by repository tests/workflows.

import argparse
import csv
import hashlib
import json
import re
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

URL="https://ndownloader.figshare.com/files/33058799"
SHA256="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
BINS={"early","middle","late"}


def clean(x: object) -> str:
    return str(x or "").strip()


def parse_date(text: object) -> datetime | None:
    value=clean(text)
    for fmt in ("%m/%d/%y","%m/%d/%Y","%Y-%m-%d"):
        try:
            return datetime.strptime(value,fmt)
        except ValueError:
            pass
    return None


def parse_clock_hour(text: object) -> tuple[int,int] | None:
    m=re.fullmatch(r"(\d{1,2}):(\d{2})",clean(text))
    if not m:
        return None
    h=int(m.group(1)); minute=int(m.group(2))
    if not (0<=h<=12 and 0<=minute<60):
        return None
    return h,minute


def nocturnal_hour(text: object) -> float | None:
    parsed=parse_clock_hour(text)
    if parsed is None:
        return None
    h,minute=parsed
    if 7<=h<=11:
        base=h+12
    elif h==12:
        base=24
    elif 0<=h<=6:
        base=h+24
    else:
        return None
    return base+minute/60.0


def literal_calendar_night_label(date_text: object, time_text: object) -> str | None:
    d=parse_date(date_text)
    t=parse_clock_hour(time_text)
    if d is None or t is None:
        return None
    h,_=t
    if h==12 or 0<=h<=6:
        d=d-timedelta(days=1)
    return d.strftime("%Y-%m-%d")


def raw_date_label(date_text: object) -> str | None:
    d=parse_date(date_text)
    return d.strftime("%Y-%m-%d") if d is not None else None


def grouping_summary(rows: list[dict], *, mode: str) -> dict:
    grouped=defaultdict(set)
    row_counts=Counter()
    for row in rows:
        grid=clean(row.get("grid"))
        time_bin=clean(row.get("time_bin")).lower()
        if not grid or time_bin not in BINS:
            continue
        if mode=="raw":
            label=raw_date_label(row.get("date"))
        elif mode=="literal_calendar_shift":
            label=literal_calendar_night_label(row.get("date"),row.get("time"))
        else:
            raise ValueError(mode)
        if label is None:
            continue
        grouped[(grid,label)].add(time_bin)
        row_counts[(grid,label)]+=1

    complete=[key for key,bins in grouped.items() if bins==BINS]
    two_plus=[key for key,bins in grouped.items() if len(bins)>=2]
    return {
        "mode":mode,
        "grid_night_groups":len(grouped),
        "groups_with_all_three_bins":len(complete),
        "groups_with_at_least_two_bins":len(two_plus),
        "complete_fraction":len(complete)/len(grouped) if grouped else None,
        "two_plus_fraction":len(two_plus)/len(grouped) if grouped else None,
        "bin_set_counts":{
            "+".join(sorted(bins)):n
            for bins,n in sorted(
                Counter(tuple(sorted(v)) for v in grouped.values()).items()
            )
        },
        "group_examples":[
            {
                "grid":key[0],
                "night_label":key[1],
                "bins":sorted(grouped[key]),
                "capture_rows":row_counts[key],
            }
            for key in sorted(grouped)[:20]
        ],
    }


def time_bin_order(rows: list[dict]) -> dict:
    values=defaultdict(list)
    invalid=0
    for row in rows:
        b=clean(row.get("time_bin")).lower()
        if b not in BINS:
            continue
        h=nocturnal_hour(row.get("time"))
        if h is None:
            invalid+=1
            continue
        values[b].append(h)

    summary={}
    for b in ("early","middle","late"):
        xs=sorted(values[b])
        if not xs:
            summary[b]=None
            continue
        n=len(xs)
        summary[b]={
            "n":n,
            "min":xs[0],
            "median":xs[n//2] if n%2 else (xs[n//2-1]+xs[n//2])/2,
            "max":xs[-1],
        }

    medians=[summary[b]["median"] for b in ("early","middle","late") if summary[b]]
    return {
        "bins":summary,
        "median_order_early_middle_late":len(medians)==3 and medians[0]<medians[1]<medians[2],
        "invalid_time_rows":invalid,
    }


def audit(rows: list[dict]) -> dict:
    raw=grouping_summary(rows,mode="raw")
    shifted=grouping_summary(rows,mode="literal_calendar_shift")
    order=time_bin_order(rows)

    raw_better=(
        raw["groups_with_all_three_bins"] > shifted["groups_with_all_three_bins"]
        and raw["complete_fraction"] > shifted["complete_fraction"]
    )

    return {
        "schema":"neon.live_trap_aliasing.night_label_semantics_audit.v1",
        "raw_date_grouping":raw,
        "literal_calendar_shift_grouping":shifted,
        "time_bin_order":order,
        "raw_date_supported_as_trapping_night_label":raw_better and order["median_order_early_middle_late"],
        "interpretation":(
            "This structural audit compares the source date as supplied against an "
            "alternative that treats the source date as a literal calendar date and "
            "moves midnight/post-midnight records to the preceding night. The grouping "
            "with greater early+middle+late coherence is better aligned with the "
            "published three-check-per-night protocol."
        ),
        "ecological_effects_inspected":False,
    }


def download_rows() -> list[dict]:
    req=urllib.request.Request(URL,headers={"User-Agent":"live-trap-night-label-audit/1.0"})
    with urllib.request.urlopen(req,timeout=180) as response:
        raw=response.read()
    if hashlib.sha256(raw).hexdigest()!=SHA256:
        raise RuntimeError("source checksum mismatch")
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    out=audit(download_rows())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
