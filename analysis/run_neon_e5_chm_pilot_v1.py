"""Actual released CHM raster access at E5; not trap-scale ecological inference.

Selection is fixed before reading height values. Named coordinates are live
and not assumed historically validated. No source identifiers are exported.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
import math
import os
from pathlib import Path
from statistics import median
from analysis.run_neon_habitat_source_link_v1 import (
    reconstruct,location_query,_request_json,_download_many,
    BASE,QUERY_URL,TOKEN_ENV,digest,
)
from analysis.neon_e5_chm_pilot_v1 import (
    PRODUCT,RELEASE,latest_month_before_cutoff,chm_manifest,
    verify_raster_bytes,inspect_reference_pixel,
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/neon_e5_chm_raster_pilot_v1.json'
MAX_BYTES=280_000_000


def explicit_epsg(location):
    datum=''.join(c for c in str(location.get('datum') or '').upper() if c.isalnum())
    zone=location['zone'];hem=location['hemisphere']
    if datum in {'WGS84','WGS1984','WORLDGEODETICSYSTEM1984'}:
        return (32600 if hem=='N' else 32700)+zone
    if datum=='NAD83' and hem=='N' and 1<=zone<=23:return 26900+zone
    return None


def run():
    token=os.environ.get(TOKEN_ENV,'').strip()
    if not token:raise RuntimeError('NEON_API_TOKEN_REQUIRED')
    units,cohort,sites,names,source=reconstruct(token)
    if (len(units),len(cohort),len(sites))!=(58,30,14):raise ValueError('fixed source cohort changed')
    if any(len(names[k])!=1 for k in cohort):raise ValueError('nonunique source namedLocation')
    references={};counts=Counter();failures=Counter();response_hashes=[]
    for key in sorted(cohort):
        named=next(iter(names[key]))+'.E5'
        _,_,loc,error,sha=location_query((key,'E5',named),token)
        if error:
            counts['E5_QUERY_OR_SCHEMA_ERROR']+=1;continue
        references[key]=loc;response_hashes.append(sha)
    meta=_request_json(BASE+'products/'+PRODUCT+'?release='+RELEASE,token=token)
    site_records=meta.get('data',{}).get('siteCodes',[])
    if not isinstance(site_records,list):raise ValueError('source product sites schema')
    months={r.get('siteCode'):r.get('availableMonths',[]) for r in site_records}
    choices={s:latest_month_before_cutoff(months.get(s,[])) for s in sites}
    candidates={};query_shapes=Counter();year_counts=Counter();manifest_hashes=[]
    for site in sorted(sites):
        month=choices[site]
        if month is None:continue
        year=int(month[:4]);year_counts[str(year)]+=1
        try:
            payload=_request_json(QUERY_URL,token=token,body={
                'productCode':PRODUCT,'siteCodes':[site],
                'startDateMonth':str(year)+'-01','endDateMonth':str(year)+'-12',
                'release':RELEASE,'package':'basic','includeProvisional':False})
            manifest_hashes.append(digest(payload))
            query_shapes['|'.join(sorted(payload.get('data',{}).keys()))]+=1
            candidates[site]=[r for r in chm_manifest(payload,site,year) if r['month']==month]
        except Exception as exc:
            failures['CHM_MANIFEST_'+type(exc).__name__]+=1
            candidates[site]=[]
    selected={};plot_tiles={};crs_for_plot={};datum_summary=Counter()
    for key,loc in references.items():
        epsg=explicit_epsg(loc)
        datum_summary['explicit_supported' if epsg is not None else 'missing_or_unsupported']+=1
        if epsg is None:
            counts['E5_DATUM_UNRESOLVED']+=1;continue
        x,y=loc['xy'];e=1000*math.floor(x/1000);n=1000*math.floor(y/1000)
        options=[r for r in candidates.get(key[0],[]) if r['tile_easting']==e and r['tile_northing']==n]
        if len(options)!=1:
            counts['NO_RELEASED_TILE_AT_E5' if not options else 'AMBIGUOUS_RELEASED_TILE']+=1
            continue
        tile=options[0];tid=(tile['site'],tile['month'],tile['name'])
        selected[tid]=tile;plot_tiles[key]=tid;crs_for_plot[key]=epsg
    nbytes=sum(r['size'] for r in selected.values())
    if nbytes>MAX_BYTES:raise ValueError('predeclared raster download budget exceeded')
    raster_data={};raster_sha=[]
    # One tile at a time bounds memory and isolates source download failures.
    for tid,tile in sorted(selected.items()):
        try:
            raw=_download_many([tile],token,max_workers=1)[0]
            verify_raster_bytes(raw,tile)
            raster_data[tid]=raw
            raster_sha.append(hashlib.sha256(raw).hexdigest())
        except Exception as exc:failures['CHM_DOWNLOAD_'+type(exc).__name__]+=1
    values=[];valid_sites=set();known_uncertainty=0;windows=[];negative=0
    for key,tid in plot_tiles.items():
        if tid not in raster_data:
            counts['RASTER_DOWNLOAD_FAILED']+=1;continue
        loc=references[key]
        try:
            report=inspect_reference_pixel(raster_data[tid],*loc['xy'],crs_for_plot[key],loc['uncertainty_m'])
        except Exception as exc:
            failures['RASTER_READ_'+type(exc).__name__]+=1
            counts['RASTER_READ_FAILED']+=1;continue
        counts[report['status']]+=1
        if report['status']=='VALID_REFERENCE_PIXEL':
            values.append(report['height_m']);valid_sites.add(key[0])
            known_uncertainty+=report['coordinate_uncertainty_known']
            negative+=report['negative_height_flag']
            if report['uncertainty_window_valid_fraction'] is not None:
                windows.append(report['uncertainty_window_valid_fraction'])
    if sum(counts.values())!=30:raise ValueError('fixed 30-plot denominator lost')
    return {
        'schema':'neon.E5_CHM_reference_pixel_access.v1',
        'status':('ACTUAL_REFERENCE_PIXELS_READ_NOT_TRAP_HABITAT_EVIDENCE'
                  if values else 'NO_VALID_REFERENCE_PIXELS_SOURCE_LINK_INCOMPLETE'),
        'executed_UTC':datetime.now(timezone.utc).isoformat(),
        'source_cohort':source,
        'fixed_original_plots':30,'fixed_original_sites':14,
        'locations_successfully_parsed':len(references),
        'location_datum_status':dict(datum_summary),
        'live_reference_location_digest_set_sha256':digest(sorted(response_hashes)),
        'product_metadata_canonical_sha256':digest(meta),
        'requested_exact_release':RELEASE,
        'selected_acquisition_year_site_counts':dict(sorted(year_counts.items())),
        'selection':'latest advertised month in 2015 through 2025 per original site; no alternative month/year substitution',
        'manifest_response_shape_counts':dict(query_shapes),
        'manifest_response_digest_set_sha256':digest(sorted(manifest_hashes)),
        'plots_with_unique_filename_candidate_tile':len(plot_tiles),
        'unique_selected_tiles':len(selected),'selected_tile_bytes':nbytes,
        'tiles_downloaded_and_MD5_size_verified':len(raster_data),
        'downloaded_raster_sha256_digest_set':digest(sorted(raster_sha)),
        'reference_pixel_status_counts':dict(counts),
        'request_or_read_errors_by_class':dict(failures),
        'valid_reference_pixels':len(values),'sites_with_valid_reference_pixel':len(valid_sites),
        'valid_reference_height_m_summary':{
            'minimum':min(values) if values else None,'median':median(values) if values else None,
            'maximum':max(values) if values else None,'zero_values':sum(x==0 for x in values),
            'negative_values_flagged':negative},
        'valid_reference_pixels_with_known_coordinate_uncertainty':known_uncertainty,
        'uncertainty_window_valid_fraction_minimum':min(windows) if windows else None,
        'scientific_boundary':{
            'E5_is_reference_only_not_100_station_substitute':True,
            'all_station_orientation_resolved':False,
            'coordinates_rotated_relabelled_or_synthesized':False,
            'historical_location_dates_and_capture_events_matched':False,
            'latest_canopy_flight_assumed_contemporaneous_with_all_captures':False,
            'height_zero_treated_as_absent_vegetation':False,
            'habitat_or_detection_effect_estimated':False,
            'corrected_recurrence_result_refitted':False,
            'raw_locations_animal_IDs_or_raster_tiles_exported':False,
            'original_density_W_B_status':'FAILED_5_OF_8','MOSA_W_B':'SEALED'}
    }


def main():
    try:result=run()
    except Exception as exc:
        result={'schema':'neon.E5_CHM_reference_pixel_access.v1',
                'status':'STOP_SOURCE_OR_RASTER_PILOT','error_class':type(exc).__name__,
                'habitat_effect_estimated':False,'raw_source_identifiers_exported':False}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
    return 3 if result['status'].startswith('STOP') else 0
if __name__=='__main__':raise SystemExit(main())
