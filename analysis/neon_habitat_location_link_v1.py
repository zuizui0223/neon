"""Source-only mammal named-location and anchor checks, not habitat effects.

Field semantics checked against NEONScience/NEON-geolocation getLocMAM.R,
getLocValues.R and getLocProperties.R on 2026-10-20. This module does not
infer 100 trap positions from plot centre/angle or assume live geometry
is valid for every historical capture date. No source IDs in summaries.
"""
from __future__ import annotations
import csv
import io
import math
from analysis.audit_neon_lineage_environmental_source_coverage_v1 import GEO_LOCATION_ISSUE_GRIDS

ANCHORS=('A1','A10','J1','J10','E5')
MISSING={'','NA','N/A','NULL','NONE','NAN'}


def capture_named_locations(raw:bytes, valid_nights:set[str])->dict[str,set[str]]:
    """Private exact source plot -> namedLocation set. Do not export this map."""
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    headers=reader.fieldnames or []
    if len(headers)!=len(set(headers)) or not {'nightuid','plotID','namedLocation'}<=set(headers):
        raise ValueError('source lacks unique nightuid/plotID/namedLocation columns')
    result={}
    for row in reader:
        if None in row or any(v is None for v in row.values()):
            raise ValueError('ragged capture source row')
        if row['nightuid'].strip() not in valid_nights:
            continue
        plot=row['plotID'].strip(); name=row['namedLocation'].strip()
        if plot.upper() in MISSING or name.upper() in MISSING:
            continue
        if name.split('.')[0]!=plot:
            raise ValueError('source namedLocation differs from exact plotID')
        result.setdefault(plot,set()).add(name)
    return result


def _number(value):
    if value is None or isinstance(value,bool):
        return None
    try:
        n=float(value)
    except (TypeError,ValueError):
        return None
    return n if math.isfinite(n) else None


def current_projected_location(payload:dict, expected_name:str)->dict:
    """Read one uniquely current API coordinate; current is NOT historical QA."""
    d=payload.get('data')
    if not isinstance(d,dict) or d.get('locationName')!=expected_name:
        raise ValueError('named location identity mismatch')
    hist=d.get('locationHistory')
    if hist is None:
        r=d; nh=0
    else:
        if not isinstance(hist,list) or any(not isinstance(h,dict) for h in hist):
            raise ValueError('invalid location history structure')
        current=[h for h in hist if str(h.get('current')).lower()=='true']
        if len(current)!=1:
            raise ValueError('no unique current location history')
        r=current[0]; nh=len(hist)
    x=_number(r.get('locationUtmEasting')); y=_number(r.get('locationUtmNorthing'))
    zone=_number(r.get('locationUtmZone',d.get('locationUtmZone')))
    hemisphere=str(r.get('locationUtmHemisphere',d.get('locationUtmHemisphere',''))).upper()
    if x is None or y is None or zone is None or zone!=int(zone) or not 1<=zone<=60 or hemisphere not in {'N','S'}:
        raise ValueError('finite projected coordinates, UTM zone and hemisphere required')
    props={}
    for rec in (d,r):
        for p in rec.get('locationProperties',[]) or []:
            if isinstance(p,dict):
                props[p.get('locationPropertyName')]=p.get('locationPropertyValue')
    uncertainty=_number(props.get('Value for Coordinate uncertainty'))
    if uncertainty is not None and uncertainty<0:
        raise ValueError('negative coordinate uncertainty')
    return {
        'xy':(x,y),'zone':int(zone),'hemisphere':hemisphere,
        'uncertainty_m':uncertainty,'history_records':nh,
        'datum':props.get('Value for Geodetic datum'),
        'historic_capture_date_link_verified':False,
    }


def grid_anchor_geometry(points:dict)->dict:
    """Descriptive five-point layout, never repairs or exports coordinates."""
    if set(points)!=set(ANCHORS):
        raise ValueError('exactly five predeclared anchors required')
    if any(not isinstance(v,(list,tuple)) or len(v)!=2 or any(_number(z) is None for z in v) for v in points.values()):
        raise ValueError('finite two-dimensional anchor coordinates required')
    def vec(a,b):return tuple(float(y)-float(x) for x,y in zip(points[a],points[b]))
    u=vec('A1','A10'); v=vec('A1','J1'); w=vec('A1','J10'); m=vec('A1','E5')
    nu=math.hypot(*u); nv=math.hypot(*v)
    closure=math.hypot(w[0]-u[0]-v[0],w[1]-u[1]-v[1])
    e5=math.hypot(m[0]-4*(u[0]+v[0])/9,m[1]-4*(u[1]+v[1])/9)
    cosine=abs(sum(a*b for a,b in zip(u,v))/(nu*nv)) if nu*nv else 1.
    def direction(vector):
        east,north=vector
        if abs(east)<1e-8 and abs(north)<1e-8:return 'zero'
        if abs(abs(east)-abs(north))<=1e-8:return 'diagonal'
        if abs(east)>abs(north):return 'east' if east>0 else 'west'
        return 'north' if north>0 else 'south'
    return {
        'A1_to_A10_dominant_direction':direction(u),
        'A1_to_J1_dominant_direction':direction(v),
        'coordinates_rotated_or_relabelled':False,
        'edge_A1_A10_m':nu,'edge_A1_J1_m':nv,
        'parallelogram_closure_error_m':closure,'E5_grid_residual_m':e5,
        'absolute_edge_cosine':cosine,
        'five_anchor_rectangular_geometry':70<=nu<=110 and 70<=nv<=110 and closure<=5 and cosine<=.1 and e5<=5,
        'standard_A10_south_J1_west_orientation':u[1]<0 and abs(u[1])>abs(u[0]) and v[0]<0 and abs(v[0])>abs(v[1]),
        'all_100_station_geolocations_verified':False,
        'historical_location_assignment_verified':False,
        'absolute_coordinates_exported':False,
    }


def source_grid_issue_summary(site_plots:set[tuple[str,str]])->dict:
    if not site_plots:
        raise ValueError('original site/plot cohort empty')
    for site,plot in site_plots:
        if not isinstance(site,str) or not isinstance(plot,str) or plot.split('_')[0]!=site:
            raise ValueError('source site/plot mismatch')
    affected={(s,p) for s,p in site_plots if p in GEO_LOCATION_ISSUE_GRIDS}
    return {
        'original_plots':len(site_plots),
        'historically_affected_grids':len(affected),
        'physical_sites_with_affected_grids':len({s for s,p in affected}),
        'special_layout_grids':sum(p=='TEAK_004' for s,p in affected),
        'unlisted_grids_not_automatically_validated':True,
        'nominal_recurrence_invalidated':False,
        'current_API_corrections_not_assumed_from_future_resolution_date':True,
    }
