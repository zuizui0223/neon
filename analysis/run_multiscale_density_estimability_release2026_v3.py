#!/usr/bin/env python3
"""Run the standardized-era effect-blind RELEASE-2026 structural audit (parallel I/O).

This runner intentionally opens only the information needed to decide whether a
future multiscale density analysis is structurally estimable. It never computes
spatial distances, W/B values, abundance slopes, habitat effects, or ecological
effect sizes.

Download strategy:
1. obtain the RELEASE-2026 site universe for DP1.10072.001;
2. query only the post-design-change era (2015-04 onward);
3. download mam_perplotnight files first and identify pathogen events with >=3 nights;
4. download mam_pertrapnight only for site-months containing those standardized events;
5. normalize the minimal structural fields and call the frozen support audit.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import tempfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from pathlib import Path
from typing import Any

from analysis.audit_multiscale_density_estimability_v1 import audit

PRODUCT = "DP1.10072.001"
RELEASE = "RELEASE-2026"
START = "2015-04"
END = "2026-09"
PRODUCT_URL = f"https://data.neonscience.org/api/v0/products/{PRODUCT}?release={RELEASE}"
QUERY_URL = "https://data.neonscience.org/api/v0/data/query"
TOKEN_ENV = "NEON_API_TOKEN"
USER_AGENT = "neon-multiscale-density-estimability/1.0"
MAX_DOWNLOAD_WORKERS = 6


def _request_json(url: str, token: str | None = None, body: dict | None = None) -> dict:
    headers = {"User-Agent": USER_AGENT}
    if token:
        headers["X-API-Token"] = token
    data = None
    method = "GET"
    if body is not None:
        data = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"
        method = "POST"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=180) as response:
        raw = response.read()
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict) or "data" not in payload:
        raise RuntimeError(f"unexpected NEON API response from {url}")
    return payload


def _site_codes(product_payload: dict) -> list[str]:
    data = product_payload["data"]
    raw = data.get("siteCodes", [])
    out: set[str] = set()
    for item in raw:
        if isinstance(item, str):
            code = item
        elif isinstance(item, dict):
            code = (
                item.get("siteCode")
                or item.get("site_code")
                or item.get("code")
                or ""
            )
        else:
            code = ""
        code = str(code).strip()
        if len(code) == 4:
            out.add(code)
    if not out:
        raise RuntimeError("no RELEASE-2026 site codes found for small-mammal product")
    return sorted(out)


def _inventory(query_payload: dict) -> list[dict[str, Any]]:
    data = query_payload["data"]
    releases = data.get("releases", [])
    blocks = [
        x for x in releases
        if isinstance(x, dict) and x.get("release") == RELEASE
    ]
    if len(blocks) != 1:
        raise RuntimeError("expected exactly one RELEASE-2026 response block")

    files: dict[tuple[str, str, str], dict[str, Any]] = {}
    for package in blocks[0].get("packages", []):
        if not isinstance(package, dict):
            continue
        site = str(package.get("siteCode", "")).strip()
        month = str(package.get("month", "")).strip()
        if str(package.get("packageType", "")) != "basic":
            continue
        for row in package.get("files", []):
            if not isinstance(row, dict):
                continue
            name = str(row.get("name", ""))
            if not name.lower().endswith(".csv"):
                continue
            if "mam_perplotnight" not in name and "mam_pertrapnight" not in name:
                continue
            md5 = str(row.get("md5", "")).lower()
            url = str(row.get("url", ""))
            size = row.get("size")
            if len(md5) != 32 or not url.startswith("https://"):
                raise RuntimeError(f"invalid inventory metadata for {name}")
            if isinstance(size, bool) or not isinstance(size, int) or size < 0:
                raise RuntimeError(f"invalid file size for {name}")
            key = (site, month, name)
            norm = {
                "site": site,
                "month": month,
                "name": name,
                "md5": md5,
                "url": url,
                "size": int(size),
            }
            if key in files and files[key] != norm:
                raise RuntimeError(f"conflicting duplicate inventory row {key}")
            files[key] = norm
    out = [files[k] for k in sorted(files)]
    if not out:
        raise RuntimeError("no structural mammal files found in RELEASE-2026 inventory")
    return out


def _download_one(row: dict[str, Any], token: str) -> bytes:
    req = urllib.request.Request(
        str(row["url"]),
        headers={"User-Agent": USER_AGENT, "X-API-Token": token},
    )
    with urllib.request.urlopen(req, timeout=240) as response:
        raw = response.read()
    if len(raw) != int(row["size"]):
        raise RuntimeError(f"size mismatch: {row['name']}")
    if hashlib.md5(raw).hexdigest() != row["md5"]:
        raise RuntimeError(f"md5 mismatch: {row['name']}")
    return raw


def _download_many(
    rows: list[dict[str, Any]],
    token: str,
    *,
    max_workers: int = 6,
) -> list[bytes]:
    """Download immutable NEON files concurrently while preserving row order."""
    if not rows:
        return []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(lambda row: _download_one(row, token), rows))


def _pick(fields: list[str], aliases: tuple[str, ...], required: bool = True) -> str | None:
    have = set(fields)
    for a in aliases:
        if a in have:
            return a
    if required:
        raise RuntimeError(f"missing required field; aliases={aliases}")
    return None


def _read_plot_rows(
    raw: bytes,
    site: str,
    month: str,
) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    fields = list(reader.fieldnames or [])
    night = _pick(fields, ("nightuid", "nightUID"))
    event = _pick(fields, ("eventID", "eventId", "event_id"))
    plot = _pick(fields, ("plotID", "plotId", "plot_id"))
    sampling = _pick(fields, ("mammalGridSamplingType", "mammalGridSampleType"), False)
    completion = _pick(fields, ("gridCompletion",), False)
    date = _pick(fields, ("collectDate", "date"), False)
    site_field = _pick(fields, ("siteID", "siteId"), False)

    out = []
    for row in reader:
        n = str(row.get(night, "")).strip()
        e = str(row.get(event, "")).strip()
        p = str(row.get(plot, "")).strip()
        if not n or not e or not p:
            continue
        out.append(
            {
                "nightuid": n,
                "eventID": e,
                "plotID": p,
                "siteID": str(row.get(site_field, "")).strip() if site_field else site,
                "mammalGridSamplingType": (
                    str(row.get(sampling, "")).strip() if sampling else ""
                ),
                "gridCompletion": (
                    str(row.get(completion, "")).strip() if completion else ""
                ),
                "collectDate": str(row.get(date, "")).strip() if date else "",
                "_site": site,
                "_month": month,
            }
        )
    return out


def _candidate_nights(plot_rows: list[dict[str, str]]) -> tuple[set[str], set[tuple[str, str]]]:
    """Return only standardized pathogen events with >=3 trapping nights.

    The 2015 design change retained three nights on pathogen grids while
    reducing diversity grids to one night. Legacy recapture bouts and other
    multi-night designs are intentionally excluded from the primary structural
    audit rather than mixed into the denominator.
    """
    nights_by_event: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    rows_by_event: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    protocol_by_event: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for row in plot_rows:
        key = (row["_site"], row["plotID"], row["eventID"])
        nights_by_event[key].add(row["nightuid"])
        rows_by_event[key].append(row)
        sampling = str(row.get("mammalGridSamplingType", "")).strip().lower()
        if sampling:
            protocol_by_event[key].add(sampling)

    eligible_events = {
        key
        for key, nights in nights_by_event.items()
        if len(nights) >= 3
        and any("pathogen" in label for label in protocol_by_event[key])
    }
    nights: set[str] = set()
    site_months: set[tuple[str, str]] = set()
    for key in eligible_events:
        for row in rows_by_event[key]:
            nights.add(row["nightuid"])
            site_months.add((row["_site"], row["_month"]))
    return nights, site_months


def _read_trap_rows(raw: bytes, candidate_nights: set[str]) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    fields = list(reader.fieldnames or [])
    night = _pick(fields, ("nightuid", "nightUID"))
    plot = _pick(fields, ("plotID", "plotId", "plot_id"))
    coord = _pick(fields, ("trapCoordinate", "trapCoord"))
    status = _pick(fields, ("trapStatus",), False)
    tag = _pick(fields, ("tagID", "tagId", "individualID", "individualId"), False)
    taxon = _pick(fields, ("taxonID", "taxonId"), False)
    sci = _pick(fields, ("scientificName", "scientific_name"), False)
    ident_qual = _pick(
        fields, ("identificationQualifier", "identification_qualifier"), False
    )
    taxon_rank = _pick(fields, ("taxonRank", "taxon_rank"), False)
    if taxon is None and sci is None:
        raise RuntimeError("pertrapnight file has neither taxonID nor scientificName")

    out = []
    for row in reader:
        n = str(row.get(night, "")).strip()
        if n not in candidate_nights:
            continue
        out.append(
            {
                "nightuid": n,
                "plotID": str(row.get(plot, "")).strip(),
                "trapCoordinate": str(row.get(coord, "")).strip(),
                "trapStatus": str(row.get(status, "")).strip() if status else "",
                "tagID": str(row.get(tag, "")).strip() if tag else "",
                "taxonID": str(row.get(taxon, "")).strip() if taxon else "",
                "scientificName": str(row.get(sci, "")).strip() if sci else "",
                "identificationQualifier": (
                    str(row.get(ident_qual, "")).strip() if ident_qual else ""
                ),
                "taxonRank": (
                    str(row.get(taxon_rank, "")).strip() if taxon_rank else ""
                ),
            }
        )
    return out


def _write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def run() -> dict:
    token = os.environ.get(TOKEN_ENV, "").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN is required for RELEASE-2026 data access")

    product_payload = _request_json(PRODUCT_URL, token=None)
    sites = _site_codes(product_payload)

    query_body = {
        "productCode": PRODUCT,
        "siteCodes": sites,
        "startDateMonth": START,
        "endDateMonth": END,
        "release": RELEASE,
        "package": "basic",
        "includeProvisional": False,
    }
    query_payload = _request_json(QUERY_URL, token=token, body=query_body)
    inventory = _inventory(query_payload)

    counters = {
        "inventory_requests": 1,
        "file_requests": 0,
        "bytes_opened": 0,
        "perplotnight_files": 0,
        "pertrapnight_files": 0,
    }

    plot_rows: list[dict[str, str]] = []
    plot_files = [r for r in inventory if "mam_perplotnight" in r["name"]]
    plot_raw = _download_many(
        plot_files, token, max_workers=MAX_DOWNLOAD_WORKERS
    )
    counters["perplotnight_files"] = len(plot_files)
    counters["file_requests"] += len(plot_files)
    counters["bytes_opened"] += sum(len(raw) for raw in plot_raw)
    for row, raw in zip(plot_files, plot_raw):
        plot_rows.extend(_read_plot_rows(raw, row["site"], row["month"]))

    candidate_nights, candidate_site_months = _candidate_nights(plot_rows)
    if not candidate_nights:
        raise RuntimeError("no multi-night sessions identified from perplotnight tables")

    trap_rows: list[dict[str, str]] = []
    trap_files = [
        r for r in inventory
        if "mam_pertrapnight" in r["name"]
        and (r["site"], r["month"]) in candidate_site_months
    ]
    trap_raw = _download_many(
        trap_files, token, max_workers=MAX_DOWNLOAD_WORKERS
    )
    counters["pertrapnight_files"] = len(trap_files)
    counters["file_requests"] += len(trap_files)
    counters["bytes_opened"] += sum(len(raw) for raw in trap_raw)
    for row, raw in zip(trap_files, trap_raw):
        trap_rows.extend(_read_trap_rows(raw, candidate_nights))

    # Remove internal provenance columns before passing the compact table to
    # the support audit. Keep only candidate multi-night rows.
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

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        plot_csv = root / "mam_perplotnight_structural.csv"
        trap_csv = root / "mam_pertrapnight_structural.csv"
        _write_csv(
            plot_csv,
            compact_plot,
            [
                "nightuid",
                "eventID",
                "plotID",
                "siteID",
                "mammalGridSamplingType",
                "gridCompletion",
                "collectDate",
            ],
        )
        _write_csv(
            trap_csv,
            trap_rows,
            [
                "nightuid",
                "plotID",
                "trapCoordinate",
                "trapStatus",
                "tagID",
                "taxonID",
                "scientificName",
                "identificationQualifier",
                "taxonRank",
            ],
        )
        result = audit(plot_csv, trap_csv)

    result["release_provenance"] = {
        "product": PRODUCT,
        "release": RELEASE,
        "query_start": START,
        "query_end": END,
        "site_count_in_release_product": len(sites),
        "site_codes": sites,
        "inventory_file_count": len(inventory),
        "standardized_pathogen_candidate_nightuid_count": len(candidate_nights),
        "standardized_pathogen_candidate_site_month_count": len(candidate_site_months),
        "primary_structural_era_start": START,
        "download_counters": counters,
        "download_max_workers": MAX_DOWNLOAD_WORKERS,
    }
    result["boundary"].update(
        {
            "ecological_effects_opened": False,
            "coordinate_distances_computed": False,
            "only_multi_night_structural_support_opened": True,
        }
    )
    return result


def main() -> int:
    result = run()
    out = Path("build/multiscale_density_estimability_release2026_v1.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "n_species_session_records": result["support"]["n_species_session_records"],
        "n_taxa_with_capture_sessions": result["support"]["n_taxa_with_capture_sessions"],
        "release_provenance": result["release_provenance"],
        "boundary": result["boundary"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
