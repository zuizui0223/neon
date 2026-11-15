#!/usr/bin/env python3
"""Source-only Portal 1996-2019 PIT/tag-individual turnover feasibility.

No rodent spatial recurrence Z, treatment effect or habitat-use response
computed. Original public source bytes pinned by Git blob SHA.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import csv,hashlib,io,json,urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/portal_identity_niche_source_20261115.json"
SOURCE_COMMIT="afd75933249ae60f3a5e9dab00b354f219e5e045"
FILES={
 "Rodents/Portal_rodent.csv":("b2c6da8e3c18ca93a2d57083c09f2eb39ed28bb5",9000000),
 "Rodents/Portal_rodent_trapping.csv":("2a4d18388a4296dd81e8bc16f8dadd92a63e0214",500000),
 "Rodents/Portal_rodent_species.csv":("bcecdbeab3fb364a7712d17486fa12b5ceda835f",15000),
 "SiteandMethods/Portal_plots.csv":("20a4b46d97509787d510df60d2bd898a2fe0ad8a",600000),
 "Plants/Portal_plant_censuses.csv":("e8f03be84e3adb9cf0f9dc6571dbed14e88299a2",1100000),
 "SiteandMethods/Portal_UTMCoords.csv":("fa96bd174b28767acb27758fddaca0b51676800f",180000),
}
YEARS=(1996,2019)
TRT=("control","exclosure")
MIN_NEW_ID=5
MIN_STAKE=3
PHASE="FETCH_PINNED_SOURCE"

def get_source(path):
    sha,cap=FILES[path]
    url="https://raw.githubusercontent.com/weecology/PortalData/"+SOURCE_COMMIT+"/"+path
    req=urllib.request.Request(url,headers={"User-Agent":"NEON-Portal-source-audit/1"})
    with urllib.request.urlopen(req,timeout=120) as f:
        raw=f.read(cap+1)
    if len(raw)>cap:raise ValueError("PINNED_SOURCE_BYTES_EXCEED_CAP")
    v=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if v!=sha:raise ValueError("PINNED_SOURCE_GIT_BLOB_SHA_MISMATCH")
    return raw

def csv_rows(raw,required):
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    fields=reader.fieldnames or []
    if not set(required).issubset(fields) or len(fields)!=len(set(fields)):
        raise ValueError("OFFICIAL_CSV_HEADER_MISSING")
    return reader,fields

def i(x):
    try:return int(x)
    except (TypeError,ValueError):return None

def stake(x):
    n=i(x)
    return n if n is not None and 1<=n//10<=7 and 1<=n%10<=7 else None

def audit(source):
    global PHASE
    PHASE="VERIFY_SOURCE_SCHEMA_AND_STAKE"
    ro,ro_fields=csv_rows(source["Rodents/Portal_rodent.csv"],
      ("year","month","period","plot","stake","species","id"))
    effort,ef_fields=csv_rows(source["Rodents/Portal_rodent_trapping.csv"],
      ("year","month","period","plot","sampled","effort","qcflag"))
    taxa,_=csv_rows(source["Rodents/Portal_rodent_species.csv"],
      ("speciescode","scientificname","rodent","granivore","censustarget","unidentified"))
    treat,_=csv_rows(source["SiteandMethods/Portal_plots.csv"],
      ("year","month","plot","treatment"))
    plants,_=csv_rows(source["Plants/Portal_plant_censuses.csv"],
      ("year","season","plot","quadrat","censused"))
    coords,_=csv_rows(source["SiteandMethods/Portal_UTMCoords.csv"],
      ("plot","type","number","east","north"))
    species={}
    for x in taxa:
        code=(x["speciescode"] or "").strip()
        if code in species:raise ValueError("DUPLICATE_TAXON_CODE")
        species[code]=x
    target={c for c,x in species.items() if x["rodent"]=="1"
            and x["granivore"]=="1" and x["censustarget"]=="1"
            and x["unidentified"]=="0"}
    if "DM" not in target or "PP" not in target:raise ValueError("FROZEN_TARGET_CODEBOOK_DRIFT")
    bytrt={}
    for x in treat:
        k=(i(x["year"]),i(x["month"]),i(x["plot"]))
        if k in bytrt:raise ValueError("DUPLICATE_YEAR_MONTH_PLOT_TREATMENT")
        bytrt[k]=(x.get("treatment") or "").strip().lower()
    station_plots=defaultdict(set)
    coord_types=Counter()
    for x in coords:
        typ=(x.get("type") or "").strip().lower()
        coord_types[typ]+=1
        if typ in ("rodent","stake","trap") and stake(x["number"]) is not None:
            station_plots[i(x["plot"])].add(stake(x["number"]))
    plant_surveys=set()
    for x in plants:
        y=i(x["year"]);p=i(x["plot"]);season=(x["season"] or "").strip().lower()
        if x["censused"]=="1" and y is not None and p is not None:
            plant_surveys.add((p,y,season))
    PHASE="VERIFY_STANDARD_OPPORTUNITY"
    sessions={};census=Counter()
    for x in effort:
        census["all_trapping_effort_records"]+=1
        y=i(x["year"]);m=i(x["month"]);p=i(x["plot"]);period=i(x["period"])
        if None in (y,m,p,period) or not YEARS[0]<=y<=YEARS[1] or period<=0:continue
        key=(p,y,m,period)
        if key in sessions:raise ValueError("DUPLICATE_TRAPPING_PERIOD")
        t=bytrt.get((y,m,p))
        effort_count=i(x["effort"])
        valid=(x["sampled"]=="1" and x["qcflag"]=="1"
               and effort_count is not None and 48<=effort_count<=49
               and t in TRT)
        sessions[key]=(valid,t)
        census["source_positive_period_1996_2019"]+=1
        census["full_QC_source_sessions"]+=int(valid)
    PHASE="VERIFY_TAGGED_INDIVIDUAL_SOURCE"
    observations=Counter();pit=Counter()
    ids_by=defaultdict(lambda:defaultdict(set))
    stations_by=defaultdict(lambda:defaultdict(set))
    for x in ro:
        observations["all_rodent_capture_rows"]+=1
        key=(i(x["plot"]),i(x["year"]),i(x["month"]),i(x["period"]))
        if key not in sessions or not sessions[key][0]:continue
        observations["rows_at_qualified_standard_session"]+=1
        code=(x.get("species") or "").strip()
        if code not in target:continue
        n=stake(x.get("stake"))
        tag=(x.get("id") or "").strip()
        if n is None:
            observations["target_stake_invalid"]+=1
            continue
        if tag.lower() in ("","na","nan","null"):
            observations["target_unique_ID_absent"]+=1
            continue
        ids_by[key][code].add(tag)
        stations_by[key][code].add((tag,n))
        pit[(x.get("pit_tag") or "").strip().lower()]+=1
        observations["target_rodent_identity_and_stake_valid_rows"]+=1
    PHASE="SOURCE_ONLY_DISJOINT_ID_ADJACENT_YEARS"
    monthly=defaultdict(list)
    for (p,y,m,period),(valid,t) in sessions.items():
        if valid:monthly[(p,y,m)].append((p,y,m,period))
    support=Counter();by_treatment=defaultdict(set);by_taxon=Counter()
    year_sources=defaultdict(set)
    for p,y,m in sorted(monthly):
        if y>=YEARS[1]:continue
        a=monthly[(p,y,m)]
        b=monthly.get((p,y+1,m),[])
        if len(a)!=1 or len(b)!=1:
            support["nonunique_or_missing_neighbour_year_month"]+=1;continue
        a,b=a[0],b[0]
        trt=sessions[a][1]
        if trt not in TRT or sessions[b][1]!=trt:
            support["treatment_switched"]+=1;continue
        support["matched_QC_same_month_adjacent_year_sessions"]+=1
        for code in sorted(set(ids_by[a])&set(ids_by[b])):
            ids_a=ids_by[a][code];ids_b=ids_by[b][code]
            if min(len(ids_a),len(ids_b))<MIN_NEW_ID:continue
            support["matched_species_ID5_each_year_pre_exclusion"]+=1
            shared=ids_a&ids_b
            fresh_a=ids_a-shared
            fresh_b=ids_b-shared
            spots_a={st for animal,st in stations_by[a][code] if animal in fresh_a}
            spots_b={st for animal,st in stations_by[b][code] if animal in fresh_b}
            if min(len(fresh_a),len(fresh_b))<MIN_NEW_ID or min(len(spots_a),len(spots_b))<MIN_STAKE:continue
            support["qualified_different_observed_ID_species_pairs"]+=1
            support["qualified_"+trt]+=1
            by_treatment[trt].add(p)
            year_sources[trt].add(y)
            by_taxon[code]+=1
    go=(support["qualified_different_observed_ID_species_pairs"]>=30
        and all(len(by_treatment[t])>=4 for t in TRT))
    return {
        "schema":"neon.portal_external_species_stake_identity_source.v1",
        "status":("SOURCE_PORTAL_DISJOINT_ID_STAKE_GO_NO_NICHE_EFFECT"
                  if go else "STOP_PORTAL_DISJOINT_ID_STAKE_SOURCE"),
        "source":{"commit":SOURCE_COMMIT,"all_original_files_git_blob_SHA_verified":True,
                  "file_bytes":{p:len(source[p]) for p in sorted(source)}},
        "frozen_source_criteria":{"years":list(YEARS),"one_QC48to49_stake_sample_per_year_month":True,
                                  "same_plot_same_month_adjacent_year":True,
                                  "treatments":list(TRT),"disjoint_observed_ID_min_per_year":MIN_NEW_ID,
                                  "distinct_stakes_min_per_year":MIN_STAKE,
                                  "source_min_pairs":30,"source_min_experimental_plots_per_treatment":4,
                                  "exclude_nonstandard_negative_periods":True},
        "source_only_summary":{"effort_rows":dict(sorted(census.items())),
                               "capture_rows":dict(sorted(observations.items())),
                               "pit_tag_field_values":dict(sorted(pit.items())),
                               "target_identified_granivore_codes":sorted(target),
                               "source_pair_counts":dict(sorted(support.items())),
                               "qualified_species_pair_counts_by_taxon":dict(sorted(by_taxon.items())),
                               "qualified_plot_clusters_by_treatment":{t:len(by_treatment[t]) for t in TRT},
                               "qualified_start_year_count_by_treatment":{t:len(year_sources[t]) for t in TRT},
                               "coordinate_type_counts":dict(sorted(coord_types.items())),
                               "coordinate_target_rodent_stake_plot_count":len(station_plots),
                               "plant_censused_plot_year_seasons":len(plant_surveys),
                               "rodent_header_columns":ro_fields},
        "scientific_limits":{
            "one_physical_Portal_landscape_not_multiple_independent_regions":True,
            "different_ID_between_years_not_demographic_death_or_immigration_proof":True,
            "rodent_capture_at_stake_not_true_niche_occupancy":True,
            "original_stake_opportunity_not_confirmed_daily_individually":True,
            "Portal_2019_habitat_patch_shifts_and_2022_resource_partition_prior_art":True,
            "no_trap_niche_Z_or_treatment_contrast_or_significance_opened":True,
            "no_original_NEON_or_Structural_mammal_ecology_refitted":True,
            "no_animal_ID_site_date_stake_or_coordinates_exported":True,
        },
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    global PHASE
    try:
        inputs={p:get_source(p) for p in FILES}
        result=audit(inputs)
        code=0
    except Exception as exc:
        result={"schema":"neon.portal_external_species_stake_identity_source.v1",
                "status":"STOP_PORTAL_SOURCE_OR_SCHEMA","source_stage":PHASE,
                "failure_class":type(exc).__name__,"no_rodent_ecological_effect_opened":True}
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True))
    return code

if __name__=="__main__":raise SystemExit(main())
