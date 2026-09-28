from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path
from typing import Iterable

import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def _load(name: str, rel: str):
    path=ROOT/rel
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V1=_load("portal_sex_v1","analysis/build_portal_sex_packing_inventory_v1.py")
GEOM=_load("portal_space_v1","analysis/build_portal_space_use_sessions_v1.py")
SUPPORT=_load("sex_support_v2","analysis/mammal_sex_trap_support_v2.py")
EFFECT=_load("sex_effect_phase3","analysis/mammal_sex_effects_phase3_v1.py")
SEXHELP=_load("sex_estimability_v1","analysis/mammal_sex_packing_estimability_v1.py")


def build_portal_sex_effect_sessions(
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

        by_id={}
        for row in ordered:
            ident=str(row.get("id","")).strip()
            by_id.setdefault(ident,row)
        retained=list(by_id.values())

        support=SUPPORT.trap_support_record(
            ordered,
            id_field="id",
            location_field="stake",
            sex_field="sex",
            pit_field="pit_tag",
        )
        if not support["trap_support_valid"]:
            continue

        males=[
            row for row in retained
            if SEXHELP.normalize_sex(row.get("sex"))=="M"
        ]
        females=[
            row for row in retained
            if SEXHELP.normalize_sex(row.get("sex"))=="F"
        ]
        if len(males)<2 or len(females)<2:
            continue

        male_xy=np.asarray(
            [GEOM.stake_xy(str(row.get("stake",""))) for row in males],
            dtype=float,
        )
        female_xy=np.asarray(
            [GEOM.stake_xy(str(row.get("stake",""))) for row in females],
            dtype=float,
        )
        effect=EFFECT.sex_packing_effect(
            GEOM.ACTIVE_TRAPS_XY,
            male_xy,
            female_xy,
        )
        if not effect["estimable"]:
            continue

        flags=EFFECT.threshold_flags(len(males),len(females))
        out.append({
            "source":"Portal",
            "site":"Portal",
            "plot_id":plot,
            "period":period,
            "year":year,
            "month":month,
            "species_code":code,
            "species":species_lookup[code],
            "n_total":support["n_total"],
            "n_known_sex":support["n_known_sex"],
            "n_unknown_sex":support["n_unknown_sex"],
            "known_sex_fraction":support["known_sex_fraction"],
            "pit_reliable_fraction":support["pit_reliable_fraction"],
            **flags,
            **effect,
        })
    return out


def summarize(rows: list[dict]) -> dict:
    return {
        "schema":"neon.public_mammal_sex_packing.portal_effect_sessions.v1",
        "portal_commit_sha":"72d7ff8568052763bf6899dc462e285684cf20f6",
        "session_count":len(rows),
        "paired_n2_sessions":sum(bool(r["paired_n2_eligible"]) for r in rows),
        "paired_n3_sessions":sum(bool(r["paired_n3_eligible"]) for r in rows),
        "paired_n5_sessions":sum(bool(r["paired_n5_eligible"]) for r in rows),
        "species_count":len({r["species"] for r in rows}),
        "ecological_effects_extracted":True,
        "ecological_model_fits":0,
    }


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
        w=csv.DictWriter(fh,fieldnames=fields,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--portal-dir",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()

    rows=build_portal_sex_effect_sessions(
        _read_csv(args.portal_dir/"Rodents"/"Portal_rodent.csv"),
        _read_csv(args.portal_dir/"Rodents"/"Portal_rodent_trapping.csv"),
        _read_csv(args.portal_dir/"Rodents"/"Portal_rodent_species.csv"),
    )
    args.output_dir.mkdir(parents=True,exist_ok=True)
    _write_csv(
        args.output_dir/"portal_heteromyid_sex_effect_sessions_v1.csv",
        rows,
    )
    inv=summarize(rows)
    (args.output_dir/"portal_heteromyid_sex_effect_inventory_v1.json").write_text(
        json.dumps(inv,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(inv,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
