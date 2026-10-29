#!/usr/bin/env python3
"""Exploratory independent two-method temporal detection comparison.

Published South-East Norway tunnel cameras and nearby cage/snap capture
traps, not original NEON site/trap observations or true ecological use.
Different method effort forbids interpreting count ratios as detection p.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean,median
from random import Random
import csv,hashlib,io,json,urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_norway_external_two_detector_20261029.json"
URL="https://zenodo.org/records/15312178/files/count_cam_vs_trap_traptype.csv?download=1"
DOI="10.5281/zenodo.15312178"
ORIGINAL_MD5="56f71c980503a4e6043b4d3d424fd53c"
TAXA={"bank vole","common shrew","wood mouse","pygmy shrew"}
CAMPAIGNS={(2018,"fall"),(2019,"fall"),(2019,"spring"),(2020,"fall"),(2020,"spring")}
TRANSITIONS=(((2018,"fall"),(2019,"fall")),((2019,"fall"),(2020,"fall")),((2019,"spring"),(2020,"spring")))
FIELDS=["site","year","season","species","count.live","count.cam","traptype"]

def original_rows(raw,*,pinned=True):
    """Require complete site×year-season×taxon source; never impute missing."""
    if pinned and hashlib.md5(raw).hexdigest()!=ORIGINAL_MD5:
        raise ValueError("2025 public Zenodo v5 MD5 differs")
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")),delimiter=";")
    if reader.fieldnames!=FIELDS:raise ValueError("Published paired detector schema")
    data={};groups=defaultdict(set);type_by_site_campaign={}
    sites=set();taxa=set()
    for row in reader:
        if None in row or any(v is None for v in row.values()):
            raise ValueError("Ragged published source row")
        site=row["site"].strip();sp=row["species"].strip().lower()
        year=int(row["year"]);season=row["season"].strip().lower()
        traptype=row["traptype"].strip().lower()
        if not site or (year,season) not in CAMPAIGNS or traptype not in {"snap","cage"}:
            raise ValueError("Invalid source site/campaign/capture gear")
        a=row["count.live"].strip();b=row["count.cam"].strip()
        if not a.isdecimal() or not b.isdecimal():
            raise ValueError("Missing/negative or noninteger observation")
        key=(site,year,season,sp)
        if key in data:raise ValueError("Duplicate source taxon record")
        data[key]=(int(a),int(b),traptype)
        sites.add(site);taxa.add(sp)
        groups[(site,year,season)].add(sp)
        k=(site,year,season)
        if k in type_by_site_campaign and type_by_site_campaign[k]!=traptype:
            raise ValueError("Inconsistent trapping gear within campaign")
        type_by_site_campaign[k]=traptype
    if pinned:
        if len(data)!=240 or len(sites)!=12 or taxa!=TAXA or len(groups)!=60:
            raise ValueError("Original 12 sites × 5 campaigns × 4 taxa universe drifted")
        if any({(y,season) for (s,y,season) in groups if s==site}!=CAMPAIGNS for site in sites):
            raise ValueError("Missing source site campaign")
        if any(v!=TAXA for v in groups.values()):
            raise ValueError("Missing source species-cell is not zero detection")
    return data,sites,taxa,groups

def summarize_observation_channels(parsed):
    data,sites,taxa,groups=parsed
    discord=Counter();per_taxon=defaultdict(Counter);site_campaign=defaultdict(dict)
    events=Counter()
    for (site,year,season,sp),(cap,cam,gear) in data.items():
        c=cam>0;t=cap>0
        label="both" if c and t else "camera_only" if c else "capture_only" if t else "neither"
        discord[label]+=1;per_taxon[sp][label]+=1
        site_campaign[(site,year,season)][sp]=(c,t)
        events["camera"]+=cam;events["ordinary_trap"]+=cap
    transition=Counter();by_species=defaultdict(Counter)
    by_gear=defaultdict(Counter);site_deltas=defaultdict(list)
    keys=("two_year_camera_detected","two_year_capture_detected",
          "camera_two_year_capture_not","capture_two_year_camera_not",
          "camera_both_capture_never","apparent_capture_loss_camera_still_both",
          "apparent_camera_loss_capture_still_both",
          "camera_first_positive_second_zero","capture_first_positive_second_zero")
    for site in sorted(sites):
        for sp in sorted(taxa):
            for (y1,s1),(y2,s2) in TRANSITIONS:
                a=data.get((site,y1,s1,sp));b=data.get((site,y2,s2,sp))
                if a is None or b is None:continue
                ac=a[1]>0;bc=b[1]>0;at=a[0]>0;bt=b[0]>0
                cp=ac and bc;tp=at and bt
                gear="same_capture_gear" if a[2]==b[2] else "switched_capture_gear"
                observed={
                    "two_year_camera_detected":cp,
                    "two_year_capture_detected":tp,
                    "camera_two_year_capture_not":cp and not tp,
                    "capture_two_year_camera_not":tp and not cp,
                    "camera_both_capture_never":cp and not at and not bt,
                    "apparent_capture_loss_camera_still_both":cp and at and not bt,
                    "apparent_camera_loss_capture_still_both":tp and ac and not bc,
                    "camera_first_positive_second_zero":ac and not bc,
                    "capture_first_positive_second_zero":at and not bt,
                }
                transition["original_site_taxon_year_transition"]+=1
                by_gear[gear]["original_site_taxon_year_transition"]+=1
                by_species[sp]["original_site_taxon_year_transition"]+=1
                for k,flag in observed.items():
                    transition[k]+=int(flag)
                    by_gear[gear][k]+=int(flag)
                    by_species[sp][k]+=int(flag)
                site_deltas[site].append(int(cp)-int(tp))
    if len(data)==240 and transition["original_site_taxon_year_transition"]!=144:
        raise AssertionError("Original 12 sites × 4 species × 3 same-season transitions")
    for k in keys: transition.setdefault(k,0)
    richness=[]
    for cells in site_campaign.values():
        richness.append(sum(c for c,t in cells.values())-sum(t for c,t in cells.values()))
    vals=[mean(v) for v in site_deltas.values() if v]
    if not vals:raise ValueError("No longitudinal two-method observations")
    random=Random(2026102915)
    boot=sorted(mean(vals[random.randrange(len(vals))] for _ in vals)
                for _ in range(10000))
    return {
        "schema":"neon.external_norway_two_detector_observation.v1",
        "status":"EXTERNAL_TWO_METHOD_TEMPORAL_OBSERVATION_REANALYZED_EXPLORATORY_NOT_NEON_REPLICATION",
        "published_original_source":{
            "doi":DOI,"v5_MD5":ORIGINAL_MD5,
            "sites":len(sites),"species":len(taxa),
            "site_campaigns":len(groups),"site_campaign_taxon_cells":len(data),
            "camera_versus_cage_and_snap_ordinary_trapping":True,
            "original_years":[2018,2019,2020],
            "four_taxa_by_name":sorted(taxa),
        },
        "paired_camera_capture_record":{
            "source_observation_cells":len(data),
            "detector_discordance":dict(sorted(discord.items())),
            "discordance_by_taxon":{sp:dict(sorted(c.items()))
                                   for sp,c in sorted(per_taxon.items())},
            "camera_minus_capture_detected_taxa_per_site_campaign":{
                "mean":mean(richness),"median":median(richness),
                "min":min(richness),"max":max(richness),
                "camera_more_detected_campaigns":sum(x>0 for x in richness),
                "capture_more_detected_campaigns":sum(x<0 for x in richness),
                "equal_detected_campaigns":sum(x==0 for x in richness),
            },
            "raw_event_sum_not_a_valid_effort_normalized_ratio":True,
        },
        "adjacent_same_season_year_comparison":{
            "calendar_pairs":["2018 fall→2019 fall","2019 fall→2020 fall",
                              "2019 spring→2020 spring"],
            "totals":dict(sorted(transition.items())),
            "by_taxon":{sp:dict(sorted(c.items())) for sp,c in sorted(by_species.items())},
            "by_trap_gear_stable_vs_switched":{
                group:dict(sorted(c.items())) for group,c in sorted(by_gear.items())
            },
            "site_equal_camera_minus_capture_both_year_positive_fraction":{
                "sites":len(vals),"mean":mean(vals),
                "median":median(vals),"min":min(vals),"max":max(vals),
                "positive_sites":sum(x>0 for x in vals),
                "negative_sites":sum(x<0 for x in vals),
                "zero_sites":sum(x==0 for x in vals),
                "site_bootstrap_95pct_descriptive_interval":[boot[250],boot[9749]],
                "resamples":10000,
            },
        },
        "scientific_limitations":{
            "camera_and_ordinary_trap_effort_not_equal":True,
            "camera_presence_not_true_occupancy_or_individual_survival":True,
            "cage_and_snap_included_and_gear_changes_reported":True,
            "source_study_already_published_camera_trap_correlation":True,
            "site_neighborhood_within_20m_not_exact_neon_station":True,
            "not_original_NEON_14_or_30_site_cohort":True,
            "norway_taxa_are_2_rodent_and_2_shrew_species":True,
            "no_original_NEON_observed_genus_station_Z_or_detection_p_refitted":True,
            "no_causal_habitat_memory_or_true_animal_absence_claim":True,
        },
        "retrieved_utc":datetime.now(timezone.utc).isoformat()
    }

def main():
    try:
        req=urllib.request.Request(URL,headers={"User-Agent":"NEON-external-two-detector-QA/1"})
        with urllib.request.urlopen(req,timeout=90) as f:
            raw=f.read(30001)
        if len(raw)>30000:raise ValueError("Published original source exceeds fixed 30KB")
        result=summarize_observation_channels(original_rows(raw))
        result["source_validation"]={
            "source_bytes":len(raw),"provider_original_MD5_verified":True,
            "2025_public_record_version":5,
            "no_original_NEON_response_opened":True,
        }
        code=0
    except Exception as exc:
        result={
            "schema":"neon.external_norway_two_detector_observation.v1",
            "status":"STOP_EXTERNAL_PUBLISHED_DETECTOR_SOURCE_SCHEMA_OR_ACCESS",
            "error_class":type(exc).__name__,
            "no_original_NEON_mammal_ecological_result_recomputed":True,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False))
    return code

if __name__=="__main__":
    raise SystemExit(main())
