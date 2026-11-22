#!/usr/bin/env python3
"""Effect-blind exact-identifier boundary audit between frozen and provisional NEON.

Downloads and checksum-checks ONLY mammal per-plot-night scheduling tables.
Compares all site × plot × event and nightuid identities from RELEASE-2026
against the exact complete three-night events provisionally available outside
its site-month inventory. No capture rows, tags, taxonomy or spatial effects.

A public site-month availability contrast alone is NOT proof of response-level
independence. This audit fails closed on overlap or source-content ambiguity.
"""
from __future__ import annotations

import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

from analysis.audit_future_neon_mammal_availability_v1 import (
    audit as availability, URL as PRODUCT_URL_PUBLIC,
)
from analysis.audit_future_neon_plot_structure_v1 import (
    select_provisional_plot_files, START as NEW_START, END as NEW_END,
    FROZEN_RELEASE,
)
from analysis.audit_future_neon_capture_support_v1 import select_complete_events
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    _request_json, _download_many, _inventory, _read_plot_rows,
    PRODUCT, QUERY_URL, TOKEN_ENV, MAX_DOWNLOAD_WORKERS,
)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/future_neon_frozen_release_disjointness_v1.json"
OLD_START = "2015-04"
OLD_END = "2026-09"


def _row_key(r: dict) -> tuple[str, str, str]:
    return (str(r.get("siteID") or "").strip(),
            str(r.get("plotID") or "").strip(),
            str(r.get("eventID") or "").strip())


def compare_identifiers(
    frozen: list[dict], provisional: list[dict],
) -> dict:
    """Compare complete candidates to entire known frozen archive, all outcomes sealed."""
    future = select_complete_events(provisional)
    new_events = set(future["events"])
    new_nights = set(future["nights"])

    old_keys = set()
    old_nights = set()
    old_night_metadata = defaultdict(set)
    for r in frozen:
        key = _row_key(r)
        night = str(r.get("nightuid") or "").strip()
        if not all(key) or not night:
            raise RuntimeError("invalid frozen plot-night event or night identity")
        old_keys.add(key)
        old_nights.add(night)
        old_night_metadata[night].add(key)
    if any(len(keys)>1 for keys in old_night_metadata.values()):
        raise RuntimeError("conflicting night uid in frozen metadata")

    key_overlap = old_keys & new_events
    night_overlap = old_nights & new_nights
    novel_events = new_events - old_keys
    if not old_keys or not new_events:
        raise RuntimeError("empty source universe makes independence unauditable")

    def hashes(values):
        # Do not emit raw event identifiers in the provenance artifact.
        return sorted(hashlib.sha256("|".join(v).encode()).hexdigest()[:12]
                      if isinstance(v,tuple) else
                      hashlib.sha256(v.encode()).hexdigest()[:12]
                      for v in values)[:8]

    complete = not key_overlap and not night_overlap
    return {
        "schema": "neon.future_mammal_release_disjointness.v1",
        "status": "IDENTIFIER_DISJOINTNESS_PASS" if complete
                  else "STOP_OVERLAPPING_FROZEN_RELEASE_IDENTIFIERS",
        "frozen_plot_night_rows": len(frozen),
        "frozen_distinct_plot_events": len(old_keys),
        "frozen_distinct_nightuids": len(old_nights),
        "provisional_plot_night_rows": len(provisional),
        "candidate_complete_events": len(new_events),
        "candidate_distinct_nightuids": len(new_nights),
        "nonoverlapping_complete_events": len(novel_events),
        "overlapping_event_count": len(key_overlap),
        "overlapping_nightuid_count": len(night_overlap),
        "overlap_event_key_hash_prefixes": hashes(key_overlap),
        "overlap_nightuid_hash_prefixes": hashes(night_overlap),
        "future_W_B_opened": False,
        "capture_records_opened": False,
        "MNKA_effects_opened": False,
        "independent_ecological_confirmation": False,
        "interpretation": (
            "A PASS establishes only record-ID disjointness for the audited "
            "immutable frozen RELEASE-2026 snapshot and live provisional plot "
            "schedule. It cannot certify complete cross-boundary tagged "
            "histories, future release stability, or biological replication."
        ),
    }


def run() -> dict:
    token = os.environ.get(TOKEN_ENV,"").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN required for verified plot-night files")

    public = availability(_request_json(PRODUCT_URL_PUBLIC), "2026-10-10")
    if public["status"] not in (
        "INVENTORY_ONLY_CANDIDATE_MONTHS",
        "NO_FULLY_NEW_SITE_MONTHS_IN_INVENTORY",
    ):
        raise RuntimeError("public release/site-month metadata not validated")
    candidate = {(r["site"],r["month"]) for r in public["site_month_candidates"]
                 if NEW_START <= r["month"] <= NEW_END}
    sites = sorted({s for s,_ in candidate})
    if not sites:
        raise RuntimeError("no provisional site-months to audit")

    new_query = _request_json(
        QUERY_URL, token=token,
        body={"productCode":PRODUCT,"siteCodes":sites,
              "startDateMonth":NEW_START,"endDateMonth":NEW_END,
              "package":"basic","includeProvisional":True},
    )
    new_files = select_provisional_plot_files(
        new_query,candidate,kind="mam_perplotnight")["files"]
    if not new_files:
        raise RuntimeError("no checksum-verified provisional plot-night inventory")

    # Authoritative frozen file inventory, never infer archive membership
    # from the provisional query's release labels.
    old_query = _request_json(
        QUERY_URL,token=token,
        body={"productCode":PRODUCT,"siteCodes":sites,
              "startDateMonth":OLD_START,"endDateMonth":OLD_END,
              "release":FROZEN_RELEASE,"package":"basic",
              "includeProvisional":False},
    )
    all_old = _inventory(old_query)
    old_files = [r for r in all_old
                 if "mam_perplotnight" in r["name"]]
    if not old_files:
        raise RuntimeError("frozen plot-night archive not accessible")

    new_rows = []
    for f,raw in zip(new_files,_download_many(
            new_files,token,max_workers=MAX_DOWNLOAD_WORKERS)):
        new_rows.extend(_read_plot_rows(raw,f["site"],f["month"]))

    frozen_rows = []
    for f,raw in zip(old_files,_download_many(
            old_files,token,max_workers=MAX_DOWNLOAD_WORKERS)):
        frozen_rows.extend(_read_plot_rows(raw,f["site"],f["month"]))

    result = compare_identifiers(frozen_rows,new_rows)
    result["frozen_release"] = FROZEN_RELEASE
    result["provisional_plot_files_verified"] = len(new_files)
    result["frozen_plot_files_verified"] = len(old_files)
    result["frozen_file_inventory_digest"] = hashlib.sha256(
        json.dumps([(r["site"],r["month"],r["name"],r["md5"])
                    for r in old_files],sort_keys=True).encode()).hexdigest()
    result["provisional_file_inventory_digest"] = hashlib.sha256(
        json.dumps([(r["site"],r["month"],r["name"],r["md5"])
                    for r in new_files],sort_keys=True).encode()).hexdigest()
    return result


if __name__ == "__main__":
    try:
        output=run()
    except (RuntimeError,ValueError) as exc:
        output={
            "schema":"neon.future_mammal_release_disjointness.v1",
            "status":"STRUCTURAL_STOP_SOURCE_OR_IDENTITY_ERROR",
            "diagnostic":str(exc),
            "future_W_B_opened":False,
            "capture_records_opened":False,
            "independent_confirmation_authorized":False,
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(output,indent=2,sort_keys=True))
    if output["status"]!="IDENTIFIER_DISJOINTNESS_PASS":
        raise SystemExit(3)
