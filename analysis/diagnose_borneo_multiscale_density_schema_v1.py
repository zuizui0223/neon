#!/usr/bin/env python3
"""Effect-blind schema diagnostic for the Chapman Borneo small-mammal dataset.

The diagnostic uses the public Dryad REST API. It downloads only the two
capture/trap CSVs and their READMEs, then reports schema and structural
identifier support. It does NOT calculate spatial distances, W, B, abundance
slopes, or ecological effect directions.
"""
from __future__ import annotations

import csv
import hashlib
import re
import http.cookiejar
import io
import json
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "borneo_multiscale_density_schema_v1.json"

DOI = "10.5061/dryad.4th3p35"
API = "https://datadryad.org/api/v2"
USER_AGENT = "neon-borneo-multiscale-density-schema/1.0"
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/141.0 Safari/537.36"
)
LANDING = "https://datadryad.org/dataset/doi:10.5061/dryad.4th3p35"
# Public landing-page file_stream IDs, verified from the published Dryad page.
LEGACY_FILE_STREAM_IDS = {
    "Chapman_capturehistories.csv": 34176,
    "README_for_Chapman_capturehistories.txt": 34177,
    "Chapman_traplocations.csv": 34178,
    "README_for_Chapman_traplocations.txt": 34179,
}
WANTED = {
    "Chapman_capturehistories.csv",
    "Chapman_traplocations.csv",
    "README_for_Chapman_capturehistories.txt",
    "README_for_Chapman_traplocations.txt",
}


def _get_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "X-API-Version": "2.1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        raw = response.read()
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"unexpected Dryad response from {url}")
    return payload


def _download(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=180) as response:
        return response.read()


def _href(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("href", ""))
    return str(value or "")


def _abs(href: str) -> str:
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if not href.startswith("/"):
        href = "/" + href
    return "https://datadryad.org" + href


def _latest_version(dataset: dict) -> dict:
    href = _href(dataset.get("_links", {}).get("stash:version"))
    if href:
        return _get_json(_abs(href))

    encoded = urllib.parse.quote(f"doi:{DOI}", safe="")
    versions = _get_json(f"{API}/datasets/{encoded}/versions?per_page=100")
    rows = versions.get("_embedded", {}).get("stash:versions", [])
    if not rows:
        raise RuntimeError("Dryad dataset has no published versions")
    rows = sorted(
        rows,
        key=lambda x: (
            int(x.get("versionNumber", 0)),
            str(x.get("publicationDate", "")),
        ),
    )
    return rows[-1]


def _file_rows(version: dict) -> list[dict]:
    href = _href(version.get("_links", {}).get("stash:files"))
    if not href:
        version_id = version.get("id")
        if version_id is None:
            raise RuntimeError("cannot resolve Dryad version file list")
        href = f"/api/v2/versions/{version_id}/files?per_page=100"
    joiner = "&" if "?" in href else "?"
    payload = _get_json(_abs(href) + f"{joiner}per_page=100")
    rows = payload.get("_embedded", {}).get("stash:files", [])
    if not isinstance(rows, list):
        raise RuntimeError("unexpected Dryad files payload")
    return rows


def _download_public_file_stream(name: str) -> bytes:
    file_id = LEGACY_FILE_STREAM_IDS.get(name)
    if file_id is None:
        raise RuntimeError(f"no public file_stream fallback for {name}")

    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(jar)
    )
    landing_req = urllib.request.Request(
        LANDING,
        headers={
            "User-Agent": BROWSER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with opener.open(landing_req, timeout=120) as response:
        response.read(4096)

    errors = []
    for url in (
        f"https://datadryad.org/downloads/file_stream/{file_id}",
        f"https://datadryad.org/stash/downloads/file_stream/{file_id}",
    ):
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": BROWSER_USER_AGENT,
                "Accept": "*/*",
                "Referer": LANDING,
            },
        )
        try:
            with opener.open(req, timeout=180) as response:
                raw = response.read()
            if raw:
                return raw
        except urllib.error.HTTPError as exc:
            errors.append(f"{url} -> HTTP {exc.code}")
    raise RuntimeError(
        f"public file_stream fallback failed for {name}: {errors}"
    )


class SourcePayloadError(RuntimeError):
    """Published file bytes could not be independently validated."""


def _reject_html(raw: bytes, name: str) -> None:
    head = raw[:2048].lstrip().lower()
    if (
        b"<!doctype html" in head
        or b"<html" in head
        or b"<head>" in head
        or b"<title>validating" in head
        or b"within.website" in head
        or b"cloudflare" in head
    ):
        raise SourcePayloadError(
            f"{name}: anti-bot HTML/verification page received instead of scientific data"
        )


def _validate_publication_file(name: str, raw: bytes, meta: dict) -> None:
    """Reject HTML and validate published byte length and optional digest.

    Never infer ecological structural eligibility from an HTML error document.
    """
    _reject_html(raw, name)
    size = meta.get("size")
    if size is not None:
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            raise SourcePayloadError(f"{name}: invalid declared file size {size!r}")
        if len(raw) != size:
            raise SourcePayloadError(
                f"{name}: byte length mismatch {len(raw)} vs published {size}"
            )
    digest = str(meta.get("digest") or "").strip()
    dtype = str(meta.get("digestType") or "").strip().lower().replace("-", "")
    if digest and dtype in ("md5", "sha256"):
        observed = hashlib.new(dtype, raw).hexdigest()
        if observed.lower() != digest.lower():
            raise SourcePayloadError(f"{name}: published {dtype} checksum mismatch")
    if name.lower().endswith(".csv"):
        text = raw.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        fields = reader.fieldnames or []
        if len(fields) < 3 or any(
            not field or "<" in field or ">" in field or "=" in field
            for field in fields
        ):
            raise SourcePayloadError(f"{name}: invalid data CSV header")
        sample = list(__import__("itertools").islice(reader, 100))
        if len(sample) < 3 or any(None in row for row in sample):
            raise SourcePayloadError(
                f"{name}: insufficient structured CSV rows or ragged records"
            )
    elif not raw.strip():
        raise SourcePayloadError(f"{name}: empty README")


def _download_file(row: dict) -> tuple[bytes, str]:
    name = str(row.get("path", ""))
    href = _href(row.get("_links", {}).get("stash:download"))
    errors = []
    if href:
        try:
            raw = _download(_abs(href))
            _validate_publication_file(name, raw, row)
            return raw, "dryad_rest_api"
        except (urllib.error.HTTPError, SourcePayloadError) as exc:
            errors.append("rest_api: " + str(exc)[:180])
    try:
        raw = _download_public_file_stream(name)
        _validate_publication_file(name, raw, row)
        return raw, "public_landing_file_stream"
    except (urllib.error.HTTPError, SourcePayloadError, RuntimeError) as exc:
        errors.append("file_stream: " + str(exc)[:180])
    raise SourcePayloadError(
        f"{name}: no independently valid published file bytes; "
        + "; ".join(errors)
    )


def _csv_diagnostic(raw: bytes) -> dict:
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    fields = list(reader.fieldnames or [])
    rows = list(reader)
    nonblank = {}
    unique_counts = {}
    for field in fields:
        vals = [str(row.get(field, "")).strip() for row in rows]
        vals = [x for x in vals if x]
        nonblank[field] = len(vals)
        # Structural cardinalities only; do not emit biological response values.
        unique_counts[field] = len(set(vals))
    return {
        "columns": fields,
        "row_count": len(rows),
        "nonblank_counts": nonblank,
        "unique_value_counts": unique_counts,
    }


def run() -> dict:
    encoded = urllib.parse.quote(f"doi:{DOI}", safe="")
    dataset = _get_json(f"{API}/datasets/{encoded}")
    version = _latest_version(dataset)
    files = _file_rows(version)

    available = {
        str(row.get("path", "")): row
        for row in files
    }
    missing = sorted(WANTED - set(available))
    if missing:
        raise RuntimeError(f"missing expected Dryad files: {missing}")

    downloaded = {}
    for name in sorted(WANTED):
        row = available[name]
        raw, download_route = _download_file(row)
        if name.lower().endswith(".csv"):
            downloaded[name] = {
                "download_route": download_route,
                "size_bytes_downloaded": len(raw),
                "declared_size": row.get("size"),
                "digest": row.get("digest"),
                "digest_type": row.get("digestType"),
                "csv": _csv_diagnostic(raw),
            }
        else:
            text = raw.decode("utf-8-sig", errors="replace")
            downloaded[name] = {
                "download_route": download_route,
                "size_bytes_downloaded": len(raw),
                "declared_size": row.get("size"),
                "text": text,
            }

    return {
        "schema": "neon.borneo_multiscale_density.schema_diagnostic.v1",
        "status": "EFFECT_BLIND_SCHEMA_ONLY",
        "dataset": {
            "doi": DOI,
            "title": dataset.get("title"),
            "version_number": version.get("versionNumber"),
            "publication_date": version.get("publicationDate"),
            "license": dataset.get("license"),
            "storage_size": dataset.get("storageSize"),
        },
        "available_file_names": sorted(available),
        "downloaded": downloaded,
        "boundary": {
            "spatial_distances_calculated": False,
            "W_opened": False,
            "B_opened": False,
            "abundance_slopes_opened": False,
            "species_effect_directions_opened": False,
            "purpose": (
                "identify exact Borneo capture/trap schema and decide whether "
                "the NEON W/B estimand is structurally auditable before any "
                "external ecological effect is calculated"
            ),
        },
    }


def main() -> int:
    try:
        result = run()
    except SourcePayloadError as exc:
        # A successful workflow must never mean a challenge page was parsed
        # as biological tabular data. Persist machine-readable STOP evidence.
        result = {
            "schema": "neon.borneo_multiscale_density.schema_diagnostic.v2",
            "status": "STOP_EXTERNAL_SOURCE_BYTES_UNVERIFIED",
            "doi": DOI,
            "error": str(exc),
            "precedent_run_retracted": 37444977522,
            "W_opened": False,
            "B_opened": False,
            "abundance_slopes_opened": False,
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 3
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary = {
        "status": result["status"],
        "dataset": result["dataset"],
        "csvs": {
            name: info["csv"]
            for name, info in result["downloaded"].items()
            if "csv" in info
        },
        "boundary": result["boundary"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
