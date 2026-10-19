#!/usr/bin/env python3
"""Effect-blind seasonal lineage recurrence *eligibility*, original NEON source.

No genus×trap cross-season intersection, no ecological overlap statistic,
no habitat effect, no movement, W/B, density or selection on outcomes.
The output is population-level aggregate support ONLY. Actual animal
identifiers and site IDs remain transient in RAM and are not returned.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
import re

COMPLETE="setting complete, processing complete"
LATTICE=re.compile(r"^([A-J])0?([1-9]|10)$",re.IGNORECASE)
MISSING={"","NA","N/A","NULL","NONE","NAN"}
MIN_TRAPS_PER_NIGHT=90


def season_ordinal(d: date) -> int:
    """Ordered winter/spring/summer/autumn seasons; Dec belongs next year."""
    if d.month in (12,1,2):
        year=d.year+(d.month==12)
        quarter=0
    elif d.month in (3,4,5):
        year=d.year
        quarter=1
    elif d.month in (6,7,8):
        year=d.year
        quarter=2
    else:
        year=d.year
        quarter=3
    return 4*int(year)+quarter


def _normal_tag(value: object) -> str | None:
    s=str(value or "").strip()
    return s if s.upper() not in MISSING else None


def _normal_coord(value: object) -> str | None:
    text=str(value or "").strip().upper()
    m=LATTICE.fullmatch(text)
    if not m:
        return None
    return m.group(1)+str(int(m.group(2)))


def _is_capture(status: object) -> bool:
    s=str(status or "").lower().strip()
    return "capture" in s and "no capture" not in s


def _events(plot_rows: list[dict]):
    groups=defaultdict(list)
    for r in plot_rows:
        site=str(r.get("_site") or r.get("siteID") or "").strip()
        plot=str(r.get("plotID") or "").strip()
        event=str(r.get("eventID") or "").strip()
        if not site or not plot or not event:
            continue
        if site != str(r.get("siteID") or site).strip():
            raise ValueError("NEON source siteID differs from inventory site")
        groups[(site,plot,event)].append(r)
    approved={}
    rejected=Counter()
    season_candidates=defaultdict(list)
    for key,rows in groups.items():
        site,plot,event=key
        if site=="SRER":
            rejected["special_nonsquare_site_sessions"]+=1
            continue
        nights={str(r.get("nightuid") or "").strip() for r in rows}
        if len(nights)!=3 or "" in nights:
            rejected["not_exact_three_night_events"]+=1
            continue
        if any(str(r.get("gridCompletion") or "").strip().lower()!=COMPLETE for r in rows):
            rejected["not_complete_events"]+=1
            continue
        try:
            dates={date.fromisoformat(str(r.get("collectDate") or "")[:10])
                   for r in rows}
        except ValueError:
            rejected["unparseable_capture_date_events"]+=1
            continue
        if len(dates)!=3 or (max(dates)-min(dates)).days>3:
            rejected["not_three_protocol_calendar_dates"]+=1
            continue
        seasons={season_ordinal(d) for d in dates}
        if len(seasons)!=1:
            rejected["straddles_meteorological_season_events"]+=1
            continue
        ordinal=next(iter(seasons))
        d0=min(dates)
        info={"site":site,"plot":plot,"event":event,"season":ordinal,
              "first":d0,"nights":nights}
        approved[key]=info
        season_candidates[(site,plot,ordinal)].append(info)
    chosen={}
    for key,vals in season_candidates.items():
        choice=min(vals,key=lambda x:(x["first"],x["event"]))
        chosen[(choice["site"],choice["plot"],choice["event"])]=choice
    rejected["alternative_bouts_in_same_season"]+=len(approved)-len(chosen)
    return chosen,rejected,approved


def source_event_support(
    plot_rows: list[dict],
    trap_rows: list[dict],
    genus_by_taxon: dict[str,str],
    *,
    internal_units: list[dict] | None = None,
) -> dict:
    """Count biologically viable adjacent-season genus replacement contrasts.

    Requires >=90 observed unique trap stations per night and >=2
    season-exclusive tags and >=2 trap positions for >=3 shared genera.
    All site, animal, trap and taxon source tokens are removed from output.
    """
    selected,rejected,all_approved=_events(plot_rows)
    if not isinstance(genus_by_taxon,dict) or not genus_by_taxon:
        raise ValueError("Authoritative target taxonomy is required")
    night_to_event={}
    for key,info in all_approved.items():
        for n in info["nights"]:
            if n in night_to_event and night_to_event[n]!=key:
                raise ValueError("One nightUID belongs to multiple source events")
            night_to_event[n]=key
    # Tag ID genus provenance is computed across *all* exact completed
    # events; selected events alone could miss source taxon conflicts.
    tag_genera=defaultdict(set)
    effort=defaultdict(set)
    captured_coords=defaultdict(set)
    ignored=Counter()
    for row in trap_rows:
        site=str(row.get("_site") or "").strip()
        plot=str(row.get("plotID") or "").strip()
        night=str(row.get("nightuid") or "").strip()
        key=night_to_event.get(night)
        if key is None or key[0]!=site or key[1]!=plot:
            continue
        coord=_normal_coord(row.get("trapCoordinate"))
        if not coord:
            ignored["noncanonical_station_rows"]+=1
        if key in selected and coord:
            effort[(key,night)].add(coord)
        if not _is_capture(row.get("trapStatus")):
            continue
        taxon=str(row.get("taxonID") or "").strip()
        genus=genus_by_taxon.get(taxon)
        tag=_normal_tag(row.get("tagID"))
        if not tag or not genus:
            ignored["capture_without_target_genus_or_tag"]+=1
            continue
        tag_genera[(site,plot,tag)].add(genus)
        if key in selected and coord:
            captured_coords[(key,night,tag)].add(coord)

    genus_conflicts={tag for tag,v in tag_genera.items() if len(v)>1}
    ambiguous_tag_events=set()
    for (event,night,tag),coords in captured_coords.items():
        if len(coords)>1:
            ambiguous_tag_events.add((event,tag))

    valid_events={}
    for key,info in selected.items():
        if all(len(effort.get((key,n),set()))>=MIN_TRAPS_PER_NIGHT
               for n in info["nights"]):
            valid_events[key]=info
        else:
            rejected["selected_event_effort_lt_90_one_or_more_nights"]+=1
    by_grid_season=defaultdict(dict)
    for key,info in valid_events.items():
        by_grid_season[(info["site"],info["plot"])][info["season"]]=key

    # Construct the structural genus × season-exclusive animal/trap sets.
    event_tags=defaultdict(lambda:defaultdict(set))
    event_coords=defaultdict(lambda:defaultdict(set))
    for (key,night,tag),coords in captured_coords.items():
        if key not in valid_events or (key,tag) in ambiguous_tag_events:
            continue
        identity=(key[0],key[1],tag)
        if identity in genus_conflicts:
            continue
        label_set=tag_genera.get(identity)
        if label_set is None or len(label_set)!=1:
            continue
        genus=next(iter(label_set))
        event_tags[key][genus].add(tag)
        event_coords[key][(genus,tag)].update(coords)

    total=Counter()
    support_sites=set()
    support_plots=set()
    eligible_events=set()
    eligible_years=set()
    genus_counts=Counter()
    bridge_total=0
    valid_candidate_pairs=0
    for (site,plot),season_map in by_grid_season.items():
        for q,key_a in season_map.items():
            if q+1 not in season_map:
                continue
            valid_candidate_pairs+=1
            key_b=season_map[q+1]
            common_tags=(set().union(*event_tags[key_a].values()) if event_tags[key_a] else set()
                        ) & (set().union(*event_tags[key_b].values()) if event_tags[key_b] else set())
            bridge_total+=len(common_tags)
            genera=set(event_tags[key_a])&set(event_tags[key_b])
            eligible=[]
            for genus in genera:
                tags_a=event_tags[key_a][genus]-common_tags
                tags_b=event_tags[key_b][genus]-common_tags
                if len(tags_a)<2 or len(tags_b)<2:
                    continue
                coords_a=set().union(*(event_coords[key_a][(genus,t)] for t in tags_a))
                coords_b=set().union(*(event_coords[key_b][(genus,t)] for t in tags_b))
                if len(coords_a)>=2 and len(coords_b)>=2:
                    eligible.append(genus)
            if len(eligible)>=2:
                total["eligible_2genus_diagnostic_pairs"]+=1
            if len(eligible)>=3:
                # A caller may request an IN-MEMORY private occupancy unit
                # after the frozen structural GO. The public support JSON
                # never serializes these source site/trap/genus matrices.
                if internal_units is not None:
                    internal_units.append({
                        "site":site,
                        "site_plot":(site,plot),
                        "season_ordinal":q,
                        "A":{
                            genus:set().union(*(
                                event_coords[key_a][(genus,t)]
                                for t in sorted(event_tags[key_a][genus]-common_tags)
                            ))
                            for genus in sorted(eligible)
                        },
                        "B":{
                            genus:set().union(*(
                                event_coords[key_b][(genus,t)]
                                for t in sorted(event_tags[key_b][genus]-common_tags)
                            ))
                            for genus in sorted(eligible)
                        },
                    })
                total["eligible_primary_pairs"]+=1
                support_sites.add(site)
                support_plots.add((site,plot))
                eligible_events.update((key_a,key_b))
                eligible_years.add((q//4,(q+1)//4))
                genus_counts[len(eligible)]+=1
            else:
                total["rejected_fewer_than_three_shared_replaced_genera"]+=1

    eligibility_sites=len(support_sites)
    eligibility_pairs=int(total["eligible_primary_pairs"])
    return {
        "schema":"neon.crossseason_genus_individual_replacement_support.v1",
        "status":(
            "SOURCE_STRUCTURAL_GO_OUTCOME_SEALED"
            if eligibility_sites>=8 and eligibility_pairs>=20
            else "STOP_NOT_ENOUGH_INDEPENDENT_GENUS_REPLACEMENT_UNITS"
        ),
        "approved_original_three_night_sessions":len(all_approved),
        "eligible_distinct_selected_events":len(eligible_events),
        "selected_one_bout_per_season_sessions":len(selected),
        "selected_bouts_with_trap_effort_ge90_per_night":len(valid_events),
        "candidate_adjacent_season_pairs_after_effort":valid_candidate_pairs,
        "eligible_primary_pairs":eligibility_pairs,
        "eligible_primary_sites":eligibility_sites,
        "eligible_primary_site_plot_units":len(support_plots),
        "eligible_primary_season_year_combinations":len(eligible_years),
        "eligible_2genus_diagnostic_pairs":int(total["eligible_2genus_diagnostic_pairs"]),
        "primary_shared_genus_count_distribution":{
            str(key):value for key,value in sorted(genus_counts.items())
        },
        "bridge_tag_histories_excluded":bridge_total,
        "cross_genus_identity_conflicts":len(genus_conflicts),
        "ambiguous_same_night_tag_event_combinations":len(ambiguous_tag_events),
        "event_source_exclusion_categories":dict(rejected),
        "capture_source_exclusion_categories":dict(ignored),
        "source_target_taxonomic_rank":"genus",
        "no_source_individual_or_geographic_ids_exported":True,
        "known_individuals_shared_betweenseason_excluded":True,
        "three_night_complete_bouts_only":True,
        "source_genus_trap_occupancy_A_B_calculated":False,
        "crossseason_spatial_overlap_opened":False,
        "crossseason_permutation_null_opened":False,
        "W_B_density_effects_opened":False,
        "ecological_recurrence_claim_authorized":False,
        "original_density_generality":"FAILED_5_OF_8",
        "MOSA_spatial_effects":"SEALED"
    }
