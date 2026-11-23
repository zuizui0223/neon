from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import urllib.parse
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
USER_AGENT="sex-bias-crossscale-transfer-estimability/1.0"

COMPLETE_GRID="setting complete, processing complete"
REQUIRED_TABLES=("mam_perplotnight","mam_pertrapnight")
EXCLUDED_SPECIES={
    "Chaetodipus baileyi",
    "Chaetodipus penicillatus",
    "Dipodomys merriami",
    "Dipodomys ordii",
    "Peromyscus maniculatus",
    "Peromyscus leucopus",
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
        url,data=data,method=method,headers=headers
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
        if taxon and name and name not in EXCLUDED_SPECIES:
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
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))),len(raw)


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


def _node_id(row: dict) -> str:
    return (
        f"{str(row.get('namedLocation','')).strip()}."
        f"{str(row.get('trapCoordinate','')).strip()}"
    )


def _collect_location_names(value: object) -> set[str]:
    out=set()
    if isinstance(value,dict):
        name=value.get("locationName")
        if isinstance(name,str) and name.strip():
            out.add(name.strip())
        for child in value.values():
            out.update(_collect_location_names(child))
    elif isinstance(value,list):
        for child in value:
            out.update(_collect_location_names(child))
    return out


def registry_nodes_for_site(site: str) -> set[str]:
    hierarchy_url=(
        "https://data.neonscience.org/api/v0/locations/"
        + urllib.parse.quote(str(site))
        + "?hierarchy=true"
    )
    req=urllib.request.Request(
        hierarchy_url,headers={"User-Agent":USER_AGENT}
    )
    with urllib.request.urlopen(req,timeout=180) as response:
        hierarchy=json.loads(response.read().decode("utf-8"))

    names=sorted(
        name for name in _collect_location_names(hierarchy)
        if name.startswith(str(site)+"_")
        and ".mammalGrid.mam." in name
        and _valid_trap_coordinate(name.rsplit(".",1)[-1])
    )
    if not names:
        return set()

    query="""
    query FindLocations($query: LocationQuery!) {
      locations: findLocations(query: $query) {
        locationName locationDecimalLatitude locationDecimalLongitude
      }
    }"""
    valid=set()
    for start in range(0,len(names),500):
        body=json.dumps({
            "query":query,
            "variables":{"query":{"locationNames":names[start:start+500]}},
        }).encode("utf-8")
        req=urllib.request.Request(
            "https://data.neonscience.org/graphql",
            data=body,
            method="POST",
            headers={
                "User-Agent":USER_AGENT,
                "Content-Type":"application/json",
            },
        )
        with urllib.request.urlopen(req,timeout=180) as response:
            result=json.loads(response.read().decode("utf-8"))
        if not isinstance(result,dict) or result.get("errors"):
            raise RuntimeError(f"{site}: location GraphQL failure")
        rows=((result.get("data") or {}).get("locations") or [])
        for row in rows:
            name=str(row.get("locationName","")).strip()
            try:
                lat=float(row.get("locationDecimalLatitude"))
                lon=float(row.get("locationDecimalLongitude"))
            except (TypeError,ValueError):
                continue
            if name in names and math.isfinite(lat) and math.isfinite(lon):
                valid.add(name)
    return valid


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
) -> dict:
    by_id={}
    for row in ordered_rows:
        ident=str(row.get(id_field,"")).strip()
        if ident:
            by_id.setdefault(ident,row)

    retained=list(by_id.values())
    locations=[str(row.get(location_field,"")).strip() for row in retained]
    nonempty=[x for x in locations if x]
    counts=Counter(nonempty)
    duplicate_excess=sum(n-1 for n in counts.values() if n>1)
    missing=sum(not x for x in locations)
    valid=(missing==0 and duplicate_excess==0)

    sexes=[normalize_sex(row.get("sex")) for row in retained]
    n_male=sum(x=="M" for x in sexes)
    n_female=sum(x=="F" for x in sexes)
    return {
        "n_total":len(retained),
        "n_male":n_male,
        "n_female":n_female,
        "support_valid":valid,
        "paired_n3_eligible":valid and n_male>=3 and n_female>=3,
    }


def build_packing_estimability(
    plot_rows: Iterable[dict],
    trap_rows: Iterable[dict],
    *,
    target_taxon_ids: set[str],
    valid_registry_nodes: set[str],
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

        active_nodes={
            _node_id(row)
            for row in session
            if _valid_trap_coordinate(row.get("trapCoordinate"))
            and is_usable_active_trap(row.get("trapStatus"))
            and _node_id(row) in valid_registry_nodes
        }
        active_coords={
            str(row.get("trapCoordinate","")).strip()
            for row in session if _node_id(row) in active_nodes
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
            if taxon not in target_taxon_ids or name in EXCLUDED_SPECIES:
                continue
            if str(row.get("taxonRank","")).strip().lower()!="species":
                continue
            if str(row.get("identificationQualifier","")).strip():
                continue
            if not str(row.get("tagID","")).strip():
                continue
            node=_node_id(row)
            row["_support_location"]=node if node in active_nodes else ""
            grouped[(taxon,name)].append(row)

        for (taxon,name),captures in sorted(grouped.items()):
            ordered=sorted(captures,key=lambda x:str(x.get("uid","")))
            support=support_counts(
                ordered,id_field="tagID",location_field="_support_location"
            )
            if not support["paired_n3_eligible"]:
                continue
            out.append({
                "endpoint":"packing",
                "site":site,
                "plot_id":plot,
                "event_id":event,
                "species":name,
                "taxon_id":taxon,
                "n_male":support["n_male"],
                "n_female":support["n_female"],
            })
    return out


def build_movement_estimability(
    plot_rows: Iterable[dict],
    trap_rows: Iterable[dict],
    *,
    target_taxon_ids: set[str],
    valid_registry_nodes: set[str],
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
        for row in event_rows:
            if not is_capture_status(row.get("trapStatus")):
                continue
            taxon=str(row.get("taxonID","")).strip()
            name=str(row.get("scientificName","")).strip()
            if taxon not in target_taxon_ids or name in EXCLUDED_SPECIES:
                continue
            if str(row.get("taxonRank","")).strip().lower()!="species":
                continue
            if str(row.get("identificationQualifier","")).strip():
                continue
            if not str(row.get("tagID","")).strip():
                continue
            if _node_id(row) not in valid_registry_nodes:
                continue
            grouped[(taxon,name)].append(dict(row))

        for (taxon,name),captures in sorted(grouped.items()):
            by_tag=defaultdict(list)
            for row in sorted(captures,key=lambda x:str(x.get("uid",""))):
                by_tag[str(row.get("tagID","")).strip()].append(row)

            n_male=0
            n_female=0
            for observations in by_tag.values():
                sexes={
                    normalize_sex(row.get("sex"))
                    for row in observations
                    if normalize_sex(row.get("sex")) is not None
                }
                if len(sexes)!=1:
                    continue
                sex=next(iter(sexes))
                nights={
                    str(row.get("nightuid","")).strip()
                    for row in observations
                    if str(row.get("nightuid","")).strip()
                    and _node_id(row) in valid_registry_nodes
                }
                if len(nights)<2:
                    continue
                if sex=="M":
                    n_male+=1
                elif sex=="F":
                    n_female+=1

            if n_male<3 or n_female<3:
                continue
            out.append({
                "endpoint":"movement",
                "site":site,
                "plot_id":plot,
                "event_id":event,
                "species":name,
                "taxon_id":taxon,
                "n_recapture_male":n_male,
                "n_recapture_female":n_female,
            })
    return out


def summarize(
    packing_rows: list[dict],
    movement_rows: list[dict],
) -> dict:
    packing_counts=Counter(
        (row["species"],row["site"]) for row in packing_rows
    )
    movement_counts=Counter(
        (row["species"],row["site"]) for row in movement_rows
    )

    all_keys=sorted(set(packing_counts)|set(movement_counts))
    strata=[]
    for species,site in all_keys:
        p=int(packing_counts[(species,site)])
        m=int(movement_counts[(species,site)])
        passed=p>=5 and m>=5
        strata.append({
            "species":species,
            "site":site,
            "packing_sessions":p,
            "movement_events":m,
            "crossscale_estimable":passed,
        })

    qualifying=[row for row in strata if row["crossscale_estimable"]]
    species=sorted({row["species"] for row in qualifying})
    sites=sorted({row["site"] for row in qualifying})
    species_site_counts=Counter(row["species"] for row in qualifying)
    replicated_species=sorted(
        name for name,count in species_site_counts.items()
        if count>=2
    )

    conditions={
        "minimum_species_site_strata":len(qualifying)>=10,
        "minimum_species":len(species)>=5,
        "minimum_sites":len(sites)>=4,
        "minimum_species_with_two_or_more_sites":len(replicated_species)>=3,
    }
    passed=all(conditions.values())

    return {
        "schema":"neon.sex_bias_crossscale_transfer.estimability.v1",
        "primary_threshold_per_sex":3,
        "excluded_species":sorted(EXCLUDED_SPECIES),
        "stratum_gate":{
            "minimum_packing_sessions":5,
            "minimum_movement_events":5,
        },
        "programme_gate":{
            "conditions":conditions,
            "qualifying_species_site_strata":len(qualifying),
            "qualifying_species":species,
            "qualifying_species_count":len(species),
            "qualifying_sites":sites,
            "qualifying_site_count":len(sites),
            "species_with_two_or_more_sites":replicated_species,
            "species_with_two_or_more_sites_count":len(replicated_species),
            "passed":passed,
            "decision":(
                "authorize_crossscale_transfer_effect_lock"
                if passed else
                "stop_crossscale_transfer_not_estimable"
            ),
        },
        "strata":strata,
        "packing_eligible_sessions":len(packing_rows),
        "movement_eligible_events":len(movement_rows),
        "packing_sex_effects_inspected":False,
        "movement_sex_effects_inspected":False,
        "crossscale_slope_fitted":False,
        "ecological_effect_models_fit":0,
    }


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("",encoding="utf-8")
        return
    fields=list(rows[0].keys())
    with path.open("w",newline="",encoding="utf-8") as fh:
        writer=csv.DictWriter(fh,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run(
    *,
    token: str,
    output_dir: Path,
    site_codes: list[str] | None=None,
) -> dict:
    product=_request_json(PRODUCT_URL,token=token)
    available_sites=sorted(collect_site_codes(product))
    if not available_sites:
        raise RuntimeError("no NEON sites discovered")
    if site_codes is None:
        sites=available_sites
    else:
        unknown=sorted(set(site_codes)-set(available_sites))
        if unknown:
            raise RuntimeError(f"requested sites absent from NEON release metadata: {unknown}")
        sites=sorted(set(site_codes))

    taxonomy=_request_json(TAXONOMY_URL,token=token)
    target_ids,target_names=target_taxa_from_taxonomy(taxonomy)
    if not target_ids:
        raise RuntimeError("no included target taxa discovered")

    packing=[]
    movement=[]
    site_stops=[]
    query_count=0
    file_count=0
    byte_count=0

    for index,site in enumerate(sites,start=1):
        print(f"TRANSFER_SITE_START {index}/{len(sites)} {site}",flush=True)
        query={
            "productCode":PRODUCT_CODE,
            "siteCodes":[site],
            "startDateMonth":"2013-01",
            "endDateMonth":"2026-09",
            "release":RELEASE,
            "package":"expanded",
            "includeProvisional":False,
        }
        try:
            payload=_request_json(QUERY_URL,token=token,body=query)
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

            registry_nodes=registry_nodes_for_site(site)
            if not registry_nodes:
                site_stops.append({
                    "site_code":site,
                    "status":"no_finite_registry_trap_nodes",
                })
                continue

            p=build_packing_estimability(
                plot_rows,trap_rows,
                target_taxon_ids=target_ids,
                valid_registry_nodes=registry_nodes,
            )
            m=build_movement_estimability(
                plot_rows,trap_rows,
                target_taxon_ids=target_ids,
                valid_registry_nodes=registry_nodes,
            )
            packing.extend(p)
            movement.extend(m)
            print(
                f"TRANSFER_SITE_DONE {site} packing={len(p)} movement={len(m)}",
                flush=True,
            )
        except Exception as error:
            site_stops.append({
                "site_code":site,
                "status":"site_error",
                "detail":f"{type(error).__name__}: {error}",
            })
            print(
                f"TRANSFER_SITE_ERROR {site} {type(error).__name__}: {error}",
                flush=True,
            )

    result=summarize(packing,movement)
    result.update({
        "product_code":PRODUCT_CODE,
        "release":RELEASE,
        "available_site_count":len(available_sites),
        "screen_site_count":len(sites),
        "screen_sites":sites,
        "processed_packing_sites":len({row["site"] for row in packing}),
        "processed_movement_sites":len({row["site"] for row in movement}),
        "target_taxon_count":len(target_ids),
        "target_taxa":target_names,
        "data_query_requests":query_count,
        "downloaded_required_file_count":file_count,
        "downloaded_required_bytes":byte_count,
        "site_stops":site_stops,
    })

    output_dir.mkdir(parents=True,exist_ok=True)
    _write_csv(
        output_dir/"sex_bias_transfer_packing_estimability_v1.csv",
        packing,
    )
    _write_csv(
        output_dir/"sex_bias_transfer_movement_estimability_v1.csv",
        movement,
    )
    _write_csv(
        output_dir/"sex_bias_transfer_strata_v1.csv",
        result["strata"],
    )
    (output_dir/"sex_bias_crossscale_transfer_estimability_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--sites",nargs="*",default=None)
    args=parser.parse_args()

    token=os.environ.get("NEON_API_TOKEN","").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN is required")

    result=run(
        token=token,
        output_dir=args.output_dir,
        site_codes=args.sites,
    )
    print(json.dumps({
        "programme_gate":result["programme_gate"],
        "packing_eligible_sessions":result["packing_eligible_sessions"],
        "movement_eligible_events":result["movement_eligible_events"],
        "site_stops":result["site_stops"],
    },indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
