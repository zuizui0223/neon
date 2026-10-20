"""Match the fixed mammal cohort to environmental metadata and named points.

Does not fit any environmental association or recompute old nulls. The live
Locations API is a timestamped external source, NOT part of RELEASE-2026.
Five anchors diagnose orientation; no other station is synthesized from them.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import urllib.error
from urllib.parse import quote
from analysis.run_neon_crossseason_direct_site_null_calibration_v1 import (
    _request_json,_site_codes,_inventory,_download_many,_read_plot_rows,
    _read_trap_rows,_candidate_nights,_taxonomy,source_event_support,
    verified_support_gate,PRODUCT,RELEASE,START,END,PRODUCT_URL,QUERY_URL,
    TOKEN_ENV,MAX_DOWNLOAD_WORKERS,SOURCE_SUPPORT,
)
from analysis.audit_neon_lineage_environmental_source_coverage_v1 import (
    PRODUCTS,GEO_LOCATION_ISSUE_SITES,GEO_LOCATION_ISSUE_GRIDS,
    summarize_habitat_product_site_coverage,
)
from analysis.neon_habitat_location_link_v1 import (
    ANCHORS,capture_named_locations,current_projected_location,
    grid_anchor_geometry,source_grid_issue_summary,
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/neon_habitat_source_link_v1.json'
BASE='https://data.neonscience.org/api/v0/'


def require(ok,message):
    if not ok: raise RuntimeError(message)


def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def reconstruct(token):
    frozen=json.loads(SOURCE_SUPPORT.read_text())
    require((RELEASE,START,END)==('RELEASE-2026','2015-04','2026-09'),'source window changed')
    sites=_site_codes(_request_json(PRODUCT_URL))
    manifest=_inventory(_request_json(QUERY_URL,token=token,body={
        'productCode':PRODUCT,'siteCodes':sites,'startDateMonth':START,
        'endDateMonth':END,'release':RELEASE,'package':'basic','includeProvisional':False,
    }))
    pf=[x for x in manifest if 'mam_perplotnight' in x['name']]
    require(len(manifest)==3547 and len(pf)==1773,'source manifest changed')
    plots=[]
    for m,raw in zip(pf,_download_many(pf,token,max_workers=MAX_DOWNLOAD_WORKERS)):
        plots.extend(_read_plot_rows(raw,m['site'],m['month']))
    nights,months=_candidate_nights(plots)
    tf=[x for x in manifest if 'mam_pertrapnight' in x['name'] and (x['site'],x['month']) in months]
    require(len(tf)==1707,'source capture file count changed')
    traps=[]; names=defaultdict(set); missing_schema=0
    for m,raw in zip(tf,_download_many(tf,token,max_workers=MAX_DOWNLOAD_WORKERS)):
        for r in _read_trap_rows(raw,nights):
            r['_site']=m['site']; traps.append(r)
        try:
            named=capture_named_locations(raw,nights)
        except ValueError as e:
            if 'columns' not in str(e): raise
            missing_schema+=1; continue
        for p,values in named.items():names[(m['site'],p)].update(values)
    require(len(plots)==21363 and len(traps)==1505827,'source row counts changed')
    units=[]
    structure=source_event_support(plots,traps,_taxonomy()[1],internal_units=units)
    verified_support_gate(structure,frozen)
    cohort={tuple(u['site_plot']) for u in units}; ecology_sites={u['site'] for u in units}
    require(len(units)==58 and len(cohort)==30 and len(ecology_sites)==14,'source cohort changed')
    return units,cohort,ecology_sites,names,{
        'release':RELEASE,'manifest_files':len(manifest),
        'downloaded_source_files_MD5_size_verified':len(pf)+len(tf),
        'perplotnight_files':len(pf),'pertrapnight_files':len(tf),
        'source_plot_rows':len(plots),'source_trap_rows':len(traps),
        'same_58_pairs_30_plots_14_sites_reproduced':True,
        'capture_files_without_required_namedLocation_schema':missing_schema,
    }


def location_query(job,token):
    site_plot,anchor,name=job
    try:
        raw=_request_json(BASE+'locations/'+quote(name,safe='')+'?history=true',token=token)
        parsed=current_projected_location(raw,name)
        return site_plot,anchor,parsed,None,digest(raw)
    except urllib.error.HTTPError as e:
        return site_plot,anchor,None,'HTTP_'+str(e.code),None
    except ValueError as e:
        return site_plot,anchor,None,'SCHEMA_'+str(e),None
    except Exception as e:
        return site_plot,anchor,None,type(e).__name__,None


def run():
    token=os.environ.get(TOKEN_ENV,'').strip()
    require(bool(token),'source access token unavailable')
    units,cohort,sites,names,source=reconstruct(token)
    metas={}; sources={}
    for product in PRODUCTS:
        raw=_request_json(BASE+'products/'+product+'?release='+RELEASE,token=token)
        metas[product]=set(_site_codes(raw))
        sources[product]={'sha256_canonical_json':digest(raw),'advertised_sites':len(metas[product]),'requested_release':RELEASE}
    coverage=summarize_habitat_product_site_coverage(sites,metas,GEO_LOCATION_ISSUE_SITES)
    issue=source_grid_issue_summary(cohort)
    mapped={key:next(iter(names[key])) for key in sorted(cohort) if len(names[key])==1}
    jobs=[(key,anchor,parent+'.'+anchor) for key,parent in sorted(mapped.items()) for anchor in ANCHORS]
    coordinates=defaultdict(dict); errors=Counter(); hash_list=[]; history_counts=Counter()
    with ThreadPoolExecutor(max_workers=4) as ex:
        for key,anchor,values,error,sha in ex.map(lambda job:location_query(job,token),jobs):
            if error:errors[error]+=1
            else:
                coordinates[key][anchor]=values
                hash_list.append(sha)
                history_counts[str(values['history_records'])]+=1
    geometry=[]; unresolved_zone=0
    for key in sorted(mapped):
        if set(coordinates[key])!=set(ANCHORS):continue
        system={(r['zone'],r['hemisphere']) for r in coordinates[key].values()}
        if len(system)!=1:unresolved_zone+=1;continue
        g=grid_anchor_geometry({a:r['xy'] for a,r in coordinates[key].items()})
        g['historically_flagged_grid']=key[1] in GEO_LOCATION_ISSUE_GRIDS
        g['anchor_uncertainty_complete']=all(r['uncertainty_m'] is not None for r in coordinates[key].values())
        geometry.append(g)
    return {
        'schema':'neon.lineage.habitat_source_and_anchor_link.v1',
        'status':'SOURCE_COHORT_RECONSTRUCTED_METADATA_AND_ANCHOR_AUDIT_COMPLETE',
        'retrieved_UTC':datetime.now(timezone.utc).isoformat(),
        'source':source,'product_metadata':sources,'site_coverage':coverage,
        'historical_issue_grid_intersection':issue,
        'source_named_location_link':{
            'fixed_original_plots':len(cohort),'plots_with_one_source_namedLocation':len(mapped),
            'plots_with_no_source_namedLocation':sum(not names[k] for k in cohort),
            'plots_with_multiple_source_namedLocations':sum(len(names[k])>1 for k in cohort),
            'location_names_constructed_only_by_official_namedLocation_plus_trapCoordinate_rule':True,
        },
        'current_named_location_anchor_audit':{
            'requested_anchor_documents':len(jobs),'successfully_parsed_documents':len(hash_list),
            'failures_by_category':dict(errors),'history_record_count_distribution':dict(history_counts),
            'response_digest_set_sha256':digest(sorted(hash_list)),
            'plots_with_five_current_projected_anchors':len(geometry),
            'plots_with_mixed_UTM_zone':unresolved_zone,
            'plots_with_five_anchor_rectangular_geometry':sum(g['five_anchor_rectangular_geometry'] for g in geometry),
            'plots_with_standard_cardinal_orientation':sum(g['standard_A10_south_J1_west_orientation'] for g in geometry),
            'historically_flagged_plots_with_standard_cardinal_orientation':sum(g['historically_flagged_grid'] and g['standard_A10_south_J1_west_orientation'] for g in geometry),
            'plots_with_all_five_anchor_uncertainties':sum(g['anchor_uncertainty_complete'] for g in geometry),
            'live_named_locations_not_RELEASE_2026':True,
            'history_matched_to_actual_capture_dates':False,
            'all_100_station_locations_verified':False,
            'raster_pixels_extracted':False,
        },
        'scientific_boundary':{
            'corrected_recurrence_result_not_refitted':True,
            'old_accepted_clock_p_values_not_reinstated':True,
            'metadata_presence_not_station_habitat_evidence':True,
            'habitat_filtering_or_detection_mechanism_established':False,
            'environmental_effect_fit_opened':False,
            'source_site_grid_trap_or_animal_identifiers_exported':False,
            'next':'Match source-dated full station coordinates and verified CHM tiles before any habitat association. Historical issue is grid-specific; do not discard all grids of a flagged site.',
        },
    }


def main():
    try:r=run()
    except Exception as e:
        r={'schema':'neon.lineage.habitat_source_and_anchor_link.v1','status':'STOP_SOURCE_OR_ENVIRONMENTAL_METADATA','error_class':type(e).__name__,'environmental_effect_fit_opened':False}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print(json.dumps(r,indent=2,sort_keys=True))
    return 3 if r['status'].startswith('STOP') else 0

if __name__=='__main__':raise SystemExit(main())
