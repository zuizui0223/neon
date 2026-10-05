#!/usr/bin/env python3
"""Effect-blind support audit for the multiscale density-accommodation programme.

This script intentionally does not calculate spatial distances, W/B decomposition,
density effects, habitat effects, or any ecological effect size. It only asks
whether species x grid x event sessions contain enough structural information to
support a later cross-scale analysis.

Inputs are NEON DP1.10072.001 mam_perplotnight and mam_pertrapnight CSV tables.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


ALIASES = {
    "nightuid": ("nightuid", "nightUID"),
    "event_id": ("eventID", "eventId", "event_id"),
    "plot_id": ("plotID", "plotId", "plot_id"),
    "sampling_type": ("mammalGridSamplingType", "mammalGridSampleType"),
    "grid_completion": ("gridCompletion",),
    "collect_date": ("collectDate", "date"),
    "trap_coordinate": ("trapCoordinate", "trapCoord"),
    "trap_status": ("trapStatus",),
    "tag_id": ("tagID", "tagId", "individualID", "individualId"),
    "taxon_id": ("taxonID", "taxonId"),
    "scientific_name": ("scientificName", "scientific_name"),
    "site_id": ("siteID", "siteId"),
}


FORBIDDEN_OUTPUT_TOKENS = (
    "distance",
    "displacement",
    "within_individual_spread",
    "between_individual_spread",
    "beta_w",
    "beta_b",
    "delta_beta",
    "habitat_effect",
)


def _clean(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"na", "nan", "none", "null"}:
        return ""
    return text


def _read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = [{k: _clean(v) for k, v in row.items()} for row in reader]
        return rows, list(reader.fieldnames or [])


def _resolve_field(fields: Iterable[str], logical: str, required: bool = True) -> str | None:
    available = set(fields)
    for candidate in ALIASES[logical]:
        if candidate in available:
            return candidate
    if required:
        raise ValueError(f"required field for {logical!r} not found; aliases={ALIASES[logical]}")
    return None


def _capture_row(row: dict[str, str], trap_status_field: str | None, tag_field: str | None) -> bool:
    if tag_field and _clean(row.get(tag_field)):
        return True
    if trap_status_field:
        return "capture" in _clean(row.get(trap_status_field)).lower()
    return False


def _taxon(row: dict[str, str], taxon_field: str | None, sci_field: str | None) -> str:
    if taxon_field:
        val = _clean(row.get(taxon_field))
        if val:
            return val
    if sci_field:
        return _clean(row.get(sci_field))
    return ""


def audit(perplotnight: Path, pertrapnight: Path) -> dict:
    plot_rows, plot_fields = _read_csv(perplotnight)
    trap_rows, trap_fields = _read_csv(pertrapnight)

    p_night = _resolve_field(plot_fields, "nightuid")
    p_event = _resolve_field(plot_fields, "event_id")
    p_plot = _resolve_field(plot_fields, "plot_id")
    p_sampling = _resolve_field(plot_fields, "sampling_type", required=False)
    p_completion = _resolve_field(plot_fields, "grid_completion", required=False)
    p_date = _resolve_field(plot_fields, "collect_date", required=False)
    p_site = _resolve_field(plot_fields, "site_id", required=False)

    t_night = _resolve_field(trap_fields, "nightuid")
    t_plot = _resolve_field(trap_fields, "plot_id")
    t_coord = _resolve_field(trap_fields, "trap_coordinate")
    t_status = _resolve_field(trap_fields, "trap_status", required=False)
    t_tag = _resolve_field(trap_fields, "tag_id", required=False)
    t_taxon = _resolve_field(trap_fields, "taxon_id", required=False)
    t_sci = _resolve_field(trap_fields, "scientific_name", required=False)

    if t_taxon is None and t_sci is None:
        raise ValueError("mam_pertrapnight must contain taxonID or scientificName")

    night_meta: dict[str, dict[str, str]] = {}
    duplicate_nightuid = 0
    conflicting_nightuid = 0
    for row in plot_rows:
        n = _clean(row.get(p_night))
        if not n:
            continue
        meta = {
            "event_id": _clean(row.get(p_event)),
            "plot_id": _clean(row.get(p_plot)),
            "sampling_type": _clean(row.get(p_sampling)) if p_sampling else "",
            "grid_completion": _clean(row.get(p_completion)) if p_completion else "",
            "collect_date": _clean(row.get(p_date)) if p_date else "",
            "site_id": _clean(row.get(p_site)) if p_site else "",
        }
        if n in night_meta:
            duplicate_nightuid += 1
            if night_meta[n] != meta:
                conflicting_nightuid += 1
        else:
            night_meta[n] = meta

    # Effort is summarized at plot x event before any species filtering.
    effort = defaultdict(lambda: {
        "nightuids": set(),
        "trap_nights": set(),
        "trap_coordinates": set(),
        "sampling_types": set(),
        "grid_completion_values": set(),
        "site_ids": set(),
    })

    capture_groups = defaultdict(lambda: {
        "capture_rows": 0,
        "tagged_capture_rows": 0,
        "untagged_capture_rows": 0,
        "capture_nightuids": set(),
        "capture_coordinates": set(),
        "individual_rows": defaultdict(list),
    })

    missing_night_join = 0
    missing_event = 0
    capture_missing_taxon = 0

    for idx, row in enumerate(trap_rows):
        n = _clean(row.get(t_night))
        meta = night_meta.get(n)
        if meta is None:
            missing_night_join += 1
            continue
        event = meta["event_id"]
        plot = meta["plot_id"] or _clean(row.get(t_plot))
        if not event:
            missing_event += 1
            continue
        key = (plot, event)
        e = effort[key]
        coord = _clean(row.get(t_coord))
        e["nightuids"].add(n)
        if coord:
            e["trap_nights"].add((n, coord))
            e["trap_coordinates"].add(coord)
        if meta["sampling_type"]:
            e["sampling_types"].add(meta["sampling_type"])
        if meta["grid_completion"]:
            e["grid_completion_values"].add(meta["grid_completion"])
        if meta["site_id"]:
            e["site_ids"].add(meta["site_id"])

        if not _capture_row(row, t_status, t_tag):
            continue
        taxon = _taxon(row, t_taxon, t_sci)
        if not taxon:
            capture_missing_taxon += 1
            continue

        g = capture_groups[(taxon, plot, event)]
        g["capture_rows"] += 1
        g["capture_nightuids"].add(n)
        if coord:
            g["capture_coordinates"].add(coord)
        tag = _clean(row.get(t_tag)) if t_tag else ""
        if tag:
            g["tagged_capture_rows"] += 1
            g["individual_rows"][tag].append((n, coord))
        else:
            g["untagged_capture_rows"] += 1

    sessions = []
    for (taxon, plot, event), g in sorted(capture_groups.items()):
        e = effort[(plot, event)]
        tag_records = g["individual_rows"]
        repeat_capture = 0
        repeat_location = 0
        repeat_night = 0
        for records in tag_records.values():
            if len(records) >= 2:
                repeat_capture += 1
            coords = {c for _, c in records if c}
            nights = {n for n, _ in records if n}
            if len(records) >= 2 and len(coords) >= 2:
                repeat_location += 1
            if len(nights) >= 2:
                repeat_night += 1

        sessions.append({
            "taxon": taxon,
            "plot_id": plot,
            "event_id": event,
            "site_ids": sorted(e["site_ids"]),
            "sampling_types": sorted(e["sampling_types"]),
            "grid_completion_values": sorted(e["grid_completion_values"]),
            "n_trapping_nights": len(e["nightuids"]),
            "n_trap_nights_observed": len(e["trap_nights"]),
            "n_distinct_trap_coordinates_in_effort": len(e["trap_coordinates"]),
            "n_capture_rows": int(g["capture_rows"]),
            "n_tagged_capture_rows": int(g["tagged_capture_rows"]),
            "n_untagged_capture_rows": int(g["untagged_capture_rows"]),
            "n_unique_tagged_individuals": len(tag_records),
            "n_repeat_capture_tagged_individuals": repeat_capture,
            "n_repeat_location_tagged_individuals": repeat_location,
            "n_multi_night_tagged_individuals": repeat_night,
            "n_capture_nights": len(g["capture_nightuids"]),
            "n_distinct_capture_coordinates": len(g["capture_coordinates"]),
        })

    species = defaultdict(lambda: {
        "sessions": 0,
        "plots": set(),
        "sites": set(),
        "sampling_types": set(),
        "sessions_with_any_repeat_capture": 0,
        "sessions_with_any_repeat_location": 0,
        "sessions_with_any_multi_night_individual": 0,
        "max_unique_tagged_individuals": 0,
        "max_repeat_location_individuals": 0,
    })
    for s in sessions:
        z = species[s["taxon"]]
        z["sessions"] += 1
        z["plots"].add(s["plot_id"])
        z["sites"].update(s["site_ids"])
        z["sampling_types"].update(s["sampling_types"])
        z["sessions_with_any_repeat_capture"] += int(s["n_repeat_capture_tagged_individuals"] > 0)
        z["sessions_with_any_repeat_location"] += int(s["n_repeat_location_tagged_individuals"] > 0)
        z["sessions_with_any_multi_night_individual"] += int(s["n_multi_night_tagged_individuals"] > 0)
        z["max_unique_tagged_individuals"] = max(
            z["max_unique_tagged_individuals"], s["n_unique_tagged_individuals"]
        )
        z["max_repeat_location_individuals"] = max(
            z["max_repeat_location_individuals"], s["n_repeat_location_tagged_individuals"]
        )

    species_summary = []
    for taxon, z in sorted(species.items()):
        species_summary.append({
            "taxon": taxon,
            "n_sessions": z["sessions"],
            "n_plots": len(z["plots"]),
            "n_sites": len(z["sites"]),
            "sampling_types": sorted(z["sampling_types"]),
            "n_sessions_with_any_repeat_capture": z["sessions_with_any_repeat_capture"],
            "n_sessions_with_any_repeat_location": z["sessions_with_any_repeat_location"],
            "n_sessions_with_any_multi_night_individual": z["sessions_with_any_multi_night_individual"],
            "max_unique_tagged_individuals_in_session": z["max_unique_tagged_individuals"],
            "max_repeat_location_individuals_in_session": z["max_repeat_location_individuals"],
        })

    result = {
        "schema": "neon.multiscale_density_accommodation.estimability_audit.v1",
        "status": "effect_blind_structural_support_only",
        "inputs": {
            "mam_perplotnight": str(perplotnight),
            "mam_pertrapnight": str(pertrapnight),
            "n_perplotnight_rows": len(plot_rows),
            "n_pertrapnight_rows": len(trap_rows),
        },
        "field_map": {
            "perplotnight": {
                "nightuid": p_night,
                "event_id": p_event,
                "plot_id": p_plot,
                "sampling_type": p_sampling,
                "grid_completion": p_completion,
                "collect_date": p_date,
                "site_id": p_site,
            },
            "pertrapnight": {
                "nightuid": t_night,
                "plot_id": t_plot,
                "trap_coordinate": t_coord,
                "trap_status": t_status,
                "tag_id": t_tag,
                "taxon_id": t_taxon,
                "scientific_name": t_sci,
            },
        },
        "data_quality": {
            "duplicate_perplotnight_nightuid_rows": duplicate_nightuid,
            "conflicting_perplotnight_nightuid_rows": conflicting_nightuid,
            "pertrapnight_rows_without_plotnight_join": missing_night_join,
            "pertrapnight_rows_without_event_id_after_join": missing_event,
            "capture_rows_without_taxon": capture_missing_taxon,
        },
        "support": {
            "n_species_session_records": len(sessions),
            "n_taxa_with_capture_sessions": len(species_summary),
            "sessions": sessions,
            "taxa": species_summary,
        },
        "boundary": {
            "effect_values_opened": False,
            "spatial_distances_calculated": False,
            "habitat_effects_calculated": False,
            "density_effects_calculated": False,
            "allowed_interpretation": "structural estimability and support only",
        },
    }

    serialized = json.dumps(result, sort_keys=True).lower()
    for token in FORBIDDEN_OUTPUT_TOKENS:
        if token in serialized:
            raise AssertionError(f"forbidden effect token leaked into output: {token}")
    return result


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--perplotnight", required=True, type=Path)
    p.add_argument("--pertrapnight", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()

    result = audit(a.perplotnight, a.pertrapnight)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
