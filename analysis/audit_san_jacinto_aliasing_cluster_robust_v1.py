from __future__ import annotations

import argparse
import importlib.util
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def _load():
    path=ROOT/"analysis"/"san_jacinto_intranight_aliasing_v1.py"
    spec=importlib.util.spec_from_file_location("aliasing",path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ALIAS=_load()


def cluster_fractions(rows: list[dict], fields: tuple[str,...]) -> list[float]:
    groups=defaultdict(list)
    for row in rows:
        key=tuple(str(row[field]) for field in fields)
        groups[key].append(int(bool(row["changed"])))
    return [statistics.mean(values) for values in groups.values()]


def t_interval(values: list[float], level: float=0.95) -> dict:
    from scipy.stats import t as student_t

    xs=[float(x) for x in values]
    n=len(xs)
    if n<2:
        raise ValueError("cluster t interval requires at least two clusters")
    mean=float(statistics.mean(xs))
    sd=float(statistics.stdev(xs))
    se=sd/math.sqrt(n)
    critical=float(student_t.ppf((1+level)/2,n-1))
    return {
        "cluster_count":n,
        "mean_fraction":mean,
        "sd_across_clusters":sd,
        "standard_error":se,
        "df":n-1,
        "ci95_low":mean-critical*se,
        "ci95_high":mean+critical*se,
    }


def audit(repeat_rows: list[dict], primary_result: dict) -> dict:
    out={}
    for species in ("PEMA","PEER"):
        srows=[row for row in repeat_rows if row["species"]==species]
        individual=t_interval(
            cluster_fractions(srows,("grid","unique_ID"))
        )
        grid=t_interval(
            cluster_fractions(srows,("grid",))
        )
        bout=t_interval(
            cluster_fractions(srows,("bout_id",))
        )
        out[species]={
            "night_level_primary_fraction":
                primary_result["species"][species]["changed_fraction"],
            "individual_equal_weight":individual,
            "grid_equal_weight":grid,
            "bout_equal_weight":bout,
            "all_cluster_ci95_lows_above_0_25":all(
                x["ci95_low"]>0.25 for x in (individual,grid,bout)
            ),
        }

    return {
        "schema":"neon.san_jacinto_intranight_aliasing.cluster_robust_audit.v1",
        "date":"2026-09-29",
        "inferential_role":"post_result_robustness_only",
        "primary_decision":primary_result["programme_gate"]["decision"],
        "species":out,
        "both_species_robust_to_individual_grid_and_bout_clustering":all(
            out[sp]["all_cluster_ci95_lows_above_0_25"]
            for sp in out
        ),
        "can_change_primary_decision":False,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--result",type=Path,required=True)
    parser.add_argument("--cache",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()

    rows=ALIAS.download_rows(args.cache)
    repeat,_=ALIAS.prepare_repeat_nights(rows)
    primary=json.loads(args.result.read_text())
    out=audit(repeat,primary)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    raise SystemExit(main())
