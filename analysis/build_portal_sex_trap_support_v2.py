from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path
from typing import Iterable

from analysis import mammal_sex_trap_support_v2 as SUPPORT

ROOT=Path(__file__).resolve().parents[1]


def _load_v1():
    path=ROOT/"analysis"/"build_portal_sex_packing_inventory_v1.py"
    spec=importlib.util.spec_from_file_location("portal_sex_v1",path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V1=_load_v1()


def build_portal_support_sessions(
    capture_rows: Iterable[dict],
    trapping_rows: Iterable[dict],
    species_rows: Iterable[dict],
) -> list[dict]:
    species_lookup=V1._species_lookup(species_rows)

    effort={}
    for raw in trapping_rows:
        row=dict(raw)
        try:
            key=(
                int(str(row.get("year","")).strip()),
                int(str(row.get("month","")).strip()),
                int(str(row.get("period","")).strip()),
                str(row.get("plot","")).strip(),
            )
        except ValueError:
            continue
        effort[key]=row

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
        if not V1.valid_stake(row.get("stake")):
            continue
        if not str(row.get("id","")).strip():
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
        grouped.setdefault((year,month,period,plot,code),[]).append(row)

    out=[]
    for (year,month,period,plot,code),captures in sorted(grouped.items()):
        ordered=sorted(captures,key=V1._record_key)
        support=SUPPORT.trap_support_record(
            ordered,
            id_field="id",
            location_field="stake",
            sex_field="sex",
            pit_field="pit_tag",
        )
        out.append({
            "source":"Portal",
            "site":"Portal",
            "plot_id":plot,
            "period":period,
            "year":year,
            "month":month,
            "species_code":code,
            "species":species_lookup[code],
            **support,
        })
    return out


def summarize(rows: list[dict]) -> dict:
    out=SUPPORT.summarize_support_sessions(rows,source="Portal")
    out.update({
        "schema":"neon.public_mammal_sex_packing.portal_trap_support.v2",
        "portal_commit_sha":"72d7ff8568052763bf6899dc462e285684cf20f6",
        "support_rule":"first retained record per individual; all retained trap locations must be valid and unique within session",
    })
    return out


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="",encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


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


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--portal-dir",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()

    rows=build_portal_support_sessions(
        _read_csv(args.portal_dir/"Rodents"/"Portal_rodent.csv"),
        _read_csv(args.portal_dir/"Rodents"/"Portal_rodent_trapping.csv"),
        _read_csv(args.portal_dir/"Rodents"/"Portal_rodent_species.csv"),
    )
    args.output_dir.mkdir(parents=True,exist_ok=True)
    _write_csv(args.output_dir/"portal_heteromyid_sex_support_sessions_v2.csv",rows)
    inv=summarize(rows)
    (args.output_dir/"portal_heteromyid_sex_support_inventory_v2.json").write_text(
        json.dumps(inv,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(inv,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
