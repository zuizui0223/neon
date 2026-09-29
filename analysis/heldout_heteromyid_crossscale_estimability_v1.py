from __future__ import annotations

import argparse
import csv
import io
import json
import os
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

PRODUCT_CODE="DP1.10072.001"
RELEASE="RELEASE-2026"
PRODUCT_URL=f"https://data.neonscience.org/api/v0/products/{PRODUCT_CODE}?release={RELEASE}"
TAXONOMY_URL=(
    "https://data.neonscience.org/api/v0/taxonomy?"
    "taxonTypeCode=SMALL_MAMMAL&verbose=true&offset=0&limit=1000"
)
QUERY_URL="https://data.neonscience.org/api/v0/data/query"
USER_AGENT="heldout-heteromyid-crossscale-estimability/1.0"

COMPLETE_GRID="setting complete, processing complete"
REQUIRED_TABLES=("mam_perplotnight","mam_pertrapnight")
HETEROMYID_GENERA={"Chaetodipus","Dipodomys","Perognathus","Microdipodops"}
EXCLUDED_INSPECTED_SPECIES={
    "Chaetodipus baileyi",
    "Chaetodipus penicillatus",
    "Dipodomys merriami",
    "Dipodomys ordii",
}


def _request_json(
    url: str,
    *,
    token: str,
    body: dict | None=None,
    timeout: int=180,
) -> dict:
    headers={
        "User-Agent":USER_AGENT,
        "X-API-Token":token,
        "Accept":"application/json",
    }
    data=None
    method="GET"
    if body is not None:
        headers["Content-Type"]="application/json"
        data=json.dumps(body).encode("utf-8")
        method="POST"
    req=urllib.request.Request(
        url,
        data=data,
        method=method,
        headers=headers,
    )
    with urllib.request.urlopen(req,timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def collect_site_codes(value: object) -> set[str]:
    out=set()
    if isinstance(value,dict):
        site=value.get("siteCode")
        if isinstance(site,str) and site.strip():
            out.add(site.strip())
        for child in value.values():
            out.update(collect_site_codes(child))
    elif isinstance(value,list):
        for child in value:
            out.update(collect_site_codes(child))
    return out


def target_taxa_from_taxonomy(payload: dict) -> tuple[set[str],dict[str,str]]:
    ids=set()
    names={}
    for row in payload.get("data",[]):
        if not isinstance(row,dict):
            continue
        if str(row.get("dwc:taxonRank","")).strip().lower()!="species":
            continue
        if str(row.get("taxonProtocolCategory","")).strip().lower()!="target":
            continue
        taxon=str(row.get("taxonID","")).strip()
        name=str(row.get("dwc:scientificName","")).strip()
        if taxon and name:
            ids.add(taxon)
            names[taxon]=name
    return ids,names


def _table_from_name(name: str) -> str | None:
    for table in REQUIRED_TABLES:
        if f".{table}." in name or table in name:
            return table
    return None


def select_required_files(payload: dict, *, release: str) -> list[dict]:
    releases=(payload.get("data") or {}).get("releases",[])
    matches=[
        row for row in releases
        if isinstance(row,dict) and row.get("release")==release
    ]
    if len(matches)!=1:
        raise RuntimeError(f"expected exactly one {release} block")
    selected={}
    for package in matches[0].get("packages",[]):
        if not isinstance(package,dict):
            continue
        if str(package.get("packageType","")).strip().lower()!="expanded":
            continue
        site=str(package.get("siteCode","")).strip()
        month=str(package.get("month","")).strip()
        for row in package.get("files",[]):
            if not isinstance(row,dict):
                continue
            name=str(row.get("name",""))
            if not name.lower().endswith(".csv"):
                continue
            table=_table_from_name(name)
            if table is None:
                continue
            item={
                "table":table,
                "site_code":site,
                "month":month,
                "name":name,
                "url":str(row.get("url","")),
                "md5":str(row.get("md5","")).lower(),
                "size":int(row.get("size",0) or 0),
            }
            key=(site,month,table,name,item["md5"])
            selected[key]=item
    return [
        selected[key]
        for key in sorted(selected,key=lambda x:(x[2],x[0],x[1],x[3],x[4]))
    ]


def _download_csv(row: dict, *, token: str) -> tuple[list[dict],int]:
    req=urllib.request.Request(
        row["url"],
        headers={
            "User-Agent":USER_AGENT,
            "X-API-Token":token,
        },
    )
    with urllib.request.urlopen(req,timeout=180) as response:
        raw=response.read()
    text=raw.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text))),len(raw)


def is_heteromyid(name: object) -> bool:
    parts=str(name or "").strip().split()
    if len(parts)<2:
        return False
    return (
        parts[0] in HETEROMYID_GENERA
        and parts[1].lower() not in {"sp","sp.","spp","spp."}
    )


def normalize_sex(value: object) -> str | None:
    text=str(value or "").strip().lower()
    if text in {"m","male","1 - male","1-male","1_male"}:
        return "M"
    if text in {"f","female","2 - female","2-female","2_female"}:
        return "F"
    return None


def _valid_trap_coordinate(value: object) -> bool:
    coord=str(value or "").strip().upper()
    if not coord or "X" in coord:
        return False
    return len(coord)>=2 and coord[0].isalpha() and coord[1:].isdigit()


def is_usable_active_trap(status: object) -> bool:
    value=str(status or "").strip()
    return value.startswith("4 -") or value.startswith("5 -") or value.startswith("6 -")


def is_capture_status(status: object) -> bool:
    value=str(status or "").strip()
    return value.startswith("4 -") or value.startswith("5 -")


def is_valid_plotnight(row: dict, *, method: str) -> bool:
    observed=str(
        row.get("mammalGridSamplingMethod",row.get("mammalGridSamplingType",""))
    ).strip().lower()
    completion=str(row.get("gridCompletion","")).strip().lower()
    impractical=str(row.get("samplingImpractical","")).strip()
    return (
        observed==method
        and completion==COMPLETE_GRID
        and impractical in {"","OK"}
    )


def support_counts(
    ordered_rows: list[dict],
    *,
    id_field: str,
    location_field: str,
    sex_field: str="sex",
) -> dict:
    by_id={}
    for row in ordered_rows:
        ident=str(row.get(id_field,"")).strip()
        if not ident:
            continue
        by_id.setdefault(ident,row)

    retained=list(by_id.values())
    sexes=[normalize_sex(row.get(sex_field)) for row in retained]
    locations=[str(row.get(location_field,"")).strip() for row in retained]
    nonempty=[x for x in locations if x]
    counts=Counter(nonempty)
    duplicate_excess=sum(n-1 for n in counts.values() if n>1)
    missing=sum(not x for x in locations)
    support_valid=(missing==0 and duplicate_excess==0)

    n_male=sum(x=="M" for x in sexes)
    n_female=sum(x=="F" for x in sexes)

    return {
        "n_total":len(retained),
        "n_male":n_male,
        "n_female":n_female,
        "trap_support_valid":support_valid,
        "duplicate_location_excess_count":duplicate_excess,
        "missing_location_count":missing,
        "paired_n3_eligible":support_valid and n_male>=3 and n_female>=3,
        "paired_n5_eligible":support_valid and n_male>=5 and n_female>=5,
    }


def build_diversity_estimability_rows(
    plot_rows: Iterable[dict],
    trap_rows: Iterable[dict],
    *,
    target_taxon_ids: set[str],
) -> list[dict]:
    plots=[dict(x) for x in plot_rows]
    traps=[dict(x) for x in trap_rows]

    expected_coords: dict[str,set[str]]=defaultdict(set)
    for row in traps:
        plot=str(row.get("plotID","")).strip()
        coord=str(row.get("trapCoordinate","")).strip()
        if plot and _valid_trap_coordinate(coord):
            expected_coords[plot].add(coord)

    by_event: dict[tuple[str,str,str],list[dict]]=defaultdict(list)
    for row in plots:
        key=(
            str(row.get("siteID","")).strip(),
            str(row.get("plotID","")).strip(),
            str(row.get("eventID","")).strip(),
        )
        if all(key):
            by_event[key].append(row)

    traps_by_night: dict[str,list[dict]]=defaultdict(list)
    for row in traps:
        night=str(row.get("nightuid","")).strip()
        if night:
            traps_by_night[night].append(row)

    out=[]
    for (site,plot,event),event_rows in sorted(by_event.items()):
        if len(event_rows)!=1:
            continue
        p=event_rows[0]
        if not is_valid_plotnight(p,method="diversity"):
            continue
        night=str(p.get("nightuid","")).strip()
        if not night:
            continue
        session=traps_by_night.get(night,[])
        if not session:
            continue

        active_coords={
            str(row.get("trapCoordinate","")).strip()
            for row in session
            if _valid_trap_coordinate(row.get("trapCoordinate"))
            and is_usable_active_trap(row.get("trapStatus"))
        }
        expected_count=len(expected_coords.get(plot,set()))
        required_active=min(90,expected_count) if expected_count else 90
        if len(active_coords)<required_active:
            continue

        grouped: dict[tuple[str,str],list[dict]]=defaultdict(list)
        for raw in session:
            row=dict(raw)
            if not is_capture_status(row.get("trapStatus")):
                continue
            taxon=str(row.get("taxonID","")).strip()
            name=str(row.get("scientificName","")).strip()
            if taxon not in target_taxon_ids:
                continue
            if str(row.get("taxonRank","")).strip().lower()!="species":
                continue
            if str(row.get("identificationQualifier","")).strip():
                continue
            if not is_heteromyid(name) or name in EXCLUDED_INSPECTED_SPECIES:
                continue
            if not str(row.get("tagID","")).strip():
                continue
            coord=str(row.get("trapCoordinate","")).strip()
            row["_support_location"]=(
                coord
                if _valid_trap_coordinate(coord) and coord in active_coords
                else ""
            )
            grouped[(taxon,name)].append(row)

        date=str(p.get("collectDate","")).strip()
        year=int(date[:4]) if len(date)>=4 and date[:4].isdigit() else None
        for (taxon,name),captures in sorted(grouped.items()):
            ordered=sorted(captures,key=lambda x:str(x.get("uid","")))
            support=support_counts(
                ordered,
                id_field="tagID",
                location_field="_support_location",
            )
            out.append({
                "endpoint":"packing_estimability",
                "site":site,
                "plot_id":plot,
                "event_id":event,
                "year":year,
                "species":name,
                "taxon_id":taxon,
                "active_trap_count":len(active_coords),
                **support,
            })
    return out


def build_recapture_estimability_rows(
    plot_rows: Iterable[dict],
    trap_rows: Iterable[dict],
    *,
    target_taxon_ids: set[str],
) -> list[dict]:
    plots=[dict(x) for x in plot_rows]
    traps=[dict(x) for x in trap_rows]

    event_nights=defaultdict(dict)
    for row in plots:
        if not is_valid_plotnight(row,method="pathogen"):
            continue
        site=str(row.get("siteID","")).strip()
        plot=str(row.get("plotID","")).strip()
        event=str(row.get("eventID","")).strip()
        night=str(row.get("nightuid","")).strip()
        date=str(row.get("collectDate","")).strip()
        if not site or not plot or not event or not night:
            continue
        event_nights[(site,plot,event)][night]=date

    traps_by_night=defaultdict(list)
    for row in traps:
        night=str(row.get("nightuid","")).strip()
        if night:
            traps_by_night[night].append(row)

    out=[]
    for (site,plot,event),night_map in sorted(event_nights.items()):
        if len(night_map)<2:
            continue

        event_rows=[]
        for night in sorted(night_map,key=lambda n:(night_map[n],n)):
            event_rows.extend(traps_by_night.get(night,[]))
        if not event_rows:
            continue

        grouped: dict[tuple[str,str],list[dict]]=defaultdict(list)
        for raw in event_rows:
            row=dict(raw)
            if not is_capture_status(row.get("trapStatus")):
                continue
            taxon=str(row.get("taxonID","")).strip()
            name=str(row.get("scientificName","")).strip()
            if taxon not in target_taxon_ids:
                continue
            if str(row.get("taxonRank","")).strip().lower()!="species":
                continue
            if str(row.get("identificationQualifier","")).strip():
                continue
            if not is_heteromyid(name) or name in EXCLUDED_INSPECTED_SPECIES:
                continue
            if not str(row.get("tagID","")).strip():
                continue
            if not _valid_trap_coordinate(row.get("trapCoordinate")):
                continue
            grouped[(taxon,name)].append(row)

        for (taxon,name),captures in sorted(grouped.items()):
            by_tag=defaultdict(list)
            for row in sorted(captures,key=lambda x:str(x.get("uid",""))):
                by_tag[str(row.get("tagID","")).strip()].append(row)

            n_male=0
            n_female=0
            n_conflict_or_unknown=0
            n_single_night=0
            for tag,observations in sorted(by_tag.items()):
                sexes={
                    normalize_sex(row.get("sex"))
                    for row in observations
                    if normalize_sex(row.get("sex")) is not None
                }
                if len(sexes)!=1:
                    n_conflict_or_unknown+=1
                    continue
                sex=next(iter(sexes))
                nights={
                    str(row.get("nightuid","")).strip()
                    for row in observations
                    if str(row.get("nightuid","")).strip()
                    and _valid_trap_coordinate(row.get("trapCoordinate"))
                }
                if len(nights)<2:
                    n_single_night+=1
                    continue
                if sex=="M":
                    n_male+=1
                elif sex=="F":
                    n_female+=1

            out.append({
                "endpoint":"movement_estimability",
                "site":site,
                "plot_id":plot,
                "event_id":event,
                "species":name,
                "taxon_id":taxon,
                "event_night_count":len(night_map),
                "n_recapture_male":n_male,
                "n_recapture_female":n_female,
                "n_conflict_or_unknown_sex":n_conflict_or_unknown,
                "n_single_night_known_sex":n_single_night,
                "paired_n3_eligible":n_male>=3 and n_female>=3,
                "paired_n5_eligible":n_male>=5 and n_female>=5,
            })
    return out


def summarize_crossscale(
    packing_rows: list[dict],
    movement_rows: list[dict],
) -> dict:
    species_names=sorted(
        {str(row["species"]) for row in packing_rows}
        | {str(row["species"]) for row in movement_rows}
    )
    species={}
    qualifying=[]

    for name in species_names:
        prows=[row for row in packing_rows if row["species"]==name]
        mrows=[row for row in movement_rows if row["species"]==name]

        p3=[row for row in prows if row["paired_n3_eligible"]]
        p5=[row for row in prows if row["paired_n5_eligible"]]
        m3=[row for row in mrows if row["paired_n3_eligible"]]
        m5=[row for row in mrows if row["paired_n5_eligible"]]

        packing_site_counts=Counter(row["site"] for row in p5)
        movement_site_counts=Counter(row["site"] for row in m5)
        overlap_sites=sorted(set(packing_site_counts)&set(movement_site_counts))
        overlap_packing_sessions=sum(packing_site_counts[site] for site in overlap_sites)
        overlap_movement_events=sum(movement_site_counts[site] for site in overlap_sites)

        packing_summary={
            "candidate_rows":len(prows),
            "paired_n3_sessions":len(p3),
            "paired_n5_sessions":len(p5),
            "paired_n5_sites":len(packing_site_counts),
            "paired_n5_site_counts":dict(sorted(packing_site_counts.items())),
        }
        movement_summary={
            "candidate_rows":len(mrows),
            "paired_n3_events":len(m3),
            "paired_n5_events":len(m5),
            "paired_n5_sites":len(movement_site_counts),
            "paired_n5_site_counts":dict(sorted(movement_site_counts.items())),
        }

        packing_pass=packing_summary["paired_n5_sessions"]>=10
        movement_pass=movement_summary["paired_n5_events"]>=5
        site_matched_pass=(
            len(overlap_sites)>=2
            and overlap_packing_sessions>=10
            and overlap_movement_events>=5
        )
        both=packing_pass and movement_pass and site_matched_pass
        if both:
            qualifying.append(name)

        species[name]={
            "packing":packing_summary,
            "movement":movement_summary,
            "packing_gate_passed":packing_pass,
            "movement_gate_passed":movement_pass,
            "overlapping_n5_sites":overlap_sites,
            "overlapping_n5_site_count":len(overlap_sites),
            "overlap_packing_n5_sessions":overlap_packing_sessions,
            "overlap_movement_n5_events":overlap_movement_events,
            "site_matched_gate_passed":site_matched_pass,
            "crossscale_gate_passed":both,
        }

    passed=len(qualifying)>=2
    return {
        "schema":"neon.heldout_heteromyid_crossscale.estimability.v1",
        "excluded_previously_inspected_species":sorted(EXCLUDED_INSPECTED_SPECIES),
        "primary_threshold_per_sex":5,
        "diagnostic_threshold_per_sex":3,
        "packing_gate":{
            "minimum_sessions_per_species":10,
            "minimum_sites_per_species":2,
        },
        "movement_gate":{
            "minimum_events_per_species":5,
            "minimum_sites_per_species":2,
        },
        "crossscale_gate":{
            "minimum_species_meeting_both":2,
            "minimum_overlapping_sites_per_species":2,
            "packing_sessions_within_overlap_minimum":10,
            "movement_events_within_overlap_minimum":5,
            "qualifying_species":qualifying,
            "qualifying_species_count":len(qualifying),
            "passed":passed,
            "decision":(
                "authorize_heldout_crossscale_effect_lock"
                if passed else
                "stop_heldout_crossscale_not_estimable"
            ),
        },
        "species":species,
        "heldout_packing_effects_inspected":False,
        "heldout_movement_distances_inspected":False,
        "ecological_effect_models_fit":0,
    }


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("",encoding="utf-8")
        return
    fields=[]
    seen=set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fields.append(key)
    with path.open("w",newline="",encoding="utf-8") as fh:
        writer=csv.DictWriter(fh,fieldnames=fields,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run(*, token: str, output_dir: Path) -> dict:
    product=_request_json(PRODUCT_URL,token=token)
    sites=sorted(collect_site_codes(product))
    if not sites:
        raise RuntimeError("no NEON sites discovered")

    taxonomy=_request_json(TAXONOMY_URL,token=token)
    target_ids,target_names=target_taxa_from_taxonomy(taxonomy)
    if not target_ids:
        raise RuntimeError("no target small-mammal taxa discovered")

    packing_rows=[]
    movement_rows=[]
    site_stops=[]
    query_count=0
    file_count=0
    byte_count=0

    for index,site in enumerate(sites,start=1):
        print(f"HELDOUT_SITE_START {index}/{len(sites)} {site}",flush=True)
        body={
            "productCode":PRODUCT_CODE,
            "siteCodes":[site],
            "startDateMonth":"2013-01",
            "endDateMonth":"2026-09",
            "release":RELEASE,
            "package":"expanded",
            "includeProvisional":False,
        }
        try:
            payload=_request_json(QUERY_URL,token=token,body=body)
            query_count+=1
            files=select_required_files(payload,release=RELEASE)
            tables={name:[] for name in REQUIRED_TABLES}
            for file_row in files:
                records,nbytes=_download_csv(file_row,token=token)
                tables[file_row["table"]].extend(records)
                file_count+=1
                byte_count+=nbytes

            plot_rows=tables["mam_perplotnight"]
            trap_rows=tables["mam_pertrapnight"]
            if not plot_rows or not trap_rows:
                site_stops.append({
                    "site_code":site,
                    "status":"no_required_capture_tables",
                })
                continue

            p=build_diversity_estimability_rows(
                plot_rows,
                trap_rows,
                target_taxon_ids=target_ids,
            )
            m=build_recapture_estimability_rows(
                plot_rows,
                trap_rows,
                target_taxon_ids=target_ids,
            )
            packing_rows.extend(p)
            movement_rows.extend(m)
            print(
                f"HELDOUT_SITE_DONE {site} packing={len(p)} movement={len(m)}",
                flush=True,
            )
        except Exception as error:
            site_stops.append({
                "site_code":site,
                "status":"site_error",
                "detail":f"{type(error).__name__}: {error}",
            })
            print(
                f"HELDOUT_SITE_ERROR {site} {type(error).__name__}: {error}",
                flush=True,
            )

    summary=summarize_crossscale(packing_rows,movement_rows)
    summary.update({
        "product_code":PRODUCT_CODE,
        "release":RELEASE,
        "available_site_count":len(sites),
        "processed_packing_site_count":len({row["site"] for row in packing_rows}),
        "processed_movement_site_count":len({row["site"] for row in movement_rows}),
        "packing_candidate_rows":len(packing_rows),
        "movement_candidate_rows":len(movement_rows),
        "target_taxon_count":len(target_ids),
        "target_taxa":target_names,
        "data_query_requests":query_count,
        "downloaded_required_file_count":file_count,
        "downloaded_required_bytes":byte_count,
        "site_stops":site_stops,
    })

    output_dir.mkdir(parents=True,exist_ok=True)
    _write_csv(
        output_dir/"heldout_heteromyid_packing_estimability_v1.csv",
        packing_rows,
    )
    _write_csv(
        output_dir/"heldout_heteromyid_movement_estimability_v1.csv",
        movement_rows,
    )
    (output_dir/"heldout_heteromyid_crossscale_estimability_v1.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()

    token=os.environ.get("NEON_API_TOKEN","").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN is required")

    result=run(token=token,output_dir=args.output_dir)
    print(json.dumps({
        "crossscale_gate":result["crossscale_gate"],
        "species":result["species"],
        "site_stops":result["site_stops"],
    },indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
