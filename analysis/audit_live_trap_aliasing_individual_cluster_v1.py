from __future__ import annotations

# AI assistance disclosure: This file was drafted or refactored with OpenAI ChatGPT (GPT-5.6 Sol, September 2026); it remains under author responsibility and is verified by repository tests/workflows.

import argparse
import csv
import hashlib
import importlib.util
import json
import random
import statistics
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
URL="https://ndownloader.figshare.com/files/33058799"
SHA256="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
SEED=20260930
BOOTSTRAP_REPLICATES=20000


def _load_positional():
    path=ROOT/"analysis"/"san_jacinto_positional_aliasing_v1.py"
    spec=importlib.util.spec_from_file_location("positional",path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


POSITIONAL=_load_positional()


def quantile(values: list[float], q: float) -> float:
    xs=sorted(float(x) for x in values)
    if not xs:
        raise ValueError("empty values")
    if len(xs)==1:
        return xs[0]
    pos=(len(xs)-1)*q
    lo=int(pos)
    hi=min(lo+1,len(xs)-1)
    w=pos-lo
    return xs[lo]*(1-w)+xs[hi]*w


def download_rows() -> list[dict]:
    req=urllib.request.Request(
        URL,
        headers={"User-Agent":"live-trap-aliasing-cluster-audit/1.0"},
    )
    with urllib.request.urlopen(req,timeout=180) as response:
        raw=response.read()
    actual=hashlib.sha256(raw).hexdigest()
    if actual!=SHA256:
        raise RuntimeError(f"source checksum mismatch: {actual}")
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))


def summarize_species(
    repeat_rows: list[dict],
    species: str,
    *,
    rng: random.Random,
    replicates: int=BOOTSTRAP_REPLICATES,
) -> dict:
    rows=[r for r in repeat_rows if r["species"]==species]
    if not rows:
        raise RuntimeError(f"no repeat rows for {species}")

    # Grid-specific individual identity avoids accidental reuse of tag IDs
    # across grids.
    by_cluster=defaultdict(list)
    by_grid_clusters=defaultdict(list)
    for row in rows:
        key=(str(row["grid"]),str(row["unique_ID"]))
        by_cluster[key].append(int(bool(row["one_spacing_shift"])))

    for key in sorted(by_cluster):
        by_grid_clusters[key[0]].append(key)

    cluster_props={
        key:statistics.mean(values)
        for key,values in by_cluster.items()
    }
    cluster_sizes={key:len(values) for key,values in by_cluster.items()}

    n_nights=len(rows)
    n_clusters=len(by_cluster)
    max_cluster_n=max(cluster_sizes.values())
    raw_fraction=sum(int(bool(r["one_spacing_shift"])) for r in rows)/n_nights
    equal_individual_fraction=statistics.mean(cluster_props.values())

    # Stratified cluster bootstrap: within each grid, resample the observed
    # individual clusters with replacement, retaining all nights from a
    # selected cluster. This preserves the grid structure while allowing
    # repeat-night dependence within individuals.
    boot=[]
    grids=sorted(by_grid_clusters)
    for _ in range(replicates):
        success=0
        total=0
        for grid in grids:
            clusters=by_grid_clusters[grid]
            sampled=[rng.choice(clusters) for _ in range(len(clusters))]
            for key in sampled:
                vals=by_cluster[key]
                success+=sum(vals)
                total+=len(vals)
        boot.append(success/total)

    # Deterministic leave-one-individual-cluster-out raw fractions.
    total_success=sum(int(bool(r["one_spacing_shift"])) for r in rows)
    loo=[]
    for key in sorted(by_cluster):
        vals=by_cluster[key]
        remain_n=n_nights-len(vals)
        if remain_n<=0:
            continue
        remain_success=total_success-sum(vals)
        loo.append(remain_success/remain_n)

    return {
        "species":species,
        "repeat_capture_nights":n_nights,
        "individual_grid_clusters":n_clusters,
        "grid_count":len(grids),
        "raw_night_weighted_shift_fraction":raw_fraction,
        "equal_individual_shift_fraction":equal_individual_fraction,
        "median_individual_shift_fraction":statistics.median(cluster_props.values()),
        "individual_shift_fraction_q25":quantile(list(cluster_props.values()),0.25),
        "individual_shift_fraction_q75":quantile(list(cluster_props.values()),0.75),
        "max_repeat_nights_from_one_individual":max_cluster_n,
        "max_single_individual_night_share":max_cluster_n/n_nights,
        "median_repeat_nights_per_individual":statistics.median(cluster_sizes.values()),
        "cluster_bootstrap_replicates":replicates,
        "cluster_bootstrap_seed":SEED,
        "cluster_bootstrap_ci95_low":quantile(boot,0.025),
        "cluster_bootstrap_ci95_high":quantile(boot,0.975),
        "leave_one_individual_fraction_min":min(loo),
        "leave_one_individual_fraction_max":max(loo),
        "material_fraction_reference":0.25,
        "cluster_bootstrap_low_above_material_fraction":quantile(boot,0.025)>0.25,
        "leave_one_individual_min_above_material_fraction":min(loo)>0.25,
    }


def audit(frozen_result: dict) -> dict:
    rows=download_rows()
    repeat=POSITIONAL.prepare_repeat_nights(rows)

    rng=random.Random(SEED)
    species={}
    for sp in ("PEMA","PEER"):
        expected=int(frozen_result["species"][sp]["repeat_capture_nights"])
        observed=sum(r["species"]==sp for r in repeat)
        if observed!=expected:
            raise RuntimeError(
                f"{sp} support mismatch: {observed} != frozen {expected}"
            )
        species[sp]=summarize_species(repeat,sp,rng=rng)

    return {
        "schema":"neon.live_trap_aliasing.individual_cluster_sensitivity.v1",
        "inferential_role":"post_result_non_rescuing_dependence_audit",
        "species":species,
        "primary_result_unchanged":True,
        "claim":(
            "This audit evaluates whether repeated nights from the same marked "
            "individual dominate the confirmatory fractions. It does not "
            "replace the frozen Wilson/grid replication decision rule."
        ),
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--frozen-result",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()

    out=audit(json.loads(args.frozen_result.read_text()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
