from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def _load_module(name: str, path: Path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PORTAL=_load_module(
    "portal_sessions",
    ROOT/"analysis"/"build_portal_space_use_sessions_v1.py",
)
PRIMARY=_load_module(
    "portal_primary",
    ROOT/"analysis"/"fit_portal_cpen_phase2_v1.py",
)
UTILS=_load_module(
    "phase2_utils",
    ROOT/"analysis"/"public_mammal_phase2_utils_v1.py",
)


LONG_TERM_PORTAL_PLOTS={
    "3","4","10","11","14","15","16","17","19","21","23",
}


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1","true","t","yes","y"}


def long_term_portal_plots() -> set[str]:
    return set(LONG_TERM_PORTAL_PLOTS)


def select_portal_sensitivity_rows(
    rows: Iterable[dict],
    *,
    n_min: int,
    long_term_only: bool=False,
) -> list[dict]:
    flag_by_n={
        3:"sensitivity_n3_eligible",
        5:"primary_n5_eligible",
        8:"sensitivity_n8_eligible",
    }
    if n_min not in flag_by_n:
        raise ValueError("n_min must be one of 3, 5, 8")
    flag=flag_by_n[n_min]
    out=[]
    for raw in rows:
        row=dict(raw)
        if str(row.get("species","")).strip()!="Chaetodipus penicillatus":
            continue
        if not _truthy(row.get(flag)):
            continue
        try:
            n=int(row.get("n_unique_individuals"))
            packing=float(row.get("packing_z"))
        except (TypeError,ValueError):
            continue
        if n < n_min or not np.isfinite(packing):
            continue
        plot=str(row.get("plot_id","")).strip()
        if not plot:
            continue
        if long_term_only and plot not in LONG_TERM_PORTAL_PLOTS:
            continue
        treatment=str(row.get("treatment","")).strip()
        if treatment not in {"control","exclosure","kangaroo_rat_exclosure"}:
            continue
        row["n_unique_individuals"]=n
        row["packing_z"]=packing
        row["plot_id"]=plot
        out.append(row)
    return out


def filter_pit_reliable_captures(rows: Iterable[dict]) -> list[dict]:
    return [dict(row) for row in rows if _truthy(row.get("pit_tag",""))]


def prepare_sensitivity_dataframe(
    rows: Iterable[dict],
    *,
    n_min: int,
    long_term_only: bool=False,
) -> pd.DataFrame:
    selected=select_portal_sensitivity_rows(
        rows,
        n_min=n_min,
        long_term_only=long_term_only,
    )
    normalized=[]
    for row in selected:
        treatment=str(row.get("treatment","")).strip()
        if treatment=="exclosure":
            treatment="kangaroo_rat_exclosure"
        normalized.append({
            "packing_z":float(row["packing_z"]),
            "treatment":treatment,
            "n_unique_individuals":int(row["n_unique_individuals"]),
            "plot_id":str(row["plot_id"]),
            "period":str(row["period"]),
        })
    df=pd.DataFrame(normalized)
    if df.empty:
        raise ValueError("no Portal sensitivity rows remain")
    if set(df["treatment"])!={"control","kangaroo_rat_exclosure"}:
        raise ValueError("Portal sensitivity data do not contain both treatment levels")
    df["z_logN"]=UTILS.z_log_n(df["n_unique_individuals"].to_numpy())
    return df.sort_values(["period","plot_id"]).reset_index(drop=True)


def fit_sensitivity_model(df: pd.DataFrame):
    return PRIMARY.fit_portal_primary(df)




def _coefficient_pair(result) -> dict[str,dict]:
    terms=PRIMARY.primary_term_names()
    return {
        "treatment":UTILS.coefficient_record(result,terms["treatment"]),
        "interaction":UTILS.coefficient_record(result,terms["interaction"]),
        "z_logN":UTILS.coefficient_record(result,"z_logN"),
    }


def fit_model_summary(
    rows: Iterable[dict],
    *,
    n_min: int,
    label: str,
    long_term_only: bool=False,
) -> dict:
    df=prepare_sensitivity_dataframe(
        rows,
        n_min=n_min,
        long_term_only=long_term_only,
    )
    result=fit_sensitivity_model(df)
    return {
        "label":str(label),
        "n_min":int(n_min),
        "long_term_only":bool(long_term_only),
        "session_count":int(len(df)),
        "cluster_count":int(df["plot_id"].nunique()),
        "period_count":int(df["period"].nunique()),
        "treatment_session_counts":{
            str(k):int(v)
            for k,v in df["treatment"].value_counts().sort_index().items()
        },
        "coefficients":_coefficient_pair(result),
        "rsquared":float(result.rsquared),
        "df_resid":float(result.df_resid),
        "estimable":True,
    }


def fit_leave_one_out(
    rows: Iterable[dict],
    *,
    unit_field: str,
    n_min: int,
) -> list[dict]:
    if unit_field not in {"plot_id","period"}:
        raise ValueError("unit_field must be plot_id or period")
    selected=select_portal_sensitivity_rows(rows,n_min=n_min)
    units=sorted({str(row.get(unit_field,"")).strip() for row in selected if str(row.get(unit_field,"")).strip()})
    output=[]
    for unit in units:
        subset=[
            row for row in selected
            if str(row.get(unit_field,"")).strip()!=unit
        ]
        try:
            summary=fit_model_summary(
                subset,
                n_min=n_min,
                label=f"leave_{unit_field}_out:{unit}",
            )
            output.append({
                "left_out":unit,
                "estimable":True,
                "coefficients":summary["coefficients"],
                "session_count":summary["session_count"],
                "cluster_count":summary["cluster_count"],
                "period_count":summary["period_count"],
            })
        except Exception as error:
            output.append({
                "left_out":unit,
                "estimable":False,
                "error":f"{type(error).__name__}: {error}",
            })
    return output

def _record_key(row: dict):
    raw=str(row.get("recordID","")).strip()
    try:
        return (0,int(raw))
    except ValueError:
        return (1,raw)


def _metric_seed(metric_name: str, n: int) -> int:
    text=f"portal-sensitivity|{metric_name}|fixed-7x7-6.25m|{n}"
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],16)


def build_metric_sensitivity_sessions(
    capture_rows: Iterable[dict],
    trapping_rows: Iterable[dict],
    plot_rows: Iterable[dict],
    species_rows: Iterable[dict],
    *,
    metric_name: str,
    pit_only: bool,
    replicates: int=999,
) -> list[dict]:
    captures=[dict(row) for row in capture_rows]
    if pit_only:
        captures=filter_pit_reliable_captures(captures)

    if metric_name=="mpd":
        sessions=PORTAL.build_portal_sessions(
            captures,
            trapping_rows,
            plot_rows,
            species_rows,
            replicates=replicates,
        )
        label="mpd_pit_only" if pit_only else "mpd"
        return [
            {**row,"metric_name":label}
            for row in sessions
            if row.get("species")=="Chaetodipus penicillatus"
        ]

    metric_by_name={
        "radius_of_gyration":radius_of_gyration,
        "nearest_neighbour":mean_nearest_neighbour_distance,
    }
    if metric_name not in metric_by_name:
        raise ValueError(f"unsupported metric_name: {metric_name}")
    metric=metric_by_name[metric_name]

    targets=PORTAL._target_species_lookup(species_rows)
    captures=PORTAL.filter_primary_capture_rows(captures,species_rows)

    effort={}
    for row in trapping_rows:
        try:
            key=(
                int(str(row.get("year","")).strip()),
                int(str(row.get("month","")).strip()),
                int(str(row.get("period","")).strip()),
                str(row.get("plot","")).strip(),
            )
        except ValueError:
            continue
        effort[key]=dict(row)

    treatment={}
    for row in plot_rows:
        try:
            key=(
                int(str(row.get("year","")).strip()),
                int(str(row.get("month","")).strip()),
                str(row.get("plot","")).strip(),
            )
        except ValueError:
            continue
        treatment[key]=str(row.get("treatment","")).strip().lower()

    grouped=defaultdict(list)
    for row in captures:
        species=str(row.get("species","")).strip()
        if targets.get(species)!="Chaetodipus penicillatus":
            continue
        try:
            year=int(str(row["year"]).strip())
            month=int(str(row["month"]).strip())
            period=int(str(row["period"]).strip())
        except (KeyError,ValueError):
            continue
        if not PORTAL._in_primary_window(year,month):
            continue
        plot=str(row.get("plot","")).strip()
        e=effort.get((year,month,period,plot))
        if e is None:
            continue
        if str(e.get("sampled","")).strip()!="1":
            continue
        if str(e.get("effort","")).strip()!="49":
            continue
        if str(e.get("qcflag","")).strip()!="1":
            continue
        trt=treatment.get((year,month,plot))
        if trt not in {"control","exclosure"}:
            continue
        grouped[(year,month,period,plot,species,trt)].append(row)

    results=[]
    for (year,month,period,plot,species,trt),rows in sorted(grouped.items()):
        by_id={}
        for row in sorted(rows,key=_record_key):
            ident=str(row.get("id","")).strip()
            by_id.setdefault(ident,row)
        retained=list(by_id.values())
        observed=np.asarray(
            [PORTAL.stake_xy(str(row["stake"]).strip()) for row in retained],
            dtype=float,
        )
        n=len(retained)
        score=standardized_geometry_metric(
            observed,
            PORTAL.ACTIVE_TRAPS_XY,
            metric=metric,
            replicates=replicates,
            seed=_metric_seed(metric_name,n),
        )
        estimable=bool(score["estimable"])
        results.append({
            "source":"Portal",
            "site":"Portal",
            "plot_id":plot,
            "period":period,
            "year":year,
            "month":month,
            "species_code":species,
            "species":targets[species],
            "treatment":trt,
            "n_unique_individuals":n,
            "packing_z":score["z"],
            "packing_estimable":estimable,
            "packing_non_estimable_reason":score["non_estimable_reason"],
            "metric_name":metric_name,
            "sensitivity_n3_eligible":estimable and n>=3,
            "primary_n5_eligible":estimable and n>=5,
            "sensitivity_n8_eligible":estimable and n>=8,
        })
    return results


def _validated_xy(values: np.ndarray, label: str) -> np.ndarray:
    xy=np.asarray(values,dtype=float)
    if xy.ndim!=2 or xy.shape[1]!=2:
        raise ValueError(f"{label} must have shape (n, 2)")
    if not np.isfinite(xy).all():
        raise ValueError(f"{label} must be finite")
    return xy


def radius_of_gyration(points_xy: np.ndarray) -> float:
    xy=_validated_xy(points_xy,"points_xy")
    if len(xy)<2:
        raise ValueError("at least two points are required")
    centroid=np.mean(xy,axis=0)
    sq=np.sum((xy-centroid)**2,axis=1)
    return float(np.sqrt(np.mean(sq)))


def mean_nearest_neighbour_distance(points_xy: np.ndarray) -> float:
    xy=_validated_xy(points_xy,"points_xy")
    if len(xy)<2:
        raise ValueError("at least two points are required")
    diff=xy[:,None,:]-xy[None,:,:]
    dist=np.sqrt(np.sum(diff*diff,axis=2))
    np.fill_diagonal(dist,np.inf)
    return float(np.mean(np.min(dist,axis=1)))


def standardized_geometry_metric(
    observed_xy: np.ndarray,
    active_traps_xy: np.ndarray,
    *,
    metric: Callable[[np.ndarray],float],
    replicates: int,
    seed: int,
) -> dict:
    observed=_validated_xy(observed_xy,"observed_xy")
    traps=_validated_xy(active_traps_xy,"active_traps_xy")
    n=len(observed)
    if n<2:
        return {
            "estimable":False,
            "non_estimable_reason":"fewer_than_two_individuals",
            "observed":None,
            "null_mean":None,
            "null_sd":None,
            "z":None,
            "null_mode":None,
            "null_draw_count":0,
        }
    if n>len(traps):
        raise ValueError("observed individual count cannot exceed active trap count")
    if replicates<1:
        raise ValueError("replicates must be positive")

    observed_value=float(metric(observed))
    combinations=math.comb(len(traps),n)
    values=[]
    if combinations<=replicates:
        mode="exact"
        for indices in itertools.combinations(range(len(traps)),n):
            values.append(float(metric(traps[list(indices)])))
    else:
        mode="monte_carlo"
        rng=np.random.default_rng(int(seed))
        for _ in range(int(replicates)):
            indices=rng.choice(len(traps),size=n,replace=False)
            values.append(float(metric(traps[indices])))

    arr=np.asarray(values,dtype=float)
    mean=float(np.mean(arr))
    sd=float(np.std(arr,ddof=0))
    if sd<=0:
        return {
            "estimable":False,
            "non_estimable_reason":"zero_null_variance",
            "observed":observed_value,
            "null_mean":mean,
            "null_sd":sd,
            "z":None,
            "null_mode":mode,
            "null_draw_count":len(values),
        }
    return {
        "estimable":True,
        "non_estimable_reason":None,
        "observed":observed_value,
        "null_mean":mean,
        "null_sd":sd,
        "z":(observed_value-mean)/sd,
        "null_mode":mode,
        "null_draw_count":len(values),
    }


def _opposite_sign(a: float, b: float) -> bool:
    return (a>0 and b<0) or (a<0 and b>0)


def direction_reversal_summary(
    primary: dict[str,float],
    checks: Iterable[dict],
) -> dict:
    rows=[dict(row) for row in checks]
    return {
        "treatment_reversal_labels":[
            str(row["label"])
            for row in rows
            if _opposite_sign(float(primary["treatment"]),float(row["treatment"]))
        ],
        "interaction_reversal_labels":[
            str(row["label"])
            for row in rows
            if _opposite_sign(float(primary["interaction"]),float(row["interaction"]))
        ],
    }

def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="",encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def _estimate_direction_row(label: str, summary: dict) -> dict:
    return {
        "label":str(label),
        "treatment":float(summary["coefficients"]["treatment"]["estimate"]),
        "interaction":float(summary["coefficients"]["interaction"]["estimate"]),
    }


def _loo_direction_rows(prefix: str, rows: Iterable[dict]) -> list[dict]:
    out=[]
    for row in rows:
        if not row.get("estimable"):
            continue
        out.append({
            "label":f"{prefix}:{row['left_out']}",
            "treatment":float(row["coefficients"]["treatment"]["estimate"]),
            "interaction":float(row["coefficients"]["interaction"]["estimate"]),
        })
    return out


def run_portal_robustness(
    session_rows: Iterable[dict],
    primary_payload: dict,
    capture_rows: Iterable[dict],
    trapping_rows: Iterable[dict],
    plot_rows: Iterable[dict],
    species_rows: Iterable[dict],
    *,
    replicates: int=999,
) -> dict:
    sessions=[dict(row) for row in session_rows]
    primary={
        "treatment":float(primary_payload["coefficients"]["treatment"]["estimate"]),
        "interaction":float(primary_payload["coefficients"]["interaction"]["estimate"]),
    }

    core=[
        fit_model_summary(sessions,n_min=3,label="n_min_3"),
        fit_model_summary(sessions,n_min=8,label="n_min_8"),
        fit_model_summary(sessions,n_min=5,label="long_term_plots",long_term_only=True),
    ]

    pit_sessions=build_metric_sensitivity_sessions(
        capture_rows,trapping_rows,plot_rows,species_rows,
        metric_name="mpd",
        pit_only=True,
        replicates=replicates,
    )
    radius_sessions=build_metric_sensitivity_sessions(
        capture_rows,trapping_rows,plot_rows,species_rows,
        metric_name="radius_of_gyration",
        pit_only=False,
        replicates=replicates,
    )
    nnd_sessions=build_metric_sensitivity_sessions(
        capture_rows,trapping_rows,plot_rows,species_rows,
        metric_name="nearest_neighbour",
        pit_only=False,
        replicates=replicates,
    )

    core.extend([
        fit_model_summary(pit_sessions,n_min=5,label="pit_only"),
        fit_model_summary(radius_sessions,n_min=5,label="radius_of_gyration"),
        fit_model_summary(nnd_sessions,n_min=5,label="nearest_neighbour"),
    ])

    leave_plot=fit_leave_one_out(sessions,unit_field="plot_id",n_min=5)
    leave_period=fit_leave_one_out(sessions,unit_field="period",n_min=5)

    direction_rows=[
        _estimate_direction_row(row["label"],row)
        for row in core
    ]
    direction_rows.extend(_loo_direction_rows("leave_plot_out",leave_plot))
    direction_rows.extend(_loo_direction_rows("leave_period_out",leave_period))

    reversal=direction_reversal_summary(primary,direction_rows)

    return {
        "schema":"neon.public_mammal_space_use.portal_phase2_sensitivity.v1",
        "species":"Chaetodipus penicillatus",
        "primary_reference":{
            "treatment":primary_payload["coefficients"]["treatment"],
            "interaction":primary_payload["coefficients"]["interaction"],
            "session_count":primary_payload.get("session_count"),
            "plot_count":primary_payload.get("plot_count"),
            "period_count":primary_payload.get("period_count"),
        },
        "core_sensitivities":core,
        "leave_one_plot_out":leave_plot,
        "leave_one_period_out":leave_period,
        "direction_reversal_summary":reversal,
        "sensitivity_rebuild":{
            "pit_only_session_count":len(pit_sessions),
            "radius_session_count":len(radius_sessions),
            "nearest_neighbour_session_count":len(nnd_sessions),
            "replicates":int(replicates),
        },
        "primary_result_overwritten":False,
    }


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--sessions",type=Path,required=True)
    parser.add_argument("--primary-json",type=Path,required=True)
    parser.add_argument("--portal-dir",type=Path,required=True)
    parser.add_argument("--output-json",type=Path,required=True)
    parser.add_argument("--replicates",type=int,default=999)
    args=parser.parse_args()

    payload=run_portal_robustness(
        _read_csv(args.sessions),
        json.loads(args.primary_json.read_text(encoding="utf-8")),
        _read_csv(args.portal_dir/"Rodents"/"Portal_rodent.csv"),
        _read_csv(args.portal_dir/"Rodents"/"Portal_rodent_trapping.csv"),
        _read_csv(args.portal_dir/"SiteandMethods"/"Portal_plots.csv"),
        _read_csv(args.portal_dir/"Rodents"/"Portal_rodent_species.csv"),
        replicates=args.replicates,
    )
    args.output_json.parent.mkdir(parents=True,exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "schema":payload["schema"],
        "core_labels":[row["label"] for row in payload["core_sensitivities"]],
        "plot_loo_count":len(payload["leave_one_plot_out"]),
        "period_loo_count":len(payload["leave_one_period_out"]),
        "treatment_reversals":payload["direction_reversal_summary"]["treatment_reversal_labels"],
        "interaction_reversals":payload["direction_reversal_summary"]["interaction_reversal_labels"],
    },sort_keys=True))


if __name__=="__main__":
    main()

