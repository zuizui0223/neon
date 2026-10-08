#!/usr/bin/env python3
"""Exploratory, non-causal test of local capture-order association.

Deliberately separate from the MEE positional-aliasing manuscript.
Capture records are NOT direct observations of undisturbed space use.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

BINS = ("early", "middle", "late")
FLAGS = {f"{letter}{i}" for letter in "ABCDEFG" for i in range(1, 8)}


def date_iso(value: object) -> str | None:
    value = str(value or "").strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def build_capture_index(rows: list[dict]) -> tuple[dict, dict]:
    """Keep unique captures; reject conflicting trap × check records."""
    by_key = defaultdict(set)
    rejects = Counter()
    for r in rows:
        grid = str(r.get("grid") or "").strip()
        day = date_iso(r.get("date"))
        slot = str(r.get("time_bin") or "").strip().lower()
        flag = str(r.get("flag") or "").strip().upper()
        species = str(r.get("species") or "").strip()
        uid = str(r.get("unique_ID") or "").strip()
        if not grid or day is None or slot not in BINS or flag not in FLAGS or not species or not uid:
            rejects["invalid_capture_row"] += 1
            continue
        by_key[(grid, day, slot, flag)].add((species, uid))

    captures = {}
    for key, occupants in by_key.items():
        if len(occupants) == 1:
            captures[key] = next(iter(occupants))
        else:
            rejects["ambiguous_trap_check_cell"] += 1

    # A night is observed in all three bins only when there is >=1 unique
    # capture entry per bin. This is NOT proof that 49 traps were all checked.
    by_night = defaultdict(set)
    for (grid, day, slot, _flag) in captures:
        by_night[(grid, day)].add(slot)
    eligible = {key for key, bins in by_night.items() if set(BINS) == bins}
    return ({key: val for key, val in captures.items() if key[:2] in eligible},
            {"eligible_grid_nights": len(eligible), "capture_cells": len(captures),
             "rejections": dict(rejects)})


def case_rows(captures: dict) -> list[dict]:
    """Pair observed subsequent captures with same-flag other-night references.

    Reference previous-bin capture is drawn at same flag, grid, month, and
    preceding time bin from a DIFFERENT night. It controls stable geography
    and seasonal species pool, but is not a randomized intervention.
    """
    days_by_grid_bout = defaultdict(set)
    for (grid, day, _slot, _flag) in captures:
        days_by_grid_bout[(grid, day[:7])].add(day)

    results = []
    for (grid, day, slot, flag), following in sorted(captures.items()):
        idx = BINS.index(slot)
        if idx == 0:
            continue
        prevslot = BINS[idx - 1]
        preceding = captures.get((grid, day, prevslot, flag))
        if preceding is None or preceding == following:
            continue  # self-recapture or no observed previous occupant
        comparisons = []
        for altday in sorted(days_by_grid_bout[(grid, day[:7])]):
            if altday == day:
                continue
            alternate = captures.get((grid, altday, prevslot, flag))
            if alternate is not None and alternate != following:
                comparisons.append(float(alternate[0] == following[0]))
        if not comparisons:
            continue
        observed_same = float(preceding[0] == following[0])
        baseline = sum(comparisons) / len(comparisons)
        results.append({
            "grid": grid, "month": day[:7], "date": day,
            "transition": prevslot + "_to_" + slot,
            "flag": flag,
            "previous_species": preceding[0],
            "following_species": following[0],
            "observed_same_species": observed_same,
            "reference_same_species": baseline,
            "difference": observed_same - baseline,
            "reference_n": len(comparisons),
        })
    return results


def summarize(cases: list[dict], *, seed: int = 20261008,
              bootstrap_replicates: int = 2000) -> dict:
    rng = random.Random(seed)
    result = {}
    for label in ("pooled", "early_to_middle", "middle_to_late"):
        a = [r for r in cases if label == "pooled" or r["transition"] == label]
        if not a:
            result[label] = {"state": "NO_MATCHED_PAIRS", "n": 0}
            continue
        clusters = defaultdict(list)
        for r in a:
            clusters[(r["grid"], r["month"])].append(r["difference"])
        observed = sum(r["observed_same_species"] for r in a) / len(a)
        reference = sum(r["reference_same_species"] for r in a) / len(a)
        ci = None
        if len(clusters) >= 3 and bootstrap_replicates > 0:
            cluster_values = list(clusters.values())
            bs = []
            for _ in range(bootstrap_replicates):
                sample = [rng.choice(cluster_values) for _ in cluster_values]
                flat = [v for group in sample for v in group]
                bs.append(sum(flat) / len(flat))
            bs.sort()
            ci = [bs[int((len(bs) - 1) * 0.025)],
                  bs[int((len(bs) - 1) * 0.975)]]
        result[label] = {
            "state": "EXPLORATORY_ONLY",
            "n": len(a), "grid_bout_clusters": len(clusters),
            "grids": len({r["grid"] for r in a}),
            "observed_same_species_fraction": observed,
            "same_flag_other_night_reference_fraction": reference,
            "matched_difference": observed - reference,
            "cluster_bootstrap95": ci,
        }
    return result


def analyze(rows: list[dict], *, replicates: int = 2000) -> dict:
    captures, qc = build_capture_index(rows)
    cases = case_rows(captures)
    return {
        "schema": "neon.san_jacinto.local_sequence.exploratory.v1",
        "state": "POST_RESULT_EXPLORATORY_NOT_CONFIRMATORY",
        "source_data_type": "capture_only",
        "no_capture_row_is_not_verified_absence": True,
        "selection": "grid nights with >=1 unambiguous capture in each of 3 bins",
        "qc": qc,
        "matched_cases": len(cases),
        "analysis": summarize(cases, bootstrap_replicates=replicates),
        "claim_boundary": (
            "A conditional same-trap capture-order association cannot identify "
            "olfactory cues, competition, free-living avoidance or causality; "
            "selection into repeat capture and trap-reset practices remain possible."
        ),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", type=Path)
    src.add_argument("--download-source", action="store_true")
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--replicates", type=int, default=2000)
    args = ap.parse_args()
    if args.replicates < 0:
        ap.error("--replicates must be nonnegative")
    if args.download_source:
        from analysis.san_jacinto_positional_aliasing_v1 import download_rows
        rows = download_rows(args.output.parent / "san_jacinto_raw_cache.csv")
    else:
        with args.input.open(newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
    result = analyze(rows, replicates=args.replicates)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"qc": result["qc"], "analysis": result["analysis"]}, indent=2))


if __name__ == "__main__":
    main()
