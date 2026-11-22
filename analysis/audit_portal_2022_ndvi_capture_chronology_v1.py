#!/usr/bin/env python3
"""Original Portal capture-vs-satellite temporal ordering: source-only, no effects.

Previously opened NDVI July--September contrast cannot explain an earlier
captured-community sample. Reconstruct exactly the 114 source population
without reading rodent composition outcome or plant-count change estimates.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
import json

from analysis.portal_external_id_niche_source_v1 import (
    FILES, TRT, get_source, csv_rows, i, stake,
)
from analysis.audit_portal_resources_competition_learning_source_v1 import (
    NEW_FILES, original_extra, cohort_source_only,
    strict_survey_census, strict_plant_match,
)
from analysis.run_portal_resource_competition_holdout_ecology_v1 import (
    fixed_capture_events,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/neon_portal_2022_ndvi_capture_chronology_20261121.json"
PROTOCOL = "docs/NEON_PORTAL_NDVI_CAPTURE_CHRONOLOGY_AUDIT_20261121.md"
PHASE = "CHECK_ORIGINAL_SOURCES"

def require(condition, label):
    if not condition:
        raise ValueError("PORTAL_NDVI_CHRONOLOGY_STOP_" + label)

def phase(day):
    """The FULL July--September seasonal satellite source interval."""
    require(isinstance(day, date), "EXPECTED_ACTUAL_CALENDAR_DATE")
    if day < date(day.year,7,1):
        return "PRE_MONSOON"
    if day <= date(day.year,9,30):
        return "DURING_MONSOON"
    return "POST_MONSOON"

def original_source_chronology(source):
    global PHASE
    frozen = cohort_source_only(source)
    require(
        frozen["status"] == "SOURCE_GO_NO_RESOURCE_OR_MAMMAL_EFFECT_OPENED"
        and frozen["new_2020_2025_outcome_blind_animal_source"][
            "eligible_pairs_with_numeric_plant_source_both_years"] == 69,
        "PREVIOUS_SOURCE_GO_DRIFT",
    )
    PHASE = "EXACT_PREANIMAL_PLOT_PLANT_PAIRS"
    quads, numeric, dates, _ = strict_survey_census(source)
    treatments, _ = csv_rows(source["SiteandMethods/Portal_plots.csv"],
        ("year","month","plot","treatment","resourcetreatment","anttreatment"))
    by_treatment={}
    for record in treatments:
        key=(i(record["plot"]),i(record["year"]),i(record["month"]))
        require(key not in by_treatment, "DUPLICATE_SOURCE_TREATMENT")
        by_treatment[key]=record
    effort, _ = csv_rows(source["Rodents/Portal_rodent_trapping.csv"],
        ("year","month","day","plot","period","sampled","qcflag","effort"))
    source_sessions, candidate = fixed_capture_events(source,by_treatment,effort)
    matched=[]
    for a,b in candidate:
        pa=strict_plant_match((a[0],a[1],a[2],source_sessions[a]["day"]),
                              quads,numeric,dates)
        pb=strict_plant_match((b[0],b[1],b[2],source_sessions[b]["day"]),
                              quads,numeric,dates)
        if pa and pb:
            require(pa["source_plant_key"] != pb["source_plant_key"],
                    "DUPLICATED_FIELD_PLANT_SURVEY")
            matched.append((a,b,pa,pb))
    require(len(candidate)==453 and len(matched)==203,
            "ORIGINAL_453_203_SOURCE_PAIRS_NOT_RECONSTRUCTED")
    PHASE = "ORIGINAL_ANIMAL_ID_ELIGIBILITY_WITHOUT_COMPOSITION"
    taxa,_=csv_rows(source["Rodents/Portal_rodent_species.csv"],
        ("speciescode","rodent","granivore","censustarget","unidentified"))
    eligible_codes={z["speciescode"].strip() for z in taxa
        if z["rodent"]=="1" and z["granivore"]=="1"
        and z["censustarget"]=="1" and z["unidentified"]=="0"}
    needed={e for a,b,_,_ in matched for e in (a,b)}
    obs=defaultdict(lambda:defaultdict(set))
    records,_=csv_rows(source["Rodents/Portal_rodent.csv"],
        ("year","month","plot","period","stake","species","id"))
    for rec in records:
        y=i(rec["year"])
        if y is None or y<2020 or y>2025:continue
        event=(i(rec["plot"]),y,i(rec["month"]),i(rec["period"]))
        if event not in needed:continue
        sp=(rec["species"] or "").strip()
        tag=(rec["id"] or "").strip()
        if sp not in eligible_codes or not tag or tag.lower() in ("na","nan","null"):
            continue
        if stake(rec["stake"]) is None:
            continue
        obs[event][tag].add(sp)
    counts={
        event:sum(1 for taxons in obs[event].values() if len(taxons)==1)
        for event in needed
    }
    PHASE="SOURCE_DATE_CHRONOLOGY_NO_BEHAVIORAL_RESPONSE"
    entries=[]
    for a,b,pa,pb in matched:
        if min(counts[a],counts[b])<5:
            continue
        day_a=date(a[1],a[2],source_sessions[a]["day"])
        day_b=date(b[1],b[2],source_sessions[b]["day"])
        require(day_b.year==day_a.year+1 and day_b.month==day_a.month,
                "ADJACENT_YEAR_SAME_MONTH_DRIFT")
        require(source_sessions[a]["treatment"] == source_sessions[b]["treatment"],
                "TREATMENT_CHANGE")
        entries.append({
            "start_year":a[1], "plot":a[0], "month":a[2],
            "treatment":source_sessions[a]["treatment"],
            "baseline_phase":phase(day_a), "followup_phase":phase(day_b),
            "plant_season_A":pa["source_plant_key"][1],
            "plant_season_B":pb["source_plant_key"][1],
        })
    require(
        len(entries)==114 and len({x["plot"] for x in entries})==18
        and sum(x["start_year"]==2022 for x in entries)==65,
        "FROZEN_114_18_65_EFFECT_SOURCE_COHORT_DRIFT",
    )
    return entries

def summary_from_entries(entries):
    require(len(entries)==114, "ORIGINAL_114_ENTRIES_REQUIRED")
    phases=("PRE_MONSOON","DURING_MONSOON","POST_MONSOON")
    per_start={}
    for y in (2021,2022,2023):
        sub=[u for u in entries if u["start_year"]==y]
        per_start[str(y)]={
            "pair_count":len(sub),
            "distinct_original_plot_clusters":len({u["plot"] for u in sub}),
            "followup_capture_month_counts":{
                str(m):sum(u["month"]==m for u in sub)
                for m in sorted({u["month"] for u in sub})},
            "followup_phase_counts":{p:sum(u["followup_phase"]==p for u in sub)
                                     for p in phases},
        }
    focus=[u for u in entries if u["start_year"]==2022]
    require(len(focus)==65,"2022_SOURCE_PAIR_COUNT")
    by_phase={
        p:{
            "matched_pairs":sum(u["followup_phase"]==p for u in focus),
            "original_plot_clusters":len({u["plot"] for u in focus
                                          if u["followup_phase"]==p})
        } for p in phases
    }
    baseline={p:sum(u["baseline_phase"]==p for u in focus) for p in phases}
    prior_both=sum(u["baseline_phase"]=="POST_MONSOON"
                   and u["followup_phase"]=="POST_MONSOON" for u in focus)
    plant_pairs=dict(Counter(
        u["plant_season_A"]+"__"+u["plant_season_B"] for u in focus))
    return {
        "schema":"neon.portal_postresult_ndvi_capture_order_source.v1",
        "status":"ORIGINAL_114_COHORT_SOURCE_CHRONOLOGY_NOT_CAUSAL_ANALYSIS",
        "source_original_portal_data":{
            "repository":"weecology/PortalData",
            "git_commit":"afd75933249ae60f3a5e9dab00b354f219e5e045",
            "eight_original_git_blobs_sha_verified":True,
            "previous_203_plant_time_source_universe_preserved":True,
            "previous_69_identity_disjoint_species_source_only_reverified":True,
            "original_114_plot_level_capture_composition_cohort_reconstructed_with_ID_counts_only":True,
            "no_capture_species_proportions_or_plant_count_totals_calculated":True,
        },
        "all_original_years":per_start,
        "2022_to_2023_specific_chronology":{
            "total_matched_pairs":len(focus),
            "followup_2023_capture_phase_counts":by_phase,
            "baseline_2022_capture_phase_counts":baseline,
            "both_2022_and_2023_captures_post_september_30":prior_both,
            "both_year_census_plant_survey_seasons":plant_pairs,
            "followup_2023_occurs_before_entire_July_September_NDVI_window":
                by_phase["PRE_MONSOON"]["matched_pairs"],
            "followup_2023_occurs_within_entire_July_September_NDVI_window":
                by_phase["DURING_MONSOON"]["matched_pairs"],
            "followup_2023_occurs_after_entire_July_September_NDVI_window":
                by_phase["POST_MONSOON"]["matched_pairs"],
            "causal_ordering_is_necessary_but_never_sufficient":True,
        },
        "limits":{
            "this_is_source_metadata_timing_not_new_mammal_ecological_effect":True,
            "any_post_or_during_period_cannot_identify_plot_resource_mechanism":True,
            "original_NDVI_2023_window_used_full_July_August_September":True,
            "satellite_NDVI_one_1km_site_area_not_plot_level":True,
            "no_plant_biomass_seed_energetics_or_learning_measured":True,
            "postresult_chronology_diagnostic_not_independent_validation":True,
            "all_original_model_coefficients_and_NDVI_source_effects_unchanged":True,
            "NEON_unified_draft_submission_HOLD":True,
        },
        "protocol":PROTOCOL,
        "retrieved_utc":datetime.now(timezone.utc).isoformat(),
    }

def run():
    original={p:get_source(p) for p in FILES}
    for path in NEW_FILES:
        original[path]=original_extra(path)
    return summary_from_entries(original_source_chronology(original))

def main():
    global PHASE
    try:
        outcome,code=run(),0
    except Exception as exc:
        outcome,code={
            "schema":"neon.portal_postresult_ndvi_capture_order_source.v1",
            "status":"STOP_ORIGINAL_114_COHORT_OR_SOURCE_CHRONOLOGY",
            "stage":PHASE,
            "error_type":type(exc).__name__,
            "error_label":str(exc)[:160],
            "no_old_or_new_biological_response_calculated":True
        },3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(outcome,sort_keys=True,indent=2)+"\n")
    print(json.dumps(outcome,sort_keys=True,indent=2))
    return code

if __name__=="__main__":
    raise SystemExit(main())
