#!/usr/bin/env python3
"""Effect-blind MOSA individual identifier forensic audit.

Explain how the published claim of 19,850 M. natalensis unique individuals
relates to the count of distinct TOE code strings in the checksum-verified
Zenodo raw table. Do not invent aliases, reassign tags, split/merge animals,
compute known-alive MNA, W/B, centroids, or density effects.

Inputs are the SAME exact archived source validated by MD5, with status STOP
when trustworthy per-animal identity remains unresolved.
"""
from __future__ import annotations

import csv
import io
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from analysis.audit_mosa_effect_blind_structure_v1 import (
    published_field_map, parse_all_dates,
)
from analysis.audit_mosa_zenodo_source_schema_v1 import (
    API, RECORD_ID, _get, select_datafile, validate_source_bytes,
    PublishedSourceError,
)

OUT=Path("build/mosa_individual_identity_integrity_v1.json")
PUBLISHED_MN_UNIQUE=19850
PUBLISHED_MN_RECORDS=45433
PUBLISHED_RAW_RECORDS=49216

def _months_between(a:date,b:date) -> int:
    return (b.year-a.year)*12+(b.month-a.month)

def examine_identity(fields,records,*,published_total=PUBLISHED_MN_UNIQUE):
    f=published_field_map(fields)
    dates=parse_all_dates([r.get(f["date"],"") for r in records])
    by_tag=defaultdict(list)
    raw_toes=set()
    stripped_toes=set()
    casefolded_toes=set()
    all_species=defaultdict(set)
    same_day_positions=defaultdict(set)
    prefix_tags=set()
    whitespace_tags=set()
    invalid_toe=0
    sex_values=defaultdict(set)
    for row in records:
        species=str(row.get(f["species"]) or "").strip().upper()
        raw=str(row.get(f["tag"]) or "")
        if raw.strip():
            all_species[raw.strip()].add(species)
        if species!="MN":continue
        tag=raw.strip()
        if not tag:
            invalid_toe+=1
            continue
        raw_toes.add(raw)
        stripped_toes.add(tag)
        casefolded_toes.add(tag.casefold())
        if raw!=tag:whitespace_tags.add(raw)
        if "/" in tag:prefix_tags.add(tag)
        ds=str(row.get(f["date"]) or "").strip()
        d=dates.get(ds)
        if d is None:raise PublishedSourceError("MOSA MN date could not be verified")
        by_tag[tag].append(d)
        # Only report counts of impossible simultaneous trap-site conflicts;
        # no individual codes, coordinates or detailed capture rows are emitted.
        x=str(row.get(f["x"]) or "").strip()
        y=str(row.get(f["y"]) or "").strip().upper()
        if x and y:
            same_day_positions[(tag,d)].add((x,y))
        if "SX" in row:
            sex=str(row.get("SX") or "").strip().upper()
            if sex and sex not in {"NA","N/A","UNKNOWN"}:
                sex_values[tag].add(sex)
    tag_span=Counter()
    span_long=[]
    top_span=0
    tag_unambiguous_days=0
    for tag,days in by_tag.items():
        unique=sorted(set(days))
        tag_unambiguous_days+=len(unique)
        span=_months_between(unique[0],unique[-1])
        tag_span[span]+=1
        top_span=max(span,top_span)
        if span>24:span_long.append(tag)
    collision_groups=sum(len(v)>1 for v in same_day_positions.values())
    collision_tags={tag for (tag,day),stations in same_day_positions.items()
                    if len(stations)>1}
    reuse_across_species=sum(len({sp for sp in species if sp})>1
                             for species in all_species.values())
    ambiguous_sexes=sum(len(x)>1 for x in sex_values.values())
    distinct=len(stripped_toes)
    diff=(published_total-distinct) if published_total is not None else None
    status=(
        "IDENTITY_COUNTS_MATCHED_SOURCE_ONLY"
        if published_total is None or diff==0
        else "STOP_MOSA_PUBLISHED_INDIVIDUAL_COUNT_MISMATCH"
    )
    return {
        "schema":"neon.external_mosa_identity_integrity.v1",
        "status":status,
        "MN_raw_capture_records_with_nonblank_TOE":sum(len(v) for v in by_tag.values()),
        "MN_distinct_raw_TOE":distinct,
        "MN_distinct_exact_unstripped_TOE":len(raw_toes),
        "MN_distinct_casefolded_TOE":len(casefolded_toes),
        "MN_TOE_values_with_leading_or_trailing_whitespace":len(whitespace_tags),
        "MN_tags_with_series_prefix":len(prefix_tags),
        "MN_tags_with_observations_in_multiple_calendar_days":sum(len(set(d))>1 for d in by_tag.values()),
        "MN_TOE_date_multiple_station_collision_groups":collision_groups,
        "MN_TOE_with_same_date_multiple_station":len(collision_tags),
        "MN_TOE_span_gt24_months":len(span_long),
        "MN_maximum_TOE_span_months":top_span,
        "MN_TOE_mixed_reported_sex":ambiguous_sexes,
        "same_raw_TOE_in_multiple_species_count":reuse_across_species,
        "MN_blank_TOE_records":invalid_toe,
        "MN_published_unique_individuals":published_total,
        "MN_individual_count_gap_published_minus_TOE":diff,
        "total_distinct_MN_TOE_day_observation_keys":tag_unambiguous_days,
        "individual_identity_reassignment_prohibited":True,
        "all_raw_tags_and_capture_coordinates_redacted":True,
        "MNA_predictor_unsealed":False,
        "W_B_or_MNA_effects_opened":False,
        "claim_boundary":(
            "The 2023 publication uses corrected/reused toe-code histories "
            "and reports 19850 animals. Distinct published TOE strings alone "
            "are not proven to identify the same 19850 animals. Do not silently "
            "change the animal denominator or interpolate lifetimes until the "
            "published companion encounter matrix and correction logic are reconciled."
        ),
    }


def run():
    meta=json.loads(_get(API).decode("utf-8"))
    if int(meta.get("id",-1))!=RECORD_ID:
        raise PublishedSourceError("MOSA Zenodo record ID mismatch")
    published=select_datafile(meta)
    raw=_get((published.get("links") or {}).get("self"))
    verified=validate_source_bytes(raw,published)
    sep={"TAB":"\t","SEMICOLON":";","COMMA":","}[verified["delimiter_type"]]
    reader=csv.DictReader(io.StringIO(raw.decode(verified["text_encoding"])),delimiter=sep)
    records=list(reader)
    if len(records)!=PUBLISHED_RAW_RECORDS:
        raise PublishedSourceError("MOSA checksum-valid source row count drift")
    counts=Counter(str(row.get("SPECIES") or "").upper().strip() for row in records)
    if counts["MN"]!=PUBLISHED_MN_RECORDS:
        raise PublishedSourceError("MOSA raw MN capture record count changed")
    result=examine_identity(reader.fieldnames,records)
    result["source"]={
        "zenodo_record":RECORD_ID,
        "verified_MD5":verified["verified_checksum"],
        "verified_byte_size":verified["verified_byte_count"],
        "published_MN_capture_rows":PUBLISHED_MN_RECORDS,
    }
    result["available_companion_files"]=[
        str(r.get("key")) for r in meta.get("files",[])
        if any(k in str(r.get("key") or "").lower()
               for k in ("primary_secondary","rmarkdown","rmd","mosa"))
    ][:30]
    return result


if __name__=="__main__":
    try: r=run()
    except (PublishedSourceError,RuntimeError,ValueError,OSError) as ex:
        r={
            "schema":"neon.external_mosa_identity_integrity.v1",
            "status":"STOP_MOSA_IDENTITY_SOURCE_ERROR",
            "error":str(ex)[:500],
            "W_B_or_MNA_effects_opened":False,
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps(r,indent=2,sort_keys=True))
    if r["status"]!="IDENTITY_COUNTS_MATCHED_SOURCE_ONLY":
        raise SystemExit(3)
