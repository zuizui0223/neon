from __future__ import annotations

import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_LOOKUP=ROOT/"data"/"external"/"neon_nlcd_group_lookup_v1.csv"


def load_nlcd_lookup(path: Path=DEFAULT_LOOKUP) -> dict[str,str]:
    with path.open(newline="",encoding="utf-8-sig") as fh:
        rows=list(csv.DictReader(fh))
    result={}
    for row in rows:
        raw=str(row.get("nlcd_class",""))
        group=str(row.get("habitat_group","")).strip()
        if not group:
            raise ValueError(f"missing habitat group for {raw!r}")
        if raw in result and result[raw]!=group:
            raise ValueError(f"conflicting NLCD mapping for {raw!r}")
        result[raw]=group
    return result


def map_neon_nlcd(value: str, *, lookup: dict[str,str] | None=None) -> str:
    mapping=load_nlcd_lookup() if lookup is None else lookup
    raw=str(value).strip()
    if raw not in mapping:
        raise KeyError(f"unmapped NLCD class: {raw!r}")
    return mapping[raw]


def portal_competition_context(treatment: str) -> str | None:
    value=str(treatment).strip().lower()
    if value=="control":
        return "control"
    if value=="exclosure":
        return "kangaroo_rat_exclosure"
    return None
