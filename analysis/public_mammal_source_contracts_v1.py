from __future__ import annotations

import json
from pathlib import Path

EXPECTED_PORTAL_FILES = {
    "Rodents/Portal_rodent.csv",
    "Rodents/Portal_rodent_trapping.csv",
    "Rodents/Portal_rodent_species.csv",
    "SiteandMethods/Portal_plots.csv",
    "SiteandMethods/Portal_UTMCoords.csv",
}
EXPECTED_NEON_TABLES = {
    "mam_perplotnight",
    "mam_pertrapnight",
    "mam_identificationHistory",
}

def load_source_manifest(path: Path) -> dict:
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise ValueError("source manifest must be a JSON object")
    return value

def validate_portal_contract(manifest: dict) -> None:
    portal=manifest["portal"]
    if portal["repository"]!="weecology/PortalData":
        raise ValueError("unexpected Portal repository")
    if portal["commit_sha"]!="72d7ff8568052763bf6899dc462e285684cf20f6":
        raise ValueError("Portal commit is not frozen")
    if set(portal["required_files"])!=EXPECTED_PORTAL_FILES:
        raise ValueError("Portal required file contract changed")

def validate_neon_contract(manifest: dict) -> None:
    neon=manifest["neon"]
    if neon["product_code"]!="DP1.10072.001":
        raise ValueError("unexpected NEON product")
    if neon["release"]!="RELEASE-2026":
        raise ValueError("unexpected NEON release")
    if neon["inferential_status"]!="retrospective_development_only":
        raise ValueError("RELEASE-2026 must remain development-only")
    if set(neon["required_tables"])!=EXPECTED_NEON_TABLES:
        raise ValueError("NEON required table contract changed")
    if neon["authentication"]["environment_variable"]!="NEON_API_TOKEN":
        raise ValueError("unexpected NEON token environment variable")
    if neon["authentication"].get("commit_token_value"):
        raise ValueError("NEON token value must never be committed")
