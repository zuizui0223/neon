from __future__ import annotations

# AI assistance disclosure: drafted/refactored with OpenAI ChatGPT (GPT-5.6 Sol,
# October 2026). Scientific interpretation remains under author responsibility.

import argparse
import csv
import hashlib
import json
import math
import random
import re
import statistics
import urllib.request
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

URL = "https://ndownloader.figshare.com/files/33058799"
SHA256 = "ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"

FOCAL_SPECIES = ("CHFA", "DKR", "LAPM", "PEER", "PEMA", "SKR")
MIN_REPEAT_NIGHTS_PER_SPECIES_UNIT = 5
MIN_SPECIES_PER_UNIT = 3
RANDOMIZATIONS = 10_000
SEED = 2026100501

ROWS = "ABCDEFG"
COLS = tuple(range(1, 8))
CANONICAL_FLAGS = tuple(f"{r}{c}" for r in ROWS for c in COLS)
FLAG_TO_XY = {
    f"{r}{c}": (ri, c - 1)
    for ri, r in enumerate(ROWS)
    for c in COLS
}


def clean(x: object) -> str:
    return str(x or "").strip()


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


def season_from_month(month: int) -> str:
    if month in (8, 9, 10):
        return "fall"
    if month in (11, 12, 1):
        return "winter"
    if month in (2, 3, 4):
        return "spring"
    if month in (5, 6, 7):
        return "summer"
    raise ValueError(month)


def squared_grid_distance(a: str, b: str) -> int:
    ax, ay = FLAG_TO_XY[a]
    bx, by = FLAG_TO_XY[b]
    return (ax - bx) ** 2 + (ay - by) ** 2


_CANDIDATES: dict[tuple[str, int], tuple[str, ...]] = {}
for origin in CANONICAL_FLAGS:
    for destination in CANONICAL_FLAGS:
        d2 = squared_grid_distance(origin, destination)
        _CANDIDATES.setdefault((origin, d2), tuple())
for key in list(_CANDIDATES):
    origin, d2 = key
    _CANDIDATES[key] = tuple(
        f for f in CANONICAL_FLAGS if squared_grid_distance(origin, f) == d2
    )


def distance_matched_candidates(origin: str, destination: str) -> tuple[str, ...]:
    return _CANDIDATES[(origin, squared_grid_distance(origin, destination))]


def download_rows(cache: Path | None = None) -> list[dict]:
    req = urllib.request.Request(URL, headers={"User-Agent": "neon-transition-niche-stage1/1.0"})
    with urllib.request.urlopen(req, timeout=180) as response:
        raw = response.read()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != SHA256:
        raise RuntimeError(f"source checksum mismatch: {actual}")
    if cache is not None:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(raw)
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))


def build_individual_nights(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str, str, str], list[tuple[float, int, str]]] = defaultdict(list)
    dates: dict[tuple[str, str, str, str], datetime] = {}

    for row_index, row in enumerate(rows):
        species = clean(row.get("species")).upper()
        if species not in FOCAL_SPECIES:
            continue
        grid = clean(row.get("grid"))
        uid = clean(row.get("unique_ID"))
        date_s = clean(row.get("date"))
        flag = clean(row.get("flag")).upper()
        t = parse_time(row.get("time"))
        dt = parse_date(date_s)
        if not grid or not uid or not date_s or flag not in FLAG_TO_XY or t is None or dt is None:
            continue
        key = (species, grid, uid, date_s)
        grouped[key].append((t, row_index, flag))
        dates[key] = dt

    out = []
    for (species, grid, uid, date_s), items in sorted(grouped.items()):
        ordered = sorted(items)
        first = ordered[0][2]
        last = ordered[-1][2]
        dt = dates[(species, grid, uid, date_s)]
        out.append(
            {
                "species": species,
                "grid": grid,
                "unique_ID": uid,
                "date": date_s,
                "season": season_from_month(dt.month),
                "raw_capture_rows": len(ordered),
                "repeat": len(ordered) >= 2,
                "first_flag": first,
                "last_flag": last,
            }
        )
    return out


def c_score(species_to_flags: dict[str, set[str]], species_order: tuple[str, ...]) -> float:
    values = []
    for a, b in combinations(species_order, 2):
        sa = species_to_flags[a]
        sb = species_to_flags[b]
        shared = len(sa & sb)
        values.append((len(sa) - shared) * (len(sb) - shared))
    if not values:
        raise ValueError("C-score requires at least two species")
    return float(statistics.mean(values))


def prepare_units(nights: list[dict]) -> list[dict]:
    by_unit: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in nights:
        by_unit[(row["grid"], row["season"])].append(row)

    units = []
    for (grid, season), rows in sorted(by_unit.items()):
        repeat_counts = {
            sp: sum(r["species"] == sp and r["repeat"] for r in rows)
            for sp in FOCAL_SPECIES
        }
        eligible_species = tuple(
            sp for sp in FOCAL_SPECIES
            if repeat_counts[sp] >= MIN_REPEAT_NIGHTS_PER_SPECIES_UNIT
        )
        if len(eligible_species) < MIN_SPECIES_PER_UNIT:
            continue

        kept = [r for r in rows if r["species"] in eligible_species]
        repeat_rows = []
        singleton_flags: dict[str, set[str]] = {sp: set() for sp in eligible_species}

        for r in kept:
            if r["repeat"]:
                candidates = distance_matched_candidates(r["first_flag"], r["last_flag"])
                if r["last_flag"] not in candidates:
                    raise AssertionError("observed LAST absent from exact-distance candidate set")
                repeat_rows.append(
                    {
                        "species": r["species"],
                        "first_flag": r["first_flag"],
                        "last_flag": r["last_flag"],
                        "d2": squared_grid_distance(r["first_flag"], r["last_flag"]),
                        "candidates": candidates,
                    }
                )
            else:
                singleton_flags[r["species"]].add(r["first_flag"])

        units.append(
            {
                "grid": grid,
                "season": season,
                "species": eligible_species,
                "repeat_counts": {sp: repeat_counts[sp] for sp in eligible_species},
                "all_nights": kept,
                "repeat_rows": repeat_rows,
                "singleton_flags": singleton_flags,
            }
        )
    return units


def endpoint_score(unit: dict, endpoint: str) -> float:
    presence = {sp: set(flags) for sp, flags in unit["singleton_flags"].items()}
    key = "first_flag" if endpoint == "first" else "last_flag"
    for r in unit["repeat_rows"]:
        presence[r["species"]].add(r[key])
    return c_score(presence, unit["species"])


def randomized_score(unit: dict, rng: random.Random) -> float:
    presence = {sp: set(flags) for sp, flags in unit["singleton_flags"].items()}
    for r in unit["repeat_rows"]:
        presence[r["species"]].add(rng.choice(r["candidates"]))
    return c_score(presence, unit["species"])


def run_test(
    rows: list[dict],
    *,
    randomizations: int = RANDOMIZATIONS,
    seed: int = SEED,
) -> dict:
    if randomizations < 100:
        raise ValueError("randomizations must be >=100")

    nights = build_individual_nights(rows)
    units = prepare_units(nights)
    rng = random.Random(seed)

    null_by_unit: list[list[float]] = [[] for _ in units]
    first_scores = []
    last_scores = []
    for unit in units:
        first_scores.append(endpoint_score(unit, "first"))
        last_scores.append(endpoint_score(unit, "last"))

    # Each replicate preserves every FIRST origin and exact FIRST-to-LAST d^2,
    # randomizing only among feasible directions on the same 7x7 grid.
    for _ in range(randomizations):
        for i, unit in enumerate(units):
            null_by_unit[i].append(randomized_score(unit, rng))

    summaries = []
    informative_indices = []
    for i, unit in enumerate(units):
        null = null_by_unit[i]
        mu = statistics.mean(null)
        sd = statistics.pstdev(null)
        z = None if sd == 0 else (last_scores[i] - mu) / sd
        if sd > 0:
            informative_indices.append(i)

        repeat_rows = unit["repeat_rows"]
        directional = sum(len(r["candidates"]) > 1 for r in repeat_rows)
        summaries.append(
            {
                "grid": unit["grid"],
                "season": unit["season"],
                "eligible_species": list(unit["species"]),
                "eligible_species_count": len(unit["species"]),
                "captured_individual_nights_all": len(unit["all_nights"]),
                "repeat_nights_randomized": len(repeat_rows),
                "repeat_nights_with_multiple_feasible_directions": directional,
                "repeat_nights_with_multiple_feasible_directions_fraction": (
                    directional / len(repeat_rows) if repeat_rows else None
                ),
                "repeat_nights_by_species": unit["repeat_counts"],
                "first_c_score": first_scores[i],
                "observed_last_c_score": last_scores[i],
                "null_mean_c_score": mu,
                "null_sd_c_score": sd,
                "observed_last_minus_first": last_scores[i] - first_scores[i],
                "null_expected_last_minus_first": mu - first_scores[i],
                "z_observed_vs_direction_null": z,
            }
        )

    if informative_indices:
        t_obs = statistics.mean(
            (last_scores[i] - statistics.mean(null_by_unit[i])) / statistics.pstdev(null_by_unit[i])
            for i in informative_indices
        )
        t_null = []
        mus = {i: statistics.mean(null_by_unit[i]) for i in informative_indices}
        sds = {i: statistics.pstdev(null_by_unit[i]) for i in informative_indices}
        for b in range(randomizations):
            t_null.append(
                statistics.mean(
                    (null_by_unit[i][b] - mus[i]) / sds[i]
                    for i in informative_indices
                )
            )
        ge = sum(x >= t_obs - 1e-15 for x in t_null)
        p_upper = (ge + 1) / (randomizations + 1)
        t_null_mean = statistics.mean(t_null)
        t_null_sd = statistics.pstdev(t_null)
    else:
        t_obs = None
        p_upper = None
        t_null_mean = None
        t_null_sd = None

    n_info = len(informative_indices)
    supported = (
        n_info >= 4
        and t_obs is not None
        and t_obs > 0
        and p_upper is not None
        and p_upper < 0.05
    )
    decision = (
        "support_directional_maintenance"
        if supported
        else "stop_no_directional_maintenance_support"
    )

    eligible_repeat_rows = [r for u in units for r in u["repeat_rows"]]
    eligible_directional = sum(len(r["candidates"]) > 1 for r in eligible_repeat_rows)

    return {
        "schema": "neon.san_jacinto_movement_direction_partitioning.v1",
        "status": "stage1_frozen_test_complete",
        "source": {
            "figshare_doi": "10.6084/m9.figshare.18295520.v1",
            "file_id": 33058799,
            "sha256_verified": True,
        },
        "frozen_design": "docs/SAN_JACINTO_TRANSITION_NICHE_EXPLORATION_V1.md",
        "design": {
            "focal_species": list(FOCAL_SPECIES),
            "season_definition": {
                "fall": [8, 9, 10],
                "winter": [11, 12, 1],
                "spring": [2, 3, 4],
                "summer": [5, 6, 7],
            },
            "min_repeat_nights_per_species_grid_season": MIN_REPEAT_NIGHTS_PER_SPECIES_UNIT,
            "min_species_per_grid_season": MIN_SPECIES_PER_UNIT,
            "randomizations": randomizations,
            "seed": seed,
            "null": "same FIRST origin and exact squared grid displacement; random feasible direction",
            "singleton_nights": "fixed in FIRST, LAST and every null replicate",
            "null_sd_definition": "population SD across Monte Carlo replicates",
        },
        "support": {
            "valid_focal_individual_nights": len(nights),
            "eligible_grid_seasons": len(units),
            "informative_grid_seasons_nonzero_null_sd": n_info,
            "eligible_repeat_nights_randomized": len(eligible_repeat_rows),
            "eligible_repeat_nights_multiple_feasible_directions": eligible_directional,
            "eligible_repeat_nights_multiple_feasible_directions_fraction": (
                eligible_directional / len(eligible_repeat_rows)
                if eligible_repeat_rows else None
            ),
        },
        "primary": {
            "global_mean_standardized_c_score_excess": t_obs,
            "null_global_mean": t_null_mean,
            "null_global_sd": t_null_sd,
            "one_sided_monte_carlo_p_upper": p_upper,
            "required_informative_grid_seasons": 4,
            "required_direction": "positive",
            "alpha": 0.05,
            "decision": decision,
        },
        "grid_seasons": summaries,
        "claim_boundary": {
            "species_pair_decomposition_opened": False,
            "habitat_mechanism_tested": False,
            "competition_causally_identified": False,
            "capture_response_excluded": False,
            "complete_natural_trajectories_observed": False,
            "interpretation_if_supported": (
                "For moves of the same length from the same starting locations, "
                "observed capture-to-recapture directions preserve more interspecific "
                "spatial segregation than feasible random directions."
            ),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, default=None)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--randomizations", type=int, default=RANDOMIZATIONS)
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    rows = download_rows(args.cache)
    result = run_test(rows, randomizations=args.randomizations, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
