"""Site-equal source-selected NEON within-bout genus re-encounter contrast.

First-night source pair and physical-site support are fully chosen BEFORE
later-night matching outcomes. The estimand is a re-encounter fraction
conditional on capture during the first night, not direct trap detection
p or true animal-use/occupancy. The 3-night mammal loader lacks fate/release.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from math import isfinite
from random import Random
from statistics import mean

from analysis.audit_neon_crossseason_genus_support_v1 import _normal_tag,_normal_coord
from analysis.neon_macro_6night_operable_trap_status_v1 import published_trap_status


def _require(v:bool,msg:str)->None:
    if not v:raise ValueError("GENUS_REENCOUNTER_SOURCE_INVARIANT: "+msg)


def firstnight_reencounter(
    private:dict, traps:list[dict], genus_by_taxon:dict[str,str],
    *,
    selected_genera:tuple[str,str],
    selected_sites:set[str],
    minimum_marked_animals_per_genus_site:int=5,
    minimum_sites:int=6,
    bootstrap_seed:int=2026102601,
    bootstrap_draws:int=2000,
)->dict:
    """Returns aggregate same-bout recorded reencounter fractions, not ids.

    We preserve the pre-outcome selected physical site IDs exclusively
    in memory and never replace them after inspecting re-encounters.
    """
    _require(len(selected_genera)==2 and selected_genera[0]!=selected_genera[1],
             "Exactly two source-selected genus identities required")
    _require(bool(selected_sites),"Source preselected sites absent")
    _require(bootstrap_seed==2026102601 and bootstrap_draws==2000,
             "Fixed pre-outcome site bootstrap contract changed")
    tags=private["original_firstnight_tagged_animal_genus_by_event"]
    night_to_event=private["event_source_night_index"]
    first_night=private["event_source_dates"]
    candidate={
        (event,tag):genus for (event,tag),genus in tags.items()
        if genus in selected_genera and event[0] in selected_sites
    }
    _require(bool(candidate),"No originally source-selected first-night animals")
    night_coords=defaultdict(set)
    invalid_genus=set()
    for row in traps:
        night=str(row.get("nightuid") or "").strip()
        event=night_to_event.get(night)
        if event is None or event[0] not in selected_sites:
            continue
        if night==first_night.get(event):
            continue
        if (str(row.get("_site") or "").strip(),str(row.get("plotID") or "").strip())!=event[:2]:
            raise ValueError("Original source trap record mismatched event site/plot")
        c,valid=published_trap_status(row.get("trapStatus"))
        if not (valid and c in ("4","5")):
            continue
        tag=_normal_tag(row.get("tagID"))
        if tag is None or (event,tag) not in candidate:
            continue
        genus=genus_by_taxon.get(str(row.get("taxonID") or "").strip())
        if genus!=candidate[(event,tag)]:
            invalid_genus.add((event,tag))
            continue
        coord=_normal_coord(row.get("trapCoordinate"))
        if coord is None:
            invalid_genus.add((event,tag))
            continue
        night_coords[(event,tag,night)].add(coord)

    ambiguous={x[:2] for x,v in night_coords.items() if len(v)!=1}
    ambiguous.update(invalid_genus)
    kept={key:g for key,g in candidate.items() if key not in ambiguous}
    # Source gate must be reassessed WITHOUT computing the new re-encounter
    # numerator; a later-night invalid location can shrink the cohort.
    denominators=defaultdict(Counter)
    for (event,tag),genus in kept.items():
        denominators[event[0]][genus]+=1
    valid_sites=[
        site for site in sorted(selected_sites)
        if all(denominators[site][g]>=minimum_marked_animals_per_genus_site
               for g in selected_genera)
    ]
    if len(valid_sites)<minimum_sites or set(valid_sites)!=selected_sites:
        return {
            "status":"STOP_SOURCE_PAIRED_SITE_SUPPORT_AFTER_LATE_CAPTURE_CONFLICT_QC",
            "preselected_source_sites":len(selected_sites),
            "sites_retaining_source_minimum_after_conflict_QC":len(valid_sites),
            "source_ambiguous_late_tag_histories":len(ambiguous),
            "subsequent_rediscovery_rates_NOT_computed":True,
            "no_alternate_genus_pair_selected":True,
        }

    later={(event,tag) for event,tag,night in night_coords
           if (event,tag) in kept}
    numerical=defaultdict(Counter)
    for (event,tag),genus in kept.items():
        if event[0] not in selected_sites:
            continue
        numerical[event[0]][(genus,"captured_firstnight")]+=1
        numerical[event[0]][(genus,"subsequently_recaptured")]+=int(
            (event,tag) in later
        )
    by_genus={}
    for g in selected_genera:
        n=sum(numerical[s][(g,"captured_firstnight")] for s in valid_sites)
        k=sum(numerical[s][(g,"subsequently_recaptured")] for s in valid_sites)
        by_genus[g]={
            "firstnight_marked_animals":n,
            "recorded_reencountered_day2_or3":k,
            "pooled_recorded_reencounter_fraction":k/n,
            "physical_site_equal_reencounter_fraction":mean(
                numerical[s][(g,"subsequently_recaptured")]
                /numerical[s][(g,"captured_firstnight")]
                for s in valid_sites),
            "not_true_detection_probability":True,
        }
    first,second=selected_genera
    site_diff=[
        numerical[s][(first,"subsequently_recaptured")] /
        numerical[s][(first,"captured_firstnight")]
        -numerical[s][(second,"subsequently_recaptured")] /
        numerical[s][(second,"captured_firstnight")]
        for s in valid_sites
    ]
    observed=mean(site_diff)
    rng=Random(bootstrap_seed)
    boot=sorted(mean(site_diff[rng.randrange(len(site_diff))]
                     for _ in site_diff) for __ in range(bootstrap_draws))
    def pct(p):
        z=p*(len(boot)-1)
        k=int(z);j=min(k+1,len(boot)-1);frac=z-k
        return boot[k]*(1-frac)+boot[j]*frac
    low,high=pct(.025),pct(.975)
    _require(isfinite(observed) and isfinite(low) and isfinite(high),
             "Non-finite rate difference")
    return {
        "status":"OBSERVED_SITE_PAIRED_GENUS_REENCOUNTER_FRACTION_DESCRIBED",
        "preselected_genera":list(selected_genera),
        "original_source_selected_physical_sites":len(selected_sites),
        "source_matched_physical_sites_retained":len(valid_sites),
        "unique_firstnight_tag_histories_in_fitted_site_genus_pairs":sum(
            n["firstnight_marked_animals"] for n in by_genus.values()
        ),
        "site_equal_observed_genus_reencounter_fraction_difference":observed,
        "direction":"positive" if observed>0 else "negative" if observed<0 else "zero",
        "whole_physical_site_bootstrap":{
            "draws":bootstrap_draws,
            "seed":bootstrap_seed,
            "percentile_95_interval":[low,high],
            "interval_excludes_zero":low>0 or high<0,
            "not_independent_new_release_validation":True,
        },
        "original_recapture_record_summary_by_genus":by_genus,
        "source_ambiguous_late_tag_histories":len(ambiguous),
        "no_alternate_genus_pair_selected":True,
        "claim_boundaries":{
            "same_original_NEON_RELEASE_2026":True,
            "not_capture_detection_p_of_animal_at_trap":True,
            "not_available_to_recapture_if_dead_or_not_released_cannot_be_identified":True,
            "not_true_site_occupancy_or_movement":True,
            "cannot_directly_explain_historical_site_exact_trap_recurrence":True,
            "original_site_plot_trap_tag_day_or_individual_id_not_exported":True,
        },
    }
