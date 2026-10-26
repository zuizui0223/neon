"""Source-only first-night marked-cohort support for NEON genus re-encounters.

Scans later capture rows only to exclude globally conflicting tag/genus
identities, NEVER matches/quantifies second- or third-night re-encounters.
Original 158 exactly-two-genus pairs and 293 uniquely selected trapping
bouts. A first-night marked individual is not necessarily a newly tagged
individual, and a subsequent re-encounter is not true detection p.
"""
from __future__ import annotations

from collections import defaultdict,Counter
from datetime import date
from itertools import combinations

from analysis.audit_neon_crossseason_genus_support_v1 import (
    _events,_normal_tag,_normal_coord
)
from analysis.neon_macro_6night_operable_trap_status_v1 import published_trap_status


def source_first_night_cohort(
    units:list[dict],plots:list[dict],traps:list[dict],
    genus_by_taxon:dict[str,str],
    *,
    expected_pairs:int=158,expected_sites:int=30,
    expected_unique_bouts:int=293,
    minimum_firstnight_animals:int=400,
    minimum_sites_with_animal:int=15,
    minimum_genus_animals:int=100,
    minimum_genus_sites:int=6,
    minimum_shared_sites:int=6,
    minimum_per_genus_per_site:int=5,
)->tuple[dict,dict]:
    """Output aggregate-only source receipt and transient selected cohort.

    Never examines second- or third-night matching of original tags.
    Scanning taxonomy consistency throughout source is a QC step only.
    """
    if len(units)!=expected_pairs or len({u["site"] for u in units})!=expected_sites:
        raise ValueError("Original exact-two source cohort changed")
    if not isinstance(genus_by_taxon,dict) or not genus_by_taxon:
        raise ValueError("Original authoritative taxonomic source missing")

    chosen,rejected,all_approved=_events(plots)
    indexed={}
    for key,meta in chosen.items():
        date_key=(key[0],key[1],meta["dates"])
        if date_key in indexed:
            raise ValueError("Two source bouts share a site/plot/date tuple")
        indexed[date_key]=key
    bout_genera=defaultdict(set)
    for u in units:
        site,plot=u["site_plot"]
        if u["site"]!=site or set(u["A"])!=set(u["B"]) or len(u["A"])!=2:
            raise ValueError("Original selected genus/site key drifted")
        for days in (tuple(u["capture_dates_A"]),tuple(u["capture_dates_B"])):
            key=indexed.get((site,plot,days))
            if key is None:
                raise ValueError("Selected original genus bout date not found")
            bout_genera[key].update(u["A"].keys())
    if len(bout_genera)!=expected_unique_bouts:
        raise ValueError("Original unique pair-linked three-night bouts drifted")

    # Resolve night dates directly from perplotnight, never lexicographic
    # nightuid order or CSV row order.
    night_to_date={}
    for row in plots:
        site=str(row.get("_site") or row.get("siteID") or "").strip()
        plot=str(row.get("plotID") or "").strip()
        night=str(row.get("nightuid") or "").strip()
        if not site or not plot or not night:
            continue
        try:
            d=date.fromisoformat(str(row.get("collectDate") or "")[:10])
        except ValueError:
            continue
        k=(site,plot,night)
        if k in night_to_date and night_to_date[k]!=d:
            raise ValueError("Night UID mapped to conflicting source dates")
        night_to_date[k]=d
    first_night={}
    first_index={}
    for event in bout_genera:
        meta=chosen[event]
        nights=sorted(meta["nights"],
                     key=lambda n:(night_to_date.get((event[0],event[1],n),date.min),n))
        if len(nights)!=3 or any((event[0],event[1],n) not in night_to_date for n in nights):
            raise ValueError("Source three-night calendars unavailable")
        if tuple(night_to_date[(event[0],event[1],n)] for n in nights)!=meta["dates"]:
            raise ValueError("Source-night chronology differs from frozen selected calendar")
        first_night[event]=nights[0]
        for night in nights:
            if night in first_index and first_index[night]!=event:
                raise ValueError("One source night assigned multiple selected bouts")
            first_index[night]=event

    # Respect taxonomic conflicts across ALL originally approved bouts at
    # same site/plot; not just events seen in an eligible two-genus pair.
    approved_nights={}
    for event,meta in all_approved.items():
        for night in meta["nights"]:
            if night in approved_nights and approved_nights[night]!=event:
                raise ValueError("One night in multiple approved bouts")
            approved_nights[night]=event
    global_tag_genera=defaultdict(set)
    first_tag_coords=defaultdict(set)
    first_tag_candidate_genus=defaultdict(set)
    raw=Counter()
    for row in traps:
        night=str(row.get("nightuid") or "").strip()
        ev=approved_nights.get(night)
        if ev is None:
            continue
        if (str(row.get("_site") or "").strip(),str(row.get("plotID") or "").strip())!=ev[:2]:
            raise ValueError("Approved mammal source site/plot/night mismatch")
        code,valid=published_trap_status(row.get("trapStatus"))
        if not (valid and code in ("4","5")):
            continue
        tag=_normal_tag(row.get("tagID"))
        genus=genus_by_taxon.get(str(row.get("taxonID") or "").strip())
        if tag is None or not genus:
            raw["capture_missing_mark_or_authoritative_target_genus"]+=1
            continue
        global_tag_genera[(ev[0],ev[1],tag)].add(genus)
        if ev in bout_genera and night==first_night[ev] and genus in bout_genera[ev]:
            pos=_normal_coord(row.get("trapCoordinate"))
            if pos is None:
                raw["invalid_first_night_named_station"]+=1
                continue
            first_tag_coords[(ev,tag)].add(pos)
            first_tag_candidate_genus[(ev,tag)].add(genus)
            raw["qualified_first_night_rows_before_conflict_resolution"]+=1

    by_genus_site=defaultdict(lambda:defaultdict(int))
    source_tags={}
    problems=Counter()
    for (ev,tag),coords in first_tag_coords.items():
        label=first_tag_candidate_genus[(ev,tag)]
        all_labels=global_tag_genera[(ev[0],ev[1],tag)]
        if len(coords)!=1:
            problems["multi_location_same_tag_first_night"]+=1
            continue
        if len(label)!=1 or len(all_labels)!=1 or label!=all_labels:
            problems["ambiguous_original_source_tag_genus"]+=1
            continue
        genus=next(iter(label))
        by_genus_site[genus][ev[0]]+=1
        source_tags[(ev,tag)]=genus

    site_n=len({ev[0] for ev,tag in source_tags})
    exposed=len(source_tags)
    candidate=[]
    genera=sorted(by_genus_site)
    totals={g:sum(by_genus_site[g].values()) for g in genera}
    for g1,g2 in combinations(genera,2):
        if min(totals[g1],totals[g2])<minimum_genus_animals:
            continue
        if min(len(by_genus_site[g1]),len(by_genus_site[g2]))<minimum_genus_sites:
            continue
        common=sorted(site for site in by_genus_site[g1]
                      if by_genus_site[g1][site]>=minimum_per_genus_per_site
                      and by_genus_site[g2].get(site,0)>=minimum_per_genus_per_site)
        if len(common)<minimum_shared_sites:
            continue
        candidate.append((g1,g2,common))
    candidate.sort(key=lambda x:(-min(totals[x[0]],totals[x[1]]),
                                  -(totals[x[0]]+totals[x[1]]),
                                  x[0],x[1]))
    enough=exposed>=minimum_firstnight_animals and site_n>=minimum_sites_with_animal
    passed=enough and bool(candidate)
    chosen_genus=candidate[0] if passed else None
    eligible_genus_coverage=sorted(
        ({"genus":g,"first_night_tagged_animals":totals[g],
          "physical_sites_with_first_night_animals":len(by_genus_site[g])}
         for g in genera if totals[g]>=minimum_genus_animals and
         len(by_genus_site[g])>=minimum_genus_sites),
        key=lambda z:(-z["first_night_tagged_animals"],z["genus"])
    )
    report={
        "schema":"neon.macro.genus_firstnight_reencounter_source.v1",
        "status":"SOURCE_MATCHED_GENUS_REENCOUNTER_COMPARISON_GO" if passed else
                 "STOP_GENUS_REENCOUNTER_COMPARATOR_SOURCE_SUPPORT",
        "original_exact_two_season_pairs":len(units),
        "original_independent_physical_sites":expected_sites,
        "unique_source_three_night_bouts":len(bout_genera),
        "source_firstnight_marked_animals":exposed,
        "independent_sites_with_firstnight_tagged_captures":site_n,
        "number_of_genera_with_one_plus_firstnight_captures":len(genera),
        "original_firstnight_capture_source_rejections":dict(sorted(problems.items())),
        "source_firstnight_rows":dict(sorted(raw.items())),
        "genera_passing_predeclared_individual_and_site_marginal_support":eligible_genus_coverage,
        "genera_with_potential_matched_site_comparisons":len({g for a,b,c in candidate for g in (a,b)}),
        "number_of_source_supported_genus_pairs":len(candidate),
        "preselected_genus_pair_if_pass":{
            "genera":[chosen_genus[0],chosen_genus[1]],
            "shared_qualified_physical_sites":len(chosen_genus[2]),
            "firstnight_all_sites_animals":[totals[chosen_genus[0]],totals[chosen_genus[1]]],
            "source_selected_only_by_firstnight_exposures":True,
        } if chosen_genus else None,
        "predeclared_source_gate":{
            "minimum_original_firstnight_tagged_animals":minimum_firstnight_animals,
            "minimum_overall_independent_sites":minimum_sites_with_animal,
            "minimum_firstnight_animals_per_genus":minimum_genus_animals,
            "minimum_sites_per_genus":minimum_genus_sites,
            "minimum_common_sites":minimum_shared_sites,
            "minimum_firstnight_animals_per_genus_per_shared_site":minimum_per_genus_per_site,
            "passed":passed,
            "no_nextnight_matching_outcomes_opened":True,
        },
        "limits":{
            "this_source_cohort_is_not_the_historical_exact_station_Z_effect":True,
            "unknown_fate_of_firstnight_tagged_individuals":True,
            "nextnight_recapture_not_equal_true_genus_detection_p":True,
            "tag_genus_conflicts_and_ambiguous_same_night_stations_excluded":True,
            "bout_duplicate_use_across_adjacent_season_comparisons_removed":True,
            "site_plot_trap_night_tag_exact_dates_not_exported":True,
            "historic_density_temperature_operability_source_failures_unchanged":True,
        }
    }
    private={
        "original_firstnight_tagged_animal_genus_by_event":source_tags,
        "source_selected_genus_pair":chosen_genus,
        "firstnight_site_genus_counts":by_genus_site,
        "event_source_night_index":first_index,
        "event_source_dates":first_night,
    }
    return report,private
