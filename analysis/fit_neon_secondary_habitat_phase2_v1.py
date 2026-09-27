from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]


def _load_module(name: str, path: Path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


UTILS=_load_module(
    "phase2_utils",
    ROOT/"analysis"/"public_mammal_phase2_utils_v1.py",
)
CONTEXT=_load_module(
    "public_mammal_context",
    ROOT/"analysis"/"public_mammal_context_v1.py",
)


def frozen_contrasts() -> list[dict]:
    return [
        {
            "species":"Chaetodipus hispidus",
            "site":"OAES",
            "habitats":["grassland_herbaceous","shrub_scrub"],
        },
        {
            "species":"Perognathus parvus",
            "site":"ONAQ",
            "habitats":["forest","shrub_scrub"],
        },
        {
            "species":"Peromyscus boylii",
            "site":"SJER",
            "habitats":["forest","grassland_herbaceous"],
        },
    ]


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1","true","t","yes"}


def prepare_contrast(rows: Iterable[dict], contrast: dict) -> pd.DataFrame:
    wanted_habitats=list(contrast["habitats"])
    out=[]
    for raw in rows:
        row=dict(raw)
        if str(row.get("species","")).strip()!=contrast["species"]:
            continue
        if str(row.get("site","")).strip()!=contrast["site"]:
            continue
        if not _truthy(row.get("primary_n5_eligible")):
            continue
        try:
            n=int(row.get("n_unique_individuals"))
            packing=float(row.get("packing_z"))
        except (TypeError,ValueError):
            continue
        if n < 5 or not np.isfinite(packing):
            continue
        try:
            habitat=CONTEXT.map_neon_nlcd(str(row.get("nlcd_class","")).strip())
        except KeyError:
            continue
        if habitat not in wanted_habitats:
            continue
        out.append({
            "species":contrast["species"],
            "site":contrast["site"],
            "habitat_group":habitat,
            "n_unique_individuals":n,
            "packing_z":packing,
        })

    df=pd.DataFrame(out)
    if df.empty:
        raise ValueError(f"no rows for frozen contrast {contrast}")
    if set(df["habitat_group"]) != set(wanted_habitats):
        raise ValueError(
            f"frozen contrast lacks both habitats {wanted_habitats}: "
            f"{sorted(set(df['habitat_group']))}"
        )
    df["z_logN"]=UTILS.z_log_n(df["n_unique_individuals"].to_numpy())
    return df.sort_values(["habitat_group","n_unique_individuals"]).reset_index(drop=True)


def habitat_term_name(habitats: list[str]) -> str:
    reference,comparison=habitats
    return (
        f"C(habitat_group, Treatment(reference='{reference}'))"
        f"[T.{comparison}]"
    )


def fit_contrast(df: pd.DataFrame, contrast: dict):
    reference=contrast["habitats"][0]
    formula=(
        f"packing_z ~ C(habitat_group, Treatment(reference='{reference}')) + z_logN"
    )
    model=smf.ols(formula,data=df)
    UTILS.assert_full_rank(model.exog,model.exog_names)
    term=habitat_term_name(contrast["habitats"])
    if term not in model.exog_names:
        raise ValueError(f"habitat term not identifiable: {term}")
    return model.fit(cov_type="HC3"), formula, term


def fit_frozen_family(rows: Iterable[dict]) -> dict:
    all_rows=[dict(row) for row in rows]
    fitted=[]
    pvalues=[]
    for contrast in frozen_contrasts():
        df=prepare_contrast(all_rows,contrast)
        result,formula,term=fit_contrast(df,contrast)
        coefficient=UTILS.coefficient_record(result,term)
        pvalues.append(coefficient["p_value"])
        fitted.append({
            "species":contrast["species"],
            "site":contrast["site"],
            "habitats":contrast["habitats"],
            "session_count":len(df),
            "habitat_session_counts":{
                h:int(np.sum(df["habitat_group"]==h))
                for h in contrast["habitats"]
            },
            "n_range":[int(df["n_unique_individuals"].min()),int(df["n_unique_individuals"].max())],
            "formula":formula,
            "habitat_effect":coefficient,
            "z_logN":UTILS.coefficient_record(result,"z_logN"),
            "rsquared":float(result.rsquared),
        })

    qvalues=UTILS.bh_adjust(pvalues)
    for row,q in zip(fitted,qvalues,strict=True):
        row["habitat_effect"]["q_value_bh3"]=q

    return {
        "schema":"neon.public_mammal_space_use.neon_secondary_habitat_phase2.v1",
        "family_size":3,
        "multiplicity_method":"Benjamini-Hochberg across exactly three frozen habitat coefficients",
        "contrasts":fitted,
        "ecological_model_fits":3,
    }


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="",encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--sessions",type=Path,required=True)
    parser.add_argument("--output-json",type=Path,required=True)
    args=parser.parse_args()

    payload=fit_frozen_family(_read_csv(args.sessions))
    args.output_json.parent.mkdir(parents=True,exist_ok=True)
    args.output_json.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(payload,sort_keys=True))


if __name__=="__main__":
    main()
