#!/usr/bin/env python3
"""Evaluate the frozen multiscale-density structural gate from an audit receipt.

This script reads only the effect-blind structural receipt and the preregistered
gate contract. It never reads capture coordinates or calculates W, B, or any
abundance-response effect.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return obj


def evaluate(receipt: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    primary = contract["primary_support_definition"]
    gates = contract["go_requires_all"]
    m = int(primary["mechanical_minimum_repeat_supported_individuals"])

    sessions = receipt["support"]["sessions"]
    eligible = [
        s for s in sessions
        if bool(s.get("primary_complete_session"))
        and int(s.get("n_repeat_coordinate_supported_tagged_individuals", 0)) >= m
    ]

    taxa = {str(s["taxon"]) for s in eligible}
    sites = {
        str(site)
        for s in eligible
        for site in s.get("site_ids", [])
        if str(site)
    }
    genera = {
        str(g)
        for s in eligible
        for g in s.get("genus_labels", [])
        if str(g)
    }

    genus_sessions = Counter()
    genus_sites: dict[str, set[str]] = defaultdict(set)
    taxon_sessions = Counter()
    taxon_sites: dict[str, set[str]] = defaultdict(set)

    for s in eligible:
        taxon = str(s["taxon"])
        taxon_sessions[taxon] += 1
        for site in s.get("site_ids", []):
            if site:
                taxon_sites[taxon].add(str(site))
        for genus in s.get("genus_labels", []):
            if not genus:
                continue
            genus = str(genus)
            genus_sessions[genus] += 1
            for site in s.get("site_ids", []):
                if site:
                    genus_sites[genus].add(str(site))

    rg = gates["replicated_genera_rule"]
    replicated_genera = sorted(
        g for g in genera
        if genus_sessions[g] >= int(rg["per_genus_minimum_eligible_session_records"])
        and len(genus_sites[g]) >= int(rg["per_genus_minimum_sites"])
    )

    checks = {
        "eligible_session_records": {
            "observed": len(eligible),
            "required_minimum": int(gates["minimum_eligible_taxon_plot_event_records"]),
        },
        "taxon_concepts": {
            "observed": len(taxa),
            "required_minimum": int(gates["minimum_taxon_concepts"]),
        },
        "resolved_genera": {
            "observed": len(genera),
            "required_minimum": int(gates["minimum_resolved_genera"]),
        },
        "sites": {
            "observed": len(sites),
            "required_minimum": int(gates["minimum_sites"]),
        },
        "replicated_genera": {
            "observed": len(replicated_genera),
            "required_minimum": int(rg["minimum_genera"]),
        },
    }
    for row in checks.values():
        row["pass"] = row["observed"] >= row["required_minimum"]

    completion_counts = Counter()
    protocol_basis_counts = Counter()
    all_pressure: list[float] = []
    taxon_pressure: list[float] = []
    conflict_rows = 0
    conflict_ids = 0
    for s in eligible:
        completion_counts[" | ".join(s.get("grid_completion_values", []))] += 1
        protocol_basis_counts[str(s.get("protocol_identification_basis", ""))] += 1
        if s.get("all_capture_trap_night_fraction_of_observed") is not None:
            all_pressure.append(float(s["all_capture_trap_night_fraction_of_observed"]))
        if s.get("taxon_capture_trap_night_fraction_of_observed") is not None:
            taxon_pressure.append(float(s["taxon_capture_trap_night_fraction_of_observed"]))
        conflict_rows += int(s.get("n_conflicted_tagged_capture_rows", 0))
        conflict_ids += int(s.get("n_conflicted_tag_ids", 0))

    def quantiles(values: list[float]) -> dict[str, float | None]:
        if not values:
            return {"n": 0, "median": None, "q90": None, "q95": None, "max": None}
        x = sorted(values)
        def q(p: float) -> float:
            idx = (len(x) - 1) * p
            lo = int(idx)
            hi = min(lo + 1, len(x) - 1)
            frac = idx - lo
            return x[lo] * (1 - frac) + x[hi] * frac
        return {
            "n": len(x),
            "median": q(0.5),
            "q90": q(0.9),
            "q95": q(0.95),
            "max": x[-1],
        }

    go = all(row["pass"] for row in checks.values())

    return {
        "schema": "neon.multiscale_density.structural_gate_evaluation.v1",
        "status": "GO" if go else "STOP",
        "mechanical_minimum_repeat_supported_individuals": m,
        "checks": checks,
        "replicated_genera": [
            {
                "genus": g,
                "eligible_sessions": genus_sessions[g],
                "sites": len(genus_sites[g]),
            }
            for g in replicated_genera
        ],
        "genus_support": [
            {
                "genus": g,
                "eligible_sessions": genus_sessions[g],
                "sites": len(genus_sites[g]),
            }
            for g in sorted(genera, key=lambda z: (-genus_sessions[z], z))
        ],
        "taxon_support": [
            {
                "taxon": t,
                "eligible_sessions": taxon_sessions[t],
                "sites": len(taxon_sites[t]),
            }
            for t in sorted(taxa, key=lambda z: (-taxon_sessions[z], z))
        ],
        "primary_session_qc": {
            "grid_completion_counts": dict(sorted(completion_counts.items())),
            "protocol_identification_basis_counts": dict(
                sorted(protocol_basis_counts.items())
            ),
            "conflicted_tagged_capture_rows_excluded_upstream": conflict_rows,
            "conflicted_tag_ids_excluded_upstream": conflict_ids,
            "all_small_mammal_capture_trap_night_fraction": quantiles(all_pressure),
            "focal_taxon_capture_trap_night_fraction": quantiles(taxon_pressure),
        },
        "effect_boundary": {
            "spatial_distances_calculated": False,
            "W_opened": False,
            "B_opened": False,
            "abundance_response_opened": False,
            "density_effects_opened": False,
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--receipt", required=True, type=Path)
    p.add_argument(
        "--contract",
        type=Path,
        default=Path("results/multiscale_density_structural_gate_contract_v2.json"),
    )
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    result = evaluate(_load(args.receipt), _load(args.contract))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
