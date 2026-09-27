from __future__ import annotations

import csv
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/"results"/"carrier_prevalence_response_v1.json"
OUT=ROOT/"manuscript"/"neon_metacommunity_redundancy"/"generated"/"figure_5_fresh_mechanism.svg"
SITE_CSV=ROOT/"manuscript"/"neon_metacommunity_redundancy"/"generated"/"table_s4_fresh_mechanism_sites.csv"
SPECIES_CSV=ROOT/"manuscript"/"neon_metacommunity_redundancy"/"generated"/"table_s5_fresh_species_mechanism.csv"


def main():
    p=json.loads(RESULT.read_text(encoding="utf-8"))
    sites=p["site_results"]
    OUT.parent.mkdir(parents=True,exist_ok=True)

    site_fields=[
        "site_code","eligible_species_count","observed_carrier_count",
        "expected_carrier_count_count_conditioned",
        "mean_species_carrier_excess",
        "mean_between_grid_allocation_component",
        "mean_within_grid_organization_component",
    ]
    with SITE_CSV.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=site_fields)
        w.writeheader()
        for s in sites:
            w.writerow({k:s[k] for k in site_fields})

    species_fields=[
        "site_code","scientific_name","positive_node_count",
        "positive_node_fraction_of_guild","observed_grid_count",
        "observed_carrier",
        "expected_carrier_probability_count_conditioned",
        "expected_carrier_probability_grid_conditioned",
        "carrier_excess","between_grid_allocation_component",
        "within_grid_organization_component",
    ]
    with SPECIES_CSV.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=species_fields)
        w.writeheader()
        for s in sites:
            for r in s["species_results"]:
                row={"site_code":s["site_code"]}
                row.update({k:r[k] for k in species_fields if k!="site_code"})
                w.writerow(row)

    by_species={}
    for s in sites:
        for r in s["species_results"]:
            by_species.setdefault(r["scientific_name"],[]).append(
                (s["site_code"],int(r["observed_carrier"]))
            )
    repeated=[
        (sp,records)
        for sp,records in by_species.items()
        if len(records)>=2
    ]
    repeated.sort(key=lambda x:(-len(x[1]),x[0]))
    switched=sum(len({v for _,v in recs})>1 for _,recs in repeated)

    width,height=1560,760
    parts=[
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111}.h{font-size:24px;font-weight:700}.s{font-size:16px;font-weight:700}.b{font-size:13px}.sm{font-size:11px}.xs{font-size:10px}.axis{stroke:#333;stroke-width:1.2}.grid{stroke:#ddd;stroke-width:1}.pos{fill:#333}.neg{fill:#aaa}.zero{fill:white;stroke:#111;stroke-width:1.5}.box{fill:#fafafa;stroke:#bbb}</style>',
        '<text x="45" y="38" class="h">Fresh validation: grid-scale allocation determines the local cohesion state</text>'
    ]

    x0,y0,w,h=45,75,700,610
    parts.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" class="box"/>')
    parts.append(f'<text x="{x0+16}" y="{y0+30}" class="s">A  Site-wide carrier excess and additive decomposition</text>')
    pl,pr,pt,pb=x0+70,x0+w-25,y0+70,y0+h-85
    vals=[
        float(s[key])
        for s in sites
        for key in (
            "mean_between_grid_allocation_component",
            "mean_within_grid_organization_component",
        )
    ]
    lim=max(abs(min(vals)),abs(max(vals)),0.1)*1.12

    def y(value: float) -> float:
        return pb-(value+lim)/(2*lim)*(pb-pt)

    yz=y(0)
    for frac in [-1,-0.5,0,0.5,1]:
        value=frac*lim
        yy=y(value)
        parts.append(f'<line x1="{pl}" y1="{yy:.1f}" x2="{pr}" y2="{yy:.1f}" class="grid"/>')
        parts.append(f'<text x="{pl-10}" y="{yy+4:.1f}" text-anchor="end" class="xs">{value:.2f}</text>')
    parts.append(f'<line x1="{pl}" y1="{yz:.1f}" x2="{pr}" y2="{yz:.1f}" class="axis"/>')

    step=(pr-pl)/len(sites)
    bw=max(8,step*0.24)
    for i,s in enumerate(sites):
        xc=pl+step*(i+0.5)
        values=[
            (-bw/2,float(s["mean_between_grid_allocation_component"]),"filled"),
            ( bw/2,float(s["mean_within_grid_organization_component"]),"open"),
        ]
        for off,value,kind in values:
            yy=y(value)
            topy=min(yz,yy)
            bh=max(1,abs(yy-yz))
            klass=("neg" if value<0 else "pos") if kind=="filled" else "zero"
            parts.append(
                f'<rect x="{xc+off-bw/2:.1f}" y="{topy:.1f}" '
                f'width="{bw:.1f}" height="{bh:.1f}" class="{klass}"/>'
            )
        parts.append(f'<text x="{xc:.1f}" y="{pb+23}" text-anchor="middle" class="xs">{escape(s["site_code"])}</text>')

    agg=p["aggregate_primary"]
    grid=p["secondary_grid_decomposition"]
    parts.append(f'<text x="{(pl+pr)/2:.1f}" y="{y0+h-36}" text-anchor="middle" class="sm">between-grid allocation = filled; within-grid organization = open</text>')
    parts.append(
        f'<text x="{x0+16}" y="{y0+h-14}" class="xs">'
        f'primary median excess={agg["median_site_effect"]:.3f}, 4/11 positive, '
        f'p={agg["one_sided_exact_sign_test_p"]:.3f}; '
        f'within-grid median={grid["median_within_grid_organization_component"]:.3f}</text>'
    )

    x0=780
    w=735
    parts.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" class="box"/>')
    parts.append(f'<text x="{x0+16}" y="{y0+30}" class="s">B  Carrier status is a species × site state</text>')
    site_codes=[s["site_code"] for s in sites]
    left=x0+225
    top=y0+75
    cellw=42
    cellh=30
    for j,site in enumerate(site_codes):
        xx=left+j*cellw
        parts.append(
            f'<text x="{xx}" y="{top-12}" text-anchor="middle" class="xs" '
            f'transform="rotate(-55 {xx} {top-12})">{site}</text>'
        )
    for i,(sp,recs) in enumerate(repeated):
        yy=top+i*cellh
        switched_flag=len({v for _,v in recs})>1
        label=sp + (" *" if switched_flag else "")
        parts.append(f'<text x="{left-14}" y="{yy+4}" text-anchor="end" class="xs">{escape(label)}</text>')
        d=dict(recs)
        for j,site in enumerate(site_codes):
            if site not in d:
                continue
            xx=left+j*cellw
            klass="pos" if d[site] else "zero"
            parts.append(f'<circle cx="{xx}" cy="{yy}" r="7" class="{klass}"/>')

    legend_y=y0+h-55
    parts.append(f'<circle cx="{x0+30}" cy="{legend_y}" r="7" class="pos"/>')
    parts.append(f'<text x="{x0+45}" y="{legend_y+4}" class="xs">carrier</text>')
    parts.append(f'<circle cx="{x0+115}" cy="{legend_y}" r="7" class="zero"/>')
    parts.append(f'<text x="{x0+130}" y="{legend_y+4}" class="xs">non-carrier</text>')
    parts.append(f'<text x="{x0+245}" y="{legend_y+4}" class="xs">* switches state among sites; {switched}/{len(repeated)} repeated species switch</text>')
    parts.append(f'<text x="{x0+16}" y="{y0+h-18}" class="xs">Grid-conditioned null reproduced observed carrier state exactly in 66/68 eligible species × site records.</text>')

    parts.append('<text x="45" y="735" class="sm">Panel A is predeclared; the species-switch summary is a post-response diagnostic and does not alter the frozen primary decision.</text>')
    parts.append('</svg>')
    OUT.write_text("\n".join(parts)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
