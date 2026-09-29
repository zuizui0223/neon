from __future__ import annotations

import argparse
import csv
import hashlib
import json
import urllib.request
from collections import Counter, defaultdict
from datetime import date as Date
from pathlib import Path


def download_verified(url: str, expected_sha256: str, path: Path) -> bytes:
    req=urllib.request.Request(url,headers={"User-Agent":"san-jacinto-semantic-audit/1.0"})
    with urllib.request.urlopen(req,timeout=180) as response:
        raw=response.read()
    actual=hashlib.sha256(raw).hexdigest()
    if actual != expected_sha256:
        raise RuntimeError(f"source sha256 mismatch: {actual} != {expected_sha256}")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw)
    return raw


def _clean(value: object) -> str:
    return str(value or "").strip()


def _parse_date(value: str) -> Date | None:
    text=_clean(value)
    for sep in ("/","-"):
        parts=text.split(sep)
        if len(parts)==3:
            try:
                nums=[int(float(x)) for x in parts]
            except ValueError:
                continue
            # support mm/dd/yyyy and yyyy-mm-dd
            if nums[0] > 1900:
                y,m,d=nums
            else:
                m,d,y=nums
            try:
                return Date(y,m,d)
            except ValueError:
                continue
    return None


def audit_rows(rows: list[dict]) -> dict:
    required=[
        "date","time_bin","time","grid","flag","species",
        "unique_ID","history","sex",
    ]
    if not rows:
        raise RuntimeError("no capture rows")
    missing_columns=[x for x in required if x not in rows[0]]
    if missing_columns:
        raise RuntimeError(f"missing expected columns: {missing_columns}")

    grid_flags=defaultdict(set)
    time_bins=set()
    sex_codes=set()
    history_codes=set()
    parsed_dates=[]
    missing=Counter()
    slot_counts=Counter()
    id_species=defaultdict(set)
    id_sex=defaultdict(set)

    for row in rows:
        grid=_clean(row.get("grid"))
        flag=_clean(row.get("flag"))
        time_bin=_clean(row.get("time_bin"))
        uid=_clean(row.get("unique_ID"))
        species=_clean(row.get("species"))
        sex=_clean(row.get("sex"))
        history=_clean(row.get("history"))
        d=_parse_date(_clean(row.get("date")))

        for col in required:
            if not _clean(row.get(col)):
                missing[col]+=1

        if grid and flag:
            grid_flags[grid].add(flag)
        if time_bin:
            time_bins.add(time_bin)
        if sex:
            sex_codes.add(sex)
        if history:
            history_codes.add(history)
        if d is not None:
            parsed_dates.append(d)

        if grid and flag and time_bin and d is not None:
            slot_counts[(grid,d.isoformat(),time_bin,flag)]+=1
        if uid and species:
            id_species[uid].add(species)
        if uid and sex:
            id_sex[uid].add(sex)

    slot_violations=[
        {"grid":k[0],"date":k[1],"time_bin":k[2],"flag":k[3],"capture_rows":n}
        for k,n in slot_counts.items() if n>1
    ]

    grid_flag_counts={grid:len(flags) for grid,flags in sorted(grid_flags.items())}
    grid_flag_examples={
        grid:sorted(flags,key=lambda x:(len(x),x))[:60]
        for grid,flags in sorted(grid_flags.items())
    }

    species_conflict_ids=sum(len(v)>1 for v in id_species.values())
    sex_conflict_ids=sum(len(v)>1 for v in id_sex.values())

    return {
        "schema":"neon.san_jacinto_crossscale.capture_semantics_audit.v1",
        "row_count":len(rows),
        "grid_values":sorted(grid_flags),
        "grid_flag_counts":grid_flag_counts,
        "grid_flag_examples":grid_flag_examples,
        "time_bin_values":sorted(time_bins),
        "sex_code_values":sorted(sex_codes),
        "history_code_values":sorted(history_codes),
        "date_min":min(parsed_dates).isoformat() if parsed_dates else None,
        "date_max":max(parsed_dates).isoformat() if parsed_dates else None,
        "parsed_date_rows":len(parsed_dates),
        "missing_structural_fields":dict(sorted(missing.items())),
        "capture_slot_count":len(slot_counts),
        "capture_slot_duplicate_count":len(slot_violations),
        "capture_slot_duplicate_excess":sum(x["capture_rows"]-1 for x in slot_violations),
        "capture_slot_duplicate_examples":slot_violations[:20],
        "individual_id_species_conflict_count":species_conflict_ids,
        "individual_id_sex_conflict_count":sex_conflict_ids,
        "expected_grid_flags_per_grid":49,
        "expected_time_bins_per_night":3,
        "geometry_support_compatible":(
            bool(grid_flag_counts)
            and all(n==49 for n in grid_flag_counts.values())
            and len(time_bins)==3
        ),
        "trap_interval_slot_uniqueness_passed":len(slot_violations)==0,
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
    source=next(
        row for row in receipt["files"]
        if row["name"]=="year round trap data.csv"
    )
    raw=download_verified(source["download_url"],source["sha256"],args.cache)
    text=raw.decode("utf-8-sig",errors="strict")
    rows=list(csv.DictReader(text.splitlines()))

    out=audit_rows(rows)
    out.update({
        "source_file":"year round trap data.csv",
        "source_sha256":source["sha256"],
        "figshare_article_id":receipt["figshare_article_id"],
        "source_doi":receipt["doi"],
    })

    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
