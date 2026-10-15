#!/usr/bin/env python3
"""MOSA effect-blind same-night station and identity-conflict summary.

Pure function accepts author-retained, first-MN verified records. It does not
compute spatial distances, centroids, W/B, MNA, or any ecological effect.
"""
from collections import defaultdict, Counter
from datetime import datetime

def audit_identity_conflicts(rows, fields, author_mn, excluded_codes, eligible_months):
    from analysis.audit_mosa_effect_blind_structure_v1 import published_field_map
    f=published_field_map(fields)
    if not set(excluded_codes).issubset(author_mn):
        raise ValueError("Excluded IDs outside verified roster")
    eligible=set(eligible_months)  # YYYY-MM strings, frozen independently
    by_tag_day=defaultdict(lambda:{"stations":set(),"species":set(),"sex":set(),"records":0})
    by_tag_month=defaultdict(set)
    by_tag_species=defaultdict(set)
    by_tag_sex=defaultdict(set)
    invalid_station=0
    for r in rows:
        tag=str(r.get(f["tag"]) or "").strip()
        if tag not in author_mn or tag in excluded_codes: continue
        d=datetime.strptime(str(r[f["date"]]).strip(),"%d/%m/%Y").date()
        month=d.strftime("%Y-%m")
        sp=str(r.get(f["species"]) or "").strip().upper()
        sex=str(r.get("SEX") or "").strip().upper()
        if sp and sp not in {"NA","N/A","UNKNOWN"}: by_tag_species[tag].add(sp)
        if sex and sex not in {"NA","N/A","UNKNOWN","U","?"}: by_tag_sex[tag].add(sex)
        if month not in eligible: continue
        if sp!="MN":continue
        try:
            x=int(str(r.get(f["x"]) or "").strip())
            y=str(r.get(f["y"]) or "").strip().upper()
            if not(1<=x<=30 and len(y)==1 and y in "ABCDEFGHIJ"):raise ValueError()
        except (ValueError,TypeError):
            invalid_station+=1;continue
        z=by_tag_day[(tag,d)]
        z["stations"].add((x,y));z["records"]+=1
        z["species"].add(sp)
        if sex:z["sex"].add(sex)
        by_tag_month[(tag,month)].add(d)
    conflicting_days={k for k,v in by_tag_day.items() if len(v["stations"])>1}
    duplicate_same_station_days={k for k,v in by_tag_day.items()
                                 if v["records"]>1 and len(v["stations"])==1}
    repeat_codes_by_month=defaultdict(set)
    for (tag,month),days in by_tag_month.items():
        if len(days)>=2:repeat_codes_by_month[month].add(tag)
    conflicting_tags={t for t,d in conflicting_days}
    species_tags={t for t,v in by_tag_species.items() if len(v)>1}
    sex_tags={t for t,v in by_tag_sex.items() if len(v)>1}
    suspect=conflicting_tags|species_tags|sex_tags
    affected={m for m,tags in repeat_codes_by_month.items() if tags&suspect}
    return {
        "schema":"neon.mosa.effect_blind_identity_conflict_summary.v1",
        "author_first_MN_codes":len(author_mn),
        "excluded_collision_codes":len(excluded_codes),
        "noncolliding_codes":len(author_mn-excluded_codes),
        "frozen_eligible_months":len(eligible),
        "distinct_valid_tag_dates":len(by_tag_day),
        "same_day_multiple_station_keys":len(conflicting_days),
        "same_day_duplicate_same_station_keys":len(duplicate_same_station_days),
        "cross_species_code_count":len(species_tags),
        "cross_sex_code_count":len(sex_tags),
        "union_suspect_code_count":len(suspect),
        "months_with_repeat_supported_suspect_codes":len(affected),
        "years_with_repeat_supported_suspect_codes":len({m[:4] for m in affected}),
        "repeat_supported_months_scored":len(repeat_codes_by_month),
        "invalid_station_rows":invalid_station,
        "potential_affected_months_upper_bound_only":True,
        "conflict_proves_two_animals":False,
        "identity_proven":False,
        "ecological_effects_opened":False,
        "decision":"HOLD_PENDING_REAL_SOURCE_RUN_AND_AUTHOR_CLARIFICATION",
    }
