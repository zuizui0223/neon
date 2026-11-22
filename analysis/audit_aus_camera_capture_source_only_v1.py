#!/usr/bin/env python3
"""Fail-closed, effect-blind original Dryad camera+Elliott-trap source audit.

NO original species-by-station capture, behaviour, visit/capture rates or model
effect sizes are computed. Use only pinned public 4 small CSVs, never images.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from hashlib import md5, sha256
from io import StringIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import csv
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/neon_aus_camera_capture_source_only_v1.json"
PROTOCOL = "docs/NEON_AUSTRALIA_CAMERA_CAPTURE_SOURCE_GATE_20261118.md"
DOI = "10.5061/dryad.18931zd8w"
ORIGINAL_LANDING = "https://datadryad.org/dataset/doi:10.5061/dryad.18931zd8w"
BASE = "https://datadryad.org/api/v2/files"
ORIGINAL_FILE_ROLES = {
    "camera": ("20250706_camera_trapping_sm_full_v2.csv", 4537877, 800000),
    "traps": ("20250117_small_mammal_trapping.csv", 4537871, 80000),
    "visits": ("20250208_visit_interaction_pa_v2.csv", 4537875, 80000),
    "effort": ("20250121_camera_sampling_effort_persite.csv", 4537873, 20000),
}
REQUIRED = {
    "camera": {"site_type", "site", "station", "species", "season",
               "DateTimeOriginal", "independent_capture", "visit_ID",
               "trap_state", "individual_ID"},
    "traps": {"site_type", "site", "individual", "date", "season",
              "trap_ID", "genus", "species", "camera_capture"},
    "visits": {"site_type", "species", "season", "visit_ID",
               "interaction_pa", "capture_pa"},
    "effort": {"site", "sampling_effort"},
}
STAGE = "ORIGINAL_FILE_METADATA"

def require(condition: bool, name: str) -> None:
    if not condition:
        raise ValueError("AU_SOURCE_STOP_" + name)

def get_bytes(url: str, max_bytes: int) -> bytes:
    """Read bounded public source only; HTTP errors never become CSV content."""
    req = Request(url, headers={
        "User-Agent": "NEON-SourceIntegrity/1.0 (public Dryad metadata audit)",
        "Accept": "application/json, text/csv, application/octet-stream;q=0.5",
        **({"Authorization": "Bearer " + os.environ["DRYAD_TOKEN"].strip()}
           if os.environ.get("DRYAD_TOKEN", "").strip() else {}),
    })
    try:
        with urlopen(req, timeout=35) as handle:
            status = getattr(handle, "status", 200)
            require(status == 200, "PUBLIC_SOURCE_HTTP_STATUS")
            data = handle.read(max_bytes + 1)
    except HTTPError as err:
        # Provider may require a valid user-held Dryad API bearer credential
        # for downloads; do not attempt browser challenge or credential bypass.
        if err.code in (401, 403):
            raise ValueError("AU_SOURCE_STOP_DRYAD_401_403_AUTH_OR_ACCESS_DENIED") from err
        if err.code == 429:
            raise ValueError("AU_SOURCE_STOP_DRYAD_429_RATE_LIMIT") from err
        raise ValueError("AU_SOURCE_STOP_DRYAD_HTTP_" + str(err.code)) from err
    except (URLError, TimeoutError, ConnectionError) as err:
        raise ValueError("AU_SOURCE_STOP_DRYAD_NETWORK_UNAVAILABLE") from err
    require(0 < len(data) <= max_bytes, "SOURCE_EMPTY_OR_TOO_LARGE")
    return data

def source_meta_and_csv(role: str):
    """Never infer another download ID, filename or source version."""
    name, ident, cap = ORIGINAL_FILE_ROLES[role]
    metadata_raw = get_bytes(f"{BASE}/{ident}", 60000)
    require(metadata_raw.lstrip().startswith(b"{"), "METADATA_JSON_NOT_HTML")
    try:
        metadata = json.loads(metadata_raw)
    except (ValueError, TypeError):
        raise ValueError("AU_SOURCE_STOP_BAD_METADATA_JSON") from None
    require(isinstance(metadata, dict), "METADATA_NOT_OBJECT")
    actual_name = metadata.get("path") or metadata.get("filename") or metadata.get("name")
    require(isinstance(actual_name, str) and actual_name.split("/")[-1] == name,
            "PINNED_FILE_ID_FILENAME_MISMATCH")
    size = metadata.get("size")
    require(isinstance(size, int) and 0 < size <= cap, "PINNED_FILE_SIZE_NOT_VALID")
    original = get_bytes(f"{BASE}/{ident}/download", cap)
    require(len(original) == size, "ORIGINAL_BYTE_COUNT_NOT_PROVIDER_SIZE")
    prefix = original[:2048].lstrip().lower()
    require(not any(prefix.startswith(v) for v in
                    (b"<!doctype", b"<html", b"<?xml", b"{", b"pk\x03\x04")),
            "ORIGINAL_IS_HTML_JSON_XML_OR_ZIP")
    require(b"\x00" not in original[:4096], "SOURCE_NUL_BINARY")
    digest_value = metadata.get("digest")
    dtype = str(metadata.get("digestType") or "").lower().replace("-", "")
    digest_verified = False
    if digest_value:
        require(isinstance(digest_value, str), "DIGEST_UNRECOGNIZED")
        value = digest_value.lower().strip().replace("md5:", "").replace("sha256:", "")
        if dtype == "md5":
            require(md5(original).hexdigest() == value, "PROVIDER_MD5_MISMATCH")
        elif dtype == "sha256":
            require(sha256(original).hexdigest() == value, "PROVIDER_SHA256_MISMATCH")
        else:
            raise ValueError("AU_SOURCE_STOP_UNKNOWN_DIGEST_TYPE")
        digest_verified = True
    links = metadata.get("_links") if isinstance(metadata.get("_links"), dict) else {}
    version_token = metadata.get("versionId") or metadata.get("version_id")
    for entry in links.values():
        href = entry.get("href") if isinstance(entry, dict) else None
        if not version_token and isinstance(href, str):
            m = re.search(r"/versions/(\d+)(?:/|$)", href)
            if m:
                version_token = m.group(1)
    rec = {
        "dryad_file_id": ident, "original_filename": name,
        "provider_size_and_actual_bytes": size,
        "original_bytes_sha256": sha256(original).hexdigest(),
        "provider_digest_verified_when_supplied": digest_verified,
        "source_version_id_from_provider_when_available": str(version_token or ""),
    }
    return original, rec

def parse_csv(original: bytes, role: str) -> list[dict[str, str]]:
    try:
        s = original.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("AU_SOURCE_STOP_ORIGINAL_INVALID_UTF8") from None
    reader = csv.DictReader(StringIO(s, newline=""))
    fields = reader.fieldnames or []
    require(len(fields) == len(set(fields)) and REQUIRED[role].issubset(set(fields)),
            "ORIGINAL_" + role.upper() + "_HEADER_MISMATCH")
    result = []
    for row in reader:
        require(None not in row and all(v is not None for v in row.values()),
                "ORIGINAL_" + role.upper() + "_RAGGED_ROW")
        result.append({key: (val or "").strip() for key, val in row.items()})
    require(len(result) > 0, "ORIGINAL_" + role.upper() + "_EMPTY_ROWS")
    return result

def parsed_date(value: str) -> str | None:
    """Pure source parser; no inferred overnight calendar shifts."""
    if not value:
        return None
    source = value.strip()
    formats = (
        ("%Y-%m-%d", source[:10]),
        ("%Y/%m/%d", source[:10]),
        ("%Y:%m:%d", source[:10]),
        ("%d/%m/%Y", source[:10]),
        ("%d-%m-%Y", source[:10]),
        ("%d/%m/%y", source[:8]),
        ("%d-%b-%Y", source[:11]),
    )
    for fmt, token in formats:
        try:
            return datetime.strptime(token, fmt).date().isoformat()
        except ValueError:
            continue
    return None

def canonical_site_station(site: str, camera_station: str, live_trap: str) -> bool:
    """No fuzzy, shortest-distance or effects-led matching."""
    if not site or not camera_station or not live_trap:
        return False
    return (camera_station == live_trap
            or camera_station == site + "-" + live_trap
            or camera_station == site + "_" + live_trap)

def support_only(rows: dict[str, list[dict[str, str]]]) -> dict:
    """Aggregate eligibility, never read capture or behavioural outcome values."""
    cam, trap, visit, effort = (
        rows["camera"], rows["traps"], rows["visits"], rows["effort"]
    )
    sites_cam = {r["site"] for r in cam if r["site"]}
    sites_trap = {r["site"] for r in trap if r["site"]}
    types = {r["site_type"].strip().lower() for r in cam if r["site_type"]}
    seasons = {r["season"].strip().lower() for r in cam if r["season"]}
    cam_stations = {(r["site"], r["station"]) for r in cam
                    if r["site"] and r["station"]}
    cap_stations = {(r["site"], r["trap_ID"]) for r in trap
                    if r["site"] and r["trap_ID"]}
    source_matched_station_keys = {
        (site, station) for site, station in cam_stations
        if any(s2 == site and canonical_site_station(site, station, trap_id)
               for s2, trap_id in cap_stations)
    }
    # Use exact visit ID identity only; no sign of interaction/capture is opened.
    camera_visits = {r["visit_ID"] for r in cam if r["visit_ID"]}
    visit_table_ids = {r["visit_ID"] for r in visit if r["visit_ID"]}
    site_season_cam = {(r["site"], r["season"].lower()) for r in cam
                       if r["site"] and r["season"]}
    site_season_trap = {(r["site"], r["season"].lower()) for r in trap
                        if r["site"] and r["season"]}
    dates_camera = {parsed_date(r.get("DateTimeOriginal", "")) for r in cam}
    dates_trap = {parsed_date(r.get("date", "")) for r in trap}
    sites_seasons_valid_cam = {
        (r["site"], r["season"].lower())
        for r in cam if r["site"] and r["season"]
        and parsed_date(r.get("DateTimeOriginal", ""))
    }
    sites_seasons_valid_trap = {
        (r["site"], r["season"].lower())
        for r in trap if r["site"] and r["season"]
        and parsed_date(r.get("date", ""))
    }
    good_effort = 0
    for r in effort:
        try:
            n = float(r["sampling_effort"])
        except (ValueError, TypeError):
            continue
        if 0 < n < 1e7:
            good_effort += 1
    observed_cam_date = sum(parsed_date(r.get("DateTimeOriginal", "")) is not None
                            for r in cam)
    observed_trap_date = sum(parsed_date(r.get("date", "")) is not None
                             for r in trap)
    site_type_common = len(types) == 2 and any("forest" in x for x in types) and any(
        "urban" in x for x in types
    )
    checks = {
        "both_source_site_types_forest_and_urban": site_type_common,
        "at_least_eight_source_camera_sites": len(sites_cam) >= 8,
        "at_least_thirty_distinct_camera_stations": len(cam_stations) >= 30,
        "spring_and_autumn_camera_seasons": "spring" in seasons
                                           and "autumn" in seasons,
        "eight_sites_with_both_original_modalities": len(sites_cam & sites_trap) >= 8,
        "five_site_seasons_with_both_modalities": len(site_season_cam & site_season_trap) >= 5,
        "two_unambiguous_original_camera_species": len({
            r["species"] for r in cam if r["species"]
        }) >= 2,
        "hundred_original_distinct_visit_ids": len(camera_visits | visit_table_ids) >= 100,
        "camera_trap_state_90pct_nonmissing": (
            sum(bool(r["trap_state"]) for r in cam) / len(cam) >= 0.9
        ),
        "twenty_unambiguous_same_site_station_links": len(source_matched_station_keys) >= 20,
        "eight_camera_and_trap_overlap_sites_with_effort_table": (
            len({r["site"] for r in effort if r["site"]} & sites_cam & sites_trap) >= 8
            and good_effort >= 8
        ),
        "camera_datetime_90pct_parseable": observed_cam_date / len(cam) >= .9,
        "live_trap_date_90pct_parseable": observed_trap_date / len(trap) >= .9,
        "five_dated_site_season_modalities": len(
            sites_seasons_valid_cam & sites_seasons_valid_trap
        ) >= 5,
    }
    return {
        "source_row_counts": {kind: len(v) for kind, v in rows.items()},
        "camera_sites": len(sites_cam),
        "trap_sites": len(sites_trap),
        "sites_with_both_recording_modalities": len(sites_cam & sites_trap),
        "distinct_original_camera_site_station_keys": len(cam_stations),
        "distinct_original_live_trap_site_station_keys": len(cap_stations),
        "strict_name_matched_station_keys": len(source_matched_station_keys),
        "camera_original_species_name_count_not_taxon_filtered": len(
            {r["species"] for r in cam if r["species"]}
        ),
        "camera_original_distinct_visit_ID_count": len(camera_visits),
        "visit_table_original_distinct_visit_ID_count": len(visit_table_ids),
        "source_camera_visit_ids_shared_with_visit_table": len(
            camera_visits & visit_table_ids
        ),
        "camera_original_trap_state_nonmissing_fraction": (
            sum(bool(r["trap_state"]) for r in cam) / len(cam)
        ),
        "camera_datetime_parseable_fraction": observed_cam_date / len(cam),
        "trap_date_parseable_fraction": observed_trap_date / len(trap),
        "camera_dates_unique_count": len(dates_camera - {None}),
        "trap_dates_unique_count": len(dates_trap - {None}),
        "source_site_season_groups_camera": len(site_season_cam),
        "source_site_season_groups_trap": len(site_season_trap),
        "original_dated_site_season_common_groups": len(
            sites_seasons_valid_cam & sites_seasons_valid_trap
        ),
        "published_site_effort_positive_numeric_rows": good_effort,
        "structural_go_checks": checks,
        "all_structural_go_checks_passed": all(checks.values()),
        "no_capture_outcomes_or_species_by_station_effect_unsealed": True,
        "no_source_animal_ids_site_codes_or_individual_coordinates_exported": True,
    }

def run() -> dict:
    global STAGE
    sources = {}
    recs = {}
    for role in ORIGINAL_FILE_ROLES:
        original, rec = source_meta_and_csv(role)
        sources[role] = parse_csv(original, role)
        recs[role] = rec
    versions = {r["source_version_id_from_provider_when_available"]
                for r in recs.values()
                if r["source_version_id_from_provider_when_available"]}
    require(len(versions) <= 1, "CROSS_FILE_DATASET_VERSION_MISMATCH")
    STAGE = "ORIGINAL_SCHEMA_AND_EFFECT_BLIND_SOURCE_SUPPORT"
    gate = support_only(sources)
    return {
        "schema": "neon.australia_paired_camera_capture_source_only.v1",
        "status": ("SOURCE_GO_ONLY_NO_ECOLOGICAL_EFFECT" if gate["all_structural_go_checks_passed"]
                   else "SOURCE_STOP_STRUCTURAL_COVERAGE_OR_JOIN"),
        "published_original_source": {
            "doi": DOI, "landing_url": ORIGINAL_LANDING,
            "publication_year": 2026,
            "matched_baited_trap_camera_design_from_published_readme": True,
            "provider_file_metadata_and_actual_download_sha256": recs,
            "version_id_consistent_if_available": len(versions) <= 1,
            "no_10GB_photo_archive_fetched": True
        },
        "effect_blind_source_support": gate,
        "scientific_scope": {
            "capture_not_true_space_use": True,
            "camera_aimed_at_baited_traps_not_independent_habitat_occupancy": True,
            "no_urban_trappability_novelty_claim_original_authors_prior_art": True,
            "no_trap_state_specific_capture_risk_or_bias_estimated": True,
            "no_station_specific_camera_uptime_in_aggregate_effort_file": True,
            "NEON_Portal_Finland_Structural_old_results_untouched": True,
            "single_NEON_manuscript_stays_DRAFT_SUBMISSION_HOLD": True,
            "effect_eligibility_frozen_in": PROTOCOL
        },
        "retrieved_utc": datetime.now(timezone.utc).isoformat()
    }

def main() -> int:
    global STAGE
    if len(sys.argv) == 2 and sys.argv[1] == "--source-stop-no-token":
        # Explicit reproducible no-credential state is not source GO.
        result = {
            "schema": "neon.australia_paired_camera_capture_source_only.v1",
            "status": "SOURCE_STOP_DRYAD_TOKEN_NOT_CONFIGURED",
            "stopped_at": "ORIGINAL_PROVIDER_AUTHENTICATION",
            "original_source_expected_doi": DOI,
            "provider_token_not_logged_or_used": True,
            "no_original_source_bytes_or_ecological_outcomes_opened": True,
            "next_authorized_input": "GitHub Actions DRYAD_TOKEN repository secret from Dryad account",
            "scientific_submission_HOLD": True,
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0  # completed source-STOP receipt; not a GO.
    try:
        result = run()
        status = 0 if result["status"] == "SOURCE_GO_ONLY_NO_ECOLOGICAL_EFFECT" else 3
    except Exception as err:
        result = {
            "schema": "neon.australia_paired_camera_capture_source_only.v1",
            "status": "SOURCE_STOP_BEFORE_BIOLOGICAL_RESPONSE",
            "stopped_at": STAGE,
            "error_type": type(err).__name__,
            "scientific_stop_reason_code": str(err)[:200],
            "original_source_expected_doi": DOI,
            "no_raw_source_or_identifiers_or_effects_exported": True,
            "no_original_NEON_Portal_Finland_Structural_results_read": True,
        }
        status = 3
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True, indent=2))
    return status

if __name__ == "__main__":
    raise SystemExit(main())
