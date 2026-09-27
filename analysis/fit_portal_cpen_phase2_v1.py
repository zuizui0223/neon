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


def _load_utils():
    path=ROOT/"analysis"/"public_mammal_phase2_utils_v1.py"
    spec=importlib.util.spec_from_file_location("phase2_utils",path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


UTILS=_load_utils()


def _load_lock(path: Path=LOCK_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1","true","t","yes"}


def prepare_portal_primary(rows: Iterable[dict], *, lock: dict | None=None) -> pd.DataFrame:
    cfg=(lock or _load_lock())["portal_primary"]
    mapping=cfg["session_treatment_mapping"]
    out=[]
    for raw in rows:
        row=dict(raw)
        if str(row.get("species","")).strip()!=cfg["species"]:
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
        raw_treatment=str(row.get("treatment","")).strip()
        treatment=mapping.get(raw_treatment)
        if treatment not in cfg["treatments"]:
            continue
        plot_id=str(row.get("plot_id","")).strip()
        period=str(row.get("period","")).strip()
        if not plot_id or not period:
            continue
        out.append({
            "packing_z":packing,
            "treatment":treatment,
            "n_unique_individuals":n,
            "plot_id":plot_id,
            "period":period,
        })

    df=pd.DataFrame(out)
    if df.empty:
        raise ValueError("no Portal primary rows remain")
    if set(df["treatment"]) != set(cfg["treatments"]):
        raise ValueError("Portal primary data do not contain both frozen treatment levels")
    df["z_logN"]=UTILS.z_log_n(df["n_unique_individuals"].to_numpy())
    return df.sort_values(["period","plot_id"]).reset_index(drop=True)


def build_portal_primary_model(df: pd.DataFrame, *, lock: dict | None=None):
    cfg=(lock or _load_lock())["portal_primary"]
    formula=cfg["implemented_formula"]
    model=smf.ols(formula,data=df)
    UTILS.assert_full_rank(model.exog,model.exog_names)
    return model


def primary_term_names() -> dict[str,str]:
    return {
        "treatment":"C(treatment, Treatment(reference='control'))[T.kangaroo_rat_exclosure]",
        "interaction":"C(treatment, Treatment(reference='control'))[T.kangaroo_rat_exclosure]:z_logN",
    }


def fit_portal_primary(df: pd.DataFrame, *, lock: dict | None=None):
    cfg=(lock or _load_lock())["portal_primary"]
    model=build_portal_primary_model(df,lock=lock)
    groups=df[cfg["cluster_variable"]].astype(str).to_numpy()
    return model.fit(
        cov_type="cluster",
        cov_kwds={
            "groups":groups,
            "use_correction":bool(cfg["small_sample_correction"]),
            "df_correction":bool(cfg["small_sample_correction"]),
        },
        use_t=bool(cfg["use_t"]),
    )


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="",encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def _prediction_rows(result, df: pd.DataFrame) -> list[dict]:
    terms=primary_term_names()
    intercept=float(result.params["Intercept"])
    zcoef=float(result.params["z_logN"])
    tr=float(result.params[terms["treatment"]])
    inter=float(result.params[terms["interaction"]])
    n_values=sorted(set([
        int(df["n_unique_individuals"].min()),
        int(round(float(df["n_unique_individuals"].median()))),
        int(df["n_unique_individuals"].max()),
    ]))
    logs=np.log(df["n_unique_individuals"].to_numpy(dtype=float))
    mean=float(np.mean(logs))
    sd=float(np.std(logs,ddof=0))
    rows=[]
    for n in n_values:
        z=(np.log(n)-mean)/sd
        for treatment in ("control","kangaroo_rat_exclosure"):
            indicator=1.0 if treatment=="kangaroo_rat_exclosure" else 0.0
            pred=intercept+zcoef*z+indicator*tr+indicator*inter*z
            rows.append({
                "n_unique_individuals":n,
                "z_logN":float(z),
                "treatment":treatment,
                "predicted_packing_z":float(pred),
            })
    return rows


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--sessions",type=Path,required=True)
    parser.add_argument("--output-json",type=Path,required=True)
    parser.add_argument("--output-predictions",type=Path,required=True)
    args=parser.parse_args()

    lock=_load_lock()
    df=prepare_portal_primary(_read_csv(args.sessions),lock=lock)
    result=fit_portal_primary(df,lock=lock)
    terms=primary_term_names()
    payload={
        "schema":"neon.public_mammal_space_use.portal_phase2_primary.v1",
        "species":lock["portal_primary"]["species"],
        "session_count":len(df),
        "plot_count":int(df["plot_id"].nunique()),
        "period_count":int(df["period"].nunique()),
        "treatment_session_counts":{
            str(k):int(v) for k,v in df["treatment"].value_counts().sort_index().items()
        },
        "n_range":[int(df["n_unique_individuals"].min()),int(df["n_unique_individuals"].max())],
        "model":{
            "formula":lock["portal_primary"]["formula"],
            "implemented_formula":lock["portal_primary"]["implemented_formula"],
            "covariance":lock["portal_primary"]["covariance"],
            "cluster_variable":lock["portal_primary"]["cluster_variable"],
            "small_sample_correction":lock["portal_primary"]["small_sample_correction"],
            "use_t":lock["portal_primary"]["use_t"],
            "cluster_count":int(df[lock["portal_primary"]["cluster_variable"]].nunique()),
            "df_resid":float(result.df_resid),
            "rsquared":float(result.rsquared),
        },
        "coefficients":{
            "treatment":UTILS.coefficient_record(result,terms["treatment"]),
            "interaction":UTILS.coefficient_record(result,terms["interaction"]),
            "z_logN":UTILS.coefficient_record(result,"z_logN"),
        },
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
