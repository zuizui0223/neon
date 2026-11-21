"""Date-effective NEON mammal station history audit, environment source ONLY.

This checks each of six original source trapping dates for the five
literal A1/A10/J1/J10/E5 official named stations. It does not use the
latest/current position to backfill past dates, nor calculate CHM/animal
spatial outcomes. Public return values are aggregate counts and years only.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from datetime import date,datetime

from analysis.neon_dated_station_location_v1 import choose_location_at_capture

ANCHORS=("A1","A10","J1","J10","E5")


def select_original_location_history(payload: dict, expected_name: str) -> list[dict]:
    """Preserve the ACTUAL NEON API history array; never use root/current."""
    if not isinstance(payload,dict):
        raise ValueError("Original location source payload is not a mapping")
    data=payload.get("data")
    if not isinstance(data,dict) or data.get("locationName")!=expected_name:
        raise ValueError("Original named location identity mismatch")
    history=data.get("locationHistory")
    if not isinstance(history,list) or not history:
        raise ValueError("No original source location history")
    if any(not isinstance(z,dict) for z in history):
        raise ValueError("Original location history is malformed")
    return history


def _failure_type(message: str) -> str:
    if "No date-valid" in message:
        return "NO_DATE_VALID_HISTORY"
    if "Ambiguous date-valid" in message:
        return "AMBIGUOUS_DATE_VALID_HISTORY"
    return "INVALID_SOURCE_HISTORY_DATE_OR_INTERVAL"


def summarize_five_anchor_date_history(
    units: list[dict],
    histories: dict[tuple[str,str,str],list[dict]|None],
    *,
    expected_pairs: int=58,
    expected_sites: int=14,
    expected_plots: int=30,
    min_pairs: int=40,
    min_sites: int=8,
    min_plots: int=20,
) -> dict:
    """Evaluate every fixed source day×anchor, no ecological effects.

    Each repeated source date in overlapping seasonal pairs contributes a
    separate *attempt*, not an independent capture or independent animal.
    """
    if not units or not isinstance(histories,dict):
        raise ValueError("Original seasonal pair and source histories are required")
    if len(units)!=expected_pairs:
        raise ValueError("Original frozen seasonal pair denominator drifted")
    source_plots=set()
    source_sites=set()
    pair_observations=[]
    for u in units:
        site=u.get("site")
        site_plot=u.get("site_plot")
        if not isinstance(site,str) or not site.strip() or not isinstance(site_plot,(tuple,list)) or len(site_plot)!=2 or site_plot[0]!=site:
            raise ValueError("Original source season pair site/plot is invalid")
        source_plots.add(tuple(site_plot))
        source_sites.add(site)
        aa=u.get("capture_dates_A")
        bb=u.get("capture_dates_B")
        if not isinstance(aa,(tuple,list)) or not isinstance(bb,(tuple,list)) or len(aa)!=3 or len(bb)!=3:
            raise ValueError("Original pair must preserve exactly three dates per season")
        all_dates=tuple(aa)+tuple(bb)
        if any(not isinstance(d,(date,datetime)) for d in all_dates) or len(set(all_dates))!=6:
            raise ValueError("Original source three plus three unique capture dates required")
        pair_observations.append((tuple(site_plot),tuple(all_dates)))
    if len(source_plots)!=expected_plots or len(source_sites)!=expected_sites:
        raise ValueError("Original plots or physical site denominator drifted")

    original_keys={(site,plot,anchor)
                   for site,plot in source_plots for anchor in ANCHORS}
    if set(histories)!=original_keys:
        raise ValueError("Original 5×plot named source history document coverage changed")

    reasons=Counter()
    counts_by_year=Counter()
    source_history_lengths=Counter()
    for key in original_keys:
        records=histories[key]
        if records is None:
            source_history_lengths["NO_LOCATION_HISTORY"]+=1
        elif not isinstance(records,list) or any(not isinstance(v,dict) for v in records):
            raise ValueError("Source history collection malformed")
        else:
            source_history_lengths[str(len(records))]+=1

    pair_all_valid=0
    plot_success=defaultdict(list)
    plot_days=defaultdict(set)
    pass_attempts=0
    failures=0
    e5_valid=0
    pair_all_E5=0

    for plot,dates in pair_observations:
        pair_valid=0
        this_E5=0
        for day in dates:
            plot_days[plot].add(day)
            counts_by_year[str(day.year)]+=len(ANCHORS)
            for anchor in ANCHORS:
                records=histories[(plot[0],plot[1],anchor)]
                if not records:
                    reasons["NO_LOCATION_HISTORY"]+=1
                    failures+=1
                    plot_success[plot].append(False)
                    continue
                try:
                    _matched=choose_location_at_capture(records,day)
                except ValueError as exc:
                    reasons[_failure_type(str(exc))]+=1
                    failures+=1
                    plot_success[plot].append(False)
                    continue
                pass_attempts+=1
                pair_valid+=1
                plot_success[plot].append(True)
                if anchor=="E5":
                    e5_valid+=1
                    this_E5+=1
        pair_all_valid+=int(pair_valid==30)
        pair_all_E5+=int(this_E5==6)

    plots_all_valid=sum(all(values) for values in plot_success.values())
    sites_at_least_one={p[0] for p,values in plot_success.items() if all(values)}
    site_level_count=len(sites_at_least_one)
    ok=(
        pair_all_valid>=min_pairs
        and plots_all_valid>=min_plots
        and site_level_count>=min_sites
    )
    if pass_attempts+failures!=len(units)*30:
        raise AssertionError("Original source anchor×day denominator was not preserved")
    return {
        "schema":"neon.historical_location.five_anchor_date_coverage.v1",
        "status":("HISTORICAL_FIVE_ANCHOR_CAPTURE_DATE_SOURCE_GO"
                  if ok else "STOP_HISTORICAL_FIVE_ANCHOR_DATE_SUPPORT"),
        "fixed_original_seasonal_pairs":len(units),
        "physical_sites":len(source_sites),
        "plots":len(source_plots),
        "five_literally_named_stations_per_plot":5,
        "fixed_original_anchor_date_attempts":len(units)*30,
        "anchor_date_valid":pass_attempts,
        "anchor_date_missing_or_ambiguous":failures,
        "valid_E5_source_capture_date_attempts":e5_valid,
        "all_E5_dates_valid_seasonal_pairs":pair_all_E5,
        "all_five_anchors_valid_for_all_six_original_dates_pairs":pair_all_valid,
        "plots_fully_valid_for_all_included_capture_days":plots_all_valid,
        "sites_with_at_least_one_fully_valid_plot":site_level_count,
        "original_distinct_plot_date_keys":sum(len(x) for x in plot_days.values()),
        "original_capture_year_anchor_attempt_distribution":dict(sorted(counts_by_year.items())),
        "historical_source_record_count_distribution":dict(sorted(source_history_lengths.items())),
        "failure_categories":dict(sorted(reasons.items())),
        "preregistered_minimum_pairs_with_all_five_valid":min_pairs,
        "preregistered_minimum_plots_fully_valid":min_plots,
        "preregistered_minimum_physical_sites":min_sites,
        "historical_capture_day_location_gate_passed":ok,
        "used_current_coordinates_outside_historical_interval":False,
        "all_other_95_station_coordinates_verified":False,
        "reused_capture_dates_are_attempts_not_independent_animals":True,
        "no_original_site_plot_anchor_date_or_animal_ids_exported":True,
        "live_NEON_API_history_not_versioned_with_RELEASE_2026":True,
        "CHM_date_matched_to_capture_event":False,
        "coordinates_or_canopy_pixels_exported":False,
        "habitat_genus_trap_ecological_effect_opened":False,
        "original_density_generality_status":"FAILED_5_OF_8",
        "MOSA_W_B_effects":"SEALED",
    }
