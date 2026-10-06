#!/usr/bin/env python3
"""Effect-blind genus-level MNKA and taxonomy-history audit.

This audit opens NEON RELEASE-2026 capture identities and event structure but
never computes spatial distances, W, B, or abundance-response slopes.

Primary response sessions remain target taxon concepts. The abundance candidate
is genus-level MNKA, following the direct NEON Peromyscus precedent: tagged
individuals are treated as known alive on eligible plot-events between their
first and last captures at that plot.

Same-genus taxonomic changes are tolerated for the abundance index; histories
that cross genera are excluded from genus MNKA and counted explicitly.
"""
from __future__ import annotations

import csv
import json
import os
import statistics
import tempfile
import urllib.request
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from analysis.audit_multiscale_density_estimability_v1 import audit
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    END,
    MAX_DOWNLOAD_WORKERS,
    PRODUCT,
    PRODUCT_URL,
    QUERY_URL,
    RELEASE,
    START,
    TOKEN_ENV,
    USER_AGENT,
    _candidate_nights,
    _download_many,
    _inventory,
    _read_plot_rows,
    _read_trap_rows,
    _request_json,
    _site_codes,
    _write_csv,
)

ROOT = Path(__file__).resolve().parents[1]
TARGET_LOCK = ROOT / "results" / "multiscale_density_target_taxon_lock_v1.json"
OUT = ROOT / "build" / "multiscale_density_mnka_variation_v1.json"
TAXONOMY_URL = (
    "https://data.neonscience.org/api/v0/taxonomy?"
    "taxonTypeCode=SMALL_MAMMAL&verbose=true&offset=0&limit=1000"
)
COMPLETE = "setting complete, processing complete"
SATURATION_MAX = 0.30
MIN_REPEAT = 5


def _capture_status(value: str) -> bool:
    s = str(value or "").strip().lower()
    return "capture" in s and "no capture" not in s


def _quantile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    x = sorted(float(v) for v in values)
    if len(x) == 1:
        return x[0]
    pos = (len(x) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(x) - 1)
    f = pos - lo
    return x[lo] * (1.0 - f) + x[hi] * f


def _taxonomy() -> tuple[set[str], dict[str, str], dict[str, str]]:
    req = urllib.request.Request(TAXONOMY_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as response:
        payload = json.loads(response.read().decode("utf-8"))
    target_ids: set[str] = set()
    genus_by_taxon: dict[str, str] = {}
    name_by_taxon: dict[str, str] = {}
    for row in payload.get("data", []):
        if str(row.get("taxonProtocolCategory", "")).strip().lower() != "target":
            continue
        tid = str(row.get("taxonID", "")).strip()
        name = str(row.get("dwc:scientificName", "")).strip()
        if not tid or not name:
            continue
        genus = name.replace("×", " ").split()[0].strip("()[]{};,/")
        if not genus:
            continue
        target_ids.add(tid)
        genus_by_taxon[tid] = genus
        name_by_taxon[tid] = name
    return target_ids, genus_by_taxon, name_by_taxon


def run() -> dict:
    token = os.environ.get(TOKEN_ENV, "").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN is required")

    response_target_lock = json.loads(TARGET_LOCK.read_text(encoding="utf-8"))
    response_target_ids = set(response_target_lock["target_taxon_ids"])
    all_target_ids, genus_by_taxon, _ = _taxonomy()

    sites = _site_codes(_request_json(PRODUCT_URL))
    query = _request_json(
        QUERY_URL,
        token=token,
        body={
            "productCode": PRODUCT,
            "siteCodes": sites,
            "startDateMonth": START,
            "endDateMonth": END,
            "release": RELEASE,
            "package": "basic",
            "includeProvisional": False,
        },
    )
    inventory = _inventory(query)

    plot_files = [r for r in inventory if "mam_perplotnight" in r["name"]]
    plot_raw = _download_many(
        plot_files, token, max_workers=MAX_DOWNLOAD_WORKERS
    )
    plot_rows: list[dict[str, str]] = []
    for meta, raw in zip(plot_files, plot_raw):
        plot_rows.extend(_read_plot_rows(raw, meta["site"], meta["month"]))

    candidate_nights, candidate_site_months = _candidate_nights(plot_rows)
    if not candidate_nights:
        raise RuntimeError("no exact-three-night plot-events found")

    trap_files = [
        r for r in inventory
        if "mam_pertrapnight" in r["name"]
        and (r["site"], r["month"]) in candidate_site_months
    ]
    trap_raw = _download_many(
        trap_files, token, max_workers=MAX_DOWNLOAD_WORKERS
    )
    trap_rows: list[dict[str, str]] = []
    for meta, raw in zip(trap_files, trap_raw):
        rows = _read_trap_rows(raw, candidate_nights)
        for row in rows:
            row["_site"] = meta["site"]
            row["_month"] = meta["month"]
        trap_rows.extend(rows)

    compact_plot = [
        {
            k: row[k]
            for k in (
                "nightuid",
                "eventID",
                "plotID",
                "siteID",
                "mammalGridSamplingType",
                "gridCompletion",
                "collectDate",
            )
        }
        for row in plot_rows
        if row["nightuid"] in candidate_nights
    ]

    # Reproduce the frozen structural response support.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        p = root / "p.csv"
        t = root / "t.csv"
        _write_csv(
            p,
            compact_plot,
            [
                "nightuid","eventID","plotID","siteID",
                "mammalGridSamplingType","gridCompletion","collectDate",
            ],
        )
        _write_csv(
            t,
            trap_rows,
            [
                "nightuid","plotID","trapCoordinate","trapStatus","tagID",
                "taxonID","scientificName","identificationQualifier","taxonRank",
            ],
        )
        structural = audit(p, t)

    response_sessions = [
        s for s in structural["support"]["sessions"]
        if s.get("primary_complete_session")
        and int(s.get("n_repeat_coordinate_supported_tagged_individuals", 0))
            >= MIN_REPEAT
        and s.get("taxon") in response_target_ids
        and float(s.get("all_capture_trap_night_fraction_of_observed", 1.0))
            <= SATURATION_MAX
    ]

    # Build exact-three-night complete standard event metadata.
    by_event: dict[tuple[str,str,str], dict[str, Any]] = {}
    rows_by_event: dict[tuple[str,str,str], list[dict[str,str]]] = defaultdict(list)
    for row in compact_plot:
        key = (row["siteID"], row["plotID"], row["eventID"])
        rows_by_event[key].append(row)
    for key, rows in rows_by_event.items():
        nights = {r["nightuid"] for r in rows}
        completions = {r["gridCompletion"] for r in rows if r["gridCompletion"]}
        dates = sorted({r["collectDate"] for r in rows if r["collectDate"]})
        site, plot, event = key
        by_event[key] = {
            "site": site,
            "plot": plot,
            "event": event,
            "nights": nights,
            "complete": (
                site != "SRER"
                and len(nights) == 3
                and completions == {COMPLETE}
            ),
            "date": dates[0] if dates else "",
        }

    night_meta: dict[str, tuple[str,str,str]] = {}
    for key, meta in by_event.items():
        for n in meta["nights"]:
            if n in night_meta and night_meta[n] != key:
                raise RuntimeError(f"nightuid maps to multiple plot-events: {n}")
            night_meta[n] = key

    # Target tagged capture histories across complete exact-three-night standard events.
    history_taxa: dict[tuple[str,str,str], set[str]] = defaultdict(set)
    history_events: dict[tuple[str,str,str], set[tuple[str,str,str]]] = defaultdict(set)
    capture_rows_target = 0
    for row in trap_rows:
        if not _capture_status(row.get("trapStatus", "")):
            continue
        tid = str(row.get("taxonID", "")).strip()
        tag = str(row.get("tagID", "")).strip()
        if tid not in all_target_ids or not tag:
            continue
        key = night_meta.get(str(row.get("nightuid", "")).strip())
        if key is None or not by_event[key]["complete"]:
            continue
        site, plot, _ = key
        h = (site, plot, tag)
        history_taxa[h].add(tid)
        history_events[h].add(key)
        capture_rows_target += 1

    same_genus_multitaxon = 0
    cross_genus = 0
    single_taxon = 0
    usable_history_genus: dict[tuple[str,str,str], str] = {}
    for h, taxa in history_taxa.items():
        genera = {genus_by_taxon[t] for t in taxa if t in genus_by_taxon}
        if len(genera) != 1:
            cross_genus += 1
            continue
        genus = next(iter(genera))
        usable_history_genus[h] = genus
        if len(taxa) > 1:
            same_genus_multitaxon += 1
        else:
            single_taxon += 1

    # Order complete events within each site x plot.
    events_by_plot: dict[tuple[str,str], list[tuple[str,str,str]]] = defaultdict(list)
    for key, meta in by_event.items():
        if meta["complete"]:
            events_by_plot[(meta["site"], meta["plot"])].append(key)
    event_index: dict[tuple[str,str,str], int] = {}
    for sp, keys in events_by_plot.items():
        keys.sort(key=lambda k: (by_event[k]["date"], k[2]))
        for i, key in enumerate(keys):
            event_index[key] = i

    # Genus-level MNKA: known alive between first and last complete event capture at a plot.
    alive_intervals: dict[tuple[str,str,str], list[tuple[int,int]]] = defaultdict(list)
    for h, genus in usable_history_genus.items():
        site, plot, _tag = h
        idx = sorted(event_index[e] for e in history_events[h] if e in event_index)
        if not idx:
            continue
        alive_intervals[(site, plot, genus)].append((idx[0], idx[-1]))

    genus_mnka: dict[tuple[str,str,str,str], int] = {}
    for (site, plot), keys in events_by_plot.items():
        for genus in {g for (s,p,g) in alive_intervals if s == site and p == plot}:
            intervals = alive_intervals[(site, plot, genus)]
            for key in keys:
                i = event_index[key]
                genus_mnka[(site, plot, key[2], genus)] = sum(
                    lo <= i <= hi for lo, hi in intervals
                )

    # Pair frozen response sessions to genus MNKA.
    paired = []
    unpaired = []
    for s in response_sessions:
        sites_here = s.get("site_ids", [])
        genera = s.get("genus_labels", [])
        if len(sites_here) != 1 or len(genera) != 1:
            unpaired.append({
                "taxon": s.get("taxon"),
                "plot_id": s.get("plot_id"),
                "event_id": s.get("event_id"),
                "reason": "site_or_genus_not_unique",
            })
            continue
        site = sites_here[0]
        genus = genera[0]
        key = (site, s["plot_id"], s["event_id"], genus)
        mnka = genus_mnka.get(key)
        if mnka is None:
            unpaired.append({
                "taxon": s["taxon"],
                "plot_id": s["plot_id"],
                "event_id": s["event_id"],
                "reason": "genus_mnka_missing",
            })
            continue
        paired.append({
            "site": site,
            "plot_id": s["plot_id"],
            "event_id": s["event_id"],
            "taxon": s["taxon"],
            "genus": genus,
            "mnka": int(mnka),
            "repeat_supported_individuals": int(
                s["n_repeat_coordinate_supported_tagged_individuals"]
            ),
        })

    # Variation is assessed within the same response taxon x site x plot series.
    series: dict[tuple[str,str,str], list[dict]] = defaultdict(list)
    for row in paired:
        series[(row["taxon"], row["site"], row["plot_id"])].append(row)

    series_rows = []
    for (taxon, site, plot), rows in sorted(series.items()):
        vals = [int(r["mnka"]) for r in rows]
        genus = rows[0]["genus"]
        series_rows.append({
            "taxon": taxon,
            "genus": genus,
            "site": site,
            "plot_id": plot,
            "n_response_sessions": len(rows),
            "n_distinct_mnka": len(set(vals)),
            "mnka_min": min(vals),
            "mnka_max": max(vals),
            "mnka_range": max(vals) - min(vals),
            "mnka_median": statistics.median(vals),
        })

    at_least3 = [x for x in series_rows if x["n_response_sessions"] >= 3]
    varying2 = [x for x in at_least3 if x["n_distinct_mnka"] >= 2]
    varying3 = [x for x in at_least3 if x["n_distinct_mnka"] >= 3]
    informative_sessions = {
        (x["taxon"], x["site"], x["plot_id"])
        for x in varying2
    }
    paired_in_informative = [
        x for x in paired
        if (x["taxon"], x["site"], x["plot_id"]) in informative_sessions
    ]

    result = {
        "schema": "neon.multiscale_density.mnka_variation_audit.v1",
        "status": "EFFECT_BLIND_ABUNDANCE_STRUCTURE_ONLY",
        "source": {
            "product": PRODUCT,
            "release": RELEASE,
            "query_start": START,
            "query_end": END,
            "target_lock": str(TARGET_LOCK.relative_to(ROOT)),
        },
        "mnka_definition": {
            "taxonomic_grain": "genus",
            "individual_key": "site x plotID x tagID",
            "known_alive_rule": (
                "within each standard complete exact-3-night plot sequence, "
                "count a usable target individual at every eligible event "
                "between its first and last target capture at that plot"
            ),
            "same_genus_taxon_switch": "retained as one individual for genus MNKA",
            "cross_genus_tag_history": "excluded from MNKA",
            "response_grain": "published target taxon concept x plot x event",
            "precedent": "O'Fallon et al. 2025 genus-level Peromyscus MNKA",
        },
        "taxonomy_history": {
            "target_tag_histories": len(history_taxa),
            "single_taxon_histories": single_taxon,
            "same_genus_multitaxon_histories": same_genus_multitaxon,
            "cross_genus_histories_excluded": cross_genus,
            "target_capture_rows_used_for_history": capture_rows_target,
        },
        "frozen_response_support_check": {
            "expected_target_guarded_sessions": 1536,
            "observed_target_guarded_sessions": len(response_sessions),
            "paired_with_genus_mnka": len(paired),
            "unpaired_count": len(unpaired),
            "unpaired_examples": unpaired[:20],
        },
        "mnka_variation": {
            "taxon_plot_series_total": len(series_rows),
            "series_with_at_least_3_response_sessions": len(at_least3),
            "series_with_at_least_3_sessions_and_2_mnka_values": len(varying2),
            "series_with_at_least_3_sessions_and_3_mnka_values": len(varying3),
            "genera_in_varying_series": len({x["genus"] for x in varying2}),
            "taxa_in_varying_series": len({x["taxon"] for x in varying2}),
            "sites_in_varying_series": len({x["site"] for x in varying2}),
            "response_sessions_in_varying_series": len(paired_in_informative),
            "mnka_range_median_among_varying_series": (
                statistics.median([x["mnka_range"] for x in varying2])
                if varying2 else None
            ),
            "mnka_range_q10_among_varying_series": _quantile(
                [x["mnka_range"] for x in varying2], 0.10
            ),
            "mnka_range_q90_among_varying_series": _quantile(
                [x["mnka_range"] for x in varying2], 0.90
            ),
            "series": series_rows,
        },
        "boundary": {
            "spatial_distances_calculated": False,
            "W_opened": False,
            "B_opened": False,
            "abundance_response_slopes_opened": False,
            "habitat_moderators_opened": False,
        },
    }
    return result


def main() -> int:
    result = run()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "taxonomy_history": result["taxonomy_history"],
        "frozen_response_support_check": result["frozen_response_support_check"],
        "mnka_variation": {
            k: v for k, v in result["mnka_variation"].items()
            if k != "series"
        },
        "boundary": result["boundary"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
