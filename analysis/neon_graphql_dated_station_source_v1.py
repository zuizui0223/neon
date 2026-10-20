#!/usr/bin/env python3
"""NEON official batched findLocations and date-effective 100-station source QA.

Does NOT infer coordinates from a grid, read genus-trap occupancy, fit any
habitat effect, change previous spatial recurrence outcomes, or serialize
geographical names / animal IDs / projected coordinates.

Official query: https://data.neonscience.org/graphql findLocations,
LocationQuery.locationNames, maximum 1,000 names per request.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from datetime import datetime,date,timezone
from math import isfinite
from statistics import median
import re

from analysis.neon_dated_station_location_v1 import (
    station_labels_10x10,choose_location_at_capture
)

STATIONS=station_labels_10x10()
STATION_SET=frozenset(STATIONS)
GRAPHQL_QUERY="""
query FrozenMammalStations($query: LocationQuery!) {
  locations: findLocations(query: $query) {
    locationName
    locationUtmEasting
    locationUtmNorthing
    locationUtmZone
    locationUtmHemisphere
    locationProperties { locationPropertyName locationPropertyValue }
    locationHistory {
      current
      locationStartDate
      locationEndDate
      locationUtmEasting
      locationUtmNorthing
      locationUtmZone
      locationUtmHemisphere
      locationProperties { locationPropertyName locationPropertyValue }
    }
  }
}
"""


def batch_names(names:list[str], size:int=500) -> list[list[str]]:
    if isinstance(size,bool) or not isinstance(size,int) or not 1<=size<=1000:
        raise ValueError("GraphQL location batch size must be 1..1000")
    if not isinstance(names,list) or any(not isinstance(n,str) or not n.strip() for n in names):
        raise ValueError("Location names must be nonempty source strings")
    if len(set(names))!=len(names):
        raise ValueError("Duplicate source station names before GraphQL request")
    return [names[i:i+size] for i in range(0,len(names),size)]


def parse_graphql_locations(payload:dict, expected_names:list[str]) -> dict[str,dict]:
    """Each response location is keyed EXACTLY to a requested source name."""
    if not isinstance(payload,dict) or (payload.get("errors") or []):
        raise ValueError("NEON GraphQL errors prevent authoritative source use")
    data=payload.get("data")
    if not isinstance(data,dict) or not isinstance(data.get("locations"),list):
        raise ValueError("GraphQL locations payload missing")
    requested=set(expected_names)
    got={}
    for row in data["locations"]:
        if not isinstance(row,dict):
            raise ValueError("GraphQL returned invalid location document")
        name=row.get("locationName")
        if name not in requested:
            raise ValueError("GraphQL returned unexpected source station identity")
        if name in got:
            raise ValueError("GraphQL duplicate source named location")
        got[name]=row
    return got


def _canonical_time(t):
    if t is None or str(t).strip()=="":
        return None
    try:
        dt=datetime.fromisoformat(str(t).strip().replace("Z","+00:00"))
    except ValueError:
        raise ValueError("Source historical time malformed") from None
    if dt.tzinfo is not None:
        dt=dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt.isoformat(timespec="seconds")


def _props(original):
    result={}
    if original is None:
        return {}
    if not isinstance(original,list):
        raise ValueError("Malformed NEON historical location properties")
    for item in original:
        if not isinstance(item,dict):
            raise ValueError("Malformed original source property entry")
        name=str(item.get("locationPropertyName") or "")
        val=item.get("locationPropertyValue")
        if name in result and str(result[name])!=str(val):
            raise ValueError("Conflicting original location property name")
        result[name]=val
    return result


def canonical_station_history_for_comparison(document:dict)->tuple:
    """Normalize REST/GQL private history fields for a source equivalence gate."""
    if not isinstance(document,dict):
        raise ValueError("Non-dictionary source location")
    history=document.get("locationHistory")
    if not isinstance(history,list) or not history:
        raise ValueError("Source named location has no actual history")
    def row_tuple(row):
        if not isinstance(row,dict):
            raise ValueError("Source location history record malformed")
        b=row.get("current")
        if isinstance(b,bool):
            current=b
        elif str(b).lower().strip() in {"true","false"}:
            current=str(b).lower().strip()=="true"
        else:
            raise ValueError("Invalid historical current label")
        return (
            current,_canonical_time(row.get("locationStartDate")),
            _canonical_time(row.get("locationEndDate")),
            None if row.get("locationUtmEasting") is None else float(row["locationUtmEasting"]),
            None if row.get("locationUtmNorthing") is None else float(row["locationUtmNorthing"]),
            row.get("locationUtmZone") or document.get("locationUtmZone"),
            str(row.get("locationUtmHemisphere") or document.get("locationUtmHemisphere") or "").upper(),
            tuple(sorted((str(k),str(v)) for k,v in _props(row.get("locationProperties")).items())),
        )
    return (
        document.get("locationName"),
        tuple(sorted(row_tuple(r) for r in history)),
        tuple(sorted((str(k),str(v)) for k,v in _props(document.get("locationProperties")).items())),
    )


def _float(v):
    if v is None or isinstance(v,bool):
        return None
    try:
        n=float(v)
        return n if isfinite(n) else None
    except (ValueError,TypeError):
        return None


def validate_history_projection(doc:dict, original_day:date)->dict:
    """Strict original date history, valid projected CRS and direct U only."""
    if not isinstance(doc,dict):
        raise ValueError("Missing source location document")
    h=doc.get("locationHistory")
    if not isinstance(h,list) or not h:
        raise ValueError("No original source location history")
    record=choose_location_at_capture(h,original_day)
    x=_float(record.get("locationUtmEasting"))
    y=_float(record.get("locationUtmNorthing"))
    zone=record.get("locationUtmZone")
    if zone is None:
        zone=doc.get("locationUtmZone")
    hemi=str(record.get("locationUtmHemisphere") or doc.get("locationUtmHemisphere") or "").upper()
    if x is None or y is None or isinstance(zone,bool) or _float(zone) is None or float(zone)!=int(float(zone)) or not 1<=int(float(zone))<=60 or hemi not in {"N","S"}:
        raise ValueError("Date-valid source record lacks finite projected UTM")
    prop=_props(doc.get("locationProperties"))
    prop.update(_props(record.get("locationProperties")))
    datum=''.join(c for c in str(prop.get("Value for Geodetic datum") or "").upper() if c.isalnum())
    nzone=int(float(zone))
    if datum in {"WGS84","WGS1984","WORLDGEODETICSYSTEM1984"}:
        epsg=(32600 if hemi=="N" else 32700)+nzone
    elif datum=="NAD83" and hemi=="N" and nzone<=23:
        epsg=26900+nzone
    else:
        raise ValueError("Projected historical source datum unsupported")
    u=_float(_props(record.get("locationProperties")).get("Value for Coordinate uncertainty"))
    if u is not None and u<0:
        raise ValueError("Negative source-reported historical uncertainty")
    return {"xy":(x,y),"utm_epsg":epsg,"direct_source_uncertainty_m":u,
            "reported_uncertainty_from_historical_record":u is not None,
            "uncertainty_absent_is_not_zero":True}


def _dist(values:list[float])->dict:
    return {
        "min":min(values) if values else None,
        "median":float(median(values)) if values else None,
        "max":max(values) if values else None,
    }


def summarize_full_station_dated_coverage(
    units:list[dict], documents:dict[tuple[str,str,str],dict|None], *,
    expected_pairs:int=58,expected_sites:int=14,expected_plots:int=30,
    min_pairs:int=40,min_sites:int=8,min_plots:int=20,
    historically_flagged_plots:set[tuple[str,str]]|None=None,
)->dict:
    """Count only original source station/day validity and assumed uncertainty.

    The summary must never expose site/plot/trap names, coordinates, source
    capture dates, genus×station occupancy, or per-plot canopy pixels.
    """
    if len(units)!=expected_pairs or not units:
        raise ValueError("Original 58-pair population changed")
    source_plots=set()
    source_sites=set()
    capture_events=[]
    for item in units:
        site=item.get("site")
        plot=item.get("site_plot")
        aa=item.get("capture_dates_A")
        bb=item.get("capture_dates_B")
        if not isinstance(site,str) or not site or not isinstance(plot,(list,tuple)) or len(plot)!=2 or plot[0]!=site:
            raise ValueError("Source site/plot identity invalid")
        if not isinstance(aa,(list,tuple)) or not isinstance(bb,(list,tuple)) or len(aa)!=3 or len(bb)!=3:
            raise ValueError("Missing source original 3+3 capture dates")
        days=tuple(aa)+tuple(bb)
        if any(not isinstance(d,date) for d in days) or len(set(days))!=6:
            raise ValueError("Original capture days must be six unique date values")
        source_sites.add(site)
        source_plots.add(tuple(plot))
        capture_events.append((tuple(plot),days))
    if len(source_sites)!=expected_sites or len(source_plots)!=expected_plots:
        raise ValueError("Original physical NEON site/plot universe drifted")
    expected_keys={(site,plot,station)
                   for site,plot in source_plots for station in STATIONS}
    if set(documents)!=expected_keys:
        raise ValueError("Original 100 named station documents per plot missing")
    all_loc_names=set()
    for key,doc in documents.items():
        if doc is None:
            continue
        if not isinstance(doc,dict):
            raise ValueError("Source station document malformed")
        name=doc.get("locationName")
        if not isinstance(name,str) or not name.endswith("."+key[2]):
            raise ValueError("Source station location identity suffix mismatch")
        if name in all_loc_names:
            raise ValueError("Source station location identity duplicated")
        all_loc_names.add(name)
    flagged=historically_flagged_plots or set()
    if not flagged.issubset(source_plots):
        raise ValueError("Original georeferencing issue plot roster drifted")

    cache={}
    valid=0
    total=0
    source_history_count=Counter()
    directU=0
    nohistory=Counter()
    date_coverage_by_plot=defaultdict(list)
    sites_valid_plots=set()
    pair_full=0
    pair_95=0
    plot_dates=defaultdict(set)
    unique_date_no_monument=set()
    unique_date_full_uncertainty=set()
    adjustedU=[]
    all_site_datums=Counter()
    for key in expected_keys:
        doc=documents[key]
        if doc is None:
            source_history_count["NO_DOCUMENT"]+=1
        else:
            z=doc.get("locationHistory")
            source_history_count[str(len(z)) if isinstance(z,list) else "NO_HISTORY"]+=1

    for plot,days in capture_events:
        pair_station_per_day=[]
        for day in days:
            plot_dates[plot].add(day)
            info_by_station={}
            for station in STATIONS:
                total+=1
                key=(plot[0],plot[1],station)
                if (key,day) not in cache:
                    doc=documents.get(key)
                    if doc is None:
                        cache[(key,day)]=("NO_DOCUMENT",None)
                    else:
                        try:
                            detail=validate_history_projection(doc,day)
                            cache[(key,day)]=("DATE_PROJECTED_VALID",detail)
                        except ValueError as exc:
                            msg=str(exc)
                            if "No date-valid" in msg:
                                status="NO_DATE_VALID_HISTORY"
                            elif "Ambiguous date-valid" in msg:
                                status="AMBIGUOUS_DATE_VALID_HISTORY"
                            elif "datum unsupported" in msg:
                                status="UNSUPPORTED_SOURCE_DATUM"
                            elif "projected UTM" in msg:
                                status="INVALID_SOURCE_UTM"
                            else:
                                status="MALFORMED_SOURCE_HISTORY"
                            cache[(key,day)]=(status,None)
                state,detail=cache[(key,day)]
                if state=="DATE_PROJECTED_VALID":
                    valid+=1
                    info_by_station[station]=detail
                    all_site_datums[str(detail["utm_epsg"])]+=1
                    directU+=int(detail["direct_source_uncertainty_m"] is not None)
                else:
                    nohistory[state]+=1
            per_day=len(info_by_station)
            pair_station_per_day.append(per_day)
            date_coverage_by_plot[plot].append(per_day)
            # Apply official geoNEON U+1 / maximum reported monument U+3:
            # report it as an ASSUMPTION not independent measurement of
            # actual historical positional accuracy.
            values=[
                z["direct_source_uncertainty_m"]
                for z in info_by_station.values()
                if z["direct_source_uncertainty_m"] is not None
            ]
            if not values:
                unique_date_no_monument.add((plot,day))
            else:
                maximum=max(values)
                if per_day==100:
                    unique_date_full_uncertainty.add((plot,day))
                for detail in info_by_station.values():
                    u=detail["direct_source_uncertainty_m"]
                    adjustedU.append(float(u)+1 if u is not None else maximum+3)
        pair_full+=int(all(v==100 for v in pair_station_per_day))
        pair_95+=int(all(v>=95 for v in pair_station_per_day))

    qualified_plots={
        plot for plot,counts in date_coverage_by_plot.items()
        if all(n>=95 for n in counts)
    }
    sites_valid_plots={key[0] for key in qualified_plots}
    ok=(len(qualified_plots)>=min_plots and
        len(sites_valid_plots)>=min_sites and pair_95>=min_pairs)
    if total!=len(units)*6*100 or valid+sum(nohistory.values())!=total:
        raise AssertionError("Original 58×6×100 source denominator changed")
    per_plot_min=[min(values) for values in date_coverage_by_plot.values()]
    return {
        "schema":"neon.mammal.original_100_station_dated_source_QA.v1",
        "status":("FULL_100_STATION_CAPTURE_DATE_SOURCE_GO"
                  if ok else "STOP_100_STATION_HISTORICAL_SOURCE_SUPPORT"),
        "original_frozen_season_pairs":len(units),
        "original_plots":len(source_plots),
        "original_physical_sites":len(source_sites),
        "original_named_station_documents_expected":len(expected_keys),
        "station_name_documents_returned":len(all_loc_names),
        "station_name_documents_unavailable":len(expected_keys)-len(all_loc_names),
        "station_history_record_count_distribution":dict(sorted(source_history_count.items())),
        "fixed_original_station_date_attempts":total,
        "historically_projected_valid_attempts":valid,
        "historically_projected_unavailable_attempts":sum(nohistory.values()),
        "unavailability_reasons":dict(sorted(nohistory.items())),
        "dates_with_any_direct_monument_uncertainty":sum(
            1 for (plot,day) in {
                (plot,d) for plot,dates in plot_dates.items() for d in dates
            } if (plot,day) not in unique_date_no_monument
        ),
        "source_dates_without_direct_monument_uncertainty":len(unique_date_no_monument),
        "dates_with_full_geoNEON_assumed_uncertainty":len(unique_date_full_uncertainty),
        "original_distinct_plot_capture_dates":sum(len(v) for v in plot_dates.values()),
        "direct_reported_uncertainty_station_date_attempts":directU,
        "geoNEON_adjusted_uncertainty_m_summary":_dist(adjustedU),
        "projected_epsg_attempts_by_code_count_only":{
            "distinct_codes":len(all_site_datums),
            "total":sum(all_site_datums.values()),
        },
        "original_source_plots_geolocation_issue_count":len(flagged),
        "plots_with_at_least_95_positions_valid_every_source_day":len(qualified_plots),
        "sites_with_at_least_one_qualified_plot":len(sites_valid_plots),
        "pairs_with_all_100_positions_valid_every_day":pair_full,
        "pairs_with_at_least_95_station_positions_valid_every_day":pair_95,
        "plot_minimum_valid_station_per_capture_date_summary":_dist(per_plot_min),
        "preregistered_minimum_qualified_plots":min_plots,
        "preregistered_minimum_qualified_sites":min_sites,
        "preregistered_minimum_qualified_pairs":min_pairs,
        "source_date_and_geographic_coverage_gate_passed":ok,
        "uncertainty_is_geoNEON_adjusted_assumption_not_empirical_confidence":True,
        "unknown_uncertainty_never_assumed_zero":True,
        "unknown_positions_reconstructed_from_grid_geometry":False,
        "source_geographic_and_animal_ids_not_exported":True,
        "actual_CHM_at_each_station_date_not_validated":True,
        "genus_habitat_ecological_effect_estimated":False,
        "original_eight_genus_WB_generality":"FAILED_5_OF_8",
        "MOSA_WB":"SEALED",
    }
