"""Source-only audit of a 2026 independently obtained camera-trap dataset.

Real observer channel is camera vs Sherman trap, but statistical errors may
remain correlated, and 1-month deployments cannot prove seasonal recurrence.
Only source availability is measured, never mammal habitat/use parameters.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from datetime import date, datetime
from math import radians,cos,sin,asin,sqrt,isfinite
import csv
import io

RODENT_FAMILIES=frozenset({"Cricetidae","Heteromyidae","Dipodidae","Muridae"})
NEON_SPATIAL_PREFILTER_M=250.0
EXACT_STATION_RADIUS_M=20.0

def _csv(raw, required):
    try:
        text=raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("Camera CSV invalid UTF-8") from None
    reader=csv.DictReader(io.StringIO(text))
    fields=reader.fieldnames or []
    if len(fields)!=len(set(fields)) or not set(required).issubset(fields):
        raise ValueError("Camera CSV schema absent or repeated")
    return reader

def _day(value):
    try:return date.fromisoformat(str(value).strip()[:10])
    except (ValueError,TypeError):return None

def parse_deployments(raw):
    """Structured camera effort; missing coordinates and dates not imputed."""
    reader=_csv(raw,("deployment_id","latitude","longitude","start_date","end_date","subproject_name"))
    out={};counts=Counter()
    for row in reader:
        counts["source_deployment_rows"]+=1
        if None in row or any(v is None for v in row.values()):
            raise ValueError("Ragged camera deployment CSV")
        ident=(row["deployment_id"] or "").strip()
        if not ident or ident in out:
            raise ValueError("Empty or duplicate camera deployment identifier")
        start,end=_day(row["start_date"]),_day(row["end_date"])
        try:
            lat=float(row["latitude"]);lon=float(row["longitude"])
        except (ValueError,TypeError):
            lat=lon=float("nan")
        valid=(start is not None and end is not None and start<=end
               and isfinite(lat) and isfinite(lon)
               and -90<=lat<=90 and -180<=lon<=180)
        counts["valid_camera_deployments"]+=int(valid)
        counts["missing_or_bad_geodate_deployments"]+=int(not valid)
        out[ident]={
            "valid":valid,"lat":lat,"lon":lon,"start":start,"end":end,
            "subproject":(row.get("subproject_name") or "").strip(),
        }
    return out,dict(sorted(counts.items()))

def _camera_dt(text):
    for fmt in ("%m/%d/%y %H:%M","%m/%d/%Y %H:%M","%Y-%m-%d %H:%M:%S"):
        try:return datetime.strptime(text.strip(),fmt)
        except (ValueError,AttributeError):pass
    return None

def parse_camera_sequences(raw, deployments):
    """Keep genus-specific rodent detections separate from unknown mammals."""
    reader=_csv(raw,("deployment_id","sequence_id","class","order","family","genus","common_name","start_time"))
    census=Counter();taxon_genus=set();bydeployment_day=defaultdict(set)
    for row in reader:
        census["camera_source_sequence_rows"]+=1
        if None in row or any(v is None for v in row.values()):
            raise ValueError("Ragged published camera sequence row")
        did=(row["deployment_id"] or "").strip()
        if did not in deployments:
            census["source_sequences_without_known_deployment"]+=1
            continue
        d=_camera_dt(row.get("start_time") or "")
        if d is None:
            census["sequences_with_unparseable_calendar_time"]+=1
            continue
        rec=deployments[did]
        if not rec["valid"] or not (rec["start"]<=d.date()<=rec["end"]):
            census["sequences_outside_camera_effort_or_invalid_deployment"]+=1
            continue
        census["time_valid_camera_sequence_rows"]+=1
        order=(row.get("order") or "").strip()
        family=(row.get("family") or "").strip()
        genus=(row.get("genus") or "").strip()
        cl=(row.get("class") or "").strip()
        common=(row.get("common_name") or "").strip().lower()
        known=bool(genus and genus.upper() not in {"NA","N/A","UNKNOWN","NULL"})
        if "small mammal" in common and not known:
            census["unidentified_small_mammal_sequences"]+=1
        if cl=="Mammalia" and order=="Rodentia":
            census["rodent_order_sequences"]+=1
            if known:
                census["known_rodent_genus_sequences"]+=1
                if family in RODENT_FAMILIES:
                    census["target_small_rodent_genus_sequences"]+=1
                    taxon_genus.add(genus)
                    bydeployment_day[(did,d.date())].add(genus)
                else:
                    census["other_rodent_family_genus_sequences"]+=1
            else:
                census["rodent_without_genus_sequences"]+=1
    return {
        "census":dict(sorted(census.items())),
        "small_rodent_genus_richness":len(taxon_genus),
        "small_rodent_genus_by_deployment_day":bydeployment_day,
        "camera_deployments_with_target_rodent_genus":len({
            did for did,day in bydeployment_day
        }),
    }

def haversine_m(lat1,lon1,lat2,lon2):
    for v in (lat1,lon1,lat2,lon2):
        if not isfinite(v):raise ValueError("Nonfinite original source longitude/latitude")
    a=radians(lat1);b=radians(lat2)
    dlat=b-a;dlon=radians(lon2-lon1)
    h=sin(dlat/2)**2+cos(a)*cos(b)*sin(dlon/2)**2
    return 2*6371008.8*asin(sqrt(min(1,max(0,h))))

def candidate_e5_pairs(units,coords_e5,deployments,*,expected_pairs=58,expected_sites=14,expected_plots=30):
    """Proximity screen only, NEVER an exact 100-station co-location claim."""
    if len(units)!=expected_pairs:raise ValueError("Original mammal source pair count drifted")
    plots={tuple(u["site_plot"]) for u in units}
    sites={u["site"] for u in units}
    if len(sites)!=expected_sites or len(plots)!=expected_plots or set(coords_e5)!=plots:
        raise ValueError("Original 30 NEON E5 named station population incomplete")
    bands={250:set(),1000:set(),5000:set(),10000:set()}
    co_temporal=set();prospective=defaultdict(list)
    for camera_id,cam in deployments.items():
        if not cam["valid"]:continue
        for plot,(lat,lon) in coords_e5.items():
            distance=haversine_m(lat,lon,cam["lat"],cam["lon"])
            for limit in bands:
                if distance<=limit:bands[limit].add((plot,camera_id))
            if distance>NEON_SPATIAL_PREFILTER_M:continue
            if any(cam["start"]<=d<=cam["end"] for u in units
                   if tuple(u["site_plot"])==plot
                   for d in tuple(u["capture_dates_A"])+tuple(u["capture_dates_B"])):
                co_temporal.add((plot,camera_id))
                prospective[plot].append(camera_id)
    report={
        "camera_plot_links_E5_within_250m":len(bands[250]),
        "camera_plot_links_E5_within_1000m":len(bands[1000]),
        "camera_plot_links_E5_within_5000m":len(bands[5000]),
        "camera_plot_links_E5_within_10000m":len(bands[10000]),
        "original_plots_with_camera_near_E5_250m_any_date":len({x[0] for x in bands[250]}),
        "original_plots_with_camera_E5_250m_and_actual_capture_day_overlap":len(prospective),
        "camera_plot_links_E5_250m_with_capture_day_overlap":len(co_temporal),
        "NEON_10x10_station_proximity_not_concluded_from_E5":True,
    }
    return report,prospective

def exact_station_camera_sources(units,station_locs,deployments,prospective,genus_days,
                                 *,expected_pairs=58):
    """Match official 100-station positions and actual day×genus photos."""
    if len(units)!=expected_pairs:raise ValueError("Original 58 comparison keys drift")
    support=Counter()
    sites=defaultdict(set);plots=defaultdict(set)
    camera_near_traps=set()
    for u in units:
        plot=tuple(u["site_plot"]);site=u["site"]
        A=tuple(u["capture_dates_A"]);B=tuple(u["capture_dates_B"])
        if plot[0]!=site or len(A)!=3 or len(B)!=3 or len(set(A+B))!=6:
            raise ValueError("Mammal original six-night unit malformed")
        near=[]
        for cam_id in prospective.get(plot,[]):
            cam=deployments[cam_id]
            if not cam["valid"]:continue
            locs=station_locs.get(plot)
            if locs is None or len(locs)!=100:
                raise ValueError("Original official 100 station positions missing for candidate plot")
            distance=min(haversine_m(cam["lat"],cam["lon"],lat,lon) for lat,lon in locs)
            if distance<=EXACT_STATION_RADIUS_M:
                near.append(cam_id)
                camera_near_traps.add((plot,cam_id))
        support["original_pairs_with_exact_camera_station_20m_any_bout"]+=bool(near)
        detected_a=set();detected_b=set()
        a_active=b_active=False
        for cam_id in near:
            cam=deployments[cam_id]
            for day in A:
                if cam["start"]<=day<=cam["end"]:
                    a_active=True
                    detected_a.update(genus_days.get((cam_id,day),set()))
            for day in B:
                if cam["start"]<=day<=cam["end"]:
                    b_active=True
                    detected_b.update(genus_days.get((cam_id,day),set()))
        support["original_pairs_with_a_camera_active_in_both_seasons"]+=a_active and b_active
        support["original_pairs_with_camera_small_rodent_genus_in_A"]+=bool(detected_a)
        support["original_pairs_with_camera_small_rodent_genus_in_B"]+=bool(detected_b)
        both=bool(detected_a and detected_b)
        support["original_pairs_with_camera_rodent_genus_detected_both_seasons"]+=both
        support["original_pairs_with_at_least_2_camera_rodent_genera_shared_A_B"]+=len(detected_a&detected_b)>=2
        if both:sites["both"].add(site);plots["both"].add(plot)
        if len(detected_a&detected_b)>=2:
            sites["two_shared"].add(site);plots["two_shared"].add(plot)
    for key in (
        "original_pairs_with_exact_camera_station_20m_any_bout",
        "original_pairs_with_a_camera_active_in_both_seasons",
        "original_pairs_with_camera_small_rodent_genus_in_A",
        "original_pairs_with_camera_small_rodent_genus_in_B",
        "original_pairs_with_camera_rodent_genus_detected_both_seasons",
        "original_pairs_with_at_least_2_camera_rodent_genera_shared_A_B"
    ):support.setdefault(key,0)
    strict=(support["original_pairs_with_at_least_2_camera_rodent_genera_shared_A_B"]>=20
            and len(sites["two_shared"])>=8
            and len(plots["two_shared"])>=12)
    return {
        "exact_20m_camera_mammal_plot_links":len(camera_near_traps),
        "source_observation_support":dict(sorted(support.items())),
        "independent_physical_sites_with_rodent_camera_both_seasons":len(sites["both"]),
        "independent_physical_sites_with_two_repeat_camera_genera":len(sites["two_shared"]),
        "original_mammal_grids_with_camera_rodent_both_seasons":len(plots["both"]),
        "strict_source_20pair_8site_12plot_two_genus_GO":strict,
        "camera_detections_not_known_true_trap_use_or_p":True,
        "no_mammal_rodent_capture_Z_or_animal_IDs_read":True,
    }
