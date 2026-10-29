#!/usr/bin/env python3
"""Frozen MOSA conservative three-MN-capture-day calendar MNA SUPPORT.

This is the pre-effect contract's strict in-calendar-month 3 consecutive
VALID-STATION MN capture-day cohort, not the 261 authors-calendar bouts
sensitivity. It applies that rule to the exactly reconstructed 2023 authors'
55 date deletions, 1 date correction, first-retained-species MN identity
roster and exclusion of 14 whitespace-colliding TOE codes.

MNA is first/last observed MONTH for each author-first-MN code, among all
author-retained capture rows of species MN. MNA is abundance index, not true
density, and MUST NOT be joined to any spatial response before frozen
structural, metric and year-level support gates pass.

No W/B, spatial distances, centroids, ecological effects or tagged identities
are exported. If published roster identities are unclear, fail closed.
"""
from __future__ import annotations

import csv
import io
import json
from collections import Counter,defaultdict
from datetime import timedelta
from pathlib import Path

from analysis.audit_mosa_author_exact_filter_v1 import (
    PROCESSING, EXPECTED_AUTHOR_REMOVALS,
    EXPECTED_CORRECTION_ORIGINAL_DATE_INDEX, EXPECTED_CORRECTION_DATE,
    parse_author_filter_commands,replay_author_schedule,source_first_species,
)
from analysis.audit_mosa_author_occasion_mask_v1 import (
    TIMEFILE,FROZEN_TOTAL,validated_author_days,
)
from analysis.audit_mosa_effect_blind_structure_v1 import (
    published_field_map,parse_all_dates,
)
from analysis.audit_mosa_encounter_toe_reconciliation_v1 import (
    _validated_download,author_matrix_species_tags,
)
from analysis.audit_mosa_zenodo_source_schema_v1 import (
    API,RECORD_ID,_get,select_datafile,validate_source_bytes,
    PublishedSourceError,
)

OUT=Path("build/mosa_conservative_mna_support_v1.json")
PREDICTORS=Path("build/mosa_conservative_mna_predictor_only_v1.json")
MIN_M=5
MAX_TAG_SPAN_MONTHS=24
ORIGINAL_MIN_MONTHS=60
ORIGINAL_MIN_YEARS=10


def conservative_month_mna_structure(
    retained_rows:list[dict],fields:list[str],
    author_mn:set[str],ambiguous_toe:set[str],
    *,require_months:int=ORIGINAL_MIN_MONTHS,
    require_years:int=ORIGINAL_MIN_YEARS,
)->tuple[dict,list[dict]]:
    f=published_field_map(fields)
    if not author_mn:
        raise ValueError("empty author-verified MN identity roster")
    if not set(ambiguous_toe).issubset(author_mn):
        raise ValueError("collision ID outside author MN roster")
    all_dates=parse_all_dates(
        [str(r.get(f["date"]) or "").strip() for r in retained_rows])
    by_valid_month=defaultdict(list)
    # MNA must count species-confirmed authored captures independently from
    # the presence of usable trap station coordinates.
    history=defaultdict(set)
    observed_months=defaultdict(set)
    excluded_bad_position=0
    n_selected_rows=0
    for r in retained_rows:
        sp=str(r.get(f["species"]) or "").strip().upper()
        if sp!="MN":
            continue
        tag=str(r.get(f["tag"]) or "").strip()
        if tag not in author_mn or tag in ambiguous_toe:
            continue
        day=all_dates[str(r.get(f["date"]) or "").strip()]
        mon=(day.year,day.month)
        history[tag].add(mon)
        observed_months[mon].add(tag)
        n_selected_rows+=1
        try:
            xi=int(str(r.get(f["x"]) or "").strip())
            yi=str(r.get(f["y"]) or "").strip().upper()
            if not (1<=xi<=30 and len(yi)==1 and yi in "ABCDEFGHIJ"):
                excluded_bad_position+=1
                continue
        except (ValueError,TypeError):
            excluded_bad_position+=1
            continue
        by_valid_month[mon].append((day,tag))

    if not history:
        raise RuntimeError("no author-confirmed raw MN tagged histories")
    spans={}
    bounds={}
    for tag,months in history.items():
        lo=min(months);hi=max(months)
        a=lo[0]*12+lo[1];b=hi[0]*12+hi[1]
        spans[tag]=b-a
        bounds[tag]=(a,b)
    long=sum(v>MAX_TAG_SPAN_MONTHS for v in spans.values())

    strict=[]
    count_3=0
    for (year,month),values in sorted(by_valid_month.items()):
        days=sorted({day for day,tag in values})
        if (len(days)!=3 or
            days[1]!=days[0]+timedelta(days=1) or
            days[2]!=days[1]+timedelta(days=1)):
            continue
        count_3+=1
        tagged=defaultdict(set)
        for day,tag in values:
            tagged[tag].add(day)
        m=sum(len(ds)>=2 for ds in tagged.values())
        if m<MIN_M:
            continue
        monidx=year*12+month
        mna=sum(a<=monidx<=b for a,b in bounds.values())
        captured=len(observed_months[(year,month)])
        if mna<captured:
            raise RuntimeError("author-source MNA under observed author-MN captures")
        strict.append({
            "year":year,"month":month,
            "year_month":f"{year:04d}-{month:02d}",
            "MNA":mna,
            "m":m,
            "observed_unique_tag_codes":captured,
            "capture_nights_with_valid_MN_stations":len(days),
        })

    by_year=defaultdict(list)
    for s in strict:by_year[s["year"]].append(s["MNA"])
    varying={year:values for year,values in by_year.items()
             if len(values)>=2 and len(set(values))>=2}
    usable=sum(len(values) for values in varying.values())
    first_n=len(author_mn)-len(ambiguous_toe)
    sufficient=(len(strict)>=require_months and
                len(varying)>=require_years and
                usable>=require_months)
    status=("STOP_LONG_TAG_REUSE_FROZEN_MNA" if long
            else "GO_FROZEN_CONSERVATIVE_MNA_SUPPORT_ONLY" if sufficient
            else "STOP_FROZEN_CONSERVATIVE_MNA_SUPPORT")
    report={
        "schema":"neon.mosa.frozen_conservative_MNA_support.v1",
        "status":status,
        "author_first_species_MN_roster_accepted":len(author_mn),
        "ambiguous_normalized_TOE_codes_excluded":len(ambiguous_toe),
        "noncolliding_author_first_MN_tag_codes":first_n,
        "source_species_MN_rows_kept_after_author_filter":n_selected_rows,
        "species_MN_rows_without_valid_lattice_position":excluded_bad_position,
        "strict_three_night_months":count_3,
        "eligible_original_conservative_months":len(strict),
        "original_min_eligible_months":require_months,
        "years_with_any_eligible_month":len(by_year),
        "years_with_ge2_distinct_MNA_levels":len(varying),
        "original_min_varying_years":require_years,
        "eligible_months_inside_MNA_varying_years":usable,
        "eligible_months_by_year":dict(sorted(Counter(s["year"] for s in strict).items())),
        "tag_histories_exceed_24_months":long,
        "longest_tag_history_months":max(spans.values(),default=0),
        "MNA_on_eligible_months":{
            "min":min((s["MNA"] for s in strict),default=None),
            "max":max((s["MNA"] for s in strict),default=None),
            "distinct_levels":len({s["MNA"] for s in strict}),
        },
        "author_363_primary_bouts_not_substituted":True,
        "MNA_interpolation_uses_full_author_retened_MN_history":True,
        "source_19850_biological_MN_individual_claim_reconciled":False,
        "no_tag_values_written_to_artifacts":True,
        "W_B_or_centroids_opened":False,
        "MNA_W_B_or_density_effects_opened":False,
        "scope":"One Tanzanian grid, conditional association only; do not reclassify original eight-genus NEON generality FAIL.",
    }
    return report,strict


def run()->tuple[dict,list[dict]]:
    meta=json.loads(_get(API).decode("utf-8"))
    if int(meta.get("id",-1))!=RECORD_ID:
        raise PublishedSourceError("MOSA Zenodo original version drift")
    files={str(z.get("key") or ""):z for z in meta["files"]}
    if TIMEFILE not in files or PROCESSING not in files:
        raise PublishedSourceError("missing author occasion and RMarkdown")
    rawfile=select_datafile(meta)
    raw=_validated_download(rawfile)
    validate=validate_source_bytes(raw,rawfile)
    sep={"SEMICOLON":";","TAB":"\t","COMMA":","}[validate["delimiter_type"]]
    reader=csv.DictReader(io.StringIO(raw.decode(validate["text_encoding"])),delimiter=sep)
    source=list(reader)
    if len(source)!=FROZEN_TOTAL:
        raise PublishedSourceError("raw original 49216-capture source drift")
    rmd=_validated_download(files[PROCESSING]).decode("utf-8-sig",errors="strict")
    commands=parse_author_filter_commands(rmd)
    if (tuple(commands["removed_original_unique_date_indices"])!=EXPECTED_AUTHOR_REMOVALS
        or commands["corrected_source_date_index"]!=EXPECTED_CORRECTION_ORIGINAL_DATE_INDEX
        or commands["corrected_to_date"]!=EXPECTED_CORRECTION_DATE):
        raise PublishedSourceError("author date commands drifted")
    times=list(csv.DictReader(
        io.StringIO(_validated_download(files[TIMEFILE]).decode("utf-8-sig")),
        delimiter=";"))
    author=validated_author_days(times)
    actual=author.pop("_author_days")
    f=published_field_map(validate["column_headers"])
    retained=replay_author_schedule(
        source,f["date"],commands,expected_author_days=actual)["retained_rows"]
    matrix,matrix_meta=author_matrix_species_tags(meta)
    first=source_first_species(retained,f["tag"],f["species"])
    author_mn={str(toe or "").strip() for sp,toe in matrix
               if str(sp or "").strip().upper()=="MN" and str(toe or "").strip()}
    if {k for k,v in first.items() if v=="MN"}!=author_mn:
        raise PublishedSourceError("source first-MN identity ≠ authors published MN roster")
    by_normalized=defaultdict(set)
    for sp,toe in matrix:
        if str(sp or "").strip().upper()!="MN":continue
        t=str(toe or "").strip()
        by_normalized[t].add(str(toe))
    collision={tag for tag,forms in by_normalized.items() if len(forms)>1}
    if len(collision)!=14:
        raise PublishedSourceError("frozen 14 author whitespace TOEs changed")

    result,predictor=conservative_month_mna_structure(
        retained,validate["column_headers"],author_mn,collision)
    result["published_original_MD5"]=validate["verified_checksum"]
    result["published_authors_processing_Rmd_MD5"]=files[PROCESSING]["checksum"]
    result["published_author_time_MD5"]=files[TIMEFILE]["checksum"]
    result["published_encounter_matrix_MD5s"]=[v["MD5"] for v in matrix_meta]
    result["authored_363_three_night_date_mask_reproduced"]=True
    result["author_first_species_roster_exactly_reproduced"]=True
    result["initial_pre_effect_contract"]="results/mosa_one_species_spatial_allocation_pre_effect_contract_v1.json"
    return result,predictor


if __name__=="__main__":
    try:
        r,rows=run()
    except (PublishedSourceError,RuntimeError,ValueError,UnicodeError,OSError) as exc:
        r={"schema":"neon.mosa.frozen_conservative_MNA_support.v1",
           "status":"STOP_SOURCE_IDENTITY_OR_MNA_SUPPORT",
           "diagnostic":str(exc)[:700],
           "MNA_W_B_or_density_effects_opened":False}
        rows=[]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if rows and r["status"]=="GO_FROZEN_CONSERVATIVE_MNA_SUPPORT_ONLY":
        PREDICTORS.write_text(json.dumps(rows,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(r,indent=2,sort_keys=True))
    if r["status"]!="GO_FROZEN_CONSERVATIVE_MNA_SUPPORT_ONLY":
        raise SystemExit(3)
