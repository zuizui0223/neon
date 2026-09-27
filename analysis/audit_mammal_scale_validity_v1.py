from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_PROTOCOL = ROOT / "validation" / "neon_metacommunity_connectivity_v1" / "protocol_v1.json"
ORIGINAL_LOCK = ROOT / "validation" / "neon_metacommunity_connectivity_v1" / "fresh_roster_lock_v1.json"
FRESH_PROTOCOL = ROOT / "validation" / "carrier_prevalence_mechanism_v1" / "protocol_v1.json"
FRESH_LOCK = ROOT / "validation" / "carrier_prevalence_mechanism_v1" / "fresh_roster_lock_v1.json"
OUT = ROOT / "results" / "generated" / "mammal_scale_geometry_audit_v1.json"


def _load_roster_module():
    import importlib.util
    path = ROOT / "analysis" / "capture_carrier_prevalence_fresh_roster_v1.py"
    spec = importlib.util.spec_from_file_location("roster_geometry", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def grid_id(node_id: str) -> str:
    if "." not in node_id:
        raise ValueError(f"node has no trap-coordinate segment: {node_id}")
    return node_id.rsplit(".", 1)[0]


def same_grid_pair_stats(
    node_ids: list[str],
    dist_km: np.ndarray,
    thresholds_km: list[float],
) -> dict[str, object]:
    if dist_km.shape != (len(node_ids), len(node_ids)):
        raise ValueError("distance matrix shape does not match node IDs")

    groups: dict[str, list[int]] = defaultdict(list)
    for i, node in enumerate(node_ids):
        groups[grid_id(node)].append(i)

    pair_distances: list[float] = []
    grid_maxima: list[float] = []
    grid_sizes: list[int] = []
    for indices in groups.values():
        grid_sizes.append(len(indices))
        if len(indices) < 2:
            grid_maxima.append(0.0)
            continue
        sub = dist_km[np.ix_(indices, indices)]
        vals = sub[np.triu_indices(len(indices), 1)]
        pair_distances.extend(float(x) for x in vals)
        grid_maxima.append(float(np.max(vals)))

    if not pair_distances:
        raise RuntimeError("no within-grid trap pairs")

    arr = np.asarray(pair_distances, dtype=float)
    max_dist = float(np.max(arr))
    threshold_rows = []
    for threshold in sorted(float(x) for x in thresholds_km):
        adjacent = int(np.sum(arr <= threshold + 1e-12))
        threshold_rows.append({
            "distance_threshold_km": threshold,
            "distance_threshold_m": threshold * 1000.0,
            "adjacent_same_grid_pair_count": adjacent,
            "adjacent_same_grid_pair_fraction": adjacent / len(arr),
            "threshold_at_least_within_grid_max": threshold + 1e-12 >= max_dist,
        })

    return {
        "grid_count": len(groups),
        "grid_size_min": min(grid_sizes),
        "grid_size_median": float(np.median(grid_sizes)),
        "grid_size_max": max(grid_sizes),
        "same_grid_pair_count": len(arr),
        "within_grid_pair_distance_km_median": float(np.median(arr)),
        "within_grid_pair_distance_km_p95": float(np.quantile(arr, 0.95)),
        "within_grid_max_distance_km": max_dist,
        "within_grid_max_distance_m": max_dist * 1000.0,
        "grid_max_distance_km_median": float(np.median(grid_maxima)),
        "thresholds": threshold_rows,
    }


def audit_site(
    *,
    site: str,
    programme: str,
    protocol: dict,
    locked: dict,
    roster_module,
    strict_world_fingerprint: bool,
) -> dict[str, object]:
    node_ids, rows, registry_fp = roster_module.registry(site)
    if len(node_ids) != int(locked["node_count"]):
        raise RuntimeError(
            f"{site}: node count drift {len(node_ids)} != {locked['node_count']}"
        )
    if registry_fp != locked["node_registry_fingerprint"]:
        raise RuntimeError(f"{site}: node registry fingerprint drift")

    dist = roster_module.haversine(rows)
    world = roster_module.worlds(site, dist, protocol)
    world_fp_match = (
        world["world_universe_fingerprint"] == locked["world_universe_fingerprint"]
    )
    if strict_world_fingerprint and not world_fp_match:
        raise RuntimeError(f"{site}: world universe fingerprint drift")
    if int(world["distinct_world_count"]) != int(locked["distinct_world_count"]):
        raise RuntimeError(f"{site}: distinct world count drift")

    thresholds = sorted({
        float(row["distance_threshold_km"])
        for row in world["canonical_worlds"]
    })
    stats = same_grid_pair_stats(node_ids, dist, thresholds)
    rows_by_threshold = stats["thresholds"]
    complete = sum(
        bool(row["threshold_at_least_within_grid_max"])
        for row in rows_by_threshold
    )
    min_row = rows_by_threshold[0]

    return {
        "site_code": site,
        "programme": programme,
        "node_count": len(node_ids),
        "canonical_world_count": len(thresholds),
        "canonical_thresholds_km": thresholds,
        "reconstructed_alias_groups": world["alias_groups"],
        "world_universe_fingerprint_matches_lock": world_fp_match,
        "world_fingerprint_verification": (
            "exact_current_schema_match"
            if strict_world_fingerprint
            else "legacy_lock_schema_differs; adjacency fingerprints require frozen-source-artifact comparison"
        ),
        "minimum_threshold_km": thresholds[0],
        "minimum_threshold_m": thresholds[0] * 1000.0,
        **stats,
        "worlds_with_all_same_grid_pairs_adjacent": complete,
        "all_canonical_worlds_make_same_grid_complete": complete == len(thresholds),
        "minimum_threshold_same_grid_pair_fraction": min_row[
            "adjacent_same_grid_pair_fraction"
        ],
        "minimum_threshold_over_max_within_grid_distance": (
            thresholds[0] / stats["within_grid_max_distance_km"]
            if stats["within_grid_max_distance_km"] > 0
            else math.inf
        ),
        "response_endpoint_requests": 0,
        "biological_response_bytes_opened": 0,
    }


def main() -> None:
    roster_module = _load_roster_module()
    original_protocol = json.loads(ORIGINAL_PROTOCOL.read_text(encoding="utf-8"))
    original_lock = json.loads(ORIGINAL_LOCK.read_text(encoding="utf-8"))
    fresh_protocol = json.loads(FRESH_PROTOCOL.read_text(encoding="utf-8"))
    fresh_lock = json.loads(FRESH_LOCK.read_text(encoding="utf-8"))

    audits: list[dict[str, object]] = []

    original_site_locks = original_lock["site_locks"]
    for site in original_lock["selected_site_codes"]:
        audits.append(
            audit_site(
                site=site,
                programme="original_16",
                protocol=original_protocol,
                locked=original_site_locks[site],
                roster_module=roster_module,
                strict_world_fingerprint=False,
            )
        )
        print(f"AUDIT_SITE {site} original_16", flush=True)

    fresh_locks = {
        row["site_code"]: row for row in fresh_lock["selected_sites"]
    }
    for site in fresh_lock["selected_site_codes"]:
        audits.append(
            audit_site(
                site=site,
                programme="fresh_11",
                protocol=fresh_protocol,
                locked=fresh_locks[site],
                roster_module=roster_module,
                strict_world_fingerprint=True,
            )
        )
        print(f"AUDIT_SITE {site} fresh_11", flush=True)

    all_world_rows = [
        {
            "site_code": site["site_code"],
            "programme": site["programme"],
            **row,
        }
        for site in audits
        for row in site["thresholds"]
    ]
    complete_worlds = [
        row for row in all_world_rows
        if row["threshold_at_least_within_grid_max"]
    ]
    min_complete_sites = [
        site for site in audits
        if site["minimum_threshold_same_grid_pair_fraction"] >= 1.0 - 1e-12
    ]
    min_near_complete_sites = [
        site for site in audits
        if site["minimum_threshold_same_grid_pair_fraction"] >= 0.95
    ]

    payload = {
        "schema": "neon.mammal_scale_geometry_audit.v1",
        "status": "metadata_only_posthoc_validity_audit",
        "scope": {
            "original_16_sites": 16,
            "fresh_11_sites": 11,
            "total_sites": 27,
            "biological_response_reopened": False,
            "input_geometry": "NEON location hierarchy and GraphQL trap coordinates only",
            "grid_id_rule": "remove final trap-coordinate segment from frozen node ID",
        },
        "site_audits": audits,
        "summary": {
            "site_count": len(audits),
            "canonical_world_count": len(all_world_rows),
            "worlds_with_all_same_grid_pairs_adjacent": len(complete_worlds),
            "fraction_worlds_with_all_same_grid_pairs_adjacent": (
                len(complete_worlds) / len(all_world_rows)
            ),
            "sites_where_minimum_threshold_makes_all_same_grid_pairs_adjacent": len(min_complete_sites),
            "sites_where_minimum_threshold_makes_at_least_95pct_same_grid_pairs_adjacent": len(min_near_complete_sites),
            "minimum_threshold_m_range": [
                min(site["minimum_threshold_m"] for site in audits),
                max(site["minimum_threshold_m"] for site in audits),
            ],
            "within_grid_max_distance_m_range": [
                min(site["within_grid_max_distance_m"] for site in audits),
                max(site["within_grid_max_distance_m"] for site in audits),
            ],
            "sites_not_complete_at_minimum_threshold": [
                {
                    "site_code": site["site_code"],
                    "programme": site["programme"],
                    "minimum_threshold_m": site["minimum_threshold_m"],
                    "within_grid_max_distance_m": site["within_grid_max_distance_m"],
                    "same_grid_pair_fraction": site["minimum_threshold_same_grid_pair_fraction"],
                }
                for site in audits
                if site["minimum_threshold_same_grid_pair_fraction"] < 1.0 - 1e-12
            ],
        },
        "interpretation_boundary": {
            "directly_tested": [
                "whether canonical adjacency thresholds collapse within-grid trap geometry",
                "the exact fraction of same-grid trap pairs admitted by every canonical threshold",
            ],
            "not_tested": [
                "home-range scale of individual mammals",
                "movement or dispersal",
                "habitat filtering",
                "capture detectability",
            ],
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("AUDIT_SUMMARY " + json.dumps(payload["summary"], sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
