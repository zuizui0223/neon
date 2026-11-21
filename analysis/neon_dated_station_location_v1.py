"""NEON mammal trap station history/uncertainty with no ecological outputs.

Direct implementation of conservative research rules grounded in official
NEONScience/NEON-geolocation geoNEON/R/getLocMAM.R and findDateMatch.R:
- true station names come from the 10×10 nominal lattice, never from E5
  coordinate rotation or interpolation;
- direct reported grid uncertainty U gets U+1 m; missing uncertainty
  gets max direct U in the SAME grid +3 m (algorithmic assumption only);
- a capture date must match exactly one historical location validity interval
  [start, end), with no fallback to the newest API location.
No actual station coordinates or animal identities are exported here.
"""
from __future__ import annotations

from datetime import date,datetime
from math import isfinite
import re

STATION_LABELS=tuple(f"{chr(ord('A')+i)}{j}" for i in range(10) for j in range(1,11))
ISO_DATE=re.compile(r"^\d{4}-\d{2}-\d{2}(?:T|$)")
NEUTRAL={"", "NA", "N/A", "NULL", "NONE", "NAN"}


def station_labels_10x10() -> tuple[str,...]:
    return STATION_LABELS


def adjust_grid_uncertainty(reported_by_station:dict[str,float|None]) -> dict[str,dict]:
    if not isinstance(reported_by_station,dict) or not reported_by_station:
        raise ValueError("At least one standard grid monument source record required")
    measured=[]
    for station,raw in reported_by_station.items():
        if station not in STATION_LABELS:
            raise ValueError("Unknown nonstandard station; no imputed location is allowed")
        if raw is None:
            continue
        if isinstance(raw,bool) or not isinstance(raw,(int,float)) or not isfinite(raw) or raw<0:
            raise ValueError("Reported uncertainty must be finite and nonnegative")
        measured.append(float(raw))
    if not measured:
        raise ValueError("No grid monument has a directly reported uncertainty")
    maximum=max(measured)
    result={}
    for station,raw in reported_by_station.items():
        known=raw is not None
        result[station]={
            "adjusted_uncertainty_m":(
                float(raw)+1.0 if known else maximum+3.0
            ),
            "source":(
                "DIRECT_REPORTED_PLUS_1M"
                if known else "ASSUMED_GRID_MAX_MONUMENT_PLUS_3M"
            ),
            "raw_uncertainty_was_measured":known,
            "algorithmic_assumption_not_empirical_confidence_bound":True,
        }
    return result


def _date_value(value, *, description:str) -> date:
    if isinstance(value,datetime):
        return value.date()
    if isinstance(value,date):
        return value
    if not isinstance(value,str):
        raise ValueError(description+" missing or invalid start/date")
    v=value.strip()
    if not ISO_DATE.match(v):
        raise ValueError(description+" invalid ISO start/date")
    try:
        return date.fromisoformat(v[:10])
    except ValueError:
        raise ValueError(description+" invalid ISO start/date") from None


def choose_location_at_capture(
    records: list[dict], capture_date:date|str|datetime
) -> dict:
    """Return original record *by identity* if and only if unique dated match."""
    d=_date_value(capture_date,description="capture date")
    if not isinstance(records,list) or not records:
        raise ValueError("No date-valid station history records available")
    compatible=[]
    for rec in records:
        if not isinstance(rec,dict):
            raise ValueError("Invalid station historical location record")
        start=_date_value(rec.get("locationStartDate"),description="history start")
        raw_end=rec.get("locationEndDate")
        if raw_end is None or (
            isinstance(raw_end,str) and raw_end.strip().upper() in NEUTRAL
        ):
            end=None
        else:
            end=_date_value(raw_end,description="history end")
        if end is not None and end<=start:
            raise ValueError("Invalid history date range: end <= start")
        if start<=d and (end is None or d<end):
            compatible.append(rec)
    if not compatible:
        raise ValueError("No date-valid station location history for original capture")
    if len(compatible)!=1:
        raise ValueError("Ambiguous date-valid station location history")
    return compatible[0]
