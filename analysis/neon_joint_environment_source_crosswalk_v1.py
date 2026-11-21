"""Exact within-original-pair source crosswalk: AOP CHM and nearby plant visits.

This is NOT a mammal habitat-choice or detection-effect analysis. Original
58 comparison keys, site/plot/date labels remain private in process memory.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from analysis.neon_historical_chm_source_support_v1 import frozen_selected_month_days
from analysis.neon_field_plant_source_support_v1 import _matching


CHM_CLASSES=("within12","within3","prior12","prior3")
PLANT_CLASSES=("numeric365","numeric90")
DESCRIPTIVE_SOURCE_RULE={"min_pairs":20,"min_independent_sites":8,"min_original_plots":12}


def joint_source_crosswalk(units, site_months, plant_events,
                           *, expected_pairs=58, expected_sites=14,
                           expected_plots=30):
    """Intersect individually fixed source eligibilities, NEVER marginal totals.

    Accepts site-month metadata only because an unchanged prior checksum-
    verified 51-tile AOP run established 100/100 actual valid CHM stations
    for *every* original ±12m candidate source day. The runner must verify
    both external source receipts before using this function.
    """
    source_days, monthly_pairs=frozen_selected_month_days(
        units,site_months,expected_pairs=expected_pairs,
        expected_sites=expected_sites,expected_plots=expected_plots)
    if len(monthly_pairs)!=len(units):
        raise AssertionError("Original source unit alignment lost")
    allkeys=set(); chm_counts=Counter();cover_counts=Counter()
    cross=Counter()
    sites_by_class=defaultdict(set)
    plots_by_class=defaultdict(set)
    for u,month in zip(units,monthly_pairs):
        plot=tuple(u["site_plot"]);site=u["site"]
        dates_a=tuple(u["capture_dates_A"])
        dates_b=tuple(u["capture_dates_B"])
        unit_key=(plot,dates_a,dates_b)
        if unit_key in allkeys:
            raise ValueError("Original seasonal pair key repeated")
        allkeys.add(unit_key)
        if site!=month["site"] or plot!=month["plot"] or dates_a+dates_b!=month["source_days"]:
            raise ValueError("Month and mammal source comparison drift")
        original_plant_events=plant_events.get(plot,{})
        vegetation={}
        for window,label in ((365,"numeric365"),(90,"numeric90")):
            matched_a=_matching(original_plant_events,dates_a,window,True)
            matched_b=_matching(original_plant_events,dates_b,window,True)
            vegetation[label]=bool(matched_a and matched_b and any(
                ka!=kb for ka in matched_a for kb in matched_b))
            cover_counts[label]+=int(vegetation[label])
        for mc in CHM_CLASSES:
            chm_counts[mc]+=int(month[mc])
            for vc in PLANT_CLASSES:
                cls=mc+"__"+vc
                both=month[mc] and vegetation[vc]
                cross[cls]+=int(both)
                if both:
                    sites_by_class[cls].add(site)
                    plots_by_class[cls].add(plot)
    if len(allkeys)!=expected_pairs or len(source_days)!=(339 if expected_pairs==58 else len(source_days)):
        raise ValueError("Original source dates and seasonal pairs changed")
    if chm_counts!={"within12":36,"within3":22,"prior12":18,"prior3":10} and expected_pairs==58:
        raise ValueError("Original verified AOP actual-raster source cohorts changed")
    if cover_counts!={"numeric365":51,"numeric90":16} and expected_pairs==58:
        raise ValueError("Original verified plant visit source cohorts changed")
    output={}
    for mc in CHM_CLASSES:
        for vc in PLANT_CLASSES:
            cls=mc+"__"+vc
            n=cross[cls]; ns=len(sites_by_class[cls]); np=len(plots_by_class[cls])
            output[cls]={
                "original_season_pairs":n,
                "independent_physical_sites":ns,
                "original_mammal_grid_plotIDs":np,
                "source_minimum_met":(
                    n>=DESCRIPTIVE_SOURCE_RULE["min_pairs"] and
                    ns>=DESCRIPTIVE_SOURCE_RULE["min_independent_sites"] and
                    np>=DESCRIPTIVE_SOURCE_RULE["min_original_plots"]
                ),
            }
    primary=output["within12__numeric365"]["original_season_pairs"]
    if not max(0,36+51-58)<=primary<=min(36,51) and expected_pairs==58:
        raise AssertionError("Source pair exact set intersection outside mathematical bounds")
    return {
        "schema":"neon.mammal.two_environment_sources_exact_pair_crosswalk.v1",
        "status":"ORIGINAL_PAIR_EXACT_ENVIRONMENT_SOURCE_CROSSWALK_NOT_BIOLOGICAL_EFFECT",
        "original_frozen_season_pairs":len(allkeys),
        "original_physical_sites":len({x["site"] for x in units}),
        "original_mammal_grids":len({tuple(x["site_plot"]) for x in units}),
        "original_distinct_plot_capture_date_keys":len(source_days),
        "frozen_actual_CHM_raster_eligible_pair_counts":dict(chm_counts),
        "frozen_nearby_plant_numeric_two_event_pair_counts":dict(cover_counts),
        "joint_source_support":output,
        "predeclared_descriptive_source_rule":DESCRIPTIVE_SOURCE_RULE,
        "same_plotID_plant_base_plot_not_actual_mammal_trap_habitat":True,
        "AOP_months_alone_only_used_because_all_original_36_source_pairs_have_actual_pixel_QA":True,
        "old_exact_two_genus_cohort_and_full_original_outcomes_not_refitted":True,
        "source_plot_date_station_genus_animal_identifiers_not_exported":True,
        "no_habitat_effect_or_genus_specific_detection_parameter_identified":True,
    }
