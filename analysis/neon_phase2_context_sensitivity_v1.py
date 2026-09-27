from __future__ import annotations

import importlib.util
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
