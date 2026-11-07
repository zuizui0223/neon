"""Effect-blind geographic selection audit for unified NEON mammal macroecology.

All original standard, effort-complete NEON three-night bouts and adjacent
season candidates stay in denominator. The already-fixed 58 three-genus
eligible pairs are a *subset*, never a selected sample of positive outcomes.
NEON /sites metadata supplies domains, core/gradient type, broad latitude
strata; no mammal recurrence, density W/B, environmental effects or per-site
coordinates are inferred.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import date
from math import isfinite
from statistics import median

from analysis.audit_neon_crossseason_genus_support_v1 import (
    _events,_normal_coord,MIN_TRAPS_PER_NIGHT
)

def require(ok:bool, msg:str)->None:
    if not ok:
        raise ValueError("MACRO_SELECTION_SOURCE_DRIFT: "+msg)

def latitude_band(lat:float)->str:
    require(-90 <= lat <= 90 and isfinite(lat),"site metadata latitude invalid")
    if lat < 35:return "lt35"
    if lat < 45:return "35to45"
    if lat < 55:return "45to55"
    return "ge55"

def site_metadata_index(rows:list[dict])->dict:
    require(isinstance(rows,list) and rows,"official NEON sites metadata missing")
    out={}
    for r in rows:
        site=str(r.get("siteCode") or "").strip().upper()
        if not site:continue
        require(site not in out,"official NEON site duplicated")
        domain=str(r.get("domainCode") or "").strip().upper()
        typ=str(r.get("siteType") or "").strip().upper()
        lat=r.get("siteLatitude")
        require(domain.startswith("D") and len(domain)==3,
                "official site domain missing")
        require(typ in {"CORE","GRADIENT"},"unexpected NEON site protocol type")
        try: lat=float(lat)
        except (ValueError,TypeError):
            raise ValueError("official site latitude missing") from None
        out[site]={"domain":domain,"type":typ,"latitude":lat,
                   "latitude_band":latitude_band(lat)}
    require(bool(out),"no valid official source sites")
    return out

def audit_geographic_selection(
    plot_rows:list[dict],trap_rows:list[dict],units:list[dict],
    site_metadata:dict,
    *, expected_eligible_pairs:int=58,expected_eligible_sites:int=14,
    expected_effort_valid_events:int=1838,expected_candidates:int=803,
)->dict:
    require(len(units)==expected_eligible_pairs,
            "frozen primary source pair count changed")
    require(len({u["site"] for u in units})==expected_eligible_sites,
            "frozen primary physical site universe changed")

    selected,_,_=_events(plot_rows)
    night_to_event={}
    for key,meta in selected.items():
        for n in meta["nights"]:
            require(n not in night_to_event or night_to_event[n]==key,
                    "one night belongs to multiple selected source events")
            night_to_event[n]=key
    effort=defaultdict(set)
    for r in trap_rows:
        n=str(r.get("nightuid") or "").strip()
        key=night_to_event.get(n)
        if key is None:continue
        site=str(r.get("_site") or "").strip()
        plot=str(r.get("plotID") or "").strip()
        require((site,plot)==key[:2],"source trap/site event membership changed")
        coord=_normal_coord(r.get("trapCoordinate"))
        if coord:
            effort[(key,n)].add(coord)
    valid_events={
        key:meta for key,meta in selected.items()
        if all(len(effort[(key,n)]) >= MIN_TRAPS_PER_NIGHT for n in meta["nights"])
    }
    require(len(valid_events)==expected_effort_valid_events,
            "original canonical 3night effort-complete bouts changed")
    byplot=defaultdict(dict)
    for key,meta in valid_events.items():
        site,plot,event=key
        byplot[(site,plot)][meta["season"]]=key
    candidates=set()
    for (site,plot),seasons in byplot.items():
        for q in seasons:
            if q+1 in seasons:
                candidates.add((site,plot,q))
    require(len(candidates)==expected_candidates,
            "candidate consecutive-season source population changed")

    approved={(u["site_plot"][0],u["site_plot"][1],u["season_ordinal"])
              for u in units}
    require(len(approved)==expected_eligible_pairs and approved.issubset(candidates),
            "frozen primary outcome eligibility not a candidate subset")
    valid_sites={k[0] for k in valid_events}
    candidate_sites={c[0] for c in candidates}
    primary_sites={u["site"] for u in units}
    require(all(s in site_metadata for s in valid_sites),
            "official domain/latitude metadata missing for original release cohort")

    bydomain=defaultdict(lambda:{"selected_sites":set(),"candidate_sites":set(),
                                 "qualified_sites":set(),
                                 "effort_valid_bouts":0,"candidate_pairs":0,
                                 "qualified_pairs":0})
    bytype=defaultdict(lambda:{"selected_sites":set(),"candidate_sites":set(),
                               "qualified_sites":set(),"effort_valid_bouts":0,
                               "candidate_pairs":0,"qualified_pairs":0})
    bylat=defaultdict(lambda:{"selected_sites":set(),"candidate_sites":set(),
                              "qualified_sites":set(),"effort_valid_bouts":0,
                              "candidate_pairs":0,"qualified_pairs":0})

    for selector,keys in [
        (bydomain,"domain"),(bytype,"type"),(bylat,"latitude_band")
    ]:
        for event in valid_events:
            site=event[0]
            ref=selector[site_metadata[site][keys]]
            ref["selected_sites"].add(site)
            ref["effort_valid_bouts"]+=1
        for site,plot,q in candidates:
            ref=selector[site_metadata[site][keys]]
            ref["candidate_sites"].add(site)
            ref["candidate_pairs"]+=1
        for site,plot,q in approved:
            ref=selector[site_metadata[site][keys]]
            ref["qualified_sites"].add(site)
            ref["qualified_pairs"]+=1

    def grouped(obj):
        return {
            cat:{
                "source_effort_valid_sites":len(row["selected_sites"]),
                "source_adjacent_season_candidate_sites":len(row["candidate_sites"]),
                "primary_eligible_sites":len(row["qualified_sites"]),
                "source_effort_valid_bouts":row["effort_valid_bouts"],
                "source_adjacent_season_candidate_pairs":row["candidate_pairs"],
                "primary_eligible_pairs":row["qualified_pairs"],
                "eligible_pair_fraction_of_candidate_pairs": (
                    row["qualified_pairs"]/row["candidate_pairs"]
                    if row["candidate_pairs"] else None
                ),
            }
            for cat,row in sorted(obj.items())
        }

    med=lambda sites:(float(median(site_metadata[s]["latitude"] for s in sites))
                      if sites else None)
    candidate_byyear=Counter(q//4 for site,plot,q in candidates)
    primary_byyear=Counter(q//4 for site,plot,q in approved)
    require(sum(candidate_byyear.values())==len(candidates)
            and sum(primary_byyear.values())==len(approved),
            "original source calendar pairing changed")
    return {
        "schema":"neon.unified_macro.biogeographic_selection_source_only.v1",
        "status":"SOURCE_ONLY_MACRO_SELECTION_RECONSTRUCTED",
        "study_window":"RELEASE-2026, 2015-04..2026-09",
        "original_source_denominators":{
            "effort_valid_three_night_bouts":len(valid_events),
            "physical_sites_with_one_or_more_effort_valid_bouts":len(valid_sites),
            "original_adjacent_season_pairs":len(candidates),
            "physical_sites_with_one_or_more_candidate_pairs":len(candidate_sites),
            "original_primary_three_genus_eligible_pairs":len(approved),
            "primary_independent_physical_sites":len(primary_sites),
            "primary_eligibility_fraction_of_candidates":len(approved)/len(candidates),
            "primary_site_fraction_of_candidate_sites":len(primary_sites)/len(candidate_sites),
        },
        "domain_grouped_source_only":grouped(bydomain),
        "field_site_core_gradient_grouped_source_only":grouped(bytype),
        "latitude_band_grouped_source_only":grouped(bylat),
        "calendar_year_pairs_source_only":{
            str(y):{"candidate_pairs":candidate_byyear[y],
                    "primary_eligible_pairs":primary_byyear[y]}
            for y in sorted(candidate_byyear)
        },
        "sampling_coverage_summary":{
            "candidate_site_latitude_median_degrees_not_capture_year_specific":med(candidate_sites),
            "eligible_site_latitude_median_degrees_not_capture_year_specific":med(primary_sites),
            "distinct_candidate_domains":len({site_metadata[s]["domain"] for s in candidate_sites}),
            "distinct_primary_domains":len({site_metadata[s]["domain"] for s in primary_sites}),
            "source_metadata_coverage_complete":True,
            "site_latitudes_not_station_geolocation":True,
        },
        "effect_boundary":{
            "historical_recurrence_Z_or_p_read":False,
            "historical_W_B_or_density_slopes_read":False,
            "time_matched_climate_soil_canopy_read":False,
            "macro_habitat_or_latitude_effect_fit":False,
            "not_an_environmental_selection_causal_test":True,
            "nonqualified_sites_not_declared_zero_recurrence":True,
            "individual_tag_station_or_site_id_exported":False,
            "some_domains_have_no_supported_site_estimand":True,
            "historical_2026_source_not_independent_confirmation":True,
        },
    }
