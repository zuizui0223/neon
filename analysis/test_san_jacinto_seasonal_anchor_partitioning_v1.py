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
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

URL = "https://ndownloader.figshare.com/files/33058799"
SHA256 = "ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
FOCAL_SPECIES = ("CHFA", "DKR", "LAPM", "PEER", "PEMA", "SKR")
RANDOMIZATIONS = 10_000
SEED = 2026100502

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


def d2(a: str, b: str) -> int:
    ax, ay = FLAG_TO_XY[a]
    bx, by = FLAG_TO_XY[b]
    return (ax - bx) ** 2 + (ay - by) ** 2


def download_rows(cache: Path | None = None) -> list[dict]:
    req = urllib.request.Request(URL, headers={"User-Agent": "neon-anchor-scale-stage2/1.0"})
    with urllib.request.urlopen(req, timeout=180) as response:
        raw = response.read()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != SHA256:
        raise RuntimeError(f"source checksum mismatch: {actual}")
    if cache is not None:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(raw)
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))


def c_score(species_to_flags: dict[str, set[str]], species_order: tuple[str, ...]) -> float:
    vals = []
    for a, b in combinations(species_order, 2):
        sa = species_to_flags[a]
        sb = species_to_flags[b]
        shared = len(sa & sb)
        vals.append((len(sa) - shared) * (len(sb) - shared))
    if not vals:
        raise ValueError("need >=2 species")
    return float(statistics.mean(vals))


def seasonal_anchor(nightly_first_flags: list[str]) -> str:
    if not nightly_first_flags:
        raise ValueError("empty individual")
    counts = Counter(nightly_first_flags)
    candidates = sorted(counts)
    best_key = None
    best_flag = None
    for cand in candidates:
        ss = sum(d2(cand, x) for x in nightly_first_flags)
        key = (ss, -counts[cand], cand)
        if best_key is None or key < best_key:
            best_key = key
            best_flag = cand
    assert best_flag is not None
    return best_flag


def prepare_dataset(rows: list[dict]) -> tuple[list[dict], dict[tuple[str, str], dict[str, set[str]]]]:
    # First capture within each calendar night.
    night_groups: dict[tuple[str, str, str, str], list[tuple[float, int, str, str]]] = defaultdict(list)
    all_capture_presence: dict[tuple[str, str], dict[str, set[str]]] = defaultdict(
        lambda: {sp: set() for sp in FOCAL_SPECIES}
    )

    for idx, row in enumerate(rows):
        sp = clean(row.get("species")).upper()
        if sp not in FOCAL_SPECIES:
            continue
        grid = clean(row.get("grid"))
        uid = clean(row.get("unique_ID"))
        date_s = clean(row.get("date"))
        flag = clean(row.get("flag")).upper()
        t = parse_time(row.get("time"))
        dt = parse_date(date_s)
        if not grid or not uid or not date_s or flag not in FLAG_TO_XY or t is None or dt is None:
            continue
        season = season_from_month(dt.month)
        night_groups[(sp, grid, uid, date_s)].append((t, idx, flag, season))
        all_capture_presence[(grid, season)][sp].add(flag)

    individual_flags: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
    for (sp, grid, uid, date_s), items in night_groups.items():
        first = min(items, key=lambda x: (x[0], x[1]))
        season = first[3]
        individual_flags[(sp, grid, season, uid)].append(first[2])

    anchors = []
    for (sp, grid, season, uid), flags in sorted(individual_flags.items()):
        anchors.append(
            {
                "species": sp,
                "grid": grid,
                "season": season,
                "unique_ID": uid,
                "night_count": len(flags),
                "anchor_flag": seasonal_anchor(flags),
            }
        )
    return anchors, all_capture_presence


def prepare_units(
    anchors: list[dict],
    all_capture_presence: dict[tuple[str, str], dict[str, set[str]]],
) -> list[dict]:
    by_unit: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for a in anchors:
        by_unit[(a["grid"], a["season"])].append(a)

    units = []
    for (grid, season), rows in sorted(by_unit.items()):
        species = tuple(sp for sp in FOCAL_SPECIES if any(r["species"] == sp for r in rows))
        if len(species) < 3:
            continue
        rows = [r for r in rows if r["species"] in species]
        labels = [r["species"] for r in rows]
        locations = [r["anchor_flag"] for r in rows]
        obs_presence = {sp: set() for sp in species}
        for sp, loc in zip(labels, locations):
            obs_presence[sp].add(loc)

        capture_presence = {
            sp: set(all_capture_presence[(grid, season)].get(sp, set()))
            for sp in species
        }

        units.append(
            {
                "grid": grid,
                "season": season,
                "species": species,
                "labels": labels,
                "locations": locations,
                "observed_anchor_c": c_score(obs_presence, species),
                "all_capture_c": c_score(capture_presence, species),
                "individual_counts": dict(Counter(labels)),
                "night_counts": [r["night_count"] for r in rows],
            }
        )
    return units


def permuted_c(unit: dict, rng: random.Random) -> float:
    labels = list(unit["labels"])
    rng.shuffle(labels)
    presence = {sp: set() for sp in unit["species"]}
    for sp, loc in zip(labels, unit["locations"]):
        presence[sp].add(loc)
    return c_score(presence, unit["species"])


def pearson(x: list[float], y: list[float]) -> float | None:
    if len(x) != len(y) or len(x) < 2:
        return None
    mx = statistics.mean(x)
    my = statistics.mean(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def run_test(
    rows: list[dict],
    *,
    randomizations: int = RANDOMIZATIONS,
    seed: int = SEED,
) -> dict:
    if randomizations < 100:
        raise ValueError("randomizations must be >=100")

    anchors, all_capture_presence = prepare_dataset(rows)
    units = prepare_units(anchors, all_capture_presence)
    rng = random.Random(seed)

    null_by_unit: list[list[float]] = [[] for _ in units]
    for _ in range(randomizations):
        for i, unit in enumerate(units):
            null_by_unit[i].append(permuted_c(unit, rng))

    summaries = []
    informative = []
    for i, unit in enumerate(units):
        null = null_by_unit[i]
        mu = statistics.mean(null)
        sd = statistics.pstdev(null)
        z = None if sd == 0 else (unit["observed_anchor_c"] - mu) / sd
        if sd > 0:
            informative.append(i)
        summaries.append(
            {
                "grid": unit["grid"],
                "season": unit["season"],
                "species": list(unit["species"]),
                "species_count": len(unit["species"]),
                "individual_anchor_count": len(unit["labels"]),
                "individual_counts_by_species": unit["individual_counts"],
                "individuals_with_multiple_nights": sum(n >= 2 for n in unit["night_counts"]),
                "anchor_c_score": unit["observed_anchor_c"],
                "anchor_null_mean_c_score": mu,
                "anchor_null_sd_c_score": sd,
                "anchor_z": z,
                "all_capture_c_score_descriptive": unit["all_capture_c"],
            }
        )

    if informative:
        mus = {i: statistics.mean(null_by_unit[i]) for i in informative}
        sds = {i: statistics.pstdev(null_by_unit[i]) for i in informative}
        t_obs = statistics.mean(
            (units[i]["observed_anchor_c"] - mus[i]) / sds[i]
            for i in informative
        )
        t_null = []
        for b in range(randomizations):
            t_null.append(
                statistics.mean(
                    (null_by_unit[i][b] - mus[i]) / sds[i]
                    for i in informative
                )
            )
        ge = sum(x >= t_obs - 1e-15 for x in t_null)
        p_upper = (ge + 1) / (randomizations + 1)
        t_null_mean = statistics.mean(t_null)
        t_null_sd = statistics.pstdev(t_null)
    else:
        t_obs = p_upper = t_null_mean = t_null_sd = None

    supported = (
        len(informative) >= 8
        and t_obs is not None
        and t_obs > 0
        and p_upper is not None
        and p_upper < 0.05
    )
    decision = (
        "support_species_specific_seasonal_anchoring"
        if supported
        else "stop_no_species_specific_seasonal_anchoring_support"
    )

    by_species = Counter(a["species"] for a in anchors)
    multi_night_by_species = Counter(
        a["species"] for a in anchors if int(a["night_count"]) >= 2
    )

    obs_anchor = [units[i]["observed_anchor_c"] for i in range(len(units))]
    obs_all = [units[i]["all_capture_c"] for i in range(len(units))]

    return {
        "schema": "neon.san_jacinto_seasonal_anchor_partitioning.v1",
        "status": "stage2_adaptive_frozen_test_complete",
        "source": {
            "figshare_doi": "10.6084/m9.figshare.18295520.v1",
            "file_id": 33058799,
            "sha256_verified": True,
        },
        "frozen_design": "docs/SAN_JACINTO_TRANSITION_NICHE_EXPLORATION_V1.md",
        "design": {
            "anchor_definition": (
                "per individual x grid x season, medoid observed trap of nightly-FIRST locations; "
                "minimize sum squared grid distances, then max nightly frequency, then lexical tie-break"
            ),
            "later_within_night_recaptures_used_for_anchor": False,
            "unit_inclusion": "all grid-seasons with >=3 focal species represented by >=1 individual anchor",
            "null": "shuffle species labels among fixed individual anchors within grid-season, preserving species individual counts",
            "randomizations": randomizations,
            "seed": seed,
        },
        "support": {
            "individual_anchor_count": len(anchors),
            "individual_anchor_count_by_species": dict(sorted(by_species.items())),
            "individuals_with_multiple_nights": sum(int(a["night_count"]) >= 2 for a in anchors),
            "individuals_with_multiple_nights_by_species": dict(sorted(multi_night_by_species.items())),
            "eligible_grid_seasons": len(units),
            "informative_grid_seasons_nonzero_null_sd": len(informative),
        },
        "primary": {
            "global_mean_standardized_anchor_c_score_excess": t_obs,
            "null_global_mean": t_null_mean,
            "null_global_sd": t_null_sd,
            "one_sided_monte_carlo_p_upper": p_upper,
            "required_informative_grid_seasons": 8,
            "required_direction": "positive",
            "alpha": 0.05,
            "decision": decision,
        },
        "secondary": {
            "correlation_anchor_vs_all_capture_raw_c_score": pearson(obs_anchor, obs_all),
            "claim_status": "descriptive_only",
        },
        "grid_seasons": summaries,
        "claim_boundary": {
            "species_pair_decomposition_opened": False,
            "alternative_anchor_definitions_opened": False,
            "habitat_mechanism_identified": False,
            "competition_causally_identified": False,
            "within_night_direction_route_rescued": False,
            "interpretation_if_supported": (
                "Species identity is non-randomly associated with seasonal spatial anchor proxies "
                "constructed without later within-night recaptures."
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
