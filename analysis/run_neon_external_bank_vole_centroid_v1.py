#!/usr/bin/env python3
"""Exploratory independent 2021 bank-vole within-animal seasonal capture centroids.

This follows a precommitted protocol; it is NOT GPS/telemetry, true habitat use,
nor a refit of any original NEON/Structural/Portal response. Never export tags.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime, timezone
from io import StringIO
from math import hypot,isfinite,fsum
from pathlib import Path
from random import Random
from statistics import mean,median
from urllib.request import Request,urlopen
import csv,hashlib,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_bank_vole_individual_seasonal_centroid_20261115.json"
SOURCE_COMMIT="47dc1e9b1f83ec2faaf7ba232e02e00f9e4cffb4"
SOURCE_FILES={
    "fulltrap21_volecapturedata.csv":(
        "343de8c3846eea21d3f0648358e159bd61bb87a2",300000
    ),
    "site_trts.csv":(
        "b4059f818650ce844472a80f6caf38eee65bfffe",5000
    )
}
FACTOR_CELLS=(
    ("fed","control"),("fed","deworm"),("unfed","control"),("unfed","deworm")
)
FROZEN_N_BY_CELL={
    ("fed","control"):16,("fed","deworm"):12,
    ("unfed","control"):15,("unfed","deworm"):8
}
MIN_PER_SEASON=2
PERM_DRAWS=2000
BOOT_DRAWS=5000
SEED=2026111501
STAGE="PINNED_PUBLIC_SOURCE"
STAGES={"PINNED_PUBLIC_SOURCE","ORIGINAL_742_ID_SUPPORT",
        "FIXED_GRID_TRAP_COORDINATES","WITHIN_INDIVIDUAL_SEASON_REASSIGNMENT",
        "PLOT_CLUSTER_BOOTSTRAP"}

def require(v,label):
    if not v:raise ValueError("BANK_VOLE_SOURCE_STOP_"+label)

def original_data(path):
    sha,max_bytes=SOURCE_FILES[path]
    req=Request("https://raw.githubusercontent.com/jmistrick/vole-spatial-manuscript/"
                +SOURCE_COMMIT+"/"+path,headers={"User-Agent":"NEON-vole-source/1"})
    with urlopen(req,timeout=100) as r:
        buf=r.read(max_bytes+1)
    require(len(buf)<=max_bytes,"ORIGINAL_SOURCE_SIZE")
    actual=hashlib.sha1(b"blob "+str(len(buf)).encode()+b"\0"+buf).hexdigest()
    require(actual==sha,"ORIGINAL_GIT_BLOB_SHA")
    return buf

def original_csv(data,expected):
    text=data.decode("utf-8-sig").replace("\r\n","\n").replace("\r","\n")
    reader=csv.DictReader(StringIO(text))
    columns=reader.fieldnames or []
    require(len(columns)==len(set(columns)) and set(expected)<=set(columns),
            "ORIGINAL_COLUMN_SCHEMA")
    return list(reader),columns

def centroid(points):
    if not points:raise ValueError("Centroid of empty original capture source")
    return (fsum(p[0] for p in points)/len(points),
            fsum(p[1] for p in points)/len(points))

def distance(a,b):
    return hypot(a[0]-b[0],a[1]-b[1])

def individual_reallocation(summer,fall,rng,draws=PERM_DRAWS):
    """Within-animal pooled captures, permuted season labels at frozen counts."""
    if len(summer)<2 or len(fall)<2:
        raise ValueError("Original two-capture per-season support missing")
    pooled=tuple(summer)+tuple(fall)
    if any(len(p)!=2 or not all(isfinite(v) for v in p) for p in pooled):
        raise ValueError("Source X/Y invalid")
    k=len(summer);n=len(pooled)
    observed=distance(centroid(summer),centroid(fall))
    total_x=fsum(p[0] for p in pooled)
    total_y=fsum(p[1] for p in pooled)
    null=[]
    for _ in range(draws):
        selected=rng.sample(range(n),k)
        x=fsum(pooled[j][0] for j in selected)
        y=fsum(pooled[j][1] for j in selected)
        c1=(x/k,y/k)
        c2=((total_x-x)/(n-k),(total_y-y)/(n-k))
        null.append(distance(c1,c2))
    null.sort()
    return {
        "observed":observed,"reference":mean(null),
        "excess":observed-mean(null),
        "above_975":observed>null[min(draws-1,int(.975*draws))],
    }

def run():
    global STAGE
    files={p:original_data(p) for p in SOURCE_FILES}
    STAGE="ORIGINAL_742_ID_SUPPORT"
    rows,headers=original_csv(files["fulltrap21_volecapturedata.csv"],(
        "year","month","season","site","food_trt","helm_trt","tag",
        "trap","x","y"
    ))
    trts,_=original_csv(files["site_trts.csv"],("site","food_trt","helm_trt"))
    require(len(rows)==2012 and len(trts)==12,"ORIGINAL_SAMPLING_DENOMINATOR")
    site_assign={}
    for row in trts:
        site=(row["site"] or "").strip()
        val=((row["food_trt"] or "").strip(),(row["helm_trt"] or "").strip())
        require(bool(site) and site not in site_assign and val in FACTOR_CELLS,
                "SITE_TREATMENT_METADATA")
        site_assign[site]=val
    individuals=defaultdict(lambda:{"summer":[],"fall":[]})
    traps={}   # original physical position of each site-specific trap
    counts=Counter()
    for row in rows:
        site=(row["site"] or "").strip()
        tag=(row["tag"] or "").strip()
        season=(row["season"] or "").strip()
        food=(row["food_trt"] or "").strip()
        helm=(row["helm_trt"] or "").strip()
        name=(row["trap"] or "").strip()
        require(site in site_assign and (food,helm)==site_assign[site],
                "SITE_ASSIGNMENT_SOURCE_MISMATCH")
        require(bool(tag) and bool(name) and season in ("summer","fall")
                and row["year"]=="2021","SOURCE_ANIMAL_SEASON_OR_TRAP")
        try:
            x=float(row["x"]);y=float(row["y"])
        except (TypeError,ValueError):
            raise ValueError("NONNUMERIC_CAPTURE_POSITION") from None
        require(isfinite(x) and isfinite(y),"NONFINITE_CAPTURE_POSITION")
        key=(site,name)
        if key in traps:
            require(traps[key]==(x,y),"SOURCE_SITE_TRAP_COORDINATE_DRIFT")
        traps[key]=(x,y)
        individuals[(site,tag)][season].append((x,y))
        counts[season]+=1
    require(counts=={"summer":905,"fall":1107}
            and len(individuals)==742 and len(site_assign)==12,
            "SOURCE_TOTALS_NOT_905_1107_742_12")
    both=[(key,obs) for key,obs in individuals.items()
          if obs["summer"] and obs["fall"]]
    eligible=[(key,obs) for key,obs in individuals.items()
              if min(len(obs["summer"]),len(obs["fall"]))>=2]
    require(len(both)==120 and len(eligible)==51,"ORIGINAL_120_51_ANIMALS")
    bycell=Counter(site_assign[site] for site,tag in
                   (key for key,obs in eligible))
    require(dict(bycell)==FROZEN_N_BY_CELL,"FOUR_FACTORIAL_SAMPLE_COUNTS")
    sites_bycell=defaultdict(set)
    for site,tag in (key for key,obs in eligible):
        sites_bycell[site_assign[site]].add(site)
    require(all(len(sites_bycell[c])==3 for c in FACTOR_CELLS),
            "THREE_INDEPENDENT_SITES_PER_FACTORIAL_CELL")
    STAGE="FIXED_GRID_TRAP_COORDINATES"
    require(bool(traps) and len(traps)>0,"NO_STATION_COORDINATES")

    STAGE="WITHIN_INDIVIDUAL_SEASON_REASSIGNMENT"
    rng=Random(SEED)
    data_by_site=defaultdict(list)
    values=[]
    for key,obs in sorted(eligible):
        result=individual_reallocation(obs["summer"],obs["fall"],rng)
        site,tag=key
        data_by_site[site].append(result)
        values.append(result)
    require(len(values)==51 and len(data_by_site)==12,
            "UNEXPECTED_CENTROID_OBSERVATION_DROP")
    site_values={site:{metric:mean(v[metric] for v in values)
                       for metric in ("observed","reference","excess")}
                 for site,values in data_by_site.items()}
    by_cell_sites={cell:tuple(sorted(s for s in site_values
                          if site_assign[s]==cell)) for cell in FACTOR_CELLS}

    def summarize_site_sample(sample):
        value={c:mean(site_values[site]["excess"] for site in sample[c])
               for c in FACTOR_CELLS}
        pooled=mean(value.values()) # exact 3-site per factorial cell
        fed=(value[("fed","control")]+value[("fed","deworm")])/2
        unfed=(value[("unfed","control")]+value[("unfed","deworm")])/2
        deworm=(value[("fed","deworm")]+value[("unfed","deworm")])/2
        control=(value[("fed","control")]+value[("unfed","control")])/2
        return pooled,fed-unfed,deworm-control,value
    point=summarize_site_sample(by_cell_sites)
    STAGE="PLOT_CLUSTER_BOOTSTRAP"
    boot={"pooled":[],"food":[],"helminth":[]}
    for _ in range(BOOT_DRAWS):
        sample={cell:tuple(by_cell_sites[cell][rng.randrange(3)] for j in range(3))
                for cell in FACTOR_CELLS}
        a,b,c,_=summarize_site_sample(sample)
        boot["pooled"].append(a);boot["food"].append(b);boot["helminth"].append(c)
    for v in boot.values():v.sort()

    def ci(v):return [v[int(.025*len(v))],v[min(len(v)-1,int(.975*len(v))-1)]]
    def stats(vals):
        return {"n":len(vals),"mean":mean(vals),"median":median(vals),
                "min":min(vals),"max":max(vals),
                "positive":sum(v>0 for v in vals),
                "negative":sum(v<0 for v in vals),
                "zero":sum(v==0 for v in vals)}
    return {
        "schema":"neon.external_bank_vole_seasonal_capture_centroid.v1",
        "status":"RETROSPECTIVE_VOLE_WITHIN_ANIMAL_SEASON_CAPTURE_CENTROIDS_NOT_NICHE_USE",
        "source_provenance":{
            "repo":"jmistrick/vole-spatial-manuscript",
            "source_commit":SOURCE_COMMIT,
            "pinned_two_files_Git_blob_verified":True,
            "original_2012_capture_rows":len(rows),
            "original_742_individuals":len(individuals),
            "both_seasons_observed_individuals":len(both),
            "original_frozen_51_two_captures_per_season":len(eligible),
            "original_distinct_sites":len(site_assign),
            "original_source_grid_trap_identities":len(traps),
            "original_source_season_counts":dict(counts),
            "frozen_protocol":"docs/NEON_BANK_VOLE_SEASONAL_CENTROID_FROZEN_20261115.md",
            "source_2024_paper_DOI":"10.1111/1365-2656.14067",
            "source_study_previous_food_and_deworm_findings_prior_art":True
        },
        "sampling_source_support":{
            "four_cell_individual_counts":{
                food+"__"+helm:bycell[(food,helm)] for food,helm in FACTOR_CELLS
            },
            "original_sites_per_factorial_cell":{
                food+"__"+helm:len(by_cell_sites[(food,helm)])
                for food,helm in FACTOR_CELLS
            },
            "original_group_sites_equal_three_each":True,
            "source_same_site_and_trap_coordinate_consistent":True,
            "source_output_anonymized_no_animal_ids_site_names_or_coordinates":True
        },
        "observed_capture_centroid_shift":{
            "units":"original local x/y GRID COORDINATE UNITS, not verified metres",
            "observed_individual_distance":stats([v["observed"] for v in values]),
            "pooled_individual_random_reallocation_reference":stats([v["reference"] for v in values]),
            "finite_sample_adjusted_excess_individual_values":stats([v["excess"] for v in values]),
            "individuals_above_personal_reference_975":sum(v["above_975"] for v in values),
            "site_equal_observed_centroid_shift":mean(v["observed"] for v in site_values.values()),
            "site_equal_expected_reallocation_shift":mean(v["reference"] for v in site_values.values()),
            "site_equal_excess":point[0],
            "site_equal_excess_bootstrap95":ci(boot["pooled"]),
            "food_fed_minus_unfed_site_equal_excess":point[1],
            "food_fed_minus_unfed_bootstrap95":ci(boot["food"]),
            "deworm_minus_control_site_equal_excess":point[2],
            "deworm_minus_control_bootstrap95":ci(boot["helminth"]),
            "four_factorial_cell_site_equal_excess":{
                food+"__"+helm:point[3][(food,helm)]
                for food,helm in FACTOR_CELLS
            },
            "original_Perm_per_individual":PERM_DRAWS,
            "site_stratified_bootstrap_draws":BOOT_DRAWS,
            "seed":SEED,
            "no_p_values_or_posthoc_effect_selection":True
        },
        "scientific_boundaries":{
            "old_2024_paper_space_use_food_parasites_prior_art":True,
            "within_individual_two_seasons_not_ID_replacement_test":True,
            "capture_centroid_not_telemetry_or_true_habitat_use":True,
            "season_reallocation_null_may_violate_effort_stationarity":True,
            "two_different_capture_periods_not_equal_detection":True,
            "four_factorial_cells_have_only_three_sites_each":True,
            "no_direct_independent_behavioral_detector":True,
            "not_a_new_NEON_14_site_or_Portal_436_pair_response_fit":True,
            "Structural_island_mammal_distribution_not_used":True,
            "one_NEON_manuscript_remains_SUBMISSION_HOLD":True
        },
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    global STAGE
    try:
        result=run();code=0
    except Exception as err:
        result={
            "schema":"neon.external_bank_vole_seasonal_capture_centroid.v1",
            "status":"STOP_VOLE_SOURCE_OR_FROZEN_COHORT_OR_GEOMETRY",
            "failed_phase":STAGE if STAGE in STAGES else "UNKNOWN",
            "error_class":type(err).__name__,
            "no_animal_positions_IDs_or_outcomes_exported":True,
            "old_NEON_14site_and_Portal_436pair_results_not_refitted":True
        };code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
