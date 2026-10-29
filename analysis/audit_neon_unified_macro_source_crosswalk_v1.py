#!/usr/bin/env python3
"""Source-only NEON unified macroecology crosswalk.

Ask whether the 58 *already frozen* genus-recurrence season pairs contain
same-site/plot/event *structural opportunities* for within/among animal W/B
measurements from frozen target taxa. No W, B, recurrence, abundance slope,
habitat coefficient, taxon-specific outcome, or new p-value is calculated.

The historical 1326-session W/B development population is NOT reconstructed:
this source-only crosswalk does not condition on >=3 varying genus-MNKA
sessions or the previously calculated B variance. Its output is eligibility
for a possible joint *new cohort*, not a verified 1326↔58 exact effect join.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from datetime import date
import json
import os
from pathlib import Path

from analysis.audit_neon_crossseason_genus_support_v1 import (
    _events, _normal_coord, _normal_tag, _is_capture,
    source_event_support,
)
from analysis.audit_multiscale_density_mnka_variation_v1 import _taxonomy
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    PRODUCT,RELEASE,START,END,PRODUCT_URL,QUERY_URL,TOKEN_ENV,
    MAX_DOWNLOAD_WORKERS,_request_json,_site_codes,_inventory,
    _download_many,_read_plot_rows,_read_trap_rows,_candidate_nights,
)
from analysis.run_neon_crossseason_direct_site_null_calibration_v1 import (
    verified_support_gate,SOURCE_SUPPORT
)

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"results/multiscale_density_target_taxon_lock_v1.json"
OUTPUT=ROOT/"build/neon_unified_macro_source_crosswalk_v1.json"
MIN_REPEAT=5
SATURATION_MAX=.30
MIN_SITES=8
MIN_PAIR_MATCHES=20
MIN_MULTI_SITE_GENERA=3


def require(ok:bool,why:str):
    if not ok:
        raise ValueError("MACRO_SOURCE_INVARIANT_STOP: "+why)


def source_crosswalk(
    units:list[dict], selected:dict, trap_rows:list[dict],
    target_taxa:set[str], genus_by_taxon:dict[str,str], *,
    expected_units:int=58, expected_sites:int=14,
    expected_plots:int=30,
    min_sites:int=MIN_SITES,min_pairs:int=MIN_PAIR_MATCHES,
    min_multi_site_genera:int=MIN_MULTI_SITE_GENERA,
)->dict:
    """Aggregate source-event overlap, without exporting original identities.

    selected: existing _events plot metadata keyed by (site,plot,event).
    units: frozen eligible pair cohort, with date tuples and supported genera.
    """
    require(len(units)==expected_units,"original seasonal pair count changed")
    require(len({u["site"] for u in units})==expected_sites,
            "original physical-site universe changed")
    require(len({tuple(u["site_plot"]) for u in units})==expected_plots,
            "original plot universe changed")
    require(bool(target_taxa) and bool(genus_by_taxon),
            "original target taxonomy unavailable")
    frozen_event_index={}
    for key,info in selected.items():
        if not isinstance(info.get("dates"),tuple):
            raise ValueError("Source event lacks exact date tuple")
        ref=(key[0],key[1],info["dates"])
        require(ref not in frozen_event_index,"source date/event key not unique")
        frozen_event_index[ref]=key
    pair_events=[]
    for u in units:
        site,plot=u["site_plot"]
        require(u["site"]==site,"original site/plot mismatch")
        e_a=frozen_event_index.get((site,plot,tuple(u["capture_dates_A"])))
        e_b=frozen_event_index.get((site,plot,tuple(u["capture_dates_B"])))
        require(e_a is not None and e_b is not None and e_a!=e_b,
                "original frozen seasonal pair cannot map to exact events")
        require(set(u["A"])==set(u["B"]) and len(u["A"])>=3,
                "original eligible genera changed or not aligned")
        pair_events.append((u,e_a,e_b))
    original_keys={k for _,a,b in pair_events for k in (a,b)}
    require(all(k in selected for k in original_keys),
            "frozen source event missing from approved selected events")

    # Build a night-to-event map for ONLY originally eligible pair events.
    night_to_event={}
    for key in original_keys:
        for n in selected[key]["nights"]:
            require(n not in night_to_event or night_to_event[n]==key,
                    "one source night in multiple cohort events")
            night_to_event[n]=key

    effort=defaultdict(set)
    all_capture_stations=defaultdict(set)
    tag_taxa=defaultdict(set)
    same_night_stations=defaultdict(set)
    target_taxon_tag_nights=defaultdict(set)
    source_status=Counter()
    for r in trap_rows:
        key=night_to_event.get(str(r.get("nightuid") or "").strip())
        if key is None: continue
        if str(r.get("_site") or "").strip()!=key[0] or str(r.get("plotID") or "").strip()!=key[1]:
            raise ValueError("source event site/plot membership invalid")
        night=str(r["nightuid"]).strip()
        pos=_normal_coord(r.get("trapCoordinate"))
        if pos:
            effort[key].add((night,pos))
        if not _is_capture(r.get("trapStatus")):
            continue
        if pos:
            all_capture_stations[key].add((night,pos))
        tag=_normal_tag(r.get("tagID"))
        taxon=str(r.get("taxonID") or "").strip()
        if not tag or not taxon:
            source_status["capture_missing_taxon_or_tag"]+=1
            continue
        # Original W/B QC excludes event×tag IDs with conflicting taxon
        # labels; the target-taxon filter is applied only AFTER that check.
        tag_taxa[(key,tag)].add(taxon)
        if pos and taxon in target_taxa and genus_by_taxon.get(taxon):
            same_night_stations[(key,tag,night)].add(pos)
            target_taxon_tag_nights[(key,taxon,tag)].add(night)

    qualified_taxa=defaultdict(set)
    candidate=Counter()
    for key in original_keys:
        denom=len(effort[key])
        require(denom>0,"original event has no actual trap-night effort")
        sat=len(all_capture_stations[key])/denom
        if sat>SATURATION_MAX:
            candidate["event_saturation_gt_guard"]+=1
            continue
        candidate["events_passing_saturation"]+=1
        by_taxon=defaultdict(int)
        for (event,taxon,tag),nightset in target_taxon_tag_nights.items():
            if event!=key:
                continue
            if len(tag_taxa[(key,tag)])>1:
                continue
            if len(nightset)<2:
                continue
            if any(len(same_night_stations[(key,tag,n)])!=1 for n in nightset):
                continue
            by_taxon[taxon]+=1
        for taxon,count in by_taxon.items():
            if count>=MIN_REPEAT:
                genus=genus_by_taxon[taxon]
                qualified_taxa[key].add(genus)
                candidate["taxon_event_at_least_five_repeat_individuals"]+=1

    by_site=defaultdict(int)
    genus_sites=defaultdict(set)
    pair_match=0
    genus_pair_match=0
    pairs_both_have_any=0
    pairs_genus_same=0
    pairs_no_repeat_opportunity=0
    for u,a,b in pair_events:
        ga=qualified_taxa[a] & set(u["A"])
        gb=qualified_taxa[b] & set(u["B"])
        if ga and gb:
            pairs_both_have_any+=1
        matches=ga&gb
        if matches:
            pair_match+=1
            genus_pair_match+=len(matches)
            pairs_genus_same+=1
            by_site[u["site"]]+=1
            for genus in matches:
                genus_sites[genus].add(u["site"])
        else:
            pairs_no_repeat_opportunity+=1
    multi_site_genera=sum(len(sites)>=2 for sites in genus_sites.values())
    independent_sites=len(by_site)
    suitable=(independent_sites>=min_sites and pair_match>=min_pairs
              and multi_site_genera>=min_multi_site_genera)
    require(pair_match+pairs_no_repeat_opportunity==len(units),
            "matched and unmatched fixed pairs fail to partition source")

    return {
        "schema":"neon.unified_macro.source_only_joint_eligibility.v1",
        "status":("CANDIDATE_MATCHED_RESPONSES_SOURCE_GO" if suitable
                  else "STOP_MATCHED_RESPONSES_NOT_STRUCTURALLY_GENERAL"),
        "original_source":{"frozen_season_pairs":len(units),
                           "sites":expected_sites,"plots":expected_plots,
                           "distinct_season_events":len(original_keys),
                           "genera_per_pair_at_least_three":True},
        "w_b_structural_opportunity":{
            "taxon_concepts_considered_from_original_lock":len(target_taxa),
            "min_repeated_tagged_individuals_per_taxon_event":MIN_REPEAT,
            "max_all_capture_trap_night_fraction":SATURATION_MAX,
            "events_passing_saturation":candidate["events_passing_saturation"],
            "qualifying_target_taxon_event_units":candidate["taxon_event_at_least_five_repeat_individuals"],
            "events_with_one_or_more_repeated_target_genera":sum(bool(qualified_taxa[x]) for x in original_keys),
            "not_the_historical_full_1326_session_W_B_fit":True,
            "genus_mnka_across_time_not_computed":True,
        },
        "exact_pair_crosswalk":{
            "pairs_with_repeat_supported_taxon_genus_in_both_events_any_genus":pairs_both_have_any,
            "pairs_with_same_original_recurrence_genus_repeat_supported_in_both_events":pair_match,
            "distinct_physical_sites_with_matched_pairs":independent_sites,
            "distinct_original_plots_with_matched_pairs":len({tuple(u["site_plot"]) for u,a,b in pair_events if (qualified_taxa[a]&qualified_taxa[b]&set(u["A"]))}),
            "matched_genus_pair_opportunities":genus_pair_match,
            "distinct_matched_genera":len(genus_sites),
            "genera_with_matched_pairs_across_at_least_two_sites":multi_site_genera,
            "pairs_with_no_same_genus_repeat_support":pairs_no_repeat_opportunity,
        },
        "new_post_result_source_feasibility_gates":{
            "minimum_independent_sites":min_sites,
            "minimum_original_matched_season_pairs":min_pairs,
            "minimum_replicated_genera":min_multi_site_genera,
            "pass":suitable,
            "not_retroactive_original_preregistration":True,
        },
        "limitations":{
            "complete_historical_W_B_analysis_session_joined":False,
            "actual_W_B_m2_calculated":False,
            "recurrence_Z_recomputed":False,
            "joint_spatial_recurrence_density_effect_computed":False,
            "site_genus_or_animal_identity_exported":False,
            "no_biotic_interaction_habitat_or_detection_mechanism_claimed":True,
            "old_eight_genus_density_generalization_still_failed":True,
            "all_tests_are_source_only":True,
            "interpretation":"source-only candidate exact same-population event overlap; does not identify joint ecological effects or reproduce frozen W/B outcome-population membership",
        },
    }


def run()->dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    require(bool(token),"original NEON release authorization unavailable")
    require((RELEASE,START,END)==("RELEASE-2026","2015-04","2026-09"),
            "source release/month selection changed")
    frozen=json.loads(SOURCE_SUPPORT.read_text(encoding="utf-8"))
    target=set(json.loads(TARGET.read_text(encoding="utf-8"))["target_taxon_ids"])
    all_target,genus_by_taxon,_=_taxonomy()
    require(target.issubset(all_target),"frozen target taxa not covered by current lookup")
    sites=_site_codes(_request_json(PRODUCT_URL))
    inventory=_inventory(_request_json(QUERY_URL,token=token,body={
        "productCode":PRODUCT,"siteCodes":sites,"startDateMonth":START,
        "endDateMonth":END,"release":RELEASE,"package":"basic",
        "includeProvisional":False,
    }))
    pf=[x for x in inventory if "mam_perplotnight" in x["name"]]
    require(len(inventory)==3547 and len(pf)==1773,
            "original release inventory changed")
    plots=[]
    for m,raw in zip(pf,_download_many(pf,token,max_workers=MAX_DOWNLOAD_WORKERS)):
        plots.extend(_read_plot_rows(raw,m["site"],m["month"]))
    nights,months=_candidate_nights(plots)
    tf=[x for x in inventory
        if "mam_pertrapnight" in x["name"] and (x["site"],x["month"]) in months]
    require(len(tf)==1707,"original trap-file count changed")
    traps=[]
    for m,raw in zip(tf,_download_many(tf,token,max_workers=MAX_DOWNLOAD_WORKERS)):
        for row in _read_trap_rows(raw,nights):
            row["_site"]=m["site"]
            traps.append(row)
    require((len(plots),len(traps))==(21363,1505827),
            "original release canonical row counts changed")
    units=[]
    support=source_event_support(plots,traps,genus_by_taxon,internal_units=units)
    verified_support_gate(support,frozen)
    selected,_,_=_events(plots)
    result=source_crosswalk(units,selected,traps,target,genus_by_taxon)
    return {
        **result,"provenance":{
            "release":RELEASE,"manifest_files_verified":len(inventory),
            "downloaded_checksum_size_verified_capture_files":len(pf)+len(tf),
            "original_source_support_recomputed_and_frozen_check_passed":True,
            "linked_observational_effects_opened":False,
            "original_2026_release_already_consumed":True,
        },
    }


def main()->int:
    try:
        out=run()
        exitcode=0 # An honest scientific structural STOP is not code failure.
    except Exception as exc:
        out={
            "schema":"neon.unified_macro.source_only_joint_eligibility.v1",
            "status":"STOP_SOURCE_AUDIT_FAILURE",
            "source_error_class":type(exc).__name__,
            "private_exception_message_suppressed":True,
            "site_genus_trap_animal_ids_exported":False,
            "W_B_or_recurrence_effects_opened":False,
        }
        exitcode=3
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return exitcode


if __name__=="__main__":
    raise SystemExit(main())
