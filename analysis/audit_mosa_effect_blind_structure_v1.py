#!/usr/bin/env python3
"""MOSA 29-year external rodent structural support, before ANY ecological effects.

Single independent Tanzanian 30x10 grid, NOT NEON 10x10 and not a multi-genus
confirmation. This checks exact published fields and literal 3 consecutive
capture dates within a calendar month without estimating W/B or abundance.
Source checksum, byte size and published 49,216 record count are mandatory.

A calendar month with missing capture dates or a bout crossing month boundaries
is conservatively ineligible. If the archive requires a different occasion
scheme, STOP and document protocol mapping before any spatial effects.
"""
from __future__ import annotations

import csv
import io
import json
import re
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

from analysis.audit_mosa_zenodo_source_schema_v1 import (
    API, RECORD_ID, OUT as SCHEMA_OUT,
    _get, select_datafile, validate_source_bytes, PublishedSourceError,
)

OUT=Path("build/mosa_external_structural_support_v1.json")
MIN_MONTHS=60
MIN_YEARS=10
MIN_M=5

ALIASES={
    "date":("DATE",),
    "grid":("GRID",),
    "species":("SPECIES","SP"),
    "tag":("TOE-ID","TOEID"),
    "x":("X",),
    "y":("Y",),
}

def _canonical(value):
    return re.sub(r"[^A-Z0-9]","",str(value).upper().strip())


def published_field_map(header):
    resolved={}
    for role,values in ALIASES.items():
        matches=[col for col in header
                 if _canonical(col) in {_canonical(x) for x in values}]
        if len(matches)!=1:
            raise PublishedSourceError(
                f"Required published MOSA {role} column ambiguous/missing: {len(matches)}"
            )
        resolved[role]=matches[0]
    if len(set(resolved.values()))!=len(resolved):
        raise PublishedSourceError("MOSA field aliases collide")
    return resolved


def parse_all_dates(raw):
    """Require one globally consistent unambiguous capture date interpretation."""
    values=sorted({s.strip() for s in raw if str(s).strip()})
    if not values:
        raise PublishedSourceError("No known capture dates")
    def try_fmt(fmt):
        parsed={}
        try:
            for s in values:
                d=date.fromisoformat(s) if fmt=="ISO" else date.strptime(s,fmt)
                if not 1994<=d.year<=2023:
                    raise ValueError("outside published 1994-2023 sampling")
                parsed[s]=d
            return parsed
        except (ValueError,TypeError):
            return None
    # date.strptime exists in Python 3.12? use datetime.strptime instead.
    from datetime import datetime
    def parse_fmt(fmt):
        out={}
        try:
            for s in values:
                d=date.fromisoformat(s) if fmt=="ISO" else datetime.strptime(s,fmt).date()
                if not 1994<=d.year<=2023:raise ValueError("year outside archive")
                out[s]=d
            return out
        except (ValueError,TypeError):
            return None
    options=[parse_fmt(fmt) for fmt in (
        "ISO","%d/%m/%Y","%m/%d/%Y","%d-%m-%Y","%m-%d-%Y",
        "%d.%m.%Y",
    )]
    unique={}
    for opt in options:
        if opt is None:continue
        fingerprint=tuple(opt[s].isoformat() for s in values)
        unique[fingerprint]=opt
    if len(unique)!=1:
        raise PublishedSourceError(
            f"Date interpretation missing/ambiguous; globally valid maps={len(unique)}"
        )
    return next(iter(unique.values()))


def effect_blind_support(fields,records):
    m=published_field_map(fields)
    calendar=parse_all_dates([r[m["date"]] for r in records])
    species=Counter()
    by_month=defaultdict(list)
    invalid_station=0
    missing_tag=0
    for row in records:
        code=str(row.get(m["species"]) or "").strip().upper()
        species[code]+=1
        if code!="MN":
            continue
        day=calendar.get(str(row.get(m["date"]) or "").strip())
        if day is None:
            raise PublishedSourceError("Mastomys capture without date")
        grid=str(row.get(m["grid"]) or "").strip().upper()
        if grid!="MOSA":
            raise PublishedSourceError("Unexpected additional grid; not a one-site MOSA study")
        x=str(row.get(m["x"]) or "").strip()
        y=str(row.get(m["y"]) or "").strip().upper()
        try:
            if not 1<=int(x)<=30 or y not in "ABCDEFGHIJ" or len(y)!=1:
                invalid_station+=1
                continue
        except (TypeError,ValueError):
            invalid_station+=1
            continue
        toe=str(row.get(m["tag"]) or "").strip()
        if not toe:
            missing_tag+=1
            continue
        by_month[(day.year,day.month)].append((day,toe))
    valid_sessions=0
    all_three=0
    year_support=Counter()
    date_histogram=Counter()
    count_unique_months=len(by_month)
    for (year,month),records in sorted(by_month.items()):
        days=sorted({day for day,_tag in records})
        date_histogram[len(days)]+=1
        if len(days)!=3 or days[1]!=days[0]+timedelta(days=1) or days[2]!=days[1]+timedelta(days=1):
            continue
        all_three+=1
        by_tag=defaultdict(set)
        for day,toe in records:
            by_tag[toe].add(day)
        m_count=sum(len(days)>=2 for days in by_tag.values())
        if m_count>=MIN_M:
            valid_sessions+=1
            year_support[year]+=1
    eligible_years=len(year_support)
    passes=valid_sessions>=MIN_MONTHS and eligible_years>=MIN_YEARS
    return {
        "schema":"neon.external_mosa_effect_blind_support.v1",
        "status":("GO_MOSA_ONE_SITE_LONGITUDINAL_SUPPORT_ONLY"
                  if passes else "STOP_MOSA_PRE_EFFECT_STRUCTURAL_SUPPORT"),
        "fields_published_protocol_exactly_mapped":m,
        "raw_records_total":len(records),
        "species_capture_counts":dict(sorted(species.items())),
        "MN_months_with_capture_records":count_unique_months,
        "monthly_observed_capture_date_count_histogram":dict(sorted(date_histogram.items())),
        "consecutive_three_day_MN_months":all_three,
        "months_with_at_least_five_distinct_two_night_MN_tags":valid_sessions,
        "distinct_years_with_support":eligible_years,
        "eligible_months_by_year":dict(sorted(year_support.items())),
        "discarded_or_unresolved_MN_station_rows":invalid_station,
        "MN_rows_missing_tag":missing_tag,
        "published_49216_records_matched":len(records)==49216,
        "published_MN_capture_total_matched":species["MN"]==45433,
        "historical_MNA_support_or_variation_opened":False,
        "W_B_or_individual_spatial_centres_computed":False,
        "density_slopes_or_biological_mechanisms_opened":False,
        "next_gate":"Freeze a full 3-night capture-status occasion map, unique MNA tag histories and 10+ independent years with 2+ MNA levels. One MOSA site cannot test spatial among-site generality.",
        "limitations":"Only capture-bearing dates are visible. A strict same-calendar-month consecutive three-night filter is conservative, and may exclude nights with zero capture or month-boundary bouts; never relax after ecological effects."
    }


def run():
    meta=json.loads(_get(API).decode("utf-8"))
    if int(meta.get("id",-1))!=RECORD_ID:
        raise PublishedSourceError("Unexpected Zenodo record")
    file=select_datafile(meta)
    raw=_get((file.get("links") or {}).get("self"))
    verified=validate_source_bytes(raw,file)
    encoding=verified["text_encoding"]
    sep={"TAB":"\t","COMMA":",","SEMICOLON":";"}[verified["delimiter_type"]]
    text=raw.decode(encoding)
    reader=csv.DictReader(io.StringIO(text),delimiter=sep)
    rows=list(reader)
    if len(rows)!=49216 or list(reader.fieldnames or [])!=verified["column_headers"]:
        raise PublishedSourceError("Published source row/header drift between checks")
    result=effect_blind_support(verified["column_headers"],rows)
    result["source"]={
        "zenodo_version_record":RECORD_ID,
        "zenodo_file_key":verified["file_name"],
        "source_MD5":verified["verified_checksum"],
        "source_bytes":verified["verified_byte_count"],
        "license":"CC-BY-4.0",
    }
    return result

if __name__=="__main__":
    import urllib.error
    try:
        r=run()
    except (PublishedSourceError,RuntimeError,urllib.error.URLError,
            TimeoutError,ValueError) as e:
        r={"schema":"neon.external_mosa_effect_blind_support.v1",
           "status":"STOP_MOSA_PRE_EFFECT_SOURCE_OR_STRUCTURAL_ERROR",
           "diagnostic":str(e)[:500],
           "ecological_response_or_abundance_slopes_opened":False}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps(r,indent=2,sort_keys=True))
    if r["status"]!="GO_MOSA_ONE_SITE_LONGITUDINAL_SUPPORT_ONLY":
        raise SystemExit(3)
