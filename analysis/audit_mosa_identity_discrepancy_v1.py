#!/usr/bin/env python3
"""Explain original MOSA published-individual-count disagreement, outcome-blind.

Only reads pinned, verified original 2023 Zenodo capture bytes. Published paper:
M. natalensis 45,433 capture records, 19,850 unique *individuals*.
Present direct parser finds 19,818 unique verbatim TOE labels. These are NOT
necessarily the same estimand when correction / ID reuse occurred.

This diagnostic counts *potential identity collisions* with NO changes to tag
identity, no merging or splitting, no W/B, no MNA time series or density effects.
Do not use these diagnostics to lower or bypass source individual-count gate.
"""
from __future__ import annotations

import csv
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

from analysis.audit_mosa_effect_blind_structure_v1 import (
    published_field_map, parse_all_dates,
)
from analysis.audit_mosa_zenodo_source_schema_v1 import (
    API, RECORD_ID, _get, select_datafile, validate_source_bytes,
    PublishedSourceError,
)

OUT=Path("build/mosa_identity_discrepancy_v1.json")
PUBLISHED_MN_CAPTURES=45433
PUBLISHED_MN_INDIVIDUALS=19850
EXPECTED_RAW_RECORDS=49216
GAP_THRESHOLD_MONTHS=24


def _month_num(day):
    return day.year*12 + day.month


def identity_diagnostics(rows:list[dict], fields:list[str]) -> dict:
    resolved=published_field_map(fields)
    parse_date=parse_all_dates([r.get(resolved["date"],"") for r in rows])
    sexfield=next((key for key in fields if key.upper()=="SX"),None)
    flagfield=next((key for key in fields if key.upper()=="FLAGS"),None)
    nfield=next((key for key in fields if key.upper()=="NUMBER"),None)
    dates_by_tag=defaultdict(set)
    sexes_by_tag=defaultdict(set)
    tag_day=Counter()
    n_other_toes=set()
    n_mn=0
    flagged=0
    raw_number_values=set()
    bad=0
    has_prefix=set()
    suffix_b=set()
    for r in rows:
        species=str(r.get(resolved["species"]) or "").strip().upper()
        toe=str(r.get(resolved["tag"]) or "").strip()
        if species!="MN":
            if toe:n_other_toes.add(toe)
            continue
        n_mn+=1
        if not toe:
            raise ValueError("MN capture missing TOE identifier; cannot infer identities")
        date=parse_date.get(str(r.get(resolved["date"]) or "").strip())
        if date is None:
            raise ValueError("unparseable MN capture date")
        dates_by_tag[toe].add(date)
        tag_day[(toe,date)]+=1
        if "/" in toe:has_prefix.add(toe)
        if toe.upper().endswith(" B"):suffix_b.add(toe)
        if sexfield:
            sex=str(r.get(sexfield) or "").strip().upper()
            if sex in {"M","F"}:
                sexes_by_tag[toe].add(sex)
        if flagfield and str(r.get(flagfield) or "").strip():
            flagged+=1
        if nfield:raw_number_values.add(str(r.get(nfield) or "").strip())

    n_tags=len(dates_by_tag)
    n_spans=0
    n_gaps=0
    extra_segments=0
    longest_span=0
    same_day_codes=sum(v>1 for v in tag_day.values())
    same_day_extras=sum(max(0,n-1) for n in tag_day.values())
    for toe,dates in dates_by_tag.items():
        monthly=sorted({_month_num(d) for d in dates})
        span=monthly[-1]-monthly[0]
        longest_span=max(longest_span,span)
        if span>GAP_THRESHOLD_MONTHS:n_spans+=1
        long_gaps=sum(b-a>GAP_THRESHOLD_MONTHS for a,b in zip(monthly,monthly[1:]))
        if long_gaps:n_gaps+=1
        extra_segments+=long_gaps
    return {
        "MN_capture_records":n_mn,
        "distinct_verbatim_toe_ids":n_tags,
        "published_MN_individuals":PUBLISHED_MN_INDIVIDUALS,
        "publication_minus_raw_TOE_strings":PUBLISHED_MN_INDIVIDUALS-n_tags,
        "tags_with_observed_first_last_span_gt24_months":n_spans,
        "tags_with_capture_gap_gt24_months":n_gaps,
        "extra_segments_if_gap_gt24_months":extra_segments,
        "hypothetical_distinct_segments":n_tags+extra_segments,
        "longest_same_label_span_months":longest_span,
        "same_toe_same_date_colliding_labels":same_day_codes,
        "same_toe_same_date_extra_records":same_day_extras,
        "tags_with_both_male_and_female_records":sum(
            {"M","F"}.issubset(x) for x in sexes_by_tag.values()),
        "MN_toe_labels_also_seen_in_other_species":len(set(dates_by_tag)&n_other_toes),
        "TOE_labels_with_prefixed_series":len(has_prefix),
        "TOE_labels_with_trailing_B":len(suffix_b),
        "MN_capture_records_with_nonblank_FLAGS":flagged,
        "distinct_NUMBER_field_values":len(raw_number_values),
        "tag_identifiers_exposed_in_output":False,
        "toe_code_reuse_automatically_resolved":False,
        "MNA_effects_unopened":True,
        "spatial_W_B_or_density_slopes_opened":False,
        "caution":(
            "A 24-month gap is diagnostic only. Neither long gaps, duplicate "
            "same-day codes, sex conflicts nor published individual count "
            "justify inserting invented animal IDs. Author-corrected identity "
            "lookup or encounter matrices are required to reconcile."
        )
    }


def run() -> dict:
    meta=json.loads(_get(API).decode("utf-8"))
    if int(meta.get("id",-1)) != RECORD_ID:
        raise PublishedSourceError("Zenodo record identity changed")
    source=select_datafile(meta)
    raw=_get((source.get("links") or {}).get("self"))
    decoded=validate_source_bytes(raw,source)
    delimiter={"SEMICOLON":";","COMMA":",","TAB":"\t"}[decoded["delimiter_type"]]
    reader=csv.DictReader(io.StringIO(raw.decode(decoded["text_encoding"])),
                          delimiter=delimiter)
    rows=list(reader)
    if len(rows)!=EXPECTED_RAW_RECORDS:
        raise PublishedSourceError("published original capture count drift")
    diagnostics=identity_diagnostics(rows,decoded["column_headers"])
    if diagnostics["MN_capture_records"]!=PUBLISHED_MN_CAPTURES:
        raise PublishedSourceError("published MN capture count drift")
    files=meta.get("files",[])
    named=[
        {"name":str(f.get("key") or ""),"bytes":f.get("size"),
         "checksum":str(f.get("checksum") or "")}
        for f in files
        if any(term in str(f.get("key") or "").lower()
               for term in ("primary_secondary","rmd","rmarkdown","mosa_feb2023"))
    ]
    return {
        "schema":"neon.external_mosa_identity_discrepancy_v1",
        "status":"AUDITED_RAW_TOE_VS_PUBLISHED_INDIVIDUAL_COUNT_UNRESOLVED",
        "source":{"doi":"10.5281/zenodo.10049811","record":RECORD_ID,
                  "file":decoded["file_name"],
                  "verified_checksum":decoded["verified_checksum"],
                  "verified_bytes":decoded["verified_byte_count"],
                  "all_49216_capture_rows_verified":True},
        "diagnostics":diagnostics,
        "available_author_preprocessed_sources":named,
        "independent_MNA_spatial_analysis_GO":False,
        "must_reconcile_before_MNA":True,
        "required_next_step":(
            "Reconcile the 32-individual gap against source-author encounter "
            "matrices and original tagged-animal correction rules. Do NOT "
            "retroactively create IDs from month or date to force 19,850."
        )
    }


if __name__=="__main__":
    try:
        out=run()
    except (PublishedSourceError,RuntimeError,ValueError,OSError) as e:
        out={"schema":"neon.external_mosa_identity_discrepancy_v1",
             "status":"SOURCE_INTEGRITY_AUDIT_FAILED",
             "reason":str(e)[:500],
             "MNA_W_B_ecological_inference_opened":False}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    if out["status"]=="SOURCE_INTEGRITY_AUDIT_FAILED":
        raise SystemExit(3)
