#!/usr/bin/env python3
"""Effect-blind diagnostic of NEON small-mammal bout keys.

Reads only mam_perplotnight from RELEASE-2026, 2015-04 onward. It reports
counts of distinct nightuid/collectDate values under candidate structural keys
and the observed mammalGridSamplingType labels. It does not read pertrapnight,
captures, taxa, coordinates, abundance, W or B.
"""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from pathlib import Path

from analysis.run_multiscale_density_estimability_release2026_v3 import (
    END,
    MAX_DOWNLOAD_WORKERS,
    PRODUCT,
    PRODUCT_URL,
    QUERY_URL,
    RELEASE,
    START,
    TOKEN_ENV,
    _download_many,
    _inventory,
    _read_plot_rows,
    _request_json,
    _site_codes,
)


def run() -> dict:
    token = os.environ.get(TOKEN_ENV, "").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN is required")

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
    files = [r for r in inventory if "mam_perplotnight" in r["name"]]
    raw_files = _download_many(
        files, token, max_workers=MAX_DOWNLOAD_WORKERS
    )

    rows = []
    for meta, raw in zip(files, raw_files):
        rows.extend(_read_plot_rows(raw, meta["site"], meta["month"]))

    type_rows = Counter()
    type_events = defaultdict(set)
    site_event_nights = defaultdict(set)
    plot_event_nights = defaultdict(set)
    plot_event_dates = defaultdict(set)
    event_plots = defaultdict(set)
    event_types = defaultdict(set)

    for row in rows:
        site = row["_site"]
        plot = row["plotID"]
        event = row["eventID"]
        night = row["nightuid"]
        date = row["collectDate"]
        typ = row["mammalGridSamplingType"].strip()
        type_rows[typ] += 1
        type_events[typ].add((site, event))
        site_event_nights[(site, event)].add(night)
        plot_event_nights[(site, plot, event)].add(night)
        if date:
            plot_event_dates[(site, plot, event)].add(date)
        event_plots[(site, event)].add(plot)
        if typ:
            event_types[(site, event)].add(typ)

    def hist(mapping):
        out = Counter(len(v) for v in mapping.values())
        return {str(k): out[k] for k in sorted(out)}

    examples = []
    ordered = sorted(
        plot_event_nights,
        key=lambda k: (
            -len(plot_event_nights[k]),
            k[0], k[1], k[2],
        ),
    )
    for key in ordered[:40]:
        site, plot, event = key
        examples.append({
            "site": site,
            "plot_id": plot,
            "event_id": event,
            "n_nightuid": len(plot_event_nights[key]),
            "n_collect_dates": len(plot_event_dates[key]),
            "sampling_types": sorted(event_types[(site, event)]),
        })

    pathogen_keys = [
        k for k in plot_event_nights
        if any(
            "pathogen" in x.lower()
            for x in event_types[(k[0], k[2])]
        )
    ]
    pathogen_hist = Counter(
        len(plot_event_nights[k]) for k in pathogen_keys
    )

    return {
        "schema": "neon.multiscale_density.bout_schema_diagnostic.v1",
        "status": "effect_blind_perplotnight_only",
        "release": RELEASE,
        "query_start": START,
        "query_end": END,
        "n_sites": len(sites),
        "n_perplotnight_files": len(files),
        "n_perplotnight_rows": len(rows),
        "sampling_type_row_counts": dict(sorted(type_rows.items())),
        "sampling_type_unique_site_event_counts": {
            k: len(v) for k, v in sorted(type_events.items())
        },
        "site_event_nightuid_histogram": hist(site_event_nights),
        "plot_event_nightuid_histogram": hist(plot_event_nights),
        "plot_event_collectdate_histogram": hist(plot_event_dates),
        "event_plot_count_histogram": hist(event_plots),
        "pathogen_plot_event_nightuid_histogram": {
            str(k): pathogen_hist[k] for k in sorted(pathogen_hist)
        },
        "largest_plot_event_examples": examples,
        "boundary": {
            "pertrapnight_opened": False,
            "capture_rows_opened": False,
            "taxa_opened": False,
            "coordinates_opened": False,
            "spatial_distances_calculated": False,
            "W_opened": False,
            "B_opened": False,
            "density_effects_opened": False,
        },
    }


def main() -> int:
    out = run()
    path = Path("build/multiscale_density_bout_schema_diagnostic_v1.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
