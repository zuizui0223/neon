from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def save(fig, stem: Path) -> None:
    stem.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(stem.with_suffix(".png"),dpi=220,bbox_inches="tight")
    fig.savefig(stem.with_suffix(".pdf"),bbox_inches="tight")
    plt.close(fig)


def figure1(outdir: Path) -> None:
    fig,ax=plt.subplots(figsize=(7.2,4.6))
    ax.set_aspect("equal")
    ax.set_xlim(-0.5,10.5)
    ax.set_ylim(-1,5.5)
    ax.axis("off")

    ft=np.array([1.0,3.8])
    lt=np.array([2.6,4.4])
    fu=np.array([7.0,1.0])
    lu=np.array([8.5,2.1])

    for p,label in [(ft,"Fₜ"),(lt,"Lₜ"),(fu,"Fᵤ"),(lu,"Lᵤ")]:
        ax.scatter(*p,s=60)
        ax.text(p[0]+0.15,p[1]+0.12,label,fontsize=12)

    ax.plot([ft[0],lt[0]],[ft[1],lt[1]],linewidth=2)
    ax.plot([fu[0],lu[0]],[fu[1],lu[1]],linewidth=2)
    ax.annotate("δₜ",xy=(1.8,4.3),fontsize=12)
    ax.annotate("δᵤ",xy=(7.8,1.8),fontsize=12)

    ax.plot([ft[0],fu[0]],[ft[1],fu[1]],linestyle="--",linewidth=1.6)
    ax.plot([lt[0],lu[0]],[lt[1],lu[1]],linestyle=":",linewidth=1.8)
    ax.text(3.6,2.05,"FIRST→FIRST",fontsize=10,rotation=-24)
    ax.text(4.55,3.55,"LAST→LAST",fontsize=10,rotation=-18)

    ax.text(
        0.3,-0.25,
        "|d(Fₜ,Fᵤ) − d(Lₜ,Lᵤ)| ≤ δₜ + δᵤ",
        fontsize=13
    )
    ax.text(
        5.6,4.75,
        "|MPD(F) − MPD(L)| ≤ 2 mean(δᵢ)",
        fontsize=11,
        ha="center"
    )
    ax.set_title("Temporal positional aliasing: one occasion, multiple valid spatial states")
    save(fig,outdir/"figure1_observation_process")


def figure2(sim: dict,outdir: Path) -> None:
    cells=sim["cells"]
    fig,axes=plt.subplots(1,2,figsize=(9.2,4.1))

    betas=[-1.0,0.0,1.0]
    labels=["span-depleted","non-informative","span-enriched"]
    for i,beta in enumerate(betas):
        rows=[r for r in cells if float(r["repeat_beta"])==beta]
        xs=np.full(len(rows),i,dtype=float)
        jitter=np.linspace(-0.12,0.12,len(rows))
        if "mean_repeat_conditioned_bias_vs_probability" in rows[0]:
            bias=[
                float(r["mean_repeat_conditioned_bias_vs_probability"])
                for r in rows
            ]
            coverage=[
                float(r["wilson_coverage_latent_probability"])
                for r in rows
            ]
        else:
            bias=[float(r["mean_repeat_conditioned_bias"]) for r in rows]
            coverage=[float(r["wilson_coverage"]) for r in rows]
        axes[0].scatter(xs+jitter,bias,s=18,alpha=0.65)
        axes[1].scatter(xs+jitter,coverage,s=18,alpha=0.65)

    axes[0].axhline(0,linewidth=1)
    axes[0].set_xticks(range(3),labels,rotation=18)
    axes[0].set_ylabel("Mean bias vs generating probability")
    axes[0].set_title("A. Observation-process bias")

    axes[1].axhline(0.95,linewidth=1,linestyle="--")
    axes[1].set_xticks(range(3),labels,rotation=18)
    axes[1].set_ylim(0,1.03)
    axes[1].set_ylabel("Wilson coverage of generating probability")
    axes[1].set_title("B. Interval coverage")

    fig.tight_layout()
    save(fig,outdir/"figure2_simulation_benchmark")


def figure3(result: dict,outdir: Path) -> None:
    species_order=["PEMA","PEER"]
    fig,ax=plt.subplots(figsize=(7.2,4.6))
    y_positions=[1,0]

    for sp,y in zip(species_order,y_positions):
        r=result["species"][sp]
        est=float(r["one_spacing_shift_fraction"])
        lo=float(r["wilson95_low"])
        hi=float(r["wilson95_high"])
        ax.errorbar(
            est,y,
            xerr=[[est-lo],[hi-est]],
            fmt="o",capsize=4,markersize=7
        )
        grids=r["grid_results"]
        eligible=[
            float(v["one_spacing_shift_fraction"])
            for v in grids.values()
            if bool(v["eligible_for_spatial_replication"])
        ]
        if eligible:
            jitter=np.linspace(-0.12,0.12,len(eligible))
            ax.scatter(eligible,np.full(len(eligible),y)+jitter,s=25,alpha=0.55)

    ax.axvline(0.25,linestyle="--",linewidth=1.2)
    ax.set_yticks(y_positions,[
        "P. maniculatus\n(n=485 nights)",
        "P. eremicus\n(n=107 nights)"
    ])
    ax.set_xlim(0,1)
    ax.set_xlabel("Fraction of repeat-capture nights shifting ≥ one trap spacing")
    ax.set_title("Prospectively held-out positional-aliasing validation")
    ax.text(0.255,1.35,"Frozen materiality threshold",fontsize=9)
    fig.tight_layout()
    save(fig,outdir/"figure3_heldout_validation")


def figure4(result: dict,denom: dict,outdir: Path) -> None:
    fig,axes=plt.subplots(1,2,figsize=(9.4,4.2))
    species_order=["PEMA","PEER"]
    x=np.arange(2)
    width=0.34

    repeat=[
        float(denom["species"][sp]["repeat_capture_fraction"])
        for sp in species_order
    ]
    lower=[
        float(
            denom["species"][sp][
                "observed_one_spacing_aliasing_lower_bound_fraction_all_nights"
            ]
        )
        for sp in species_order
    ]
    axes[0].bar(x-width/2,repeat,width,label="Repeat-observed")
    axes[0].bar(x+width/2,lower,width,label="Observed ≥1-spacing shift\n(all-night lower bound)")
    axes[0].set_xticks(x,["P. maniculatus","P. eremicus"],rotation=12)
    axes[0].set_ylim(0,0.5)
    axes[0].set_ylabel("Fraction of all valid individual-nights")
    axes[0].legend(frameon=False,fontsize=8)
    axes[0].set_title("A. Denominator context")

    med=[
        float(result["species"][sp]["median_first_last_distance_m"])/6.25
        for sp in species_order
    ]
    q90=[
        float(result["species"][sp]["q90_first_last_distance_m"])/6.25
        for sp in species_order
    ]
    axes[1].scatter(x,med,s=55,label="Median")
    for i,(m,q) in enumerate(zip(med,q90)):
        axes[1].plot([i,i],[m,q],linewidth=2)
        axes[1].scatter(i,q,marker="^",s=48)
    axes[1].axhline(1,linestyle="--",linewidth=1.2)
    axes[1].set_xticks(x,["P. maniculatus","P. eremicus"],rotation=12)
    axes[1].set_ylabel("First-to-last span (trap spacings)")
    axes[1].set_title("B. Span magnitude")
    axes[1].text(0.02,1.08,"one spacing",fontsize=8)
    fig.tight_layout()
    save(fig,outdir/"figure4_denominator_and_span")


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--simulation",type=Path,required=True)
    parser.add_argument("--validation",type=Path,required=True)
    parser.add_argument("--denominator",type=Path,required=True)
    parser.add_argument("--outdir",type=Path,required=True)
    args=parser.parse_args()

    sim=json.loads(args.simulation.read_text())
    result=json.loads(args.validation.read_text())
    denom=json.loads(args.denominator.read_text())

    figure1(args.outdir)
    figure2(sim,args.outdir)
    figure3(result,args.outdir)
    figure4(result,denom,args.outdir)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
