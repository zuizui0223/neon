from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import urllib.request
from collections import Counter, defaultdict
from datetime import date as Date
from pathlib import Path

CANONICAL_FLAGS={f"{row}{col}" for row in "ABCDEFG" for col in range(1,8)}
CANONICAL_TIME_BINS={"early","middle","late"}


def download_verified(url: str, expected_sha256: str, path: Path) -> bytes:
    req=urllib.request.Request(url,headers={"User-Agent":"san-jacinto-semantic-audit-v2/1.0"})
    with urllib.request.urlopen(req,timeout=180) as response:
        raw=response.read()
    actual=hashlib.sha256(raw).hexdigest()
    if actual != expected_sha256:
        raise RuntimeError(f"source sha256 mismatch: {actual} != {expected_sha256}")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw)
    return raw


def clean(value: object) -> str:
    return str(value or "").strip()


def normalize_flag(value: object) -> str:
    return clean(value).upper()


def normalize_sex(value: object) -> str | None:
    value=clean(value).upper()
    return value if value in {"M","F"} else None


def parse_date(value: object) -> Date | None:
    text=clean(value)
    for sep in ("/","-"):
        parts=text.split(sep)
        if len(parts)!=3:
            continue
        try:
            nums=[int(float(x)) for x in parts]
        except ValueError:
            continue
        if nums[0] > 1900:
            y,m,d=nums
        else:
            m,d,y=nums
            if y < 100:
                y += 2000
        try:
            return Date(y,m,d)
        except ValueError:
            continue
    return None


def audit_rows(rows: list[dict]) -> dict:
    if not rows:
        raise RuntimeError("no capture rows")

    required=("date","time_bin","time","grid","flag","species","unique_ID","history","sex")
    missing_columns=[x for x in required if x not in rows[0]]
    if missing_columns:
        raise RuntimeError(f"missing expected columns: {missing_columns}")

    missing=Counter()
    time_bins=set()
    grids=set()
    flags_seen=defaultdict(set)
    noncanonical=Counter()
    dates=[]
    history_codes=set()
    sex_codes=set()

    exact_rows=Counter()
    slot_rows=defaultdict(list)
    identity_sexes=defaultdict(set)

    for row in rows:
        for col in required:
            if not clean(row.get(col)):
                missing[col]+=1

        grid=clean(row.get("grid"))
        flag=normalize_flag(row.get("flag"))
        time_bin=clean(row.get("time_bin")).lower()
        species=clean(row.get("species"))
        uid=clean(row.get("unique_ID"))
        history=clean(row.get("history")).upper()
        sex=normalize_sex(row.get("sex"))
        d=parse_date(row.get("date"))

        if grid:
            grids.add(grid)
        if grid and flag:
            flags_seen[grid].add(flag)
            if flag not in CANONICAL_FLAGS:
                noncanonical[(grid,flag)]+=1
        if time_bin:
            time_bins.add(time_bin)
        if d:
            dates.append(d)
        if history:
            history_codes.add(history)
        raw_sex=clean(row.get("sex"))
        if raw_sex:
            sex_codes.add(raw_sex)

        exact_key=tuple(clean(row.get(col)) for col in rows[0].keys())
        exact_rows[exact_key]+=1

        if grid and flag and time_bin and d:
            slot=(grid,d.isoformat(),time_bin,flag)
            slot_rows[slot].append({
                "unique_ID":uid,
                "species":species,
                "sex":clean(row.get("sex")),
                "history":clean(row.get("history")),
                "time":clean(row.get("time")),
            })

        if grid and species and uid and sex:
            identity_sexes[(grid,species,uid)].add(sex)

    exact_duplicate_excess=sum(n-1 for n in exact_rows.values() if n>1)
    duplicate_slots={k:v for k,v in slot_rows.items() if len(v)>1}
    multi_individual_slots={
        k:v for k,v in duplicate_slots.items()
        if len({x["unique_ID"] for x in v if x["unique_ID"]})>1
    }
    same_individual_repeat_slots={
        k:v for k,v in duplicate_slots.items()
        if len({x["unique_ID"] for x in v if x["unique_ID"]})<=1
    }

    def slot_examples(mapping: dict, limit: int=25) -> list[dict]:
        out=[]
        for k,v in list(sorted(mapping.items()))[:limit]:
            out.append({
                "grid":k[0],"date":k[1],"time_bin":k[2],"flag":k[3],
                "rows":v,
            })
        return out

    grid_dates=defaultdict(set)
    for row in rows:
        grid=clean(row.get("grid"))
        d=parse_date(row.get("date"))
        if grid and d:
            grid_dates[grid].add(d)
    grid_date_counts={g:len(v) for g,v in sorted(grid_dates.items())}

    # Structural monthly bout diagnostic: start a new block whenever capture
    # dates within a grid are separated by > 2 days.
    grid_bout_lengths={}
    for grid,dset in sorted(grid_dates.items()):
        ordered=sorted(dset)
        bouts=[]
        current=[]
        for d in ordered:
            if current and (d-current[-1]).days>2:
                bouts.append(current)
                current=[]
            current.append(d)
        if current:
            bouts.append(current)
        grid_bout_lengths[grid]=[len(x) for x in bouts]

    sex_conflicts=sum(len(v)>1 for v in identity_sexes.values())

    return {
        "schema":"neon.san_jacinto_crossscale.capture_semantics_audit.v2",
        "audit_revision":"correct two-digit years; fixed canonical 7x7 geometry; decompose slot duplicates; grid-species-ID sex consistency",
        "row_count":len(rows),
        "date_min":min(dates).isoformat() if dates else None,
        "date_max":max(dates).isoformat() if dates else None,
        "grid_values":sorted(grids),
        "grid_distinct_capture_date_counts":grid_date_counts,
        "grid_bout_date_lengths":grid_bout_lengths,
        "time_bin_values":sorted(time_bins),
        "time_bin_canonical_passed":time_bins==CANONICAL_TIME_BINS,
        "sex_raw_code_values":sorted(sex_codes),
        "history_code_values":sorted(history_codes),
        "missing_structural_fields":dict(sorted(missing.items())),
        "canonical_geometry":{
            "rows":"A-G",
            "columns":"1-7",
            "flag_count":49,
            "spacing_m":6.25,
            "source":"published fixed 7x7 grid design",
        },
        "observed_capture_flag_counts_by_grid":{
            grid:len(flags) for grid,flags in sorted(flags_seen.items())
        },
        "noncanonical_flag_row_count":sum(noncanonical.values()),
        "noncanonical_flag_values":[
            {"grid":g,"flag":f,"rows":n}
            for (g,f),n in sorted(noncanonical.items())
        ],
        "all_observed_flags_compatible_with_canonical_geometry":not noncanonical,
        "exact_duplicate_row_excess":exact_duplicate_excess,
        "duplicate_capture_slot_count":len(duplicate_slots),
        "duplicate_capture_slot_excess":sum(len(v)-1 for v in duplicate_slots.values()),
        "multi_individual_capture_slot_count":len(multi_individual_slots),
        "same_individual_repeat_slot_count":len(same_individual_repeat_slots),
        "multi_individual_capture_slot_examples":slot_examples(multi_individual_slots),
        "same_individual_repeat_slot_examples":slot_examples(same_individual_repeat_slots),
        "grid_species_identity_sex_conflict_count":sex_conflicts,
        "geometry_semantics_passed":(
            not noncanonical
            and time_bins==CANONICAL_TIME_BINS
        ),
        "species_specific_support_counts_inspected":False,
        "sex_specific_support_counts_inspected":False,
        "movement_distances_computed":False,
        "packing_effects_computed":False,
        "ecological_effect_models_fit":0,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-receipt",type=Path,required=True)
    parser.add_argument("--cache",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()

    receipt=json.loads(args.source_receipt.read_text())
    source=next(x for x in receipt["files"] if x["name"]=="year round trap data.csv")
    raw=download_verified(source["download_url"],source["sha256"],args.cache)
    rows=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    out=audit_rows(rows)
    out.update({
        "source_file":source["name"],
        "source_sha256":source["sha256"],
        "source_doi":receipt["doi"],
        "figshare_article_id":receipt["figshare_article_id"],
    })
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
