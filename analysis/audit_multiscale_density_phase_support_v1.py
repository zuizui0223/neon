#!/usr/bin/env python3
"""Effect-blind support for a density-path / spatial-memory question.

Only chronology, taxon/site/plot identity and MNKA are inspected.
No W/B, home-range or abundance-response slopes are computed here.

In particular MNKA is a retrospective known-alive index and uses later
captures. Temporal differences in MNKA must NOT be interpreted as causal
signals available to animals at the sampling time.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from analysis.audit_multiscale_density_mnka_variation_v1 import run as run_mnka

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "multiscale_density_phase_support_v1.json"
GENERA = {"Chaetodipus", "Dipodomys", "Myodes", "Peromyscus", "Sigmodon"}
MODES = {"packing": {"Chaetodipus", "Myodes", "Peromyscus"},
         "compression": {"Dipodomys", "Sigmodon"}}
MAX_GAP_DAYS = 370
MAX_CURRENT_ABUNDANCE_DIFFERENCE = 2


def assess(rows: list[dict]) -> dict:
    """Detect whether within-series near-equal MNKA events have opposite histories."""
    by_series = defaultdict(list)
    for row in rows:
        if row["genus"] not in GENERA:
            continue
        key = (str(row["taxon"]), str(row["site"]), str(row["plot_id"]))
        by_series[key].append(row)
    transitions = []
    chronology_errors = Counter()
    for key, session in sorted(by_series.items()):
        sorted_events = sorted(session, key=lambda r: (r["event_date"], str(r["event_id"])))
        seen_dates = set()
        if len({r["event_id"] for r in session}) != len(session):
            chronology_errors["duplicated_event_ids"] += 1
            continue
        for r in sorted_events:
            d = date.fromisoformat(str(r["event_date"])[:10])
            if d in seen_dates:
                chronology_errors["repeated_date_within_series"] += 1
            seen_dates.add(d)
        for a, b in zip(sorted_events, sorted_events[1:]):
            gap = (date.fromisoformat(str(b["event_date"])[:10])
                   - date.fromisoformat(str(a["event_date"])[:10])).days
            if gap <= 0:
                chronology_errors["nonpositive_gap"] += 1
                continue
            delta = int(b["mnka"]) - int(a["mnka"])
            transitions.append({
                "series": key, "genus": b["genus"], "site": key[1],
                "prior_n": int(a["mnka"]), "current_n": int(b["mnka"]),
                "delta_n": delta, "gap_days": gap,
                "phase": "increasing" if delta > 0 else "decreasing" if delta < 0 else "stable",
            })
    eligible = [r for r in transitions if 0 < r["gap_days"] <= MAX_GAP_DAYS]
    per_series = defaultdict(list)
    for r in eligible:
        per_series[r["series"]].append(r)

    # Count *pairs* of events with similar current abundance, but opposite
    # abundance trends, with both events from the same taxon × plot series.
    # These are support pairs, NOT independent observations.
    pair_info = []
    for series, rs in per_series.items():
        ups = [r for r in rs if r["phase"] == "increasing"]
        downs = [r for r in rs if r["phase"] == "decreasing"]
        for a in ups:
            for b in downs:
                if abs(a["current_n"] - b["current_n"]) <= MAX_CURRENT_ABUNDANCE_DIFFERENCE:
                    pair_info.append({"series": series, "genus": a["genus"], "site": a["site"]})

    def summary(genera: set[str]) -> dict:
        ts = [r for r in eligible if r["genus"] in genera]
        ps = [r for r in pair_info if r["genus"] in genera]
        paired_series = {r["series"] for r in ps}
        return {
            "transitions": len(ts),
            "sites_with_transitions": len({r["site"] for r in ts}),
            "series_with_transitions": len({r["series"] for r in ts}),
            "increasing": sum(r["phase"] == "increasing" for r in ts),
            "decreasing": sum(r["phase"] == "decreasing" for r in ts),
            "stable": sum(r["phase"] == "stable" for r in ts),
            "near_equal_opposite_phase_pairs": len(ps),
            "paired_taxon_plot_series": len(paired_series),
            "paired_sites": len({r["site"] for r in ps}),
        }

    results = {g: summary({g}) for g in sorted(GENERA)}
    mode_results = {m: summary(gs) for m, gs in MODES.items()}
    # A deliberately conservative estimability threshold, NOT a significance
    # criterion or biological-effect guard; this support gate is frozen before
    # any new phase × W/B effects are opened.
    mode_gate = {
        m: (
            a["near_equal_opposite_phase_pairs"] >= 20
            and a["paired_taxon_plot_series"] >= 10
            and a["paired_sites"] >= 3
        )
        for m, a in mode_results.items()
    }
    return {
        "schema": "neon.multiscale_density.phase_support.v1",
        "state": "SUPPORT_ONLY_EFFECT_BLIND_TO_NEW_PHASE_W_B_FITS",
        "source": "RELEASE-2026 genus MNKA; not future confirmatory data",
        "retrospective_mnka_lookahead": True,
        "max_preceding_event_gap_days": MAX_GAP_DAYS,
        "near_equal_current_mnka_tolerance": MAX_CURRENT_ABUNDANCE_DIFFERENCE,
        "input_rows": len(rows),
        "series_considered": len(by_series),
        "total_transitions_all_gaps": len(transitions),
        "gap_le_120": sum(0 < r["gap_days"] <= 120 for r in transitions),
        "gap_121_to_370": sum(120 < r["gap_days"] <= 370 for r in transitions),
        "gap_gt_370": sum(r["gap_days"] > 370 for r in transitions),
        "chronology_errors": dict(chronology_errors),
        "genera": results,
        "modes": mode_results,
        "mode_gate": mode_gate,
        "both_modes_structurally_supportable": all(mode_gate.values()),
        "interpretation": (
            "Even a passed support gate only licenses exploratory path-dependence "
            "analysis, not causality, density memory, independent confirmation "
            "or updates to the frozen 6/8 generality result."
        ),
    }


def run() -> dict:
    mnka = run_mnka()
    if len(mnka["paired_sessions"]) != 1536:
        raise RuntimeError("frozen MNKA support drift")
    return assess(mnka["paired_sessions"])


if __name__ == "__main__":
    result = run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
