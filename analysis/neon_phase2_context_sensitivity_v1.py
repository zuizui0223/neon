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


FROZEN_SITE_CONTEXT_SPECIES={
    "Chaetodipus hispidus",
    "Chaetodipus penicillatus",
    "Dipodomys merriami",
    "Dipodomys ordii",
    "Myodes rutilus",
    "Onychomys leucogaster",
    "Peromyscus gossypinus",
    "Peromyscus leucopus",
    "Peromyscus maniculatus",
    "Sigmodon hispidus",
}

PEROMYSCUS_COMPLEX={
    "Peromyscus maniculatus",
    "Peromyscus leucopus",
}


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1","true","t","yes","y"}


def frozen_site_context_species() -> set[str]:
    return set(FROZEN_SITE_CONTEXT_SPECIES)


def _eligibility_flag(n_min: int) -> str:
    mapping={
        3:"sensitivity_n3_eligible",
        5:"primary_n5_eligible",
        8:"sensitivity_n8_eligible",
    }
    if n_min not in mapping:
        raise ValueError("n_min must be one of 3, 5, 8")
    return mapping[n_min]


def prepare_context_dataframe(
    rows: Iterable[dict],
    species: str,
    *,
    n_min: int,
) -> pd.DataFrame:
    if species not in FROZEN_SITE_CONTEXT_SPECIES:
        raise ValueError(f"species not in frozen site-context family: {species}")
    flag=_eligibility_flag(n_min)
    out=[]
    for raw in rows:
        row=dict(raw)
        if str(row.get("species","")).strip()!=species:
            continue
        if not _truthy(row.get(flag)):
            continue
        try:
            n=int(row.get("n_unique_individuals"))
            packing=float(row.get("packing_z"))
        except (TypeError,ValueError):
            continue
        if n<n_min or not np.isfinite(packing):
            continue
        site=str(row.get("site","")).strip()
        if not site:
            continue
        year=str(row.get("year","")).strip()
        out.append({
            "packing_z":packing,
            "n_unique_individuals":n,
            "site":site,
            "year":year,
        })
    df=pd.DataFrame(out)
    if df.empty:
        raise ValueError("no context rows remain")
    if df["site"].nunique()<2:
        raise ValueError("context analysis requires at least two sites")
    df["z_logN"]=UTILS.z_log_n(df["n_unique_individuals"].to_numpy())
    return df.sort_values(["site","year","n_unique_individuals"]).reset_index(drop=True)


def fit_context_summary(
    rows: Iterable[dict],
    species: str,
    *,
    n_min: int,
) -> dict:
    df=prepare_context_dataframe(rows,species,n_min=n_min)
    model=smf.ols("packing_z ~ z_logN + C(site)",data=df)
    UTILS.assert_full_rank(model.exog,model.exog_names)
    result=model.fit(cov_type="HC3")
    means={}
    for site in sorted(df["site"].unique()):
        pred=result.predict(pd.DataFrame({
            "z_logN":[0.0],
            "site":[site],
        }))
        means[site]=float(pred.iloc[0])
    values=list(means.values())
    return {
        "species":species,
        "n_min":int(n_min),
        "session_count":int(len(df)),
        "site_count":int(df["site"].nunique()),
        "adjusted_site_means":means,
        "site_adjusted_range":float(max(values)-min(values)),
        "site_adjusted_sd":float(np.std(values,ddof=0)),
        "z_logN":UTILS.coefficient_record(result,"z_logN"),
        "rsquared":float(result.rsquared),
    }


def prepare_myodes_threshold(
    rows: Iterable[dict],
    *,
    n_min: int,
) -> pd.DataFrame:
    flag=_eligibility_flag(n_min)
    out=[]
    for raw in rows:
        row=dict(raw)
        if str(row.get("species","")).strip()!="Myodes rutilus":
            continue
        site=str(row.get("site","")).strip()
        if site not in {"BONA","DEJU"}:
            continue
        if not _truthy(row.get(flag)):
            continue
        try:
            n=int(row.get("n_unique_individuals"))
            packing=float(row.get("packing_z"))
        except (TypeError,ValueError):
            continue
        if n<n_min or not np.isfinite(packing):
            continue
        try:
            habitat=CONTEXT.map_neon_nlcd(str(row.get("nlcd_class","")).strip())
        except KeyError:
            continue
        if habitat not in {"forest","shrub_scrub"}:
            continue
        out.append({
            "packing_z":packing,
            "n_unique_individuals":n,
            "site":site,
            "year":str(row.get("year","")).strip(),
            "habitat_group":habitat,
        })
    df=pd.DataFrame(out)
    if df.empty:
        raise ValueError("no Myodes threshold rows remain")
    df["z_logN"]=UTILS.z_log_n(df["n_unique_individuals"].to_numpy())
    return df.sort_values(["site","habitat_group","year"]).reset_index(drop=True)




def _myodes_habitat_term() -> str:
    return "C(habitat_group, Treatment(reference='forest'))[T.shrub_scrub]"


def fit_myodes_threshold_summary(
    rows: Iterable[dict],
    *,
    n_min: int,
    label: str,
    exclude_site: str | None=None,
    exclude_year: str | None=None,
) -> dict:
    raw_rows=[dict(row) for row in rows]
    if exclude_site is not None:
        raw_rows=[
            row for row in raw_rows
            if str(row.get("site","")).strip()!=str(exclude_site)
        ]
    if exclude_year is not None:
        raw_rows=[
            row for row in raw_rows
            if str(row.get("year","")).strip()!=str(exclude_year)
        ]

    df=prepare_myodes_threshold(raw_rows,n_min=n_min)
    if set(df["habitat_group"])!={"forest","shrub_scrub"}:
        raise ValueError("Myodes sensitivity requires both frozen habitats")

    formula=(
        "packing_z ~ C(habitat_group, Treatment(reference='forest')) "
        "+ z_logN + C(site)"
    )
    model=smf.ols(formula,data=df)
    UTILS.assert_full_rank(model.exog,model.exog_names)
    term=_myodes_habitat_term()
    if term not in model.exog_names:
        raise ValueError("Myodes habitat effect is not identifiable")
    result=model.fit(cov_type="HC3")
    return {
        "label":str(label),
        "n_min":int(n_min),
        "session_count":int(len(df)),
        "site_count":int(df["site"].nunique()),
        "habitat_session_counts":{
            h:int(np.sum(df["habitat_group"]==h))
            for h in ("forest","shrub_scrub")
        },
        "n_range":[
            int(df["n_unique_individuals"].min()),
            int(df["n_unique_individuals"].max()),
        ],
        "coefficients":{
            "habitat_effect":UTILS.coefficient_record(result,term),
            "z_logN":UTILS.coefficient_record(result,"z_logN"),
        },
        "rsquared":float(result.rsquared),
        "estimable":True,
    }


def fit_myodes_leave_one_out(
    rows: Iterable[dict],
    *,
    unit_field: str,
    n_min: int,
) -> list[dict]:
    if unit_field not in {"site","year"}:
        raise ValueError("unit_field must be site or year")
    df=prepare_myodes_threshold(rows,n_min=n_min)
    units=sorted({str(value) for value in df[unit_field] if str(value)})
    out=[]
    for unit in units:
        kwargs={
            "exclude_site":unit if unit_field=="site" else None,
            "exclude_year":unit if unit_field=="year" else None,
        }
        try:
            summary=fit_myodes_threshold_summary(
                rows,
                n_min=n_min,
                label=f"leave_{unit_field}_out:{unit}",
                **kwargs,
            )
            out.append({
                "left_out":unit,
                "estimable":True,
                "session_count":summary["session_count"],
                "site_count":summary["site_count"],
                "coefficients":summary["coefficients"],
            })
        except Exception as error:
            out.append({
                "left_out":unit,
                "estimable":False,
                "error":f"{type(error).__name__}: {error}",
            })
    return out


def fit_frozen_context_family(
    rows: Iterable[dict],
    *,
    n_min: int,
) -> dict[str,dict]:
    all_rows=[dict(row) for row in rows]
    out={}
    for species in sorted(FROZEN_SITE_CONTEXT_SPECIES):
        out[species]=fit_context_summary(
            all_rows,
            species,
            n_min=n_min,
        )
    return out

def aggregate_peromyscus_complex_rows(rows: Iterable[dict]) -> list[dict]:
    out=[]
    for raw in rows:
        row=dict(raw)
        name=str(row.get("scientificName","")).strip()
        if name in PEROMYSCUS_COMPLEX:
            row["scientificName"]="Peromyscus_maniculatus_leucopus_complex"
            row["taxonID"]="PEROMYSCUS_ML_COMPLEX"
        out.append(row)
    return out

def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="",encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def run_session_context_sensitivity(rows: Iterable[dict]) -> dict:
    all_rows=[dict(row) for row in rows]
    myodes={
        "n_min_3":fit_myodes_threshold_summary(
            all_rows,n_min=3,label="n_min_3",
        ),
        "n_min_8":fit_myodes_threshold_summary(
            all_rows,n_min=8,label="n_min_8",
        ),
        "leave_one_site_out":fit_myodes_leave_one_out(
            all_rows,unit_field="site",n_min=5,
        ),
        "leave_one_year_out":fit_myodes_leave_one_out(
            all_rows,unit_field="year",n_min=5,
        ),
    }
    context=fit_frozen_context_family(all_rows,n_min=5)
    return {
        "schema":"neon.public_mammal_space_use.neon_phase2_context_sensitivity.v1",
        "myodes_robustness":myodes,
        "site_context_family_n5":context,
        "site_context_species":sorted(FROZEN_SITE_CONTEXT_SPECIES),
        "cryptic_complex_sensitivity":{
            "required":True,
            "status":"separate_raw_response_rebuild_required",
            "species":sorted(PEROMYSCUS_COMPLEX),
        },
        "primary_result_overwritten":False,
    }


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--sessions",type=Path,required=True)
    parser.add_argument("--output-json",type=Path,required=True)
    args=parser.parse_args()

    payload=run_session_context_sensitivity(_read_csv(args.sessions))
    args.output_json.parent.mkdir(parents=True,exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "schema":payload["schema"],
        "context_species_count":len(payload["site_context_species"]),
        "myodes_site_loo_count":len(payload["myodes_robustness"]["leave_one_site_out"]),
        "myodes_year_loo_count":len(payload["myodes_robustness"]["leave_one_year_out"]),
        "cryptic_complex_status":payload["cryptic_complex_sensitivity"]["status"],
    },sort_keys=True))


if __name__=="__main__":
    main()

