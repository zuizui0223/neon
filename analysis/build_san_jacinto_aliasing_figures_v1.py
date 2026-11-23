from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


SPECIES_ORDER=["PEMA","PEER"]
LABELS={
    "PEMA":"Peromyscus maniculatus",
    "PEER":"Peromyscus eremicus",
}


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="",encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def save_fraction_figure(result: dict, path: Path) -> None:
    estimates=[]
    lower=[]
    upper=[]
    labels=[]
    ns=[]
    for sp in SPECIES_ORDER:
        row=result["species"][sp]
        estimates.append(row["changed_fraction"])
        lower.append(row["changed_fraction_ci95_low"])
        upper.append(row["changed_fraction_ci95_high"])
        labels.append(LABELS[sp])
        ns.append(row["repeat_capture_nights"])

    y=np.arange(len(labels))
    x=np.asarray(estimates)
    err=np.vstack([
        x-np.asarray(lower),
        np.asarray(upper)-x,
    ])

    fig,ax=plt.subplots(figsize=(7.2,3.6))
    ax.errorbar(x,y,xerr=err,fmt="o",capsize=4)
    ax.axvline(0.25,linestyle="--",linewidth=1.2)
    ax.set_yticks(y,labels)
    ax.set_xlim(0,1)
    ax.set_xlabel("Fraction of repeat-capture individual-nights\nwith different first and last trap flags")
    ax.set_title("Held-out confirmation of intra-night positional aliasing")
    for i,(value,n) in enumerate(zip(estimates,ns)):
        ax.text(min(value+0.03,0.92),i,f"{value*100:.1f}%  (n={n})",va="center")
    ax.invert_yaxis()
    fig.tight_layout()
    path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path,format="svg",bbox_inches="tight")
    plt.close(fig)


def save_ecdf(rows: list[dict], path: Path) -> None:
    fig,ax=plt.subplots(figsize=(7.2,4.3))
    for sp in SPECIES_ORDER:
        values=sorted(
            float(row["distance_m"])
            for row in rows if row["species"]==sp
        )
        x=np.asarray(values)
        y=np.arange(1,len(x)+1)/len(x)
        ax.step(x,y,where="post",label=LABELS[sp])
    for value in (6.25,12.5,18.75):
        ax.axvline(value,linestyle="--",linewidth=1.0)
    ax.set_xlabel("First-to-last trap distance within night (m)")
    ax.set_ylabel("Empirical cumulative fraction")
    ax.set_ylim(0,1.02)
    ax.legend(frameon=False)
    ax.set_title("Spatial scale of intra-night positional aliasing")
    fig.tight_layout()
    path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path,format="svg",bbox_inches="tight")
    plt.close(fig)


def save_grid_figure(rows: list[dict], result: dict, path: Path) -> None:
    by=defaultdict(list)
    for row in rows:
        by[(row["species"],str(row["grid"]))].append(
            str(row["changed"]).strip().lower()=="true"
        )

    fig,ax=plt.subplots(figsize=(7.2,4.3))
    offset={"PEMA":-0.08,"PEER":0.08}
    for sp in SPECIES_ORDER:
        grids=sorted(
            grid for species,grid in by if species==sp
        )
        xs=[int(g) for g in grids]
        ys=[sum(by[(sp,g)])/len(by[(sp,g)]) for g in grids]
        ax.scatter(
            [x+offset[sp] for x in xs],
            ys,
            label=LABELS[sp],
        )
        overall=result["species"][sp]["changed_fraction"]
        ax.axhline(overall,linewidth=0.9,alpha=0.55)
    ax.axhline(0.25,linestyle="--",linewidth=1.2)
    ax.set_xticks(range(1,9))
    ax.set_xlabel("Trap grid")
    ax.set_ylabel("Changed first-to-last flag fraction")
    ax.set_ylim(0,1)
    ax.legend(frameon=False)
    ax.set_title("Aliasing remains high across occupied grids")
    fig.tight_layout()
    path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path,format="svg",bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--result",type=Path,required=True)
    parser.add_argument("--nights",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()

    result=json.loads(args.result.read_text())
    rows=read_csv(args.nights)
    save_fraction_figure(result,args.output_dir/"fig1_aliasing_fraction.svg")
    save_ecdf(rows,args.output_dir/"fig2_distance_ecdf.svg")
    save_grid_figure(rows,result,args.output_dir/"fig3_grid_robustness.svg")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
