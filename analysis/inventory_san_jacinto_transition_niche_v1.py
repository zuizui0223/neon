from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ARTICLE_ID = 18295520
API_URL = f"https://api.figshare.com/v2/articles/{ARTICLE_ID}"
CAPTURE_FILE_ID = 33058799
CAPTURE_SHA256 = "ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
CANONICAL_FLAGS = {f"{r}{c}" for r in "ABCDEFG" for c in range(1, 8)}


def clean(x: object) -> str:
    return str(x or "").strip()


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "neon-transition-niche-inventory/1.0"})
    with urllib.request.urlopen(req, timeout=180) as response:
        return response.read()


def parse_time(x: object) -> float | None:
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", clean(x))
    if not m:
        return None
    h = int(m.group(1))
    minute = int(m.group(2))
    if minute >= 60:
        return None
    if 7 <= h <= 11:
        h += 12
    elif h == 12:
        h = 24
    elif 0 <= h <= 6:
        h += 24
    else:
        return None
    return h + minute / 60.0


def parse_date(x: object) -> datetime | None:
    s = clean(x)
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d", "%m-%d-%Y", "%m-%d-%y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None


def summarize_capture_rows(rows: list[dict]) -> dict:
    species_rows = defaultdict(int)
    individuals = defaultdict(set)
    valid_rows = defaultdict(int)
    date_values = defaultdict(list)
    groups = defaultdict(list)

    required = {"species", "unique_ID", "grid", "date", "time", "flag"}
    columns = sorted({k for row in rows for k in row.keys() if k is not None})
    missing = sorted(required - set(columns))

    for idx, row in enumerate(rows):
        species = clean(row.get("species"))
        if not species:
            continue
        species_rows[species] += 1

        uid = clean(row.get("unique_ID"))
        grid = clean(row.get("grid"))
        date_s = clean(row.get("date"))
        flag = clean(row.get("flag")).upper()
        t = parse_time(row.get("time"))
        dt = parse_date(date_s)

        if uid:
            individuals[species].add((grid, uid))
        if dt is not None:
            date_values[species].append(dt)

        if uid and grid and date_s and flag in CANONICAL_FLAGS and t is not None:
            valid_rows[species] += 1
            groups[(species, grid, uid, date_s)].append((t, idx, dt))

    repeat_nights = defaultdict(int)
    consecutive_transitions = defaultdict(int)
    summer_repeat_nights = defaultdict(int)
    summer_transitions = defaultdict(int)

    for (species, _grid, _uid, _date), items in groups.items():
        if len(items) < 2:
            continue
        items = sorted(items)
        repeat_nights[species] += 1
        consecutive_transitions[species] += len(items) - 1
        dt = next((x[2] for x in items if x[2] is not None), None)
        if dt is not None and dt.year == 2016 and 5 <= dt.month <= 7:
            summer_repeat_nights[species] += 1
            summer_transitions[species] += len(items) - 1

    species_summary = {}
    for species in sorted(species_rows):
        dates = sorted(date_values.get(species, []))
        species_summary[species] = {
            "rows": species_rows[species],
            "unique_individuals_with_id": len(individuals.get(species, set())),
            "valid_spatiotemporal_rows": valid_rows.get(species, 0),
            "repeat_capture_nights": repeat_nights.get(species, 0),
            "consecutive_within_night_transition_count": consecutive_transitions.get(species, 0),
            "may_july_2016_repeat_capture_nights": summer_repeat_nights.get(species, 0),
            "may_july_2016_consecutive_transition_count": summer_transitions.get(species, 0),
            "date_min": dates[0].date().isoformat() if dates else None,
            "date_max": dates[-1].date().isoformat() if dates else None,
        }

    env_tokens = ("veget", "soil", "habitat", "shrub", "forb", "grass", "litter", "debris", "sand", "silt", "clay")
    possible_environment_columns = [
        c for c in columns if any(tok in c.lower() for tok in env_tokens)
    ]

    return {
        "columns": columns,
        "required_capture_columns_missing": missing,
        "possible_environment_columns": possible_environment_columns,
        "species": species_summary,
    }


def read_csv_header(raw: bytes) -> list[str]:
    text = raw.decode("utf-8-sig", errors="replace")
    reader = csv.reader(io.StringIO(text))
    return next(reader, [])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    metadata = json.loads(fetch_bytes(API_URL).decode("utf-8"))
    files = metadata.get("files", [])
    inventory = []

    capture_file = None
    for f in files:
        rec = {
            "id": f.get("id"),
            "name": f.get("name"),
            "size": f.get("size"),
            "download_url": f.get("download_url"),
            "is_link_only": f.get("is_link_only"),
            "supplied_md5": f.get("supplied_md5"),
            "computed_md5": f.get("computed_md5"),
        }
        name = clean(f.get("name"))
        url = clean(f.get("download_url"))
        size = int(f.get("size") or 0)
        if name.lower().endswith(".csv") and url and size <= 5_000_000:
            try:
                rec["csv_header"] = read_csv_header(fetch_bytes(url))
            except Exception as exc:
                rec["csv_header_error"] = type(exc).__name__
        inventory.append(rec)
        if int(f.get("id") or -1) == CAPTURE_FILE_ID:
            capture_file = f

    if capture_file is None:
        raise RuntimeError(f"capture file id {CAPTURE_FILE_ID} absent from Figshare metadata")

    raw = fetch_bytes(capture_file["download_url"])
    actual_sha = hashlib.sha256(raw).hexdigest()
    if actual_sha != CAPTURE_SHA256:
        raise RuntimeError(f"capture source checksum mismatch: {actual_sha}")

    rows = list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    capture_summary = summarize_capture_rows(rows)

    env_file_tokens = ("veget", "soil", "habitat", "resource", "microhab", "cover")
    possible_environment_files = [
        {
            "id": x["id"],
            "name": x["name"],
            "size": x["size"],
            "csv_header": x.get("csv_header"),
        }
        for x in inventory
        if any(tok in clean(x.get("name")).lower() for tok in env_file_tokens)
    ]

    result = {
        "schema": "neon.san_jacinto_transition_niche_inventory.v1",
        "status": "stage0_feasibility_only_no_transition_outcomes_opened",
        "article_id": ARTICLE_ID,
        "article_title": metadata.get("title"),
        "article_version": metadata.get("version"),
        "article_doi": metadata.get("doi"),
        "file_count": len(inventory),
        "files": inventory,
        "capture_file": {
            "id": CAPTURE_FILE_ID,
            "sha256_verified": True,
            "row_count": len(rows),
            **capture_summary,
        },
        "possible_environment_files": possible_environment_files,
        "stage0_claim_boundary": {
            "transition_distances_opened": False,
            "transition_directions_opened": False,
            "habitat_transition_differences_opened": False,
            "species_transition_kernels_opened": False,
            "community_cscore_transition_effect_opened": False,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
