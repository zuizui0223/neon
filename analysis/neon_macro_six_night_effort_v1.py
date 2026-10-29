"""Effect-blind six-night recorded trap opportunity source audit.

Recorded `mam_pertrapnight` rows are not calibrated trap functionality;
this measures *documented station opportunity* only. Keeps original
taxon ID exclusions, three-night event calendars and 158 exact-two
source pair keys unchanged. No observed cross-season overlap is opened.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from statistics import median
from analysis.audit_neon_crossseason_genus_support_v1 import (
    _events,_normal_coord,_is_capture,
)


def _checked_status(status:object)->bool:
    s=str(status or "").strip().lower()
    return _is_capture(status) or "no capture" in s


def recorded_station_opportunity(
    original_two:list[dict],
    plot_rows:list[dict],
    trap_rows:list[dict],
    domain_by_site:dict[str,str],
    *,
    expected_pairs:int=158,
    expected_sites:int=30,
    minimum_all_six_stations:int=90,
    min_selected_pairs:int=80,
    min_selected_sites:int=18,
    min_selected_domains:int=10,
)->tuple[dict,list[dict]]:
    """Return safe aggregate receipt and transient private restricted matrices."""
    if len(original_two)!=expected_pairs or len({u["site"] for u in original_two})!=expected_sites:
        raise ValueError("Original exactly-two source population drift")
    chosen,_,_=_events(plot_rows)
    by_date={}
    for key,meta in chosen.items():
        identity=(key[0],key[1],meta["dates"])
        if identity in by_date:
            raise ValueError("One original site plot date-set has multiple chosen events")
        by_date[identity]=key

    pairs=[]
    events={}
    for u in original_two:
        site,plot=tuple(u["site_plot"])
        if site!=u["site"] or site not in domain_by_site:
            raise ValueError("Original site or official domain metadata unavailable")
        assert len(u["A"])==len(u["B"])==2
        keyA=by_date.get((site,plot,tuple(u["capture_dates_A"])))
        keyB=by_date.get((site,plot,tuple(u["capture_dates_B"])))
        if keyA is None or keyB is None or keyA==keyB:
            raise ValueError("Original source event dates cannot match selected six nights")
        events[keyA]=chosen[keyA]
        events[keyB]=chosen[keyB]
        pairs.append((u,keyA,keyB))
    night_index={}
    for key,meta in events.items():
        if len(meta["nights"])!=3:
            raise ValueError("Source event no longer has three nights")
        for n in meta["nights"]:
            if n in night_index and night_index[n]!=key:
                raise ValueError("Original source night reused across events")
            night_index[n]=key
    effort=defaultdict(set)
    explicitly_checked=defaultdict(set)
    status_summary=Counter()
    for row in trap_rows:
        night=str(row.get("nightuid") or "").strip()
        key=night_index.get(night)
        if key is None:
            continue
        if (str(row.get("_site") or "").strip(),str(row.get("plotID") or "").strip())!=key[:2]:
            raise ValueError("Trap station source row mapped to wrong plot")
        station=_normal_coord(row.get("trapCoordinate"))
        if station is None:
            status_summary["noncanonical_record"]+=1
            continue
        effort[(key,night)].add(station)
        if _checked_status(row.get("trapStatus")):
            explicitly_checked[(key,night)].add(station)
            status_summary["explicit_capture_or_no_capture"]+=1
        else:
            status_summary["status_does_not_show_capture_or_no_capture"]+=1

    common_sizes=[]
    checked_sizes=[]
    supports=[]
    retained=[]
    bydomain=defaultdict(lambda:{"source_pairs":0,"recorded_six_night_eligible_pairs":0})
    byyear=Counter()
    original_station_retention=Counter()
    for u,a,b in pairs:
        nights=tuple(sorted(events[a]["nights"]))+tuple(sorted(events[b]["nights"]))
        if len(nights)!=6:
            raise ValueError("Original six sampling nights malformed")
        required=[effort[(k,n)] for k,n in ((a,x) for x in nights[:3])]
        required += [effort[(b,n)] for n in nights[3:]]
        common=set.intersection(*required) if required else set()
        checked=[explicitly_checked[(a,n)] for n in nights[:3]]+[
            explicitly_checked[(b,n)] for n in nights[3:]
        ]
        common_checked=set.intersection(*checked) if checked else set()
        common_sizes.append(len(common))
        checked_sizes.append(len(common_checked))
        region=domain_by_site[u["site"]]
        bydomain[region]["source_pairs"]+=1
        byyear[str(u["season_ordinal"]//4)]+=1
        enough=len(common)>=minimum_all_six_stations
        matA={g:set(stations)&common for g,stations in u["A"].items()}
        matB={g:set(stations)&common for g,stations in u["B"].items()}
        taxon_supported=all(len(matA[g])>=2 and len(matB[g])>=2 for g in matA)
        if not enough:original_station_retention["common_lt_90"]+=1
        elif not taxon_supported:original_station_retention["original_genus_station_support_lost_after_common"]+=1
        else:
            original_station_retention["both_common90_and_two_genus_support"]+=1
            bydomain[region]["recorded_six_night_eligible_pairs"]+=1
            retained.append({
                "site":u["site"],"site_plot":u["site_plot"],
                "season_ordinal":u["season_ordinal"],
                "A":matA,"B":matB,
            })
        supports.append((enough,taxon_supported))
    nsites=len({u["site"] for u in retained})
    ndomains=len({domain_by_site[u["site"]] for u in retained})
    passes=len(retained)>=min_selected_pairs and nsites>=min_selected_sites and ndomains>=min_selected_domains
    if sum(original_station_retention.values())!=len(original_two):
        raise AssertionError("Original 158 source pairs no longer exhaustively accounted")
    if sum(r["source_pairs"] for r in bydomain.values())!=len(original_two):
        raise AssertionError("Original 158 source pair domains no longer sum")

    def dist(vals):
        return {
            "min":min(vals) if vals else None,
            "median":median(vals) if vals else None,
            "max":max(vals) if vals else None,
            "mean":sum(vals)/len(vals) if vals else None,
        }

    result={
        "schema":"neon.macro.six_night_common_recorded_station_support.v1",
        "status":("SOURCE_COMMON_SIX_NIGHT_RECORDED_STATION_GO"
                  if passes else "STOP_COMMON_SIX_NIGHT_STATION_COVERAGE"),
        "original_exact_two_genus_pairs":len(original_two),
        "original_exact_two_genus_sites":expected_sites,
        "distinct_original_three_night_bouts":len(events),
        "required_separate_source_nights":6,
        "each_bout_original_meteorological_season_unchanged":True,
        "all_six_recorded_station_count_distribution":dist(common_sizes),
        "all_six_explicit_capture_or_no_capture_station_count_distribution":dist(checked_sizes),
        "source_trap_row_status_classification_counts":dict(sorted(status_summary.items())),
        "source_six_night_station_retention_categories":dict(sorted(original_station_retention.items())),
        "retained_pairs":len(retained),
        "retained_independent_physical_sites":nsites,
        "retained_NEON_ecological_domains":ndomains,
        "by_ecological_domain_source_only":dict(sorted(bydomain.items())),
        "source_start_year_pair_counts":dict(sorted(byyear.items())),
        "predeclared_effect_blind_gate":{
            "minimum_recorded_all_six_stations":minimum_all_six_stations,
            "minimum_retained_pairs":min_selected_pairs,
            "minimum_physical_sites":min_selected_sites,
            "minimum_NEON_domains":min_selected_domains,
            "passed":passes,
        },
        "scientific_scope":{
            "recorded_trap_not_proven_operable":True,
            "unknown_trap_status_not_imputed":True,
            "original_capture_identification_cohort_or_tag_exclusion_unchanged":True,
            "no_genus_x_trap_temporal_overlap_computed":True,
            "no_density_or_thermal_or_habitat_effect_computed":True,
            "cannot_exclude_genus_specific_catchability":True,
            "no_original_site_plot_tag_station_or_exact_dates_exported":True,
        },
    }
    return result,retained
