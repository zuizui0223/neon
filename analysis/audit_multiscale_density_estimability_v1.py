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
    "identification_qualifier": ("identificationQualifier", "identification_qualifier"),
    "taxon_rank": ("taxonRank", "taxon_rank"),
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
    """Prospectively identify capture rows from NEON trapStatus semantics.

    When trapStatus is available it is authoritative: positive capture labels
    contain "capture" but explicit "no capture" labels must be excluded.
    tagID is used only as a fallback when trapStatus is unavailable.
    """
    if trap_status_field:
        status = _clean(row.get(trap_status_field)).lower()
        if status:
            return "capture" in status and "no capture" not in status
    return bool(tag_field and _clean(row.get(tag_field)))


def _taxon(row: dict[str, str], taxon_field: str | None, sci_field: str | None) -> str:
    if taxon_field:
        val = _clean(row.get(taxon_field))
        if val:
            return val
    if sci_field:
        return _clean(row.get(sci_field))
    return ""


def _genus_from_scientific_name(name: str) -> str:
    """Return a conservative genus label from a published taxon name.

    Composite/cryptic names that begin with one full genus name retain that
    genus. Empty or non-binomial labels remain unresolved rather than being
    guessed from taxonID.
    """
    text = _clean(name)
    if not text:
        return ""
    first = text.replace("×", " ").split()[0].strip("()[]{};,/")
    if not first or first[0].islower():
        return ""
    return first


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
    t_ident_qual = _resolve_field(
        trap_fields, "identification_qualifier", required=False
    )
    t_rank = _resolve_field(trap_fields, "taxon_rank", required=False)

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
        "coordinate_bearing_capture_rows": 0,
        "individual_rows": defaultdict(list),
        "scientific_names": set(),
        "taxon_ranks": set(),
        "identification_qualifiers": Counter(),
    })

    missing_night_join = 0
    missing_event = 0
    capture_missing_taxon = 0
    tagged_noncapture_status_rows = 0
    capture_rows_with_identification_qualifier = 0
    event_tag_taxa = defaultdict(set)

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

        if t_tag and _clean(row.get(t_tag)) and t_status:
            status_text = _clean(row.get(t_status)).lower()
            if status_text and (
                "capture" not in status_text or "no capture" in status_text
            ):
                tagged_noncapture_status_rows += 1

        if not _capture_row(row, t_status, t_tag):
            continue
        taxon = _taxon(row, t_taxon, t_sci)
        if not taxon:
            capture_missing_taxon += 1
            continue

        g = capture_groups[(taxon, plot, event)]
        sci_name = _clean(row.get(t_sci)) if t_sci else ""
        if sci_name:
            g["scientific_names"].add(sci_name)
        taxon_rank = _clean(row.get(t_rank)) if t_rank else ""
        if taxon_rank:
            g["taxon_ranks"].add(taxon_rank)
        ident_qual = _clean(row.get(t_ident_qual)) if t_ident_qual else ""
        if ident_qual:
            capture_rows_with_identification_qualifier += 1
            g["identification_qualifiers"][ident_qual] += 1
        g["capture_rows"] += 1
        g["capture_nightuids"].add(n)
        if coord:
            g["coordinate_bearing_capture_rows"] += 1
        tag = _clean(row.get(t_tag)) if t_tag else ""
        if tag:
            event_tag_taxa[(plot, event, tag)].add(taxon)
            g["tagged_capture_rows"] += 1
            # Store support only, not coordinate identity or displacement.
            g["individual_rows"][tag].append((n, bool(coord)))
        else:
            g["untagged_capture_rows"] += 1

    sessions = []
    for (taxon, plot, event), g in sorted(capture_groups.items()):
        e = effort[(plot, event)]
        tag_records = g["individual_rows"]
        repeat_capture = 0
        repeat_coordinate_supported = 0
        repeat_night = 0
        coordinate_supported_individuals = 0
        for records in tag_records.values():
            if len(records) >= 2:
                repeat_capture += 1
            n_with_coord = sum(int(has_coord) for _, has_coord in records)
            if n_with_coord >= 1:
                coordinate_supported_individuals += 1
            if n_with_coord >= 2:
                repeat_coordinate_supported += 1
            nights = {n for n, _ in records if n}
            if len(nights) >= 2:
                repeat_night += 1

        scientific_names = sorted(g["scientific_names"])
        genera = sorted({
            genus
            for genus in (_genus_from_scientific_name(x) for x in scientific_names)
            if genus
        })

        sessions.append({
            "taxon": taxon,
            "taxon_id_character_count": len(taxon),
            "scientific_names": scientific_names,
            "genus_labels": genera,
            "taxon_ranks": sorted(g["taxon_ranks"]),
            "identification_qualifier_counts": dict(
                sorted(g["identification_qualifiers"].items())
            ),
            "n_capture_rows_with_identification_qualifier": int(
                sum(g["identification_qualifiers"].values())
            ),
            "plot_id": plot,
            "event_id": event,
            "site_ids": sorted(e["site_ids"]),
            "sampling_types": sorted(e["sampling_types"]),
            "grid_completion_values": sorted(e["grid_completion_values"]),
            "n_trapping_nights": len(e["nightuids"]),
            "n_trap_nights_observed": len(e["trap_nights"]),
            "n_distinct_trap_coordinates_in_effort": len(e["trap_coordinates"]),
            "n_capture_rows": int(g["capture_rows"]),
            "n_coordinate_bearing_capture_rows": int(g["coordinate_bearing_capture_rows"]),
            "n_tagged_capture_rows": int(g["tagged_capture_rows"]),
            "n_untagged_capture_rows": int(g["untagged_capture_rows"]),
            "n_unique_tagged_individuals": len(tag_records),
            "n_coordinate_supported_tagged_individuals": coordinate_supported_individuals,
            "n_repeat_capture_tagged_individuals": repeat_capture,
            "n_repeat_coordinate_supported_tagged_individuals": repeat_coordinate_supported,
            "n_multi_night_tagged_individuals": repeat_night,
            "n_capture_nights": len(g["capture_nightuids"]),
        })

    species = defaultdict(lambda: {
        "sessions": 0,
        "plots": set(),
        "sites": set(),
        "sampling_types": set(),
        "scientific_names": set(),
        "genera": set(),
        "taxon_ranks": set(),
        "identification_qualifiers": Counter(),
        "sessions_with_any_identification_qualifier": 0,
        "sessions_with_any_repeat_capture": 0,
        "sessions_with_any_repeat_coordinate_support": 0,
        "sessions_with_any_multi_night_individual": 0,
        "max_unique_tagged_individuals": 0,
        "max_repeat_coordinate_supported_individuals": 0,
    })
    for s in sessions:
        z = species[s["taxon"]]
        z["sessions"] += 1
        z["plots"].add(s["plot_id"])
        z["sites"].update(s["site_ids"])
        z["sampling_types"].update(s["sampling_types"])
        z["scientific_names"].update(s["scientific_names"])
        z["genera"].update(s["genus_labels"])
        z["taxon_ranks"].update(s["taxon_ranks"])
        z["identification_qualifiers"].update(
            s["identification_qualifier_counts"]
        )
        z["sessions_with_any_identification_qualifier"] += int(
            s["n_capture_rows_with_identification_qualifier"] > 0
        )
        z["sessions_with_any_repeat_capture"] += int(s["n_repeat_capture_tagged_individuals"] > 0)
        z["sessions_with_any_repeat_coordinate_support"] += int(
            s["n_repeat_coordinate_supported_tagged_individuals"] > 0
        )
        z["sessions_with_any_multi_night_individual"] += int(s["n_multi_night_tagged_individuals"] > 0)
        z["max_unique_tagged_individuals"] = max(
            z["max_unique_tagged_individuals"], s["n_unique_tagged_individuals"]
        )
        z["max_repeat_coordinate_supported_individuals"] = max(
            z["max_repeat_coordinate_supported_individuals"],
            s["n_repeat_coordinate_supported_tagged_individuals"],
        )

    species_summary = []
    for taxon, z in sorted(species.items()):
        species_summary.append({
            "taxon": taxon,
            "n_sessions": z["sessions"],
            "n_plots": len(z["plots"]),
            "n_sites": len(z["sites"]),
            "sampling_types": sorted(z["sampling_types"]),
            "scientific_names": sorted(z["scientific_names"]),
            "genus_labels": sorted(z["genera"]),
            "taxon_ranks": sorted(z["taxon_ranks"]),
            "identification_qualifier_counts": dict(
                sorted(z["identification_qualifiers"].items())
            ),
            "sessions_with_any_identification_qualifier": z[
                "sessions_with_any_identification_qualifier"
            ],
            "taxon_id_character_count": len(taxon),
            "is_eight_character_taxon_id": len(taxon) == 8,
            "n_sessions_with_any_repeat_capture": z["sessions_with_any_repeat_capture"],
            "n_sessions_with_any_repeat_coordinate_support": z[
                "sessions_with_any_repeat_coordinate_support"
            ],
            "n_sessions_with_any_multi_night_individual": z["sessions_with_any_multi_night_individual"],
            "max_unique_tagged_individuals_in_session": z["max_unique_tagged_individuals"],
            "max_repeat_coordinate_supported_individuals_in_session": z[
                "max_repeat_coordinate_supported_individuals"
            ],
        })

    # Effect-blind support frontier for prospectively choosing a minimum
    # repeat-supported individual count. No coordinate identities or distances
    # enter this table.
    support_frontier = []
    for minimum_individuals in (2, 3, 5, 8, 10, 15, 20):
        eligible_sessions = [
            s for s in sessions
            if s["n_repeat_coordinate_supported_tagged_individuals"]
            >= minimum_individuals
        ]
        taxa_set = {s["taxon"] for s in eligible_sessions}
        genus_set = {
            genus
            for s in eligible_sessions
            for genus in s["genus_labels"]
        }
        plots_set = {s["plot_id"] for s in eligible_sessions}
        sites_set = {
            site
            for s in eligible_sessions
            for site in s["site_ids"]
            if site
        }
        taxon_sites = defaultdict(set)
        taxon_sessions = Counter()
        genus_sites = defaultdict(set)
        genus_sessions = Counter()
        for s in eligible_sessions:
            taxon_sessions[s["taxon"]] += 1
            for genus in s["genus_labels"]:
                genus_sessions[genus] += 1
            for site in s["site_ids"]:
                if site:
                    taxon_sites[s["taxon"]].add(site)
                    for genus in s["genus_labels"]:
                        genus_sites[genus].add(site)
        support_frontier.append({
            "minimum_repeat_coordinate_supported_individuals": minimum_individuals,
            "n_eligible_species_session_records": len(eligible_sessions),
            "n_taxa": len(taxa_set),
            "n_resolved_genera": len(genus_set),
            "n_plots": len(plots_set),
            "n_sites": len(sites_set),
            "n_taxa_with_at_least_3_sessions": sum(
                n >= 3 for n in taxon_sessions.values()
            ),
            "n_taxa_with_at_least_2_sites": sum(
                len(v) >= 2 for v in taxon_sites.values()
            ),
            "n_taxa_with_at_least_3_sessions_and_2_sites": sum(
                taxon_sessions[t] >= 3 and len(taxon_sites[t]) >= 2
                for t in taxa_set
            ),
            "n_genera_with_at_least_3_sessions_and_2_sites": sum(
                genus_sessions[g] >= 3 and len(genus_sites[g]) >= 2
                for g in genus_set
            ),
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
                "identification_qualifier": t_ident_qual,
                "taxon_rank": t_rank,
            },
        },
        "data_quality": {
            "duplicate_perplotnight_nightuid_rows": duplicate_nightuid,
            "conflicting_perplotnight_nightuid_rows": conflicting_nightuid,
            "pertrapnight_rows_without_plotnight_join": missing_night_join,
            "pertrapnight_rows_without_event_id_after_join": missing_event,
            "capture_rows_without_taxon": capture_missing_taxon,
            "tagged_rows_with_noncapture_status": tagged_noncapture_status_rows,
            "capture_rows_with_identification_qualifier": (
                capture_rows_with_identification_qualifier
            ),
            "event_tag_ids_with_multiple_taxon_ids": sum(
                len(v) > 1 for v in event_tag_taxa.values()
            ),
        },
        "support": {
            "n_species_session_records": len(sessions),
            "n_taxa_with_capture_sessions": len(species_summary),
            "sessions": sessions,
            "taxa": species_summary,
            "repeat_support_frontier": support_frontier,
        },
        "boundary": {
            "effect_values_opened": False,
            "spatial_distances_calculated": False,
            "habitat_effects_calculated": False,
            "density_effects_calculated": False,
            "allowed_interpretation": "structural estimability and support only",
        },
    }

    # Guard the scientific support payload against accidental effect leakage.
    # Boundary/provenance fields intentionally contain phrases such as
    # "spatial_distances_calculated": false, so scanning the entire receipt
    # would make the guard reject its own negative audit declaration.
    serialized = json.dumps(result["support"], sort_keys=True).lower()
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
