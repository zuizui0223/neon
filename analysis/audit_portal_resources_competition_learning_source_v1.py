#!/usr/bin/env python3
"""Portal 2020-25 independent-time resource and competitor SOURCE audit.

NO live animal species composition outcomes, spatial recurrence, plant abundance
values, treatment-effect estimates, or memory/learning coefficient are computed.
Requires immutable original source Git blob SHA validation. Existing Portal
1996-2019 ecological responses are never recomputed.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from hashlib import sha1
from io import StringIO
from math import isfinite
from pathlib import Path
from urllib.request import Request, urlopen
import csv
import json

from analysis.portal_external_id_niche_source_v1 import (
    SOURCE_COMMIT, FILES, TRT, audit, csv_rows, get_source, i, stake
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/neon_portal_2020_2025_three_mechanism_source_v1.json"
PROTOCOL = "docs/NEON_RESOURCE_COMPETITION_LEARNING_DISCRIMINATION_20261120.md"
NEW_FILES = {
    "Plants/Portal_plant_quadrats.csv": (
        "82b296aceb964f64864e979a34a0c7bc455a87f8", 100_000_000
    ),
    "Plants/Portal_plant_census_dates.csv": (
        "2ab18f4f9e603da3e8c0b472d24c8a4d5caa8ef8", 30_000
    ),
}
YR_START, YR_END = 2020, 2025
OBS_MIN = 5
STATIONS_MIN = 3
MIN_QUADRATS = 12
MAX_PRIOR_DAYS = 90
FROZEN_PREANIMAL_PAIR_COUNT = 203
FROZEN_PREANIMAL_PAIR_CONTROL = 113
FROZEN_PREANIMAL_PAIR_EXCLOSURE = 90
MIN_PAIRS = 30
MIN_PLOTS = 8
MIN_PLOTS_TREATMENT = 4
MIN_START_YEARS = 3
MIN_TAXA = 2
PHASE = "PINNED_ORIGINAL_SOURCE"

def require(value, reason):
    if not value:
        raise ValueError("PORTAL_3MECH_SOURCE_STOP_" + reason)

def original_extra(path):
    expected, max_bytes = NEW_FILES[path]
    raw_url = ("https://raw.githubusercontent.com/weecology/PortalData/"
               + SOURCE_COMMIT + "/" + path)
    with urlopen(Request(raw_url, headers={"User-Agent":"NEON-Portal-source/2"}),
                 timeout=90) as fh:
        raw = fh.read(max_bytes + 1)
    require(0 < len(raw) <= max_bytes, "EXTRA_SOURCE_SIZE_OR_EMPTY")
    actual = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    require(actual == expected, "EXTRA_SOURCE_BLOB_HASH")
    return raw

def survey_day(year, month, day):
    y, m, d = i(year), i(month), i(day)
    if y is None or m is None or d is None:
        return None
    try:
        return date(y, m, d)
    except ValueError:
        return None

def strict_survey_census(sources):
    """Record source validity only; never plant abundance totals."""
    dates, _ = csv_rows(
        sources["Plants/Portal_plant_census_dates.csv"],
        ("year","season","censusdone","start_month","start_day","end_month","end_day")
    )
    source_cens, _ = csv_rows(
        sources["Plants/Portal_plant_censuses.csv"],
        ("year","season","plot","quadrat","censused","area")
    )
    numeric_quads = defaultdict(set)
    plant_rows, _ = csv_rows(
        sources["Plants/Portal_plant_quadrats.csv"],
        ("year","season","plot","quadrat","species","abundance","cover","cf","notes")
    )
    quad_census = defaultdict(set)
    census_rows = 0
    for row in source_cens:
        y, p, q = i(row["year"]), i(row["plot"]), i(row["quadrat"])
        if y is None or p is None or q is None or not YR_START <= y <= YR_END:
            continue
        if row["censused"] != "1":
            continue
        try:
            area = float(row["area"])
        except (TypeError, ValueError):
            continue
        require(area == .25, "QUADRAT_AREA_DRIFT")
        quad_census[(y, row["season"].strip().lower(), p)].add(q)
        census_rows += 1
    numeric_source_rows = 0
    nonnumeric_source_rows = 0
    all_plant_source_rows = 0
    for row in plant_rows:
        y, p, q = i(row["year"]), i(row["plot"]), i(row["quadrat"])
        if y is None or p is None or q is None or not YR_START <= y <= YR_END:
            continue
        all_plant_source_rows += 1
        ab = (row["abundance"] or "").strip()
        if not ab:
            nonnumeric_source_rows += 1
            continue
        try:
            f = float(ab)
            good = isfinite(f) and f >= 0
        except (ValueError, TypeError):
            good = False
        if good:
            numeric_quads[(y, row["season"].strip().lower(), p)].add(q)
            numeric_source_rows += 1
        else:
            nonnumeric_source_rows += 1
    source_dates = []
    all_rows = 0
    for row in dates:
        all_rows += 1
        y = i(row["year"])
        if y is None or not YR_START <= y <= YR_END:
            continue
        if (row["censusdone"] or "").strip().lower() != "yes":
            continue
        day = survey_day(y, row["end_month"], row["end_day"])
        if day is None:
            continue
        source_dates.append((y, row["season"].strip().lower(), day))
    return quad_census, numeric_quads, source_dates, {
        "original_census_metadata_rows": all_rows,
        "original_plants_surveyed_quadrat_rows_2020_25": census_rows,
        "original_plant_quadrat_species_rows_2020_25": all_plant_source_rows,
        "original_numeric_plant_abundance_rows_2020_25": numeric_source_rows,
        "original_plant_abundance_nonnumeric_or_missing_rows_2020_25":
            nonnumeric_source_rows,
        "distinct_dated_completed_original_plant_seasons": len(source_dates),
        "no_plant_counts_cover_or_biomass_summed": True,
    }

def strict_plant_match(session, quad_census, numeric_quads, dates):
    plot, year, month, day = session[:4]
    capture_day = survey_day(year, month, day)
    if capture_day is None:
        return None
    matched = []
    for y, season, survey_end in dates:
        if y != year:
            continue
        lag = (capture_day - survey_end).days
        if lag < 0 or lag > MAX_PRIOR_DAYS:
            continue
        name = (y, season, plot)
        if len(quad_census.get(name, set())) < MIN_QUADRATS:
            continue
        matched.append((lag, season, name))
    if not matched:
        return None
    matched.sort(key=lambda x:(x[0], x[1]))
    key = matched[0][2]
    return {
        "source_plant_key": key,
        "numeric_plant_abundance_source_present": bool(
            numeric_quads.get(key, set())
        ),
        "source_lag_days": matched[0][0],
    }

def cohort_source_only(source):
    global PHASE
    PHASE = "VERIFY_HISTORICAL_SCHEMA_AND_SOURCE_ONLY_CONTINUITY"
    old = {p:source[p] for p in FILES}
    old_summary = audit(old)
    old_counts = old_summary.get("source_only_summary", {}).get(
        "source_pair_counts", {})
    require(old_summary.get("status") ==
            "SOURCE_PORTAL_DISJOINT_ID_STAKE_GO_NO_NICHE_EFFECT"
            and old_counts.get("qualified_different_observed_ID_species_pairs") ==
            436, "OLD_436_SOURCE_COHORT_DRIFT")
    PHASE = "2020_2025_EFFORT_TREATMENT_AND_PLANT_SOURCE"
    quad, numeric, dates, plant_support = strict_survey_census(source)
    taxa, _ = csv_rows(source["Rodents/Portal_rodent_species.csv"],
        ("speciescode","rodent","granivore","censustarget","unidentified"))
    target = {r["speciescode"].strip() for r in taxa
            if r["rodent"]=="1" and r["granivore"]=="1" and
            r["censustarget"]=="1" and r["unidentified"]=="0"}
    treatments, _ = csv_rows(source["SiteandMethods/Portal_plots.csv"],
        ("year","month","plot","treatment","resourcetreatment","anttreatment"))
    treatment = {}
    for row in treatments:
        key=(i(row["plot"]),i(row["year"]),i(row["month"]))
        require(key not in treatment,"DUPLICATED_PLOT_TREATMENT_SOURCE")
        treatment[key]=row
    sessions, bytime = {}, defaultdict(list)
    effort, _ = csv_rows(source["Rodents/Portal_rodent_trapping.csv"],
        ("day","year","month","period","plot","sampled","effort","qcflag"))
    for row in effort:
        y, m, p, period, day = (i(row[c]) for c in
                               ("year","month","plot","period","day"))
        if None in (y,m,p,period,day) or not YR_START <= y <= YR_END:
            continue
        if period <= 0 or row["sampled"]!="1" or row["qcflag"]!="1" or (
                i(row["effort"]) not in (48,49)):
            continue
        meta=treatment.get((p,y,m))
        if not meta or meta["treatment"] not in TRT:
            continue
        key=(p,y,m,period)
        require(key not in sessions, "DUPLICATED_PLOT_SOURCE_SESSION")
        sessions[key] = {
            "day":day, "treatment":meta["treatment"],
            "resource_treatment":meta["resourcetreatment"],
            "ant_treatment":meta["anttreatment"],
        }
        bytime[(p,y,m)].append(key)
    base_pairs = []
    for plot,y,m in sorted(bytime):
        if y >= YR_END:
            continue
        AA,BB=bytime[(plot,y,m)],bytime.get((plot,y+1,m),[])
        if len(AA)!=1 or len(BB)!=1:
            continue
        a,b=AA[0],BB[0]
        if sessions[a]["treatment"]!=sessions[b]["treatment"]:
            continue
        base_pairs.append((a,b))
    plant_pairs = []
    for a,b in base_pairs:
        sa = strict_plant_match(
            (a[0],a[1],a[2],sessions[a]["day"]),quad,numeric,dates
        )
        sb = strict_plant_match(
            (b[0],b[1],b[2],sessions[b]["day"]),quad,numeric,dates
        )
        if sa and sb:
            require(sa["source_plant_key"]!=sb["source_plant_key"],
                    "SAME_PLANT_CENSUS_REUSED_ACROSS_YEARS")
            plant_pairs.append((a,b,sa,sb))
    pair_trt=Counter(sessions[a]["treatment"] for a,b,_,_ in plant_pairs)
    require(len(base_pairs)==453 and len(sessions)==860
            and len(plant_pairs)==FROZEN_PREANIMAL_PAIR_COUNT
            and pair_trt["control"]==FROZEN_PREANIMAL_PAIR_CONTROL
            and pair_trt["exclosure"]==FROZEN_PREANIMAL_PAIR_EXCLOSURE,
            "FROZEN_2020_25_PLOT_PLANT_DATE_SOURCE_DRIFT")
    PHASE = "FROZEN_2020_2025_ID_SOURCE_ELIGIBILITY"
    needed=set()
    for a,b,_,_ in plant_pairs:
        needed.update((a,b))
    source_locations=defaultdict(lambda:defaultdict(lambda:defaultdict(set)))
    by_code=defaultdict(set)
    raw_rodents, _ = csv_rows(source["Rodents/Portal_rodent.csv"],
        ("plot","year","month","period","stake","species","id"))
    row_counts=Counter()
    for row in raw_rodents:
        yy=i(row["year"])
        if yy is None or yy<YR_START or yy>YR_END:
            continue
        event=(i(row["plot"]), yy, i(row["month"]), i(row["period"]))
        if event not in needed:
            continue
        code=(row["species"] or "").strip()
        animal=(row["id"] or "").strip()
        loc=stake(row["stake"])
        row_counts["original_2020_25_rows_at_matched_source_events"]+=1
        if code not in target or not animal or animal.lower() in (
                "na","nan","null") or loc is None:
            row_counts["rows_not_valid_identified_target_stake_ID"]+=1
            continue
        source_locations[event][code][animal].add(loc)
        by_code[(event,animal)].add(code)
        row_counts["source_valid_recorded_stake_ID_taxon"]+=1
    disjoint_qual=[]
    conflicting_in_single=0
    conflicting_taxon=0
    for a,b,pa,pb in plant_pairs:
        ta=sessions[a]["treatment"]
        for code in sorted(set(source_locations[a])&set(source_locations[b])):
            items=[]
            for ev in (a,b):
                vals={}
                for tag,positions in source_locations[ev][code].items():
                    if len(positions)!=1:
                        conflicting_in_single+=1
                        continue
                    if len(by_code[(ev,tag)])!=1:
                        conflicting_taxon+=1
                        continue
                    vals[tag]=next(iter(positions))
                items.append(vals)
            aa,bb=items
            common=set(aa)&set(bb)
            aa={tag:loc for tag,loc in aa.items() if tag not in common}
            bb={tag:loc for tag,loc in bb.items() if tag not in common}
            if min(len(aa),len(bb))<OBS_MIN or min(
                    len(set(aa.values())),len(set(bb.values())))<STATIONS_MIN:
                continue
            disjoint_qual.append({
                "plot":a[0], "start_year":a[1], "code":code,
                "treatment":ta, "plant_numeric_both":(
                    pa["numeric_plant_abundance_source_present"] and
                    pb["numeric_plant_abundance_source_present"]),
            })
    have_plant=[p for p in disjoint_qual if p["plant_numeric_both"]]
    distinct_plots={p["plot"] for p in have_plant}
    plots_by_trt={t:{p["plot"] for p in have_plant if p["treatment"]==t}
                  for t in TRT}
    trt_count=Counter(p["treatment"] for p in have_plant)
    years={p["start_year"] for p in have_plant}
    species={p["code"] for p in have_plant}
    checks={
        "frozen_203_original_plot_plant_pairs":len(plant_pairs)==203,
        "animal_ID_disjoint_eligible_species_pairs_ge30":
            len(have_plant)>=MIN_PAIRS,
        "at_least_8_distinct_physical_plots":len(distinct_plots)>=MIN_PLOTS,
        "at_least_4_physical_plots_in_both_treatments":
            all(len(plots_by_trt[t])>=MIN_PLOTS_TREATMENT for t in TRT),
        "at_least_3_distinct_adjacent_year_start_years":
            len(years)>=MIN_START_YEARS,
        "at_least_2_original_identified_target_species":
            len(species)>=MIN_TAXA,
        "at_least_90pct_plant_time_pairs_readable":
            len(plant_pairs)>=.90*FROZEN_PREANIMAL_PAIR_COUNT,
    }
    return {
        "schema":"neon.portal_resource_interaction_learning_holdout_source.v1",
        "status":("SOURCE_GO_NO_RESOURCE_OR_MAMMAL_EFFECT_OPENED"
                  if all(checks.values()) else
                  "SOURCE_STOP_HOLDOUT_ID_OR_RESOURCE_SUPPORT"),
        "published_source":{
            "original_github_repo":"weecology/PortalData",
            "original_git_commit":SOURCE_COMMIT,
            "eight_original_file_blob_hashes_verified":True,
            "new_plant_raw_source_blobs":{p:NEW_FILES[p][0] for p in NEW_FILES},
            "original_historical_1996_2019_source_436_verified_without_effect":True,
        },
        "original_2020_2025_preanimal_source":{
            "eligible_QC_plot_sessions":len(sessions),
            "adjacent_year_source_plot_month_pairs":len(base_pairs),
            "prior_90d_both_plant_survey_pairs":len(plant_pairs),
            "prior_90d_plant_pairs_by_frozen_treatment":dict(sorted(pair_trt.items())),
            "original_plant_support":plant_support,
        },
        "new_2020_2025_outcome_blind_animal_source":{
            "source_animal_counts":dict(sorted(row_counts.items())),
            "identified_target_genus_species_count_without_outcome":len(target),
            "eligible_different_observed_ID_species_plot_year_pairs_all":
                len(disjoint_qual),
            "eligible_pairs_with_numeric_plant_source_both_years":len(have_plant),
            "same_experimental_treatment_pairs_with_numeric_plant_source":
                dict(sorted(trt_count.items())),
            "source_physical_plot_count_with_numeric_plant":len(distinct_plots),
            "source_plots_per_treatment_with_numeric_plant":
                {t:len(plots_by_trt[t]) for t in TRT},
            "source_start_years_with_numeric_plant":len(years),
            "source_distinct_species_codes_with_numeric_plant":len(species),
            "same_census_conflicting_ID_station_records_excluded":
                conflicting_in_single,
            "same_census_conflicting_ID_taxonomy_excluded":conflicting_taxon,
            "original_source_eligibility_checks":checks,
        },
        "ecological_inference_limits":{
            "plant_individual_counts_not_seed_biomass_or_edible_energy":True,
            "plant_quadrat_16_positions_not_49_stake_exact_food_data":True,
            "past_capture_history_not_experimental_learning":True,
            "exclosure_not_treatment_randomized_every_year":True,
            "only_one_original_Portal_landscape":True,
            "actual_plant_abundance_totals_not_calculated":True,
            "species_composition_turnover_not_calculated":True,
            "no_species_station_overlap_or_spatial_effect_calculated":True,
            "no_treatment_coefficients_or_learning_effect_calculated":True,
            "no_future_cohort_substitutions_if_source_STOP":True,
            "old_1996_2019_Portal_436_ecology_unchanged":True,
            "NEON_Finland_Structural_original_results_untouched":True,
            "single_NEON_manuscript_stays_DRAFT_SUBMISSION_HOLD":True,
        },
        "frozen_protocol":PROTOCOL,
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    global PHASE
    try:
        sources = {p:get_source(p) for p in FILES}
        for path in NEW_FILES:
            sources[path] = original_extra(path)
        result=cohort_source_only(sources)
        # Source STOP is a scientific decision, not a malformed CI file.
        exitcode=0 if result["status"]=="SOURCE_GO_NO_RESOURCE_OR_MAMMAL_EFFECT_OPENED" else 3
    except Exception as error:
        result={
            "schema":"neon.portal_resource_interaction_learning_holdout_source.v1",
            "status":"SOURCE_STOP_ORIGINAL_FILE_OR_CODE",
            "stopped_phase":PHASE,
            "error_type":type(error).__name__,
            "error_label":str(error)[:180],
            "no_2020_25_animal_or_plant_biological_outcomes_opened":True,
        }
        exitcode=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return exitcode

if __name__=="__main__":
    raise SystemExit(main())
