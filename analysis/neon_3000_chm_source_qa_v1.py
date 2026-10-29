"""Source-only NEON full trap CHM and acquisition-month temporal audit.

Only aggregate metadata and heights. No genus x trap capture rows, habitat
selection, detection correction or other ecological effects are computed.
"""
from __future__ import annotations
from collections import defaultdict, Counter
from datetime import date
from math import isfinite
from statistics import median

from analysis.neon_dated_station_location_v1 import station_labels_10x10

STATIONS=tuple(station_labels_10x10())
ANCHORS=("A1","A10","J1","J10","E5")
VALID="VALID_REFERENCE_PIXEL"


def month_gap(capture_day:date, flight_month:str)->int:
    """Positive means acquisition calendar month is AFTER capture month."""
    if not isinstance(capture_day,date) or not isinstance(flight_month,str):
        raise ValueError("Date and original acquisition month required")
    if len(flight_month)!=7 or flight_month[4]!="-":
        raise ValueError("Malformed acquisition month")
    y,m=int(flight_month[:4]),int(flight_month[5:])
    if not 1<=m<=12 or not 2013<=y<=2026:
        raise ValueError("Invalid published flight acquisition month")
    return 12*(y-capture_day.year)+(m-capture_day.month)


def original_month_source_alignment(units:list[dict], months:dict[str,str|None],
                                     *,expected_pairs:int=58,expected_sites:int=14,
                                     expected_plots:int=30)->dict:
    """No spatial response or genus identity used, only original source dates."""
    if len(units)!=expected_pairs:
        raise ValueError("Original seasonal population changed")
    sites=set()
    plots=set()
    repeated=[]
    distinct=set()
    all_both_12=0
    all_six_same_flight_year=0
    same_or_within3=0
    for u in units:
        site=u["site"]
        plot=tuple(u["site_plot"])
        days=tuple(u["capture_dates_A"])+tuple(u["capture_dates_B"])
        if len(days)!=6 or plot[0]!=site or len(set(days))!=6:
            raise ValueError("Original source six nights invalid")
        sites.add(site);plots.add(plot)
        month=months.get(site)
        gaps=[month_gap(d,month) if month else None for d in days]
        for d,g in zip(days,gaps):
            repeated.append(g);distinct.add((plot,d))
        if all(g is not None and abs(g)<=12 for g in gaps):
            all_both_12+=1
        if all(month and d.year==int(month[:4]) for d in days):
            all_six_same_flight_year+=1
        if all(g is not None and abs(g)<=3 for g in gaps):
            same_or_within3+=1
    if len(sites)!=expected_sites or len(plots)!=expected_plots or set(months)!=sites:
        raise ValueError("Frozen geographical denominator or month source missing")
    finite=[g for g in repeated if g is not None]
    return {
        "original_season_pairs":len(units),
        "original_physical_sites":len(sites),
        "original_source_plots":len(plots),
        "paired_source_day_attempts":len(repeated),
        "unique_source_plot_day_keys":len(distinct),
        "site_flight_month_available":sum(month is not None for month in months.values()),
        "acquisition_year_site_counts":dict(sorted(Counter(m[:4] for m in months.values() if m).items())),
        "flight_month_after_capture_month_attempts":sum(g>0 for g in finite),
        "flight_month_before_capture_month_attempts":sum(g<0 for g in finite),
        "same_calendar_month_attempts":sum(g==0 for g in finite),
        "abs_month_gap_3_or_less_attempts":sum(abs(g)<=3 for g in finite),
        "abs_month_gap_12_or_less_attempts":sum(abs(g)<=12 for g in finite),
        "abs_month_gap_24_or_less_attempts":sum(abs(g)<=24 for g in finite),
        "pairs_all_six_days_within_3_calendar_months":same_or_within3,
        "pairs_all_six_days_within_12_calendar_months":all_both_12,
        "pairs_all_six_days_same_acquisition_year":all_six_same_flight_year,
        "absolute_month_gap_summary":{
            "min":min(map(abs,finite)) if finite else None,
            "median":median(map(abs,finite)) if finite else None,
            "max":max(map(abs,finite)) if finite else None,
        },
        "month_not_exact_flight_day":True,
        "acquisition_not_assumed_contemporaneous_with_capture":True,
        "original_capture_tags_or_spatial_response_read":False,
    }


def aggregate_full_station_chm(rows:list[dict], *,expected_plots:int=30,
                               stations:tuple[str,...]=STATIONS)->dict:
    """Private rows are aggregated without any plot/station/height vectors."""
    if len(stations)<2 or len(set(stations))!=len(stations):
        raise ValueError("Unique fixed canonical stations required")
    groups=defaultdict(dict)
    states=Counter()
    for row in rows:
        key=row.get("plot_key")
        station=row.get("station")
        state=row.get("status")
        value=row.get("height_m")
        flag=row.get("historically_flagged_plot")
        if not isinstance(key,tuple) or len(key)!=2 or not all(isinstance(t,str) and t for t in key):
            raise ValueError("Invalid private source plot")
        if station not in stations or station in groups[key]:
            raise ValueError("Duplicate or noncanonical station")
        if state==VALID:
            if isinstance(value,bool) or not isinstance(value,(float,int)) or not isfinite(value):
                raise ValueError("Valid raster pixel must have finite height")
        elif value is not None:
            raise ValueError("Invalid pixel must not have reported height")
        if not isinstance(flag,bool):
            raise ValueError("Flagged NEON location issue state missing")
        groups[key][station]=row
        states[state]+=1
    if len(groups)!=expected_plots or len(rows)!=expected_plots*len(stations):
        raise ValueError("Original 30x100 source station coverage changed")
    if any(set(group)!=set(stations) for group in groups.values()):
        raise ValueError("Missing one or more original source trap stations")
    valid=zero=negative=0
    ranges=[]
    all100=two=nonzero_plot=allzero=0
    e5zero_otherpositive=0
    flagged_plots=0
    qualified_95=0
    for group in groups.values():
        flags={r["historically_flagged_plot"] for r in group.values()}
        if len(flags)!=1:
            raise ValueError("Historical plot issue metadata inconsistent")
        flagged_plots+=int(True in flags)
        v=[float(r["height_m"]) for r in group.values() if r["status"]==VALID]
        valid+=len(v)
        zero+=sum(x==0 for x in v)
        negative+=sum(x<0 for x in v)
        all100+=int(len(v)==len(stations))
        qualified_95+=int(len(v)>=.95*len(stations))
        two+=int(len(v)>=2)
        if len(v)>=2:
            rg=max(v)-min(v)
            ranges.append(rg)
            nonzero_plot+=int(rg>1e-9)
        allzero+=int(len(v)==len(stations) and all(x==0 for x in v))
        if "E5" in group:
            e5=group["E5"]
            if e5["status"]==VALID and e5["height_m"]==0 and any(
                r["status"]==VALID and r["height_m"]>0 for k,r in group.items() if k!="E5"
            ):
                e5zero_otherpositive+=1
    return {
        "source_station_positions":len(rows),
        "original_plots":len(groups),
        "pixel_status_counts":dict(sorted(states.items())),
        "valid_station_pixels":valid,
        "valid_zero_pixels":zero,
        "negative_height_pixels_flagged":negative,
        "plots_all_station_pixels_valid":all100,
        "plots_at_least_95pct_pixels_valid":qualified_95,
        "plots_at_least_two_valid_pixels":two,
        "plots_with_nonzero_full_station_height_range":nonzero_plot,
        "plots_all_stations_zero_canopy":allzero,
        "plots_E5_zero_but_another_station_positive":e5zero_otherpositive,
        "full_station_height_range_m_summary":{
            "minimum":min(ranges) if ranges else None,
            "median":median(ranges) if ranges else None,
            "maximum":max(ranges) if ranges else None,
        },
        "historically_flagged_original_plots_retained":flagged_plots,
        "raw_station_plot_site_coordinates_heights_or_taxon_ids_exported":False,
        "CHM_zero_is_not_no_understory_vegetation":True,
        "CHM_canopy_minimum_height_not_low_ground_cover":True,
        "full_historical_habitat_or_detection_effect_estimated":False,
    }


def protected_five_anchor_replay(rows:list[dict], *,expected_plots:int=30)->dict:
    """Reproduce the pre-existing 150 source CHM records as an identity check."""
    groups=defaultdict(dict)
    for row in rows:
        if row["station"] in ANCHORS:
            groups[row["plot_key"]][row["station"]]=row
    if len(groups)!=expected_plots or any(set(x)!=set(ANCHORS) for x in groups.values()):
        raise ValueError("Original five anchor population drifted")
    all_valid=all(all(x["status"]==VALID for x in group.values()) for group in groups.values())
    nvalid=sum(x["status"]==VALID for g in groups.values() for x in g.values())
    zero=sum(x["height_m"]==0 for g in groups.values() for x in g.values() if x["status"]==VALID)
    e5zero=sum(g["E5"]["status"]==VALID and g["E5"]["height_m"]==0 for g in groups.values())
    ranges=sum(
        len({g[a]["height_m"] for a in ANCHORS})>1
        for g in groups.values() if all(x["status"]==VALID for x in g.values())
    )
    return {
        "five_named_anchor_pixels_valid":nvalid,
        "five_anchor_zero_pixels":zero,
        "E5_zero_pixels":e5zero,
        "plots_five_anchor_positive_canopy_range":ranges,
        "all_original_five_anchor_pixels_valid":all_valid,
    }
