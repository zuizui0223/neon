#!/usr/bin/env python3
"""MOSA effect-blind monthly Minimum Number Alive (MNA) support.

Source: checksum-verified original Zenodo 10049811 capture records, 1994-2023.
MNA is constructed from the FIRST/LAST observed month of each *published
fully qualified* TOE-ID, including series prefixes: never conflate "1520"
and "5/1520" nor strip leading zeroes. Interpolate months with no recapture
between those endpoints as known-alive; this is an index, NOT true density.

No coordinates are converted into distances, no individual centroids or
W/B values are computed, no MNA-spatial effect or mechanism is opened.
Only structural support and separate predictor-only eligible month values.
"""
from __future__ import annotations

import csv
import io
import json
import os
from collections import Counter, defaultdict
from datetime import timedelta
from pathlib import Path

from analysis.audit_mosa_effect_blind_structure_v1 import (
    published_field_map, parse_all_dates, effect_blind_support,
    MIN_M, MIN_MONTHS, MIN_YEARS,
)
from analysis.audit_mosa_zenodo_source_schema_v1 import (
    API, RECORD_ID, _get, select_datafile, validate_source_bytes,
    PublishedSourceError,
)

OUT=Path("build/mosa_mna_effect_blind_support_v1.json")
PREDICTORS=Path("build/mosa_mna_predictor_only_v1.json")
SOURCE_N=49216
SOURCE_MN=45433
SOURCE_MN_INDIVIDUALS=19850
MAX_REASONABLE_TAG_LIFETIME_MONTHS=24

def month_key(day):
    return (day.year,day.month)

def month_number(month):
    return 12*month[0]+month[1]

def build_known_alive_by_month(records,fields):
    m=published_field_map(fields)
    all_dates=parse_all_dates([r.get(m["date"],"") for r in records])
    tags=defaultdict(set)
    seen=defaultdict(set)
    for row in records:
        if str(row.get(m["species"]) or "").strip().upper()!="MN":
            continue
        raw=str(row.get(m["tag"]) or "").strip()
        if not raw:raise PublishedSourceError("MOSA MN has blank TOE-ID; do not invent identity")
        d=all_dates.get(str(row.get(m["date"]) or "").strip())
        if d is None:raise PublishedSourceError("MOSA MN capture missing parsed date")
        month=month_key(d)
        tags[raw].add(month)
        seen[month].add(raw)
    if not tags:raise PublishedSourceError("zero monthly MOSA tagged rodents")
    months=sorted(seen)
    first_last={}
    too_long=[]
    for tag,observed in tags.items():
        lo=min(observed);hi=max(observed)
        duration=month_number(hi)-month_number(lo)
        first_last[tag]=(lo,hi)
        if duration>MAX_REASONABLE_TAG_LIFETIME_MONTHS:
            too_long.append((tag,duration))
    starts=Counter();ends=Counter()
    for lo,hi in first_last.values():
        starts[month_number(lo)]+=1
        ends[month_number(hi)+1]+=1
    mnka={}
    active=0
    for month in months:
        idx=month_number(month)
        # Avoid skipping event deltas when a calendar month has no captures.
        active=sum(month_number(lo)<=idx<=month_number(hi)
                   for lo,hi in first_last.values())
        if active<len(seen[month]):
            raise PublishedSourceError("MNA less than tags captured in an observed month")
        mnka[month]=active
    return {
        "MNA_by_month":mnka,
        "captured_unique_by_month":{k:len(v) for k,v in seen.items()},
        "unique_tags":len(tags),
        "tag_histories_over_24_months":len(too_long),
        "longest_tag_history_months":max(
            month_number(hi)-month_number(lo)
            for lo,hi in first_last.values()),
        "month_count_with_MN_captures":len(months),
        "fully_qualified_toe_prefixes_retained":True,
        "no_individual_tags_exposed_in_summary":True,
    }


def eligible_repeat_months(records,fields):
    """Reproduce the exact locked three-day / 5-repeat-support filter."""
    m=published_field_map(fields)
    all_dates=parse_all_dates([r.get(m["date"],"") for r in records])
    by_month=defaultdict(list)
    for r in records:
        if str(r.get(m["species"]) or "").strip().upper()!="MN":continue
        d=all_dates.get(str(r.get(m["date"]) or "").strip())
        if d is None:raise PublishedSourceError("MOSA source has unparsed MN day")
        if str(r.get(m["grid"]) or "").strip().upper()!="MOSA":
            raise PublishedSourceError("unexpected MOSA site identity")
        try:
            x=int(str(r.get(m["x"]) or "").strip())
            y=str(r.get(m["y"]) or "").strip().upper()
            if not 1<=x<=30 or y not in "ABCDEFGHIJ" or len(y)!=1:
                continue
        except (TypeError,ValueError):
            continue
        tag=str(r.get(m["tag"]) or "").strip()
        if not tag:continue
        by_month[month_key(d)].append((d,tag))
    supported=[]
    exact_dates=0
    for month,rec in sorted(by_month.items()):
        dates=sorted({d for d,_ in rec})
        if len(dates)!=3 or not(
            dates[1]==dates[0]+timedelta(days=1)
            and dates[2]==dates[1]+timedelta(days=1)):
            continue
        exact_dates+=1
        captured_days=defaultdict(set)
        for d,tag in rec:captured_days[tag].add(d)
        count=sum(len(nights)>=2 for nights in captured_days.values())
        if count>=MIN_M:
            supported.append({
                "year":month[0],"month":month[1],"repeat_supported_m":count,
                "observed_distinct_tag_count":len(captured_days),
            })
    return exact_dates,supported


def compute_mna_support(records,fields,*,expect_published=True):
    if expect_published and len(records)!=SOURCE_N:
        raise PublishedSourceError("MOSA original raw source row count changed")
    official=effect_blind_support(fields,records)
    computed=build_known_alive_by_month(records,fields)
    n_mn=sum(str(r.get(published_field_map(fields)["species"]) or "").strip().upper()=="MN"
             for r in records)
    if expect_published and (
        n_mn!=SOURCE_MN or computed["unique_tags"]!=SOURCE_MN_INDIVIDUALS
    ):
        raise PublishedSourceError(
            f"Published species records/fully-qualified tagged individuals do not match: "
            f"{n_mn}, {computed['unique_tags']}"
        )
    exact,supported=eligible_repeat_months(records,fields)
    if (exact!=official["consecutive_three_day_MN_months"] or
        len(supported)!=official["months_with_at_least_five_distinct_two_night_MN_tags"]):
        raise PublishedSourceError("MOSA structural cohorts drifted from locked effect-blind test")
    by_year=defaultdict(list)
    predictor_only=[]
    for r in supported:
        month=(r["year"],r["month"])
        if month not in computed["MNA_by_month"]:
            raise PublishedSourceError("MOSA eligible month not in MNA history")
        mna=computed["MNA_by_month"][month]
        if mna<r["observed_distinct_tag_count"]:
            raise PublishedSourceError("MOSA month MNA smaller than captured cohort")
        by_year[r["year"]].append(mna)
        predictor_only.append({
            "year":r["year"],"month":r["month"],
            "year_month":f'{r["year"]:04d}-{r["month"]:02d}',
            "MNA":mna,
            "m":r["repeat_supported_m"],
            "observed_unique_tags":r["observed_distinct_tag_count"],
        })
    supported_varying={
        year:vals for year,vals in by_year.items()
        if len(vals)>=2 and len(set(vals))>=2
    }
    variation_n=sum(len(vals) for vals in supported_varying.values())
    passes=(
        len(supported)>=MIN_MONTHS
        and len(supported_varying)>=MIN_YEARS
        and variation_n>=MIN_MONTHS
        and computed["tag_histories_over_24_months"]==0
    )
    result={
        "schema":"neon.external_mosa_mna_effect_blind_support.v1",
        "status":"GO_MOSA_YEAR_BLOCK_MNA_VARIATION_SUPPORT_ONLY"
                 if passes else "STOP_MOSA_MNA_VARIATION_SUPPORT",
        "record_count":len(records),
        "species_MN_capture_records":n_mn,
        "MNA_identity":"Published verbatim fully-qualified TOE-ID including collision series prefixes and B suffix; no normalization or splitting after observing effects",
        "MNA_method":"Monthly minimum number alive from first/last captured month of each tag over entire 1994-2023 archive, including intervening uncaptured months",
        "MNA_not_true_density":True,
        "published_unique_MN_tags":computed["unique_tags"],
        "source_years_with_MN_captures":len({
            k[0] for k in computed["MNA_by_month"]
        }),
        "months_with_MN_captures":computed["month_count_with_MN_captures"],
        "candidate_exact_three_night_months":exact,
        "months_with_repeat_supported_m_ge5":len(supported),
        "years_with_eligible_months":len(by_year),
        "years_with_two_MNA_levels":len(supported_varying),
        "eligible_months_in_MNA_varying_years":variation_n,
        "required_years":MIN_YEARS,
        "required_months":MIN_MONTHS,
        "tag_histories_exceeding_24_months":computed["tag_histories_over_24_months"],
        "longest_tag_history_months":computed["longest_tag_history_months"],
        "MNA_summary_on_eligible_months":{
            "min":min(r["MNA"] for r in predictor_only) if predictor_only else None,
            "max":max(r["MNA"] for r in predictor_only) if predictor_only else None,
            "distinct_levels":len({r["MNA"] for r in predictor_only}),
        },
        "eligible_months_by_year":dict(sorted(Counter(r["year"] for r in supported).items())),
        "eligible_within_year_varying_years":sorted(supported_varying),
        "remaining_MNA_predictor_artifact_separate":True,
        "capture_coordinate_distances_computed":False,
        "W_B_or_centroid_values_opened":False,
        "density_slopes_opened":False,
        "no_29year_independent_site_claim":True,
        "interpretation":"Effect-blind predictor support from one MOSA grid. Repeated monthly observations within one year are not independent sites; year-block replication and fixed month/year effects required after metric-only QC. MNA may use future recaptures for known-alive interpolation and is not a causal observed cue.",
    }
    return result,predictor_only


def run():
    meta=json.loads(_get(API).decode("utf-8"))
    if int(meta.get("id",-1))!=RECORD_ID:
        raise PublishedSourceError("MOSA source record identity drift")
    file=select_datafile(meta)
    raw=_get((file.get("links") or {}).get("self"))
    validated=validate_source_bytes(raw,file)
    text=raw.decode(validated["text_encoding"])
    sep={"TAB":"\t","COMMA":",","SEMICOLON":";"}[
        validated["delimiter_type"]]
    reader=csv.DictReader(io.StringIO(text),delimiter=sep)
    records=list(reader)
    if list(reader.fieldnames or [])!=validated["column_headers"]:
        raise PublishedSourceError("MOSA archive schema changed between validation and calculation")
    result,predictors=compute_mna_support(
        records,validated["column_headers"],expect_published=True)
    result["source"]={
        "Zenodo_DOI":"10.5281/zenodo.10049811",
        "record_id":RECORD_ID,
        "file":validated["file_name"],
        "original_bytes":validated["verified_byte_count"],
        "MD5":validated["verified_checksum"],
    }
    return result,predictors


if __name__=="__main__":
    try:
        result,predictors=run()
    except (PublishedSourceError,RuntimeError,ValueError,OSError) as e:
        result={
            "schema":"neon.external_mosa_mna_effect_blind_support.v1",
            "status":"STOP_MOSA_SOURCE_IDENTITY_OR_MNA_SUPPORT",
            "diagnostic":str(e)[:600],
            "W_B_or_density_slopes_opened":False,
            "ecological_confirmation":False,
        }
        predictors=[]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if predictors and result["status"]=="GO_MOSA_YEAR_BLOCK_MNA_VARIATION_SUPPORT_ONLY":
        PREDICTORS.write_text(json.dumps(predictors,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    if result["status"]!="GO_MOSA_YEAR_BLOCK_MNA_VARIATION_SUPPORT_ONLY":
        raise SystemExit(3)
