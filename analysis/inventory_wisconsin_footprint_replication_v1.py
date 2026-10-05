from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.parse
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

DOI = "10.5061/dryad.zpc866thw"
DATASET_ZIP_URL = (
    "https://datadryad.org/api/v2/datasets/"
    + urllib.parse.quote("doi:" + DOI, safe="")
    + "/download"
)
CAPTURE_NAME = "CaptureMaster.csv"
MIN_MULTI_NIGHT_INDIVIDUALS_PER_SPECIES = 3
MIN_SPECIES_PER_UNIT = 3
MIN_UNITS = 8


def clean(x: object) -> str:
    s = str(x or "").strip()
    return "" if s.lower() in {"na", "nan", "none"} else s


def parse_date(x: object) -> str | None:
    s = clean(x)
    if not s:
        return None
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def truthy_remove(x: object) -> bool:
    s = clean(x).lower()
    return s in {"1", "1.0", "true", "t", "yes", "y"}


def fetch_dataset_zip() -> bytes:
    req = urllib.request.Request(
        DATASET_ZIP_URL,
        headers={"User-Agent": "neon-wisconsin-footprint-feasibility/1.0"},
    )
    with urllib.request.urlopen(req, timeout=180) as response:
        return response.read()


def extract_capture_csv(raw_zip: bytes) -> tuple[bytes, list[str]]:
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as zf:
        names = zf.namelist()
        matches = [n for n in names if Path(n).name == CAPTURE_NAME]
        if len(matches) != 1:
            raise RuntimeError(f"expected exactly one {CAPTURE_NAME}, found {matches}")
        return zf.read(matches[0]), names


def recap_pairs(row: dict) -> list[tuple[str, str]]:
    out = []
    for k in range(1, 9):
        d = parse_date(row.get(f"Recap Date {k}"))
        t = clean(row.get(f"Recap Trap {k}"))
        if d is not None and t:
            out.append((d, t))
    return out


def tag_key(row: dict) -> str | None:
    left = clean(row.get("Ear Tag L"))
    right = clean(row.get("Ear Tag R"))
    if not left and not right:
        return None
    return f"{left}|{right}"


def inventory(rows: list[dict], columns: list[str]) -> dict:
    species_rows = Counter()
    usable_rows = Counter()
    multi_rows = Counter()
    unit_histories: dict[tuple[str, str], list[dict]] = defaultdict(list)
    capture_date_count_dist = Counter()
    distinct_trap_count_dist = Counter()
    session_values: dict[tuple[str, str], set[str]] = defaultdict(set)

    invalid_initial_date = 0
    missing_initial_trap = 0
    recap_date_without_trap = 0
    recap_trap_without_date = 0
    excluded_remove = 0
    repeated_same_date_records = 0
    recap_outside_initial_site_season_uncheckable = 0

    tags: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    tagless_rows = 0

    recap_date_cols = [f"Recap Date {k}" for k in range(1, 9)]
    recap_trap_cols = [f"Recap Trap {k}" for k in range(1, 9)]

    for idx, row in enumerate(rows):
        species = clean(row.get("Species"))
        site = clean(row.get("Site"))
        season = clean(row.get("Season"))
        session = clean(row.get("Session"))
        species_rows[species or "<missing>"] += 1
        if site and season and session:
            session_values[(site, season)].add(session)

        if truthy_remove(row.get("Remove")):
            excluded_remove += 1
            continue

        initial_date = parse_date(row.get("Capture Date"))
        initial_trap = clean(row.get("Trap ID"))
        if initial_date is None:
            invalid_initial_date += 1
        if not initial_trap:
            missing_initial_trap += 1

        for dc, tc in zip(recap_date_cols, recap_trap_cols):
            d_raw = clean(row.get(dc))
            t_raw = clean(row.get(tc))
            d = parse_date(d_raw)
            if d is not None and not t_raw:
                recap_date_without_trap += 1
            if t_raw and d is None:
                recap_trap_without_date += 1

        if not species or not site or not season or initial_date is None or not initial_trap:
            continue

        events = [(initial_date, initial_trap)] + recap_pairs(row)
        by_date: dict[str, set[str]] = defaultdict(set)
        for d, t in events:
            by_date[d].add(t)
        if any(len(v) > 1 for v in by_date.values()):
            repeated_same_date_records += 1

        # Feasibility uses dates only; if duplicate entries occur on the same
        # date they count as one capture date. Distinct trap count is reported
        # as support only and no pairwise overlap is calculated.
        capture_dates = sorted(by_date)
        traps = sorted({t for vals in by_date.values() for t in vals})
        usable_rows[species] += 1
        capture_date_count_dist[len(capture_dates)] += 1

        history = {
            "row_index": idx,
            "species": species,
            "site": site,
            "season": season,
            "session": session,
            "capture_date_count": len(capture_dates),
            "distinct_trap_count": len(traps),
        }
        unit_histories[(site, season)].append(history)

        if len(capture_dates) >= 2:
            multi_rows[species] += 1
            distinct_trap_count_dist[len(traps)] += 1

        tk = tag_key(row)
        if tk is None:
            tagless_rows += 1
        else:
            tags[(site, season, tk)].append(idx)

    duplicate_tag_groups = {
        f"{site}|{season}|{tag}": ids
        for (site, season, tag), ids in tags.items()
        if len(ids) > 1
    }

    units = []
    eligible_units = []
    for (site, season), hs in sorted(unit_histories.items()):
        by_species = Counter(
            h["species"] for h in hs if h["capture_date_count"] >= 2
        )
        eligible_species = sorted(
            sp
            for sp, n in by_species.items()
            if n >= MIN_MULTI_NIGHT_INDIVIDUALS_PER_SPECIES
        )
        record = {
            "id": f"{site}|{season}",
            "site": site,
            "season": season,
            "session_values": sorted(session_values.get((site, season), set())),
            "usable_initial_histories": len(hs),
            "multi_night_individuals": sum(
                h["capture_date_count"] >= 2 for h in hs
            ),
            "multi_night_individuals_by_species": dict(sorted(by_species.items())),
            "support_eligible_species": eligible_species,
            "support_eligible_species_count": len(eligible_species),
            "candidate_unit_eligible": len(eligible_species) >= MIN_SPECIES_PER_UNIT,
        }
        units.append(record)
        if record["candidate_unit_eligible"]:
            eligible_units.append(record["id"])

    required = {
        "Season", "Site", "Session", "Capture Date", "Trap ID", "Species", "Remove"
    } | set(recap_date_cols) | set(recap_trap_cols)
    missing_required = sorted(required - set(columns))

    return {
        "schema": "neon.wisconsin_footprint_feasibility.v1",
        "status": "stage6a_support_only_no_spatial_overlap_outcomes_opened",
        "source": {
            "doi": DOI,
            "dataset_zip_url": DATASET_ZIP_URL,
        },
        "columns": columns,
        "missing_required_columns": missing_required,
        "raw_rows": len(rows),
        "species_raw_rows": dict(sorted(species_rows.items())),
        "usable_histories_by_species": dict(sorted(usable_rows.items())),
        "multi_night_individuals_by_species": dict(sorted(multi_rows.items())),
        "capture_date_count_distribution_all_usable_histories": {
            str(k): v for k, v in sorted(capture_date_count_dist.items())
        },
        "distinct_trap_count_distribution_multi_night_histories": {
            str(k): v for k, v in sorted(distinct_trap_count_dist.items())
        },
        "data_quality": {
            "excluded_remove_rows": excluded_remove,
            "invalid_initial_date_rows": invalid_initial_date,
            "missing_initial_trap_rows": missing_initial_trap,
            "recap_date_without_trap_cells": recap_date_without_trap,
            "recap_trap_without_valid_date_cells": recap_trap_without_date,
            "rows_with_multiple_trap_ids_same_capture_date": repeated_same_date_records,
            "tagless_rows_after_remove_filter": tagless_rows,
            "duplicate_nonblank_tag_groups_within_site_season": len(duplicate_tag_groups),
            "duplicate_tag_groups_preview": dict(list(sorted(duplicate_tag_groups.items()))[:20]),
            "recap_outside_initial_site_season_uncheckable": recap_outside_initial_site_season_uncheckable,
        },
        "support_rule": {
            "minimum_distinct_capture_dates_per_individual": 2,
            "minimum_multi_night_individuals_per_species_unit": MIN_MULTI_NIGHT_INDIVIDUALS_PER_SPECIES,
            "minimum_eligible_species_per_site_season": MIN_SPECIES_PER_UNIT,
            "minimum_candidate_site_seasons_required": MIN_UNITS,
        },
        "site_seasons": units,
        "candidate_eligible_site_seasons": eligible_units,
        "candidate_eligible_site_season_count": len(eligible_units),
        "decision": (
            "authorize_stage6b_design_freeze"
            if len(eligible_units) >= MIN_UNITS and not missing_required
            else "stop_wisconsin_replication_for_support"
        ),
        "claim_boundary": {
            "jaccard_opened": False,
            "conspecific_heterospecific_overlap_opened": False,
            "trap_distance_opened": False,
            "species_trap_maps_opened": False,
            "permutation_test_opened": False,
            "habitat_or_season_effect_opened": False,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--cache-zip", type=Path)
    args = ap.parse_args()

    raw_zip = fetch_dataset_zip()
    if args.cache_zip is not None:
        args.cache_zip.parent.mkdir(parents=True, exist_ok=True)
        args.cache_zip.write_bytes(raw_zip)

    capture_raw, names = extract_capture_csv(raw_zip)
    rows = list(csv.DictReader(capture_raw.decode("utf-8-sig").splitlines()))
    columns = list(rows[0].keys()) if rows else []
    result = inventory(rows, columns)
    result["source"]["dataset_zip_sha256"] = hashlib.sha256(raw_zip).hexdigest()
    result["source"]["capture_csv_sha256"] = hashlib.sha256(capture_raw).hexdigest()
    result["source"]["archive_file_names"] = names

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "decision": result["decision"],
        "candidate_eligible_site_season_count": result["candidate_eligible_site_season_count"],
        "candidate_eligible_site_seasons": result["candidate_eligible_site_seasons"],
        "multi_night_individuals_by_species": result["multi_night_individuals_by_species"],
        "data_quality": result["data_quality"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
