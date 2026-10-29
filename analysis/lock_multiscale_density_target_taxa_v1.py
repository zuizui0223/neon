#!/usr/bin/env python3
"""Freeze NEON taxonomy metadata for structurally eligible density taxa.

No biological response files are opened. The script intersects the already
frozen 44 structurally supported taxon concepts with the current public NEON
SMALL_MAMMAL taxonomy endpoint. Composite/species-group concepts are retained
as published concepts; no forced species resolution is performed.
"""
from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "results" / "multiscale_density_primary_taxon_roster_v1.json"
OUT = ROOT / "build" / "multiscale_density_target_taxon_lock_v1.json"
URL = (
    "https://data.neonscience.org/api/v0/taxonomy?"
    "taxonTypeCode=SMALL_MAMMAL&verbose=true&offset=0&limit=1000"
)
USER_AGENT = "neon-multiscale-density-taxonomy-lock/1.0"


def canonical_sha(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def download_json() -> dict:
    req = urllib.request.Request(URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as response:
        raw = response.read()
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise RuntimeError("unexpected NEON taxonomy response")
    return payload


def normalize(row: dict) -> dict:
    return {
        "taxon_id": str(row.get("taxonID", "")).strip(),
        "scientific_name": str(row.get("dwc:scientificName", "")).strip(),
        "taxon_rank": str(row.get("dwc:taxonRank", "")).strip(),
        "protocol_category": str(row.get("taxonProtocolCategory", "")).strip(),
        "accepted_taxon_id": str(
            row.get("acceptedTaxonID", row.get("dwc:acceptedNameUsageID", ""))
        ).strip(),
    }


def lock(roster: dict, taxonomy_payload: dict) -> dict:
    requested = list(roster["primary_taxon_concepts"])
    rows = [normalize(x) for x in taxonomy_payload.get("data", [])]
    by_id: dict[str, list[dict]] = {}
    for row in rows:
        if row["taxon_id"]:
            by_id.setdefault(row["taxon_id"], []).append(row)

    matched = []
    missing = []
    ambiguous = []
    for taxon_id in requested:
        hits = by_id.get(taxon_id, [])
        if not hits:
            missing.append(taxon_id)
            continue
        unique = {
            (
                h["scientific_name"],
                h["taxon_rank"],
                h["protocol_category"],
                h["accepted_taxon_id"],
            )
            for h in hits
        }
        if len(unique) != 1:
            ambiguous.append({
                "taxon_id": taxon_id,
                "rows": hits,
            })
            continue
        row = dict(hits[0])
        row["is_target"] = row["protocol_category"].lower() == "target"
        matched.append(row)

    target = sorted(
        [x for x in matched if x["is_target"]],
        key=lambda x: x["taxon_id"],
    )
    non_target = sorted(
        [x for x in matched if not x["is_target"]],
        key=lambda x: x["taxon_id"],
    )
    ranks: dict[str, int] = {}
    for x in target:
        key = x["taxon_rank"] or "<blank>"
        ranks[key] = ranks.get(key, 0) + 1

    result = {
        "schema": "neon.multiscale_density.target_taxon_lock.v1",
        "status": "FROZEN_PUBLIC_TAXONOMY_METADATA_ONLY",
        "source_roster": str(ROSTER.relative_to(ROOT)),
        "taxonomy_url": URL,
        "taxonomy_fingerprint": canonical_sha(taxonomy_payload),
        "requested_taxon_count": len(requested),
        "matched_taxon_count": len(matched),
        "target_taxon_count": len(target),
        "non_target_taxon_count": len(non_target),
        "missing_taxon_count": len(missing),
        "ambiguous_taxon_count": len(ambiguous),
        "target_taxon_concepts": target,
        "non_target_taxon_concepts": non_target,
        "missing_taxon_ids": sorted(missing),
        "ambiguous_taxon_ids": ambiguous,
        "target_rank_counts": dict(sorted(ranks.items())),
        "primary_rule": (
            "retain structurally supported published NEON taxon concepts when "
            "taxonProtocolCategory == target; do not force composite concepts "
            "to species rank"
        ),
        "effect_boundary": {
            "biological_response_files_opened": False,
            "spatial_distances_calculated": False,
            "W_opened": False,
            "B_opened": False,
            "abundance_response_opened": False,
        },
    }
    result["fingerprint"] = canonical_sha(result)
    return result


def main() -> int:
    roster = json.loads(ROSTER.read_text(encoding="utf-8"))
    taxonomy = download_json()
    result = lock(roster, taxonomy)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["missing_taxon_count"] or result["ambiguous_taxon_count"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
