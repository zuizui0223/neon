from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path
from typing import Iterable

ROOT=Path(__file__).resolve().parents[1]
VALID_STAKES={f"{r}{c}" for r in range(1,8) for c in range(1,8)}


def _load_helper():
    path=ROOT/"analysis"/"mammal_sex_packing_estimability_v1.py"
    spec=importlib.util.spec_from_file_location("mammal_sex_packing_estimability_v1",path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SEXHELP=_load_helper()


def valid_stake(value: object) -> bool:
    return str(value).strip() in VALID_STAKES


def _species_lookup(species_rows: Iterable[dict]) -> dict[str,str]:
    out={}
    for raw in species_rows:
        row=dict(raw)
        if str(row.get("rodent","")).strip()!="1":
            continue
        if str(row.get("censustarget","")).strip()!="1":
            continue
        if str(row.get("unidentified","")).strip()=="1":
            continue
        code=str(row.get("speciescode","")).strip()
        name=str(row.get("scientificname","")).strip()
        if code and SEXHELP.is_heteromyid(name):
            out[code]=name
    return out


def _record_key(row: dict):
    raw=str(row.get("recordID","")).strip()
    try:
        return (0,int(raw))
    except ValueError:
        return (1,raw)


def build_portal_sex_sessions(
    capture_rows: Iterable[dict],
    trapping_rows: Iterable[dict],
    species_rows: Iterable[dict],
) -> list[dict]:
    species_lookup=_species_lookup(species_rows)

    effort={}
    for raw in trapping_rows:
        row=dict(raw)
        try:
            year=int(str(row.get("year","")).strip())
            month=int(str(row.get("month","")).strip())
            period=int(str(row.get("period","")).strip())
        except ValueError:
            continue
        plot=str(row.get("plot","")).strip()
        effort[(year,month,period,plot)]=row

    grouped={}
    for raw in capture_rows:
        row=dict(raw)
        try:
            year=int(str(row.get("year","")).strip())
            month=int(str(row.get("month","")).strip())
            period=int(str(row.get("period","")).strip())
        except ValueError:
            continue
        if period<=0:
            continue
        plot=str(row.get("plot","")).strip()
        code=str(row.get("species","")).strip()
        if code not in species_lookup:
            continue
        if not valid_stake(row.get("stake")):
            continue
        ident=str(row.get("id","")).strip()
        if not ident:
            continue
        e=effort.get((year,month,period,plot))
        if e is None:
            continue
        if str(e.get("sampled","")).strip()!="1":
            continue
        if str(e.get("effort","")).strip()!="49":
            continue
        if str(e.get("qcflag","")).strip()!="1":
            continue
        key=(year,month,period,plot,code)
        grouped.setdefault(key,[]).append(row)

    rows=[]
    for (year,month,period,plot,code),captures in sorted(grouped.items()):
        ordered=sorted(captures,key=_record_key)
        counts=SEXHELP.sex_count_record(
            ordered,
            id_field="id",
            pit_field="pit_tag",
            sex_field="sex",
        )
        rows.append({
            "source":"Portal",
            "site":"Portal",
            "plot_id":plot,
            "period":period,
            "year":year,
            "month":month,
            "species_code":code,
            "species":species_lookup[code],
            **counts,
        })
    return rows


def summarize_portal_sex_sessions(rows: Iterable[dict]) -> dict:
    out=SEXHELP.summarize_sex_estimability(rows,source="Portal")
    out["schema"]="neon.public_mammal_sex_packing.portal_inventory.v1"
    out["portal_commit_sha"]="72d7ff8568052763bf6899dc462e285684cf20f6"
    out["ecological_model_fits"]=0
    return out


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="",encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("",encoding="utf-8")
        return
    fields=list(rows[0].keys())
    with path.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--portal-dir",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()

    captures=_read_csv(args.portal_dir/"Rodents"/"Portal_rodent.csv")
    trapping=_read_csv(args.portal_dir/"Rodents"/"Portal_rodent_trapping.csv")
    species=_read_csv(args.portal_dir/"Rodents"/"Portal_rodent_species.csv")

    rows=build_portal_sex_sessions(captures,trapping,species)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    _write_csv(args.output_dir/"portal_heteromyid_sex_sessions_v1.csv",rows)
    inv=summarize_portal_sex_sessions(rows)
    (args.output_dir/"portal_heteromyid_sex_inventory_v1.json").write_text(
        json.dumps(inv,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(inv,sort_keys=True))


if __name__=="__main__":
    main()
