from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import urllib.request
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

DATA_QUERY_URL = "https://data.neonscience.org/api/v0/data/query"
TAXONOMY_URL = (
    "https://data.neonscience.org/api/v0/taxonomy?"
    "taxonTypeCode=SMALL_MAMMAL&verbose=true&offset=0&limit=1000"
)
TOKEN_ENV = "NEON_API_TOKEN"
USER_AGENT = "neon-spatial-template-feasibility/1.0"

FIXED_SITES = (
    "SRER", "STEI", "STER", "TALL", "TEAK", "TOOL",
    "TREE", "UKFS", "WOOD", "WREF", "YELL",
)

QUERY_BODY = {
    "productCode": "DP1.10072.001",
    "release": "RELEASE-2026",
    "package": "basic",
    "startDateMonth": "2010-01",
    "endDateMonth": "2026-09",
    "includeProvisional": False,
    "siteCodes": list(FIXED_SITES),
}

MISSING = {"", "na", "nan", "none", "null"}
CANONICAL_COORD = re.compile(r"^[A-Z][0-9]+$")


def clean(x: object) -> str:
    s = str(x or "").strip()
    return "" if s.lower() in MISSING else s


def get_json(url: str, token: str | None = None) -> dict[str, Any]:
    headers = {"User-Agent": USER_AGENT}
    if token:
        headers["X-API-Token"] = token
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        out = json.loads(resp.read().decode("utf-8"))
    if not isinstance(out, dict):
        raise RuntimeError("unexpected JSON schema")
    return out


def post_query(token: str) -> dict[str, Any]:
    req = urllib.request.Request(
        DATA_QUERY_URL,
        data=json.dumps(QUERY_BODY, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        method="POST",
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            "X-API-Token": token,
        },
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        out = json.loads(resp.read().decode("utf-8"))
    if not isinstance(out, dict) or not isinstance(out.get("data"), dict):
        raise RuntimeError("unexpected NEON query schema")
    return out


def file_inventory(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = payload["data"]
    if data.get("productCode") != "DP1.10072.001":
        raise RuntimeError("product drift")
    rel = [x for x in data.get("releases", []) if isinstance(x, dict) and x.get("release") == "RELEASE-2026"]
    if len(rel) != 1:
        raise RuntimeError("expected one RELEASE-2026 block")

    wanted = ("mam_perplotnight", "mam_pertrapnight")
    seen: dict[tuple[str, str, str], dict[str, Any]] = {}
    for pkg in rel[0].get("packages", []):
        if not isinstance(pkg, dict):
            continue
        site = clean(pkg.get("siteCode"))
        if site not in FIXED_SITES:
            raise RuntimeError(f"undeclared site in query response: {site}")
        if clean(pkg.get("packageType")).lower() != "basic":
            continue
        month = clean(pkg.get("month"))
        for f in pkg.get("files", []):
            if not isinstance(f, dict):
                continue
            name = clean(f.get("name"))
            table = next((x for x in wanted if x in name and name.lower().endswith(".csv")), None)
            if table is None:
                continue
            md5 = clean(f.get("md5")).lower()
            url = clean(f.get("url"))
            size = f.get("size")
            if len(md5) != 32 or not url.startswith("https://") or not isinstance(size, int):
                raise RuntimeError(f"invalid file metadata: {name}")
            rec = {"site": site, "month": month, "table": table, "name": name, "md5": md5, "url": url, "size": size}
            key = (site, month, name)
            if key in seen and seen[key] != rec:
                raise RuntimeError(f"conflicting file metadata: {key}")
            seen[key] = rec
    out = [seen[k] for k in sorted(seen)]
    if not out:
        raise RuntimeError("no NEON mammal files found")
    return out


def download_file(rec: dict[str, Any], token: str) -> bytes:
    req = urllib.request.Request(rec["url"], headers={"User-Agent": USER_AGENT, "X-API-Token": token})
    with urllib.request.urlopen(req, timeout=180) as resp:
        raw = resp.read()
    if len(raw) != rec["size"]:
        raise RuntimeError(f"size mismatch {rec['name']}")
    if hashlib.md5(raw).hexdigest() != rec["md5"]:
        raise RuntimeError(f"md5 mismatch {rec['name']}")
    return raw


def target_taxa(token: str) -> dict[str, str]:
    p = get_json(TAXONOMY_URL, token)
    out: dict[str, str] = {}
    for row in p.get("data", []):
        if not isinstance(row, dict):
            continue
        if clean(row.get("dwc:taxonRank")).lower() != "species":
            continue
        if clean(row.get("taxonProtocolCategory")).lower() != "target":
            continue
        tid = clean(row.get("taxonID"))
        name = clean(row.get("dwc:scientificName"))
        if tid and name:
            out[tid] = name
    if not out:
        raise RuntimeError("no target small-mammal taxa")
    return out


def parse_plotnight(raw: bytes, site: str, mapping: dict[str, dict[str, str]], counters: Counter) -> None:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    fields = set(reader.fieldnames or [])
    required = {"nightuid", "plotID", "collectDate", "eventID"}
    if not required.issubset(fields):
        raise RuntimeError(f"{site}: mam_perplotnight missing {sorted(required-fields)}")
    sample_field = "mammalGridSamplingType" if "mammalGridSamplingType" in fields else (
        "mammalGridSampleType" if "mammalGridSampleType" in fields else None
    )
    if sample_field is None:
        raise RuntimeError(f"{site}: mammal grid sampling type field absent")

    for row in reader:
        counters["perplotnight_rows"] += 1
        night = clean(row.get("nightuid"))
        plot = clean(row.get("plotID"))
        event = clean(row.get("eventID"))
        collect = clean(row.get("collectDate"))
        sampling = clean(row.get(sample_field)).lower()
        if not night or not plot or not event or not collect:
            counters["perplotnight_missing_key"] += 1
            continue
        value = {"site": site, "plotID": plot, "eventID": event, "collectDate": collect, "samplingType": sampling}
        if night in mapping and mapping[night] != value:
            raise RuntimeError(f"{site}: conflicting nightuid metadata {night}")
        mapping[night] = value


def parse_trapnight(
    raw: bytes,
    site: str,
    targets: dict[str, str],
    captures: list[dict[str, str]],
    counters: Counter,
) -> None:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    fields = set(reader.fieldnames or [])
    required = {"nightuid", "plotID", "collectDate", "trapCoordinate", "trapStatus", "taxonID", "tagID"}
    if not required.issubset(fields):
        raise RuntimeError(f"{site}: mam_pertrapnight missing {sorted(required-fields)}")
    seen = set()
    for row in reader:
        counters["pertrapnight_rows"] += 1
        status = clean(row.get("trapStatus")).lower()
        if "capture" not in status or "no capture" in status:
            continue
        counters["capture_rows"] += 1
        taxon = clean(row.get("taxonID"))
        if taxon not in targets:
            counters["non_target_capture_rows"] += 1
            continue
        counters["target_capture_rows"] += 1
        coord = clean(row.get("trapCoordinate")).upper()
        if not CANONICAL_COORD.fullmatch(coord) or "X" in coord:
            counters["noncanonical_coordinate_rows"] += 1
            continue
        tag = clean(row.get("tagID"))
        if not tag:
            counters["untagged_target_capture_rows"] += 1
            continue
        night = clean(row.get("nightuid"))
        plot = clean(row.get("plotID"))
        collect = clean(row.get("collectDate"))
        if not night or not plot or not collect:
            counters["tagged_target_missing_key_rows"] += 1
            continue
        key = (site, plot, collect, coord, tag, taxon)
        if key in seen:
            counters["duplicate_tagged_capture_rows"] += 1
            continue
        seen.add(key)
        captures.append({
            "site": site, "nightuid": night, "plotID": plot, "collectDate": collect,
            "trapCoordinate": coord, "taxonID": taxon, "tagID": tag,
        })
        counters["tagged_target_capture_rows"] += 1


def parse_date(x: str) -> date:
    # NEON collectDate is ISO date in current releases; tolerate timestamp suffix.
    return date.fromisoformat(x[:10])


def build_support(
    mapping: dict[str, dict[str, str]],
    captures: list[dict[str, str]],
    targets: dict[str, str],
) -> dict[str, Any]:
    join_missing = 0
    joined: list[dict[str, str]] = []
    for r in captures:
        meta = mapping.get(r["nightuid"])
        if meta is None:
            join_missing += 1
            continue
        if meta["plotID"] != r["plotID"]:
            raise RuntimeError(f"plot mismatch for {r['nightuid']}")
        if "pathogen" not in meta["samplingType"]:
            continue
        x = dict(r)
        x["eventID"] = meta["eventID"]
        x["samplingType"] = meta["samplingType"]
        joined.append(x)

    # Conservative identity consistency: a site x tag with multiple target taxa is excluded.
    taxa_by_tag: dict[tuple[str, str], set[str]] = defaultdict(set)
    for r in joined:
        taxa_by_tag[(r["site"], r["tagID"])].add(r["taxonID"])
    ambiguous = {k for k, v in taxa_by_tag.items() if len(v) != 1}
    joined = [r for r in joined if (r["site"], r["tagID"]) not in ambiguous]

    by_event: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for r in joined:
        by_event[(r["site"], r["plotID"], r["eventID"])].append(r)

    usable_events: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    all_events = []
    for (site, plot, event), rows in sorted(by_event.items()):
        nights = sorted({r["collectDate"] for r in rows})
        if len(nights) < 2:
            continue
        first_date = min(parse_date(x) for x in nights)
        ids = {(r["tagID"], r["taxonID"]) for r in rows}
        rec = {
            "site": site,
            "plotID": plot,
            "eventID": event,
            "first_date": first_date,
            "capture_nights": len(nights),
            "tagged_individuals": len({x[0] for x in ids}),
            "target_species": len({x[1] for x in ids}),
            "rows": rows,
        }
        usable_events[(site, plot)].append(rec)
        all_events.append(rec)

    units = []
    candidate_pairs = 0
    total_shared = 0
    for (site, plot), events in sorted(usable_events.items()):
        events = sorted(events, key=lambda x: (x["first_date"], x["eventID"]))
        for a, b in zip(events, events[1:]):
            candidate_pairs += 1
            aid = {r["tagID"] for r in a["rows"]}
            bid = {r["tagID"] for r in b["rows"]}
            shared = aid & bid
            total_shared += len(shared)

            a_ex = [r for r in a["rows"] if r["tagID"] not in shared]
            b_ex = [r for r in b["rows"] if r["tagID"] not in shared]

            a_sp: dict[str, set[str]] = defaultdict(set)
            b_sp: dict[str, set[str]] = defaultdict(set)
            for r in a_ex:
                a_sp[r["taxonID"]].add(r["tagID"])
            for r in b_ex:
                b_sp[r["taxonID"]].add(r["tagID"])

            eligible = sorted(
                sp for sp in set(a_sp) & set(b_sp)
                if len(a_sp[sp]) >= 2 and len(b_sp[sp]) >= 2
            )
            unit = {
                "id": f"{site}|{plot}|{a['eventID']}->{b['eventID']}",
                "site": site,
                "plotID": plot,
                "event_a": a["eventID"],
                "event_b": b["eventID"],
                "date_a": a["first_date"].isoformat(),
                "date_b": b["first_date"].isoformat(),
                "capture_nights_a": a["capture_nights"],
                "capture_nights_b": b["capture_nights"],
                "shared_tagged_individuals_removed": len(shared),
                "eligible_species": eligible,
                "eligible_species_names": [targets[x] for x in eligible],
                "exclusive_individuals_a": {sp: len(a_sp[sp]) for sp in eligible},
                "exclusive_individuals_b": {sp: len(b_sp[sp]) for sp in eligible},
                "eligible": len(eligible) >= 3,
            }
            units.append(unit)

    eligible_units = [u for u in units if u["eligible"]]
    eligible_sites = sorted({u["site"] for u in eligible_units})
    eligible_plots = sorted({f"{u['site']}|{u['plotID']}" for u in eligible_units})
    pass_gate = (
        len(eligible_units) >= 12
        and len(eligible_sites) >= 6
        and len(eligible_plots) >= 8
    )

    site_summary = {}
    for site in FIXED_SITES:
        su = [u for u in eligible_units if u["site"] == site]
        site_summary[site] = {
            "usable_pathogen_plot_events": sum(e["site"] == site for e in all_events),
            "eligible_adjacent_bout_units": len(su),
            "eligible_physical_plots": len({u["plotID"] for u in su}),
        }

    return {
        "join_missing_tagged_capture_rows": join_missing,
        "ambiguous_site_tag_ids_excluded": len(ambiguous),
        "usable_pathogen_plot_events": len(all_events),
        "candidate_adjacent_bout_pairs": candidate_pairs,
        "shared_tagged_identities_removed_across_candidate_pairs": total_shared,
        "eligible_adjacent_bout_units": len(eligible_units),
        "eligible_sites": eligible_sites,
        "eligible_site_count": len(eligible_sites),
        "eligible_plots": eligible_plots,
        "eligible_plot_count": len(eligible_plots),
        "advance_gate": {
            "required_units": 12,
            "required_sites": 6,
            "required_plots": 8,
            "passed": pass_gate,
            "decision": (
                "authorize_exploratory_external_recurrence_test"
                if pass_gate else "stop_external_replication_insufficient_support"
            ),
        },
        "site_summary": site_summary,
        "eligible_units": eligible_units,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    token = os.environ.get(TOKEN_ENV, "").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN missing")

    targets = target_taxa(token)
    payload = post_query(token)
    files = file_inventory(payload)

    mapping: dict[str, dict[str, str]] = {}
    captures: list[dict[str, str]] = []
    counters: Counter = Counter()
    receipts = []

    # Parse plot-night metadata first so all capture rows can be joined deterministically.
    for rec in files:
        if rec["table"] != "mam_perplotnight":
            continue
        raw = download_file(rec, token)
        parse_plotnight(raw, rec["site"], mapping, counters)
        receipts.append({k: rec[k] for k in ("site", "month", "table", "name", "size", "md5")})

    for rec in files:
        if rec["table"] != "mam_pertrapnight":
            continue
        raw = download_file(rec, token)
        parse_trapnight(raw, rec["site"], targets, captures, counters)
        receipts.append({k: rec[k] for k in ("site", "month", "table", "name", "size", "md5")})

    support = build_support(mapping, captures, targets)

    result = {
        "schema": "neon.external_spatial_template_feasibility.v1",
        "status": "support_only_no_spatial_recurrence_opened",
        "inferential_status": "RELEASE-2026 response-consumed; feasibility only",
        "frozen_design": "docs/NEON_SPATIAL_TEMPLATE_EXTERNAL_FEASIBILITY_V1.md",
        "data_source": {
            "product": "DP1.10072.001",
            "release": "RELEASE-2026",
            "fixed_sites": list(FIXED_SITES),
            "query": QUERY_BODY,
        },
        "taxonomy": {
            "target_species_count": len(targets),
        },
        "file_receipts": receipts,
        "row_counts": dict(counters),
        "support": support,
        "claim_boundary": {
            "species_trap_recurrence_opened": False,
            "trap_overlap_opened": False,
            "c_score_opened": False,
            "spatial_null_opened": False,
            "effect_direction_opened": False,
            "p_values_opened": False,
            "confirmatory": False,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "support": support["advance_gate"],
        "eligible_units": support["eligible_adjacent_bout_units"],
        "eligible_sites": support["eligible_site_count"],
        "eligible_plots": support["eligible_plot_count"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
