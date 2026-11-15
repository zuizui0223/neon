#!/usr/bin/env python3
"""Observed seasonal pair-identity spatial arrangement in original 2021 bank voles.

Follow-up retrospective ecology only. Frozen before THIS dyad outcome in
docs/NEON_BANK_VOLE_DYAD_PERSISTENCE_FROZEN_20261115.md.
Does NOT estimate animal contacts, transmission or true movement.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timezone
from itertools import combinations
from math import atan2,cos,hypot,isfinite,pi,sin,fsum
from pathlib import Path
from random import Random
from statistics import mean,median
import json

from analysis.run_neon_external_bank_vole_centroid_v1 import (
    SOURCE_COMMIT,SOURCE_FILES,FACTOR_CELLS,FROZEN_N_BY_CELL,
    original_csv,original_data,centroid,distance,require
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_bank_vole_partner_geometry_20261115.json"
DYAD_PERM_DRAWS=2000
DIRECTION_PERM_DRAWS=2000
SITE_BOOT_DRAWS=5000
SEED=2026111553
MIN_GROUP_N=3
MIN_UNIQUE_DISTANCES=3
MIN_INFORMATIVE_SITES=8
MIN_INFORMATIVE_PAIRS=60
MIN_SITES_PER_TREATMENT_CELL=2
SOURCE_EXPECTED_CANDIDATE_SITES=10
SOURCE_EXPECTED_CANDIDATE_PAIRS=102
STAGE="PINNED_EXTERNAL_SOURCE"
STAGES={"PINNED_EXTERNAL_SOURCE","ORIGINAL_COHORT_NO_NEW_ANIMALS",
        "PREDECLARED_SPATIAL_VARIATION_GATE","SOURCE_FROZEN_PAIR_IDENTITY_NULL",
        "SOURCE_FROZEN_DIRECTIONAL_NULL","STRATIFIED_SITE_BOOTSTRAP"}

def average_ranks(v):
    """Deterministic tie-aware midranks for distances (rounded 1e-10)."""
    ix=sorted(range(len(v)),key=lambda j:(round(v[j],10),j))
    result=[0.0]*len(v)
    at=0
    while at<len(ix):
        end=at+1
        while end<len(ix) and round(v[ix[end]],10)==round(v[ix[at]],10):
            end+=1
        value=(at+end-1)/2+1.0
        for k in range(at,end):
            result[ix[k]]=value
        at=end
    return result

def pearson_ranks(a,b):
    if len(a)!=len(b) or len(a)<3:
        raise ValueError("At least three comparable dyad ranks required")
    ra=average_ranks(a);rb=average_ranks(b)
    av=mean(ra);bv=mean(rb)
    ca=[x-av for x in ra];cb=[y-bv for y in rb]
    va=fsum(x*x for x in ca);vb=fsum(y*y for y in cb)
    if va<=0 or vb<=0:
        raise ValueError("Source pair rank variation absent")
    return fsum(x*y for x,y in zip(ca,cb))/(va*vb)**.5

def pair_distances(points):
    n=len(points)
    return [distance(points[i],points[j]) for i,j in combinations(range(n),2)]

def dyad_reshuffle(summer,fall,rng,draws=DYAD_PERM_DRAWS):
    """Permute AUTUMN animal IDs, preserve complete seasonal point clouds."""
    if len(summer)!=len(fall) or len(summer)<MIN_GROUP_N:
        raise ValueError("Need same >=3 documented individuals in both seasons")
    if any(not all(isfinite(z) for z in p) for p in summer+fall):
        raise ValueError("Invalid source captured centroid coordinates")
    a=pair_distances(summer)
    b=pair_distances(fall)
    obs=pearson_ranks(a,b)
    null=[]
    n=len(summer)
    for _ in range(draws):
        ids=list(range(n))
        rng.shuffle(ids)
        shuffled=[fall[j] for j in ids]
        null.append(pearson_ranks(a,pair_distances(shuffled)))
    return {"observed":obs,"identity_shuffle_null_mean":mean(null),
            "identity_excess":obs-mean(null),
            "permutation_count":draws}

def directional_alignment(summer,fall,rng,draws=DIRECTION_PERM_DRAWS):
    """Coherent group displacement vs independent random directions at fixed lengths."""
    if len(summer)!=len(fall) or len(summer)<3:
        raise ValueError("Same >=3 animals required")
    shifts=[(fall[j][0]-summer[j][0],fall[j][1]-summer[j][1])
            for j in range(len(summer))]
    lengths=[hypot(x,y) for x,y in shifts]
    if mean(lengths)<=0:
        return {"estimable":False,"reason":"NO_OBSERVED_CENTROID_DISPLACEMENTS"}
    denom=mean(lengths)
    obs=hypot(mean(x for x,y in shifts),mean(y for x,y in shifts))/denom
    null=[]
    for _ in range(draws):
        x=fsum(length*cos(2*pi*rng.random()) for length in lengths)/len(lengths)
        y=fsum(length*sin(2*pi*rng.random()) for length in lengths)/len(lengths)
        null.append(hypot(x,y)/denom)
    return {"estimable":True,"directional_observed":obs,"directional_rotation_null_mean":mean(null),
            "directional_excess":obs-mean(null),
            "random_angle_count":draws}

def source_and_site_centroids():
    global STAGE
    raw={path:original_data(path) for path in SOURCE_FILES}
    STAGE="ORIGINAL_COHORT_NO_NEW_ANIMALS"
    records,headers=original_csv(raw["fulltrap21_volecapturedata.csv"],
        ("year","season","site","tag","food_trt","helm_trt","trap","x","y"))
    codebook,_=original_csv(raw["site_trts.csv"],("site","food_trt","helm_trt"))
    require(len(records)==2012 and len(codebook)==13,"EXACT_FROZEN_2012_AND_13")
    trts={}
    for row in codebook:
        s=(row["site"] or "").strip()
        group=((row["food_trt"] or "").strip(),(row["helm_trt"] or "").strip())
        require(s and s not in trts and group in FACTOR_CELLS,
                "ORIGINAL_EXACT_SITE_ASSIGNMENTS")
        trts[s]=group
    captures=defaultdict(lambda:{"summer":[],"fall":[]})
    locations={}
    counts=Counter()
    for row in records:
        site=(row["site"] or "").strip()
        tag=(row["tag"] or "").strip()
        season=(row["season"] or "").strip()
        trap=(row["trap"] or "").strip()
        group=((row["food_trt"] or "").strip(),(row["helm_trt"] or "").strip())
        require(site in trts and group==trts[site] and tag
                and trap and row["year"]=="2021" and season in ("summer","fall"),
                "EXACT_SOURCE_CAPTURE_METADATA")
        try: xy=(float(row["x"]),float(row["y"]))
        except (ValueError,TypeError):
            raise ValueError("Non-numeric original source positions") from None
        require(all(isfinite(z) for z in xy),"FINITE_CAPTURE_XY")
        position_key=(site,trap)
        if position_key in locations:
            require(locations[position_key]==xy,
                    "SOURCE_TRAP_NAME_CONFLICT")
        locations[position_key]=xy
        captures[(site,tag)][season].append(xy)
        counts[season]+=1
    actual_sites={s for s,t in captures}
    require(len(captures)==742 and len(actual_sites)==12
            and len(trts)==13 and len(set(trts)-actual_sites)==1
            and len(locations)==563
            and counts=={"summer":905,"fall":1107},
            "EXACT_ORIGINAL_FROZEN_SOURCE_SUPPORT")
    both=sum(bool(v["summer"] and v["fall"]) for v in captures.values())
    selected={key:v for key,v in captures.items()
              if min(len(v["summer"]),len(v["fall"]))>=2}
    require(both==120 and len(selected)==51,
            "SAME_ORIGINAL_51_IDENTITY_SUBSET")
    bycell=Counter(trts[s] for s,t in selected)
    require(dict(bycell)==FROZEN_N_BY_CELL,"SAME_ORIGINAL_4_CELL_COUNTS")
    sorted_by_site=defaultdict(list)
    for (site,tag),seasons in sorted(selected.items()):
        sorted_by_site[site].append((
            tag,centroid(seasons["summer"]),centroid(seasons["fall"])
        ))
    original_sites={s for s,t in selected}
    require(len(original_sites)==12 and set(sorted_by_site)==original_sites,
            "SAME_ORIGINAL_12_SITES")
    return sorted_by_site,trts,{
        "raw_capture_rows":len(records),
        "all_source_animal_keys":len(captures),
        "both_seasons_tags":both,
        "same_frozen_51_tags":len(selected),
        "original_12_sampling_sites":len(actual_sites),
        "source_13_metadata_sites":len(trts),
        "source_station_name_to_coordinate_identities":len(locations),
        "summer_source_captures":counts["summer"],
        "fall_source_captures":counts["fall"],
        "frozen_cell_counts":{
            food+"__"+helm:bycell[(food,helm)] for food,helm in FACTOR_CELLS
        }
    }

def run():
    global STAGE
    site_data,group,census=source_and_site_centroids()
    STAGE="PREDECLARED_SPATIAL_VARIATION_GATE"
    candidate={s:v for s,v in site_data.items() if len(v)>=MIN_GROUP_N}
    candidate_pairs=sum(len(rows)*(len(rows)-1)//2
                        for rows in candidate.values())
    require(len(candidate)==SOURCE_EXPECTED_CANDIDATE_SITES and
            candidate_pairs==SOURCE_EXPECTED_CANDIDATE_PAIRS,
            "FROZEN_TEN_SITE_102_PAIR_GEOMETRY_UNIVERSE")
    eligible={}
    nonestimable=Counter()
    bycell=defaultdict(list)
    for site,rows in sorted(candidate.items()):
        a=[z[1] for z in rows];b=[z[2] for z in rows]
        unique_a=len({round(x,10) for x in pair_distances(a)})
        unique_b=len({round(x,10) for x in pair_distances(b)})
        if min(unique_a,unique_b)<MIN_UNIQUE_DISTANCES:
            nonestimable["INSUFFICIENT_PAIR_DISTANCE_VARIATION"]+=1
            continue
        eligible[site]=rows
        bycell[group[site]].append(site)
    pair_count=sum(len(rows)*(len(rows)-1)//2 for rows in eligible.values())
    gate_pass=(len(eligible)>=MIN_INFORMATIVE_SITES
               and pair_count>=MIN_INFORMATIVE_PAIRS
               and all(len(bycell[c])>=MIN_SITES_PER_TREATMENT_CELL
                       for c in FACTOR_CELLS))
    source_provenance={
        "original_repository":"jmistrick/vole-spatial-manuscript",
        "original_immutable_git_sha":SOURCE_COMMIT,
        "source_git_file_blobs_sha_verified":True,
        "original_source_exactly_reconstructed":census,
        "this_is_REVISIT_of_already_opened_original_2021_capture_dataset":True,
        "this_endpoint_predeclared_before_dyad_ranks_were_inspected":True,
        "protocol_path":"docs/NEON_BANK_VOLE_DYAD_PERSISTENCE_FROZEN_20261115.md"
    }
    source_counts={
        "original_repeated_animal_sites":len(site_data),
        "original_individuals_with_two_captures_both_seasons":sum(map(len,site_data.values())),
        "site_with_at_least_three_matched_individuals":len(candidate),
        "all_possible_dyads_at_n_ge3_sites":candidate_pairs,
        "site_with_at_least_three_unique_pair_distances_in_both_seasons":len(eligible),
        "dyads_at_eligible_sites":pair_count,
        "nonestimable_site_reason_counts":dict(nonestimable),
        "site_count_per_original_factorial_group":{
            food+"__"+helm:len(bycell[(food,helm)]) for food,helm in FACTOR_CELLS
        },
        "min_source_site_gate":MIN_INFORMATIVE_SITES,
        "min_source_dyads_gate":MIN_INFORMATIVE_PAIRS,
        "min_original_sites_per_factorial_cell":MIN_SITES_PER_TREATMENT_CELL,
        "source_gate_pass":gate_pass,
        "no_original_site_names_individual_tags_or_locations_exported":True,
    }
    if not gate_pass:
        return {
            "schema":"neon.external_vole_identity_specific_pair_geometry.v1",
            "status":"STOP_FROZEN_BANK_VOLE_DYAD_GEOMETRY_SOURCE_GATE",
            "source_provenance":source_provenance,
            "source_eligibility":source_counts,
            "no_dyad_rho_or_directional_ecological_effect_calculated":True,
            "original_NEON_Portal_Structural_results_not_read":True,
        }
    STAGE="SOURCE_FROZEN_PAIR_IDENTITY_NULL"
    rng=Random(SEED)
    bysite={}
    for site,rows in sorted(eligible.items()):
        a=[v[1] for v in rows];b=[v[2] for v in rows]
        pair=dyad_reshuffle(a,b,rng,draws=DYAD_PERM_DRAWS)
        bysite[site]=pair
    STAGE="SOURCE_FROZEN_DIRECTIONAL_NULL"
    for site,rows in sorted(eligible.items()):
        a=[v[1] for v in rows];b=[v[2] for v in rows]
        directional=directional_alignment(a,b,rng,draws=DIRECTION_PERM_DRAWS)
        require(directional["estimable"],
                "SITE_DIRECTIONAL_ZERO_DISPLACEMENT_GATE")
        bysite[site].update(directional)
    require(len(bysite)==len(eligible),"SITE_VALUES_MISSING")

    primary=[bysite[s]["identity_excess"] for s in sorted(eligible)]
    directional=[bysite[s]["directional_excess"] for s in sorted(eligible)]
    actual=[bysite[s]["observed"] for s in sorted(eligible)]
    null=[bysite[s]["identity_shuffle_null_mean"] for s in sorted(eligible)]
    coherence=[bysite[s]["directional_observed"] for s in sorted(eligible)]
    # Preserve original source factorial sampling groups with bootstrapped sites.
    STAGE="STRATIFIED_SITE_BOOTSTRAP"
    boot={"partner":[],"direction":[]}
    for _ in range(SITE_BOOT_DRAWS):
        sample=[]
        for cell in FACTOR_CELLS:
            avail=sorted(bycell[cell])
            sample.extend(avail[rng.randrange(len(avail))] for k in avail)
        boot["partner"].append(mean(bysite[s]["identity_excess"] for s in sample))
        boot["direction"].append(mean(bysite[s]["directional_excess"] for s in sample))
    for x in boot.values():x.sort()
    def ci(v):return [v[int(.025*len(v))],v[int(.975*len(v))-1]]
    def basic(v):return {"mean":mean(v),"median":median(v),
                         "min":min(v),"max":max(v),
                         "positive_sites":sum(z>0 for z in v),
                         "negative_sites":sum(z<0 for z in v),
                         "zero_sites":sum(z==0 for z in v)}
    return {
        "schema":"neon.external_vole_identity_specific_pair_geometry.v1",
        "status":"EXTERNAL_BANK_VOLE_DYAD_IDENTITY_GEOMETRY_RETROSPECTIVE_NOT_TRUE_CONTACT",
        "source_provenance":source_provenance,
        "source_eligibility":source_counts,
        "dyad_rank_maintenance":{
            "estimand":"Within-site same-tag individual pair centroid distance Spearman rho SUMMER vs FALL, minus 2000 within-site AUTUMN animal-identity shuffle reference",
            "observed_site_rho":basic(actual),
            "reference_site_permuted_rho":basic(null),
            "site_equal_identity_specific_excess_rho":basic(primary),
            "stratified_site_bootstrap95":ci(boot["partner"]),
            "individual_identity_permutations_each_site":DYAD_PERM_DRAWS,
            "no_direct_contact_or_transmission_observed":True,
            "original_monthly_overlap_networks_previously_published":True,
        },
        "common_directional_position_change":{
            "estimand":"Norm of mean within-individual seasonal capture centroid displacement vector divided by mean vector length, minus random-orientation reference",
            "site_directional_coherence_observed":basic(coherence),
            "site_directional_coherence_null":basic([bysite[s]["directional_rotation_null_mean"] for s in sorted(eligible)]),
            "site_directional_coherence_excess":basic(directional),
            "stratified_site_bootstrap95":ci(boot["direction"]),
            "random_directional_angle_rotations_each_site":DIRECTION_PERM_DRAWS,
            "cannot_identify_true_coordinated_group_movement":True
        },
        "uncertainty_and_boundaries":{
            "captured_centroid_not_true_animal_utilization_distribution":True,
            "summer_and_autumn_effort_and_species_specific_detection_not_identified":True,
            "some_original_sites_only_2_repeated_animals_are_not_estimable":True,
            "dyads_are_dependent_within_site":True,
            "all_CI_are_descriptive_site_bootstrap_not_confirmatory_p_values":True,
            "already_published_original_2024_home_range_overlap_and_network_metrics_not_new":True,
            "old_51_individual_centroid_outcome_was_seen_before_this_followup":True,
            "no_original_NEON_Portal_or_Structural_ecological_results_changed":True,
            "single_neon_mammal_paper_remains_DRAFT_SUBMISSION_HOLD":True,
            "no_p_value_or_taxon_treatment_subgroup_search":True,
        },
        "implementation":{
            "seed":SEED,"site_bootstrap_draws":SITE_BOOT_DRAWS,
            "tie_aware_average_ranks":True,
            "site_stratification_original_food_x_helminth":True,
            "original_source_coordinates_kept_in_grid_units":True,
        },
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    global STAGE
    try:
        result=run()
        status=0
    except Exception as err:
        result={
            "schema":"neon.external_vole_identity_specific_pair_geometry.v1",
            "status":"STOP_BANK_VOLE_ORIGINAL_SOURCE_OR_IMPLEMENTATION",
            "stopped_phase":STAGE if STAGE in STAGES else "UNKNOWN",
            "error_class":type(err).__name__,
            "no_vole_raw_pair_identity_or_coords_exported":True,
            "old_neon_portal_structural_ecology_effects_unchanged":True,
        }
        status=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return status

if __name__=="__main__":raise SystemExit(main())
