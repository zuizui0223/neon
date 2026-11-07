"""Pure, ecological-effect-blind support logic for historical source-dated AOP CHM.

Exact original 58 seasonal comparisons are used as an immutable source
denominator; no genus-to-trap overlap, animal identifiers or Z values.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import date

def frozen_selected_month_days(units, site_months, *, expected_pairs=58,
                               expected_sites=14, expected_plots=30):
    from analysis.run_neon_aop_historical_flight_month_v1 import nearest_flight_month
    if len(units)!=expected_pairs:
        raise ValueError("Original seasonal pair denominator changed")
    sites=set(); plots=set(); days={}
    pair_flags=[]
    for unit in units:
        site=unit["site"]; plot=tuple(unit["site_plot"])
        ds=tuple(unit["capture_dates_A"])+tuple(unit["capture_dates_B"])
        if plot[0]!=site or len(ds)!=6 or len(set(ds))!=6 or any(not isinstance(d,date) for d in ds):
            raise ValueError("Original six source dates or original plot invalid")
        sites.add(site); plots.add(plot)
        selected=[nearest_flight_month(d,site_months.get(site,[])) for d in ds]
        for day,choice in zip(ds,selected):
            key=(plot,day)
            if key in days and days[key]!=choice:
                raise ValueError("Reused source date has inconsistent selected month")
            days[key]=choice
        pair_flags.append({
            "site":site,"plot":plot,
            "source_days":ds,
            "within12":all(lag is not None and abs(lag)<=12 for month,lag in selected),
            "within3":all(lag is not None and abs(lag)<=3 for month,lag in selected),
            "prior12":all(lag is not None and -12<=lag<=0 for month,lag in selected),
            "prior3":all(lag is not None and -3<=lag<=0 for month,lag in selected),
        })
    if len(sites)!=expected_sites or len(plots)!=expected_plots or set(site_months)!=sites:
        raise ValueError("Original site and plot source universe drift")
    if expected_pairs==58 and len(days)!=339:
        raise ValueError("Original unique plot-day denominator changed")
    return days,pair_flags

def source_month_manifest_support(units, site_months, manifests, *,
                                  expected_pairs=58, expected_sites=14,
                                  expected_plots=30):
    """Actual published CHM tile counts, never just a site-month metadata claim.

    manifests: (site,month) -> list[official tile metadata] or None.
    Missing/error records stay absent and do not become negative biology.
    """
    days,pairs=frozen_selected_month_days(units,site_months,
        expected_pairs=expected_pairs,expected_sites=expected_sites,expected_plots=expected_plots)
    selected={(plot[0],month) for (plot,_),(month,lag) in days.items() if month}
    if set(manifests)!=selected:
        raise ValueError("Official selected site-month manifests missing from source inventory")
    records=[len(manifests[key]) if manifests[key] is not None else None for key in selected]
    needed12={(plot[0],month) for (plot,_),(month,lag) in days.items()
              if month and lag is not None and abs(lag)<=12}
    return {
        "selected_original_site_flight_months":len(selected),
        "selected_within12_site_flight_months":len(needed12),
        "original_selected_site_months_with_source_manifest":sum(manifests[k] is not None for k in selected),
        "original_selected_site_months_with_one_plus_CHM_tile":sum(manifests[k] is not None and len(manifests[k])>0 for k in selected),
        "within12_selected_months_with_CHM_tiles":sum(manifests[k] is not None and len(manifests[k])>0 for k in needed12),
        "source_monthly_CHM_tile_count_summary":{
            "min":min(x for x in records if x is not None) if any(x is not None for x in records) else None,
            "max":max(x for x in records if x is not None) if any(x is not None for x in records) else None,
        },
        "original_pairs_with_closest_AOP_month_abs_lag12":sum(x["within12"] for x in pairs),
        "original_pairs_with_closest_AOP_month_abs_lag3":sum(x["within3"] for x in pairs),
        "original_pairs_with_closest_prior_or_same_month_lag12":sum(x["prior12"] for x in pairs),
        "original_pairs_with_closest_prior_or_same_month_lag3":sum(x["prior3"] for x in pairs),
        "source_day_attempts_repeated_in_pairs":6*len(units),
        "unique_source_plot_day_keys":len(days),
        "no_habitat_or_detectability_ecological_effect":True,
    }

def summarize_actual_historical_pixels(units, site_months, day_valid_count,
                                      *, expected_pairs=58,expected_sites=14,
                                      expected_plots=30,threshold=95):
    """Private date×plot cell pixel support -> anonymous pair-level summary.

    Missing and out-of-window stations are NOT treated as canopy height 0.
    """
    days,pairs=frozen_selected_month_days(units,site_months,
        expected_pairs=expected_pairs,expected_sites=expected_sites,expected_plots=expected_plots)
    target={key for key,(month,lag) in days.items()
            if month is not None and lag is not None and abs(lag)<=12}
    if set(day_valid_count)!=target or any(
        not isinstance(v,int) or isinstance(v,bool) or not 0<=v<=100
        for v in day_valid_count.values()
    ):
        raise ValueError("Selected day/capture source coverage incomplete or invalid")
    # Explicit zero-valued category counts: a failed feasibility check
    # must retain its scientific STOP rather than omit its output key.
    categories=("within12","within3","prior12","prior3")
    subset=Counter({name+"_metadata_eligible_pairs":0 for name in categories})
    subset.update({name+"_actually_qualified_pairs":0 for name in categories})
    sites=defaultdict(set); plots=defaultdict(set)
    for p in pairs:
        support=all(day_valid_count.get((p["plot"],day),0)>=threshold for day in p["source_days"])
        for name in ("within12","within3","prior12","prior3"):
            if p[name]:
                subset[name+"_metadata_eligible_pairs"]+=1
                if support:
                    subset[name+"_actually_qualified_pairs"]+=1
                    sites[name].add(p["site"])
                    plots[name].add(p["plot"])
    return {
        **dict(sorted(subset.items())),
        "valid_original_selected_plot_day_keys_at_least95":sum(v>=threshold for v in day_valid_count.values()),
        "selected_plot_day_keys_within12":len(target),
        "qualified_physical_sites_by_class":{k:len(sites[k]) for k in ("within12","within3","prior12","prior3")},
        "qualified_original_plots_by_class":{k:len(plots[k]) for k in ("within12","within3","prior12","prior3")},
        "no_outcome_driven_site_selection":True,
        "source_data_only_not_genus_response":True,
        "no_site_plot_station_date_identifiers_exported":True,
    }
