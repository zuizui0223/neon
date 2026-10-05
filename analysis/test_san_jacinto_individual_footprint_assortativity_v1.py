from __future__ import annotations

# AI assistance disclosure: drafted/refactored with OpenAI ChatGPT (GPT-5.6 Sol,
# October 2026). Scientific interpretation remains under author responsibility.

import argparse
import csv
import hashlib
import json
import math
import re
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

URL = "https://ndownloader.figshare.com/files/33058799"
SHA256 = "ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
FOCAL = ("CHFA", "DKR", "LAPM", "PEER", "PEMA", "SKR")
EXCLUDED_UNITS = {"3|winter", "7|winter"}
MIN_NIGHTS = 2
MIN_INDIVIDUALS_PER_SPECIES = 3
MIN_SPECIES_PER_UNIT = 3
MIN_INFORMATIVE_UNITS = 8
PERMUTATIONS = 10_000
SEED = 2026100505
ROWS = "ABCDEFG"
FLAGS = {f"{r}{c}" for r in ROWS for c in range(1, 8)}


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


def download_rows(cache: Path | None = None) -> list[dict]:
    req = urllib.request.Request(URL, headers={"User-Agent": "neon-footprint-assortativity-stage5/1.0"})
    with urllib.request.urlopen(req, timeout=180) as response:
        raw = response.read()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != SHA256:
        raise RuntimeError(f"source checksum mismatch: {actual}")
    if cache is not None:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(raw)
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))


def build_footprints(rows: list[dict]) -> list[dict]:
    nights: dict[tuple[str, str, str, str], list[tuple[float, int, str, str]]] = defaultdict(list)

    for idx, row in enumerate(rows):
        sp = clean(row.get("species")).upper()
        if sp not in FOCAL:
            continue
        grid = clean(row.get("grid"))
        uid = clean(row.get("unique_ID"))
        date_s = clean(row.get("date"))
        flag = clean(row.get("flag")).upper()
        t = parse_time(row.get("time"))
        dt = parse_date(date_s)
        if not grid or not uid or not date_s or flag not in FLAGS or t is None or dt is None:
            continue
        season = season_from_month(dt.month)
        nights[(sp, grid, uid, date_s)].append((t, idx, flag, season))

    first_by_individual: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
    for (sp, grid, uid, _date), items in nights.items():
        first = min(items, key=lambda x: (x[0], x[1]))
        season = first[3]
        first_by_individual[(sp, grid, season, uid)].append(first[2])

    out = []
    for (sp, grid, season, uid), nightly_flags in sorted(first_by_individual.items()):
        if len(nightly_flags) < MIN_NIGHTS:
            continue
        fp = frozenset(nightly_flags)
        out.append(
            {
                "species": sp,
                "grid": grid,
                "season": season,
                "unique_ID": uid,
                "night_count": len(nightly_flags),
                "footprint": fp,
                "footprint_size": len(fp),
            }
        )
    return out


def jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    u = len(a | b)
    return 0.0 if u == 0 else len(a & b) / u


def prepare_units(footprints: list[dict]) -> list[dict]:
    by_unit: dict[str, list[dict]] = defaultdict(list)
    for x in footprints:
        uid = f'{x["grid"]}|{x["season"]}'
        if uid in EXCLUDED_UNITS:
            continue
        by_unit[uid].append(x)

    units = []
    for unit_id, rows in sorted(by_unit.items()):
        counts = Counter(r["species"] for r in rows)
        eligible_species = tuple(
            sp for sp in FOCAL if counts.get(sp, 0) >= MIN_INDIVIDUALS_PER_SPECIES
        )
        if len(eligible_species) < MIN_SPECIES_PER_UNIT:
            continue
        kept = [r for r in rows if r["species"] in eligible_species]
        labels = np.array([eligible_species.index(r["species"]) for r in kept], dtype=np.int16)
        sizes = np.array([r["footprint_size"] for r in kept], dtype=np.int16)
        fps = [r["footprint"] for r in kept]

        ii, jj = np.triu_indices(len(kept), 1)
        sims = np.array([jaccard(fps[i], fps[j]) for i, j in zip(ii, jj)], dtype=float)

        strata = {}
        for s in sorted(set(sizes.tolist())):
            strata[int(s)] = np.where(sizes == s)[0]

        units.append(
            {
                "id": unit_id,
                "grid": kept[0]["grid"],
                "season": kept[0]["season"],
                "species": eligible_species,
                "rows": kept,
                "labels": labels,
                "sizes": sizes,
                "ii": ii,
                "jj": jj,
                "sims": sims,
                "strata": strata,
            }
        )
    return units


def contrast(labels: np.ndarray, ii: np.ndarray, jj: np.ndarray, sims: np.ndarray) -> tuple[float, float, float]:
    same = labels[ii] == labels[jj]
    if not np.any(same) or np.all(same):
        return math.nan, math.nan, math.nan
    con = float(np.mean(sims[same]))
    het = float(np.mean(sims[~same]))
    return con - het, con, het


def permute_labels_within_size(
    labels: np.ndarray,
    strata: dict[int, np.ndarray],
    rng: np.random.Generator,
) -> np.ndarray:
    out = labels.copy()
    for idx in strata.values():
        if len(idx) > 1:
            out[idx] = rng.permutation(out[idx])
    return out


def pearson(x: list[float], y: list[float]) -> float | None:
    if len(x) != len(y) or len(x) < 3:
        return None
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    keep = np.isfinite(xa) & np.isfinite(ya)
    if int(np.sum(keep)) < 3:
        return None
    if float(np.std(xa[keep])) == 0 or float(np.std(ya[keep])) == 0:
        return None
    return float(np.corrcoef(xa[keep], ya[keep])[0, 1])


def run_test(
    rows: list[dict],
    *,
    permutations: int = PERMUTATIONS,
    seed: int = SEED,
    stage4_result: dict | None = None,
) -> dict:
    if permutations < 100:
        raise ValueError("permutations must be >=100")

    footprints = build_footprints(rows)
    units = prepare_units(footprints)
    rng = np.random.default_rng(seed)

    nulls = []
    observed = []
    summaries = []
    informative = []

    for uidx, u in enumerate(units):
        d_obs, con_obs, het_obs = contrast(u["labels"], u["ii"], u["jj"], u["sims"])
        observed.append(d_obs)
        vals = np.empty(permutations, dtype=float)
        for b in range(permutations):
            lab = permute_labels_within_size(u["labels"], u["strata"], rng)
            vals[b] = contrast(lab, u["ii"], u["jj"], u["sims"])[0]
        nulls.append(vals)

        finite = vals[np.isfinite(vals)]
        mu = float(np.mean(finite)) if finite.size else math.nan
        sd = float(np.std(finite, ddof=0)) if finite.size else math.nan
        z = (d_obs - mu) / sd if math.isfinite(sd) and sd > 0 and math.isfinite(d_obs) else None
        if z is not None:
            informative.append(uidx)

        size_counts = Counter(int(r["footprint_size"]) for r in u["rows"])
        sp_counts = Counter(r["species"] for r in u["rows"])
        summaries.append(
            {
                "id": u["id"],
                "grid": u["grid"],
                "season": u["season"],
                "eligible_species": list(u["species"]),
                "multi_night_individuals": len(u["rows"]),
                "individuals_by_species": dict(sorted(sp_counts.items())),
                "footprint_size_distribution": {str(k): v for k, v in sorted(size_counts.items())},
                "observed_mean_conspecific_jaccard": con_obs,
                "observed_mean_heterospecific_jaccard": het_obs,
                "observed_difference": d_obs,
                "null_mean_difference": mu,
                "null_sd_difference": sd,
                "z_observed": z,
            }
        )

    if informative:
        zs = []
        for i in informative:
            vals = nulls[i]
            finite = vals[np.isfinite(vals)]
            mu = float(np.mean(finite))
            sd = float(np.std(finite, ddof=0))
            zs.append((observed[i] - mu) / sd)
        t_obs = float(np.mean(zs))

        t_null = np.empty(permutations, dtype=float)
        for b in range(permutations):
            zz = []
            for i in informative:
                vals = nulls[i]
                finite = vals[np.isfinite(vals)]
                mu = float(np.mean(finite))
                sd = float(np.std(finite, ddof=0))
                val = vals[b]
                if math.isfinite(val):
                    zz.append((val - mu) / sd)
            t_null[b] = float(np.mean(zz)) if zz else math.nan
        finite_t = t_null[np.isfinite(t_null)]
        ge = int(np.sum(finite_t >= t_obs - 1e-15))
        p_upper = (ge + 1) / (len(finite_t) + 1)
        t_null_mean = float(np.mean(finite_t))
        t_null_sd = float(np.std(finite_t, ddof=0))
    else:
        t_obs = p_upper = t_null_mean = t_null_sd = None

    supported = (
        len(informative) >= MIN_INFORMATIVE_UNITS
        and t_obs is not None
        and t_obs > 0
        and p_upper is not None
        and p_upper < 0.05
    )
    decision = (
        "support_species_specific_multinight_footprints"
        if supported
        else "stop_no_species_specific_multinight_footprint_support"
    )

    footprint_counts = Counter(x["species"] for x in footprints)
    footprint_size_counts = Counter(int(x["footprint_size"]) for x in footprints)

    stage4_corr = None
    if stage4_result is not None and "night_first" in stage4_result:
        ses_by_id = {
            x["id"]: x.get("ses")
            for x in stage4_result["night_first"]
            if x.get("analyzable") and x.get("ses") is not None
        }
        zx, sy = [], []
        for s in summaries:
            if s["z_observed"] is not None and s["id"] in ses_by_id:
                zx.append(float(s["z_observed"]))
                sy.append(float(ses_by_id[s["id"]]))
        stage4_corr = pearson(zx, sy)

    return {
        "schema": "neon.san_jacinto_individual_footprint_assortativity.v1",
        "status": "stage5_frozen_test_complete",
        "source": {
            "figshare_doi": "10.6084/m9.figshare.18295520.v1",
            "file_id": 33058799,
            "sha256_verified": True,
        },
        "frozen_design": "docs/SAN_JACINTO_TRANSITION_NICHE_EXPLORATION_V1.md",
        "design": {
            "footprint": "set of distinct nightly-FIRST traps for individual x grid x season",
            "minimum_distinct_nights": MIN_NIGHTS,
            "minimum_multinight_individuals_per_species_unit": MIN_INDIVIDUALS_PER_SPECIES,
            "minimum_species_per_unit": MIN_SPECIES_PER_UNIT,
            "excluded_stage4_source_mismatch_units": sorted(EXCLUDED_UNITS),
            "pair_similarity": "Jaccard",
            "unit_statistic": "mean conspecific Jaccard minus mean heterospecific Jaccard",
            "null": "shuffle species labels only within exact individual footprint-size strata inside grid-season",
            "permutations": permutations,
            "seed": seed,
        },
        "support": {
            "multi_night_individuals_before_unit_filter": len(footprints),
            "multi_night_individuals_by_species": dict(sorted(footprint_counts.items())),
            "footprint_size_distribution": {str(k): v for k, v in sorted(footprint_size_counts.items())},
            "eligible_grid_seasons": len(units),
            "informative_grid_seasons_nonzero_null_sd": len(informative),
        },
        "primary": {
            "global_mean_standardized_footprint_assortativity": t_obs,
            "null_global_mean": t_null_mean,
            "null_global_sd": t_null_sd,
            "one_sided_monte_carlo_p_upper": p_upper,
            "required_informative_grid_seasons": MIN_INFORMATIVE_UNITS,
            "required_direction": "positive",
            "alpha": 0.05,
            "decision": decision,
        },
        "secondary": {
            "positive_raw_difference_units": sum(
                1 for s in summaries if s["observed_difference"] is not None and s["observed_difference"] > 0
            ),
            "eligible_units": len(summaries),
            "correlation_unit_z_with_stage4_night_first_ses": stage4_corr,
            "claim_status": "descriptive_only",
        },
        "grid_seasons": summaries,
        "claim_boundary": {
            "species_pair_decomposition_opened": False,
            "alternative_overlap_metric_opened": False,
            "alternative_footprint_size_binning_opened": False,
            "alternative_minimum_nights_opened": False,
            "habitat_mechanism_identified": False,
            "competition_causally_identified": False,
            "interpretation_if_supported": (
                "Same-species individuals repeatedly use more similar spatial footprints than "
                "different-species individuals after exact control for footprint size."
            ),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, default=None)
    ap.add_argument("--stage4-result", type=Path, required=False)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--permutations", type=int, default=PERMUTATIONS)
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    rows = download_rows(args.cache)
    stage4 = None
    if args.stage4_result is not None:
        stage4 = json.loads(args.stage4_result.read_text())
    result = run_test(
        rows,
        permutations=args.permutations,
        seed=args.seed,
        stage4_result=stage4,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["support"], indent=2, sort_keys=True))
    print(json.dumps(result["primary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
