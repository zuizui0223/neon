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
LOCK_PATH=ROOT/"validation"/"public_mammal_space_use_v1"/"phase2_analysis_lock_v1.json"


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


def _load_lock(path: Path=LOCK_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1","true","t","yes"}


def prepare_neon_myodes_primary(
    rows: Iterable[dict],
    *,
    lock: dict | None=None,
) -> pd.DataFrame:
    cfg=(lock or _load_lock())["neon_primary"]
    out=[]
    for raw in rows:
        row=dict(raw)
        if str(row.get("species","")).strip()!=cfg["species"]:
            continue
        site=str(row.get("site","")).strip()
        if site not in cfg["sites"]:
            continue
        if not _truthy(row.get("primary_n5_eligible")):
            continue
        try:
            n=int(row.get("n_unique_individuals"))
            packing=float(row.get("packing_z"))
        except (TypeError,ValueError):
            continue
        if n < int(cfg["n_min"]) or not np.isfinite(packing):
            continue
        raw_nlcd=str(row.get("nlcd_class","")).strip()
        try:
            habitat=CONTEXT.map_neon_nlcd(raw_nlcd)
        except KeyError:
            continue
        if habitat not in cfg["habitats"]:
            continue
        out.append({
            "packing_z":packing,
            "habitat_group":habitat,
            "n_unique_individuals":n,
            "site":site,
            "nlcd_class":raw_nlcd,
        })

    df=pd.DataFrame(out)
    if df.empty:
        raise ValueError("no NEON Myodes primary rows remain")

    expected_sites=set(cfg["sites"])
    expected_habitats=set(cfg["habitats"])
    if set(df["site"]) != expected_sites:
        raise ValueError("NEON Myodes primary data do not contain both frozen sites")
    for site in cfg["sites"]:
        observed=set(df.loc[df["site"]==site,"habitat_group"])
        if observed != expected_habitats:
            raise ValueError(
                f"site {site} does not contain both frozen primary habitats: {observed}"
            )

    df["z_logN"]=UTILS.z_log_n(df["n_unique_individuals"].to_numpy())
    return df.sort_values(["site","habitat_group","n_unique_individuals"]).reset_index(drop=True)


def primary_habitat_term_name() -> str:
    return "C(habitat_group, Treatment(reference='forest'))[T.shrub_scrub]"


def build_neon_myodes_model(df: pd.DataFrame, *, lock: dict | None=None):
    cfg=(lock or _load_lock())["neon_primary"]
    formula=(
        "packing_z ~ C(habitat_group, Treatment(reference='forest')) "
        "+ z_logN + C(site)"
    )
    if cfg["formula"]!="packing_z ~ habitat_group + z_logN + site":
        raise ValueError("NEON primary formula lock drift")
    model=smf.ols(formula,data=df)
    UTILS.assert_full_rank(model.exog,model.exog_names)
    if primary_habitat_term_name() not in model.exog_names:
        raise ValueError("frozen Myodes habitat contrast is not identifiable")
    return model


def fit_neon_myodes_primary(df: pd.DataFrame, *, lock: dict | None=None):
    model=build_neon_myodes_model(df,lock=lock)
    return model.fit(cov_type="HC3")


def _site_descriptive_effects(df: pd.DataFrame) -> list[dict]:
    rows=[]
    for site in sorted(df["site"].unique()):
        subset=df.loc[df["site"]==site].copy()
        if set(subset["habitat_group"])!={"forest","shrub_scrub"}:
            continue
        subset["z_logN_site"]=UTILS.z_log_n(subset["n_unique_individuals"].to_numpy())
        model=smf.ols(
            "packing_z ~ C(habitat_group, Treatment(reference='forest')) + z_logN_site",
            data=subset,
        )
        UTILS.assert_full_rank(model.exog,model.exog_names)
        result=model.fit(cov_type="HC3")
        term=primary_habitat_term_name()
        rows.append({
            "site":site,
            "session_count":len(subset),
            "forest_sessions":int(np.sum(subset["habitat_group"]=="forest")),
            "shrub_scrub_sessions":int(np.sum(subset["habitat_group"]=="shrub_scrub")),
            "habitat_effect":UTILS.coefficient_record(result,term),
        })
    return rows


def _prediction_rows(result, df: pd.DataFrame) -> list[dict]:
    term=primary_habitat_term_name()
    site_term="C(site)[T.DEJU]"
    intercept=float(result.params["Intercept"])
    habitat=float(result.params[term])
    zcoef=float(result.params["z_logN"])
    sitecoef=float(result.params.get(site_term,0.0))

    logs=np.log(df["n_unique_individuals"].to_numpy(dtype=float))
    mean=float(np.mean(logs))
    sd=float(np.std(logs,ddof=0))
    n_values=sorted(set([
        int(df["n_unique_individuals"].min()),
        int(round(float(df["n_unique_individuals"].median()))),
        int(df["n_unique_individuals"].max()),
    ]))
    rows=[]
    for site in ("BONA","DEJU"):
        for habitat_group in ("forest","shrub_scrub"):
            for n in n_values:
                z=(np.log(n)-mean)/sd
                pred=(
                    intercept
                    + habitat*(1.0 if habitat_group=="shrub_scrub" else 0.0)
                    + zcoef*z
                    + sitecoef*(1.0 if site=="DEJU" else 0.0)
                )
                rows.append({
                    "site":site,
                    "habitat_group":habitat_group,
                    "n_unique_individuals":n,
                    "z_logN":float(z),
                    "predicted_packing_z":float(pred),
                })
    return rows


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="",encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--sessions",type=Path,required=True)
    parser.add_argument("--output-json",type=Path,required=True)
    parser.add_argument("--output-predictions",type=Path,required=True)
    args=parser.parse_args()

    lock=_load_lock()
    df=prepare_neon_myodes_primary(_read_csv(args.sessions),lock=lock)
    result=fit_neon_myodes_primary(df,lock=lock)
    habitat_term=primary_habitat_term_name()

    payload={
        "schema":"neon.public_mammal_space_use.neon_myodes_phase2_primary.v1",
        "species":lock["neon_primary"]["species"],
        "session_count":len(df),
        "sites":sorted(df["site"].unique()),
        "site_habitat_session_counts":{
            site:{
                habitat:int(np.sum((df["site"]==site)&(df["habitat_group"]==habitat)))
                for habitat in lock["neon_primary"]["habitats"]
            }
            for site in lock["neon_primary"]["sites"]
        },
        "n_range":[int(df["n_unique_individuals"].min()),int(df["n_unique_individuals"].max())],
        "model":{
            "formula":lock["neon_primary"]["formula"],
            "implemented_formula":(
                "packing_z ~ C(habitat_group, Treatment(reference='forest')) "
                "+ z_logN + C(site)"
            ),
            "covariance":lock["neon_primary"]["covariance"],
            "design_rank":int(np.linalg.matrix_rank(result.model.exog)),
            "design_columns":int(result.model.exog.shape[1]),
            "nobs":int(result.nobs),
            "rsquared":float(result.rsquared),
        },
        "coefficients":{
            "habitat_shrub_scrub_vs_forest":UTILS.coefficient_record(result,habitat_term),
            "z_logN":UTILS.coefficient_record(result,"z_logN"),
            "site_DEJU_vs_BONA":UTILS.coefficient_record(result,"C(site)[T.DEJU]"),
        },
        "site_specific_descriptive_effects":_site_descriptive_effects(df),
        "ecological_model_fits":1,
    }

    args.output_json.parent.mkdir(parents=True,exist_ok=True)
    args.output_json.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    preds=_prediction_rows(result,df)
    args.output_predictions.parent.mkdir(parents=True,exist_ok=True)
    with args.output_predictions.open("w",newline="",encoding="utf-8") as fh:
        writer=csv.DictWriter(fh,fieldnames=list(preds[0]))
        writer.writeheader()
        writer.writerows(preds)

    print(json.dumps(payload,sort_keys=True))


if __name__=="__main__":
    main()
