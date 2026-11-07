#!/usr/bin/env python3
"""Effect-blind Portal support audit for the multiscale density programme.

This script never computes spatial distances or W/B values. It asks only whether
the pinned Portal Project capture table contains enough repeated captures of the
same marked individual inside the same trapping period/plot to estimate an
individual-scale spatial variance on the same session as a population footprint.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


VALID_STAKES = {f"{r}{c}" for r in range(1, 8) for c in range(1, 8)}


def _clean(v: object) -> str:
    return "" if v is None else str(v).strip()


def _read(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def _targets(species_rows: list[dict]) -> dict[str, str]:
    out = {}
    for row in species_rows:
        if _clean(row.get("rodent")) != "1":
            continue
        if _clean(row.get("censustarget")) != "1":
            continue
        if _clean(row.get("unidentified")) == "1":
            continue
        code = _clean(row.get("speciescode"))
        name = _clean(row.get("scientificname"))
        if code and name:
            out[code] = name
    return out


def audit(portal_dir: Path, start=(2009, 8), end=(2015, 3)) -> dict:
    capture = _read(portal_dir / "Rodents" / "Portal_rodent.csv")
    trapping = _read(portal_dir / "Rodents" / "Portal_rodent_trapping.csv")
    species = _read(portal_dir / "Rodents" / "Portal_rodent_species.csv")
    targets = _targets(species)

    effort = {}
    for row in trapping:
        try:
            key = (
                int(_clean(row.get("year"))),
                int(_clean(row.get("month"))),
                int(_clean(row.get("period"))),
                _clean(row.get("plot")),
            )
        except ValueError:
            continue
        effort[key] = row

    grouped = defaultdict(lambda: {
        "rows": 0,
        "days": set(),
        "ids": defaultdict(list),
    })
    excluded = Counter()

    for row in capture:
        try:
            year = int(_clean(row.get("year")))
            month = int(_clean(row.get("month")))
            period = int(_clean(row.get("period")))
        except ValueError:
            excluded["invalid_time"] += 1
            continue
        if period <= 0:
            excluded["nonprimary_period"] += 1
            continue
        if (year, month) < start or (year, month) > end:
            excluded["outside_window"] += 1
            continue

        sp = _clean(row.get("species"))
        if sp not in targets:
            excluded["nontarget_taxon"] += 1
            continue
        plot = _clean(row.get("plot"))
        ident = _clean(row.get("id"))
        stake = _clean(row.get("stake"))
        if not plot or not ident:
            excluded["missing_plot_or_id"] += 1
            continue

        erow = effort.get((year, month, period, plot))
        if erow is None:
            excluded["missing_effort"] += 1
            continue
        if _clean(erow.get("sampled")) != "1":
            excluded["not_sampled"] += 1
            continue
        if _clean(erow.get("effort")) != "49":
            excluded["nonstandard_effort"] += 1
            continue
        if _clean(erow.get("qcflag")) != "1":
            excluded["failed_qc"] += 1
            continue

        key = (year, month, period, plot, sp)
        g = grouped[key]
        g["rows"] += 1
        day = _clean(row.get("day"))
        if day:
            g["days"].add(day)
        g["ids"][ident].append(stake in VALID_STAKES)

    sessions = []
    for (year, month, period, plot, sp), g in sorted(grouped.items()):
        repeat_capture = 0
        repeat_coordinate_supported = 0
        coordinate_supported = 0
        for records in g["ids"].values():
            n = len(records)
            n_coord = sum(int(x) for x in records)
            if n_coord >= 1:
                coordinate_supported += 1
            if n >= 2:
                repeat_capture += 1
            if n_coord >= 2:
                repeat_coordinate_supported += 1
        sessions.append({
            "year": year,
            "month": month,
            "period": period,
            "plot": plot,
            "species_code": sp,
            "species": targets[sp],
            "n_capture_rows": g["rows"],
            "n_unique_individuals": len(g["ids"]),
            "n_coordinate_supported_individuals": coordinate_supported,
            "n_repeat_capture_individuals": repeat_capture,
            "n_repeat_coordinate_supported_individuals": repeat_coordinate_supported,
            "n_distinct_capture_days": len(g["days"]),
        })

    by_species = defaultdict(lambda: {
        "sessions": 0,
        "plots": set(),
        "years": set(),
        "sessions_with_repeat": 0,
        "sessions_with_repeat_coordinate_support": 0,
        "max_repeat_coordinate_supported": 0,
        "repeat_coordinate_supported_individual_sessions": 0,
    })
    for s in sessions:
        z = by_species[s["species"]]
        z["sessions"] += 1
        z["plots"].add(s["plot"])
        z["years"].add(s["year"])
        z["sessions_with_repeat"] += int(s["n_repeat_capture_individuals"] > 0)
        z["sessions_with_repeat_coordinate_support"] += int(
            s["n_repeat_coordinate_supported_individuals"] > 0
        )
        z["max_repeat_coordinate_supported"] = max(
            z["max_repeat_coordinate_supported"],
            s["n_repeat_coordinate_supported_individuals"],
        )
        z["repeat_coordinate_supported_individual_sessions"] += (
            s["n_repeat_coordinate_supported_individuals"]
        )

    species_summary = []
    for sp, z in sorted(by_species.items()):
        species_summary.append({
            "species": sp,
            "n_sessions": z["sessions"],
            "n_plots": len(z["plots"]),
            "n_years": len(z["years"]),
            "n_sessions_with_any_repeat_capture": z["sessions_with_repeat"],
            "n_sessions_with_any_repeat_coordinate_support": z[
                "sessions_with_repeat_coordinate_support"
            ],
            "max_repeat_coordinate_supported_individuals_in_session": z[
                "max_repeat_coordinate_supported"
            ],
            "total_repeat_coordinate_supported_individual_sessions": z[
                "repeat_coordinate_supported_individual_sessions"
            ],
        })

    totals = {
        "n_sessions": len(sessions),
        "n_species": len(species_summary),
        "n_sessions_with_any_repeat_capture": sum(
            s["n_repeat_capture_individuals"] > 0 for s in sessions
        ),
        "n_sessions_with_any_repeat_coordinate_support": sum(
            s["n_repeat_coordinate_supported_individuals"] > 0 for s in sessions
        ),
        "n_sessions_with_at_least_3_repeat_coordinate_supported_individuals": sum(
            s["n_repeat_coordinate_supported_individuals"] >= 3 for s in sessions
        ),
        "n_sessions_with_at_least_5_repeat_coordinate_supported_individuals": sum(
            s["n_repeat_coordinate_supported_individuals"] >= 5 for s in sessions
        ),
    }

    return {
        "schema": "neon.portal_multiscale_density_support.v1",
        "status": "effect_blind_structural_support_only",
        "portal_window": [f"{start[0]:04d}-{start[1]:02d}", f"{end[0]:04d}-{end[1]:02d}"],
        "support": {
            "totals": totals,
            "species": species_summary,
            "sessions": sessions,
        },
        "excluded_rows": dict(excluded),
        "boundary": {
            "spatial_distances_calculated": False,
            "within_individual_variance_calculated": False,
            "between_individual_variance_calculated": False,
            "density_slopes_calculated": False,
            "distinct_location_change_used_for_eligibility": False,
            "allowed_interpretation": "same-session capture support only",
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--portal-dir", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    result = audit(a.portal_dir)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "totals": result["support"]["totals"],
        "species_with_repeat_support": [
            x for x in result["support"]["species"]
            if x["n_sessions_with_any_repeat_coordinate_support"] > 0
        ],
        "boundary": result["boundary"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
