#!/usr/bin/env python3
"""Effect-blind support for the MOSA authors' 363 exact three-night occasions.

Reuses the original Zenodo-verified 55-date deletions and correction (already
confirmed exact 1089 author days) and first-retained-species MN identities.
Excludes all normalized TOE strings with >1 verbatim author encounter form;
never treats unknown species NA as MN or disambiguates reused toe codes.

This reports only repeated captured station IDs, year coverage and suspect
>24-month identity histories. It does NOT calculate distances, centroids,
MNA abundance levels or any MNKA/MNA ~ W/B slopes.

IMPORTANT: the older preregistered MOSA conservative within-calendar-month
bout criterion is NOT retrospectively replaced by this author's calendar
structural sensitivity. Passing it does not authorize an ecological effect.
"""
from __future__ import annotations
import csv
import io
import json
from collections import Counter,defaultdict
from datetime import date,datetime
from pathlib import Path

from analysis.audit_mosa_effect_blind_structure_v1 import (
    published_field_map, parse_all_dates,
)
from analysis.audit_mosa_author_occasion_mask_v1 import (
    TIMEFILE,FROZEN_TOTAL,validated_author_days,
)
from analysis.audit_mosa_author_exact_filter_v1 import (
    PROCESSING,parse_author_filter_commands,replay_author_schedule,
    source_first_species,EXPECTED_AUTHOR_REMOVALS,
    EXPECTED_CORRECTION_ORIGINAL_DATE_INDEX,EXPECTED_CORRECTION_DATE,
)
from analysis.audit_mosa_encounter_toe_reconciliation_v1 import (
    _validated_download,author_matrix_species_tags,
)
from analysis.audit_mosa_zenodo_source_schema_v1 import (
    API,RECORD_ID,_get,select_datafile,validate_source_bytes,
    PublishedSourceError,
)

OUT=Path("build/mosa_author_verified_bout_support_v1.json")
MIN_M=5
MIN_OCCASIONS=60
MIN_YEARS=10


def _calendar_month_number(d:date)->int:
    return d.year*12+d.month


def author_bout_support(
    retained_rows:list[dict], fields:list[str],
    authored_time_rows:list[dict],author_mn:set[str],ambiguous_toe:set[str],
    *, expected_primary:int|None=363
)->dict:
    calendar=validated_author_days(
        authored_time_rows,expected_sessions=expected_primary)
    if not set(ambiguous_toe).issubset(author_mn):
        raise ValueError("whitespace-collision code outside authenticated MN roster")
    f=published_field_map(fields)
    date_primary={}
    first_dates={}
    for row in authored_time_rows:
        d=datetime.strptime(str(row["date"]),"%d/%m/%Y").date()
        p=str(row["prim_capt"])
        if d in date_primary and date_primary[d]!=p:
            raise ValueError("authored date maps to multiple primary occasions")
        date_primary[d]=p
        if p not in first_dates or d<first_dates[p]:
            first_dates[p]=d
    if len(date_primary)!=calendar["secondary_nights"]:
        raise ValueError("official author date map has duplicate nights")

    first=source_first_species(retained_rows,f["tag"],f["species"])
    predicted_mn={t for t,s in first.items() if s=="MN"}
    if predicted_mn!=author_mn:
        raise ValueError(
            "first-retained source species MN IDs not identical to author encounter roster"
        )

    by_primary=defaultdict(lambda:defaultdict(set))
    all_days=defaultdict(list)
    invalid_station=0
    n_records=0
    for row in retained_rows:
        t=str(row.get(f["tag"]) or "").strip()
        if t not in author_mn or t in ambiguous_toe:
            continue
        if str(row.get(f["species"]) or "").strip().upper()!="MN":
            # Later source record for initially-MN toe may change species;
            # never implicitly claim it is an MN biological animal.
            continue
        ds=str(row.get(f["date"]) or "").strip()
        d=datetime.strptime(ds,"%d/%m/%Y").date()
        primary=date_primary.get(d)
        if primary is None:
            raise ValueError("retained raw MN record date outside authors' time table")
        n_records+=1
        all_days[t].append(d)
        try:
            x=int(str(row.get(f["x"]) or "").strip())
            y=str(row.get(f["y"]) or "").strip().upper()
            if x<1 or x>30 or len(y)!=1 or y not in "ABCDEFGHIJ":
                invalid_station+=1
                continue
        except (ValueError,TypeError):
            invalid_station+=1
            continue
        by_primary[primary][t].add(d)

    repeat_by_primary=Counter()
    eligible=[]
    support_by_year=Counter()
    for p in first_dates:
        repeated=sum(len(days)>=2 for days in by_primary[p].values())
        repeat_by_primary[p]=repeated
        if repeated>=MIN_M:
            eligible.append(p)
            support_by_year[first_dates[p].year]+=1
    year_lengths={}
    for toe,days in all_days.items():
        duration=_calendar_month_number(max(days))-_calendar_month_number(min(days))
        year_lengths[toe]=duration
    long_tags=sum(n>24 for n in year_lengths.values())
    max_tag_span=max(year_lengths.values(),default=0)

    # This full official-month calendar is a newly reported *structural*
    # sensitivity, not a replacement for frozen exact-3-MN-capture-date
    # within-calendar-month threshold.
    structural_pass=(len(eligible)>=MIN_OCCASIONS and
                     len(support_by_year)>=MIN_YEARS)
    status=(
        "STOP_LONG_TERM_REUSED_TAG_IDENTITIES" if long_tags
        else "AUTHOR_OFFICIAL_BOUT_SUPPORT_EXISTS_NOT_ORIGINAL_CONFIRMATION"
             if structural_pass
        else "STOP_OFFICIAL_BOUT_REPEAT_YEAR_SUPPORT"
    )
    return {
        "schema":"neon.mosa_author_verified_bout_support.v1",
        "status":status,
        "official_three_night_primary_occasions":len(first_dates),
        "official_trapping_nights":calendar["secondary_nights"],
        "author_MN_tag_roster_verified":True,
        "authored_normalized_MN_TOE_count":len(author_mn),
        "ambiguous_normalized_TOE_codes_excluded":len(ambiguous_toe),
        "unique_author_MN_TOE_after_ambiguity_exclusion":
            len(author_mn-ambiguous_toe),
        "strict_per_record_species_MN_capture_rows":n_records,
        "MN_capture_rows_invalid_or_missing_lattice_station":invalid_station,
        "occasions_m_ge5":len(eligible),
        "occasions_m_ge4":sum(n>=4 for n in repeat_by_primary.values()),
        "supported_years":len(support_by_year),
        "supported_occasions_by_year":dict(sorted(support_by_year.items())),
        "tag_histories_exceed_24_months":long_tags,
        "max_observed_tag_history_months":max_tag_span,
        "satisfies_min60_bouts_and_min10_years":structural_pass,
        "year_repeated_sampling_not_independent_sites":True,
        "author_calendar_not_the_preregistered_conservative_month_cohort":True,
        "publication_19850_biological_individual_count_reconciled":False,
        "W_B_distance_or_centroids_opened":False,
        "MNA_W_B_or_density_effects_opened":False,
        "no_individual_tags_exported":True,
        "claim_boundary":"Only one MOSA grid, 29 years of unbalanced sampling. The author calendar structure alone cannot rescue the original failed NEON 6/8 genus guard or establish an ecological spatial mechanism.",
    }


def run():
    meta=json.loads(_get(API).decode("utf-8"))
    if int(meta.get("id",-1))!=RECORD_ID:
        raise PublishedSourceError("MOSA published source version changed")
    byname={str(f.get("key") or ""):f for f in meta.get("files",[])}
    if PROCESSING not in byname or TIMEFILE not in byname:
        raise PublishedSourceError("missing immutable published author dates/code")
    f=select_datafile(meta)
    raw=_validated_download(f)
    valid=validate_source_bytes(raw,f)
    sep={"SEMICOLON":";","COMMA":",","TAB":"\t"}[valid["delimiter_type"]]
    reader=csv.DictReader(io.StringIO(raw.decode(valid["text_encoding"])),delimiter=sep)
    original=list(reader)
    if len(original)!=FROZEN_TOTAL:
        raise PublishedSourceError("MOSA raw capture row count drift")
    method=_validated_download(byname[PROCESSING]).decode("utf-8-sig")
    cmds=parse_author_filter_commands(method)
    if (tuple(cmds["removed_original_unique_date_indices"])!=EXPECTED_AUTHOR_REMOVALS
        or cmds["corrected_source_date_index"]!=EXPECTED_CORRECTION_ORIGINAL_DATE_INDEX
        or cmds["corrected_to_date"]!=EXPECTED_CORRECTION_DATE):
        raise PublishedSourceError("author RMarkdown deletion code changed")
    t=_validated_download(byname[TIMEFILE])
    times=list(csv.DictReader(io.StringIO(t.decode("utf-8-sig")),delimiter=";"))
    cal=validated_author_days(times)
    authored_days=cal.pop("_author_days")
    replay=replay_author_schedule(
        original,published_field_map(valid["column_headers"])["date"],cmds,
        expected_author_days=authored_days,
    )
    matrix,files=author_matrix_species_tags(meta)
    raw_mn_forms=defaultdict(set)
    mn_tags=set()
    for sp,toe in matrix:
        if str(sp or "").strip().upper()!="MN":continue
        t=str(toe or "").strip()
        if not t:raise PublishedSourceError("blank MN identity in published author matrix")
        mn_tags.add(t)
        raw_mn_forms[t].add(str(toe))
    conflicting={toe for toe,forms in raw_mn_forms.items() if len(forms)>1}
    report=author_bout_support(
        replay["retained_rows"],valid["column_headers"],times,
        mn_tags,conflicting)
    report["source_original_MD5"]=valid["verified_checksum"]
    report["author_RMarkdown_MD5"]=byname[PROCESSING]["checksum"]
    report["author_time_MD5"]=byname[TIMEFILE]["checksum"]
    report["author_matrix_MD5s"]=[x["MD5"] for x in files]
    report["authored_calendar_exactly_reproduced"]=True
    report["event_construction_after_all_55_deletions_and_one_date_correction"]=True
    return report


if __name__=="__main__":
    try:
        result=run()
    except (PublishedSourceError,RuntimeError,ValueError,UnicodeError,OSError) as e:
        result={
            "schema":"neon.mosa_author_verified_bout_support.v1",
            "status":"STOP_MOSA_AUTHOR_VERIFIED_SOURCE_OR_IDENTITY",
            "diagnostic":str(e)[:600],
            "MNA_W_B_or_density_effects_opened":False,
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    if result["status"]!="AUTHOR_OFFICIAL_BOUT_SUPPORT_EXISTS_NOT_ORIGINAL_CONFIRMATION":
        raise SystemExit(3)
