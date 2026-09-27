from __future__ import annotations

import csv
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "data" / "derived" / "site_metrics_v1.csv"
SUMMARY = ROOT / "results" / "carrier_turnover_v1.json"
OUT = ROOT / "manuscript" / "neon_metacommunity_redundancy" / "generated" / "figure_3_two_scale_redundancy.svg"


def load_rows():
    with SITE.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main():
    rows = load_rows()
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    OUT.parent.mkdir(parents=True, exist_ok=True)

    width, height = 1320, 720
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111}.h{font-size:23px;font-weight:700}.s{font-size:16px;font-weight:700}.b{font-size:13px}.sm{font-size:11px}.axis{stroke:#333;stroke-width:1.2}.grid{stroke:#ddd;stroke-width:1}.pt{fill:#333}.bar{fill:#777}.box{fill:#fafafa;stroke:#bbb}</style>',
        '<text x="45" y="38" class="h">Within-site redundancy with among-site turnover in local-cohesion carriers</text>',
    ]

    # Panel A: richness vs redundancy depth
    x0, y0, w, h = 45, 85, 390, 550
    parts.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" class="box"/>')
    parts.append(f'<text x="{x0+15}" y="{y0+28}" class="s">A  Redundancy depth</text>')
    pl, pr, pt, pb = x0+55, x0+w-25, y0+60, y0+h-250
    parts.append(f'<line x1="{pl}" y1="{pb}" x2="{pr}" y2="{pb}" class="axis"/>')
    parts.append(f'<line x1="{pl}" y1="{pt}" x2="{pl}" y2="{pb}" class="axis"/>')
    max_r = max(int(r["observed_target_species_count"]) for r in rows)
    max_d = max(int(r["best_species_count"]) for r in rows)
    for r in rows:
        richness = int(r["observed_target_species_count"])
        depth = int(r["best_species_count"])
        px = pl + (richness-1)/(max_r-1)*(pr-pl)
        py = pb - (depth-1)/(max_d-1)*(pb-pt)
        parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" class="pt"/>')
    parts.append(f'<text x="{(pl+pr)/2:.1f}" y="{y0+h-58}" text-anchor="middle" class="b">target-species richness</text>')
    parts.append(f'<text x="{x0+12}" y="{y0+h-25}" class="sm">redundancy depth = individually sufficient species</text>')
    parts.append(f'<text x="{x0+15}" y="{y0+52}" class="sm">Spearman rho = {summary["exploratory_rank_associations"]["richness_vs_redundancy_depth_rho"]:.3f}</text>')

    # Panel B: carrier frequency distribution
    x0 = 465
    parts.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" class="box"/>')
    parts.append(f'<text x="{x0+15}" y="{y0+28}" class="s">B  Carrier reuse across sites</text>')
    counts = {int(k): v for k,v in summary["carrier_frequency_distribution"].items()}
    bx0, baseline = x0+70, y0+h-145
    barw, gap = 55, 55
    maxc=max(counts.values())
    for idx,k in enumerate(sorted(counts)):
        val=counts[k]
        bh=220*val/maxc
        x=bx0+idx*(barw+gap)
        parts.append(f'<rect x="{x}" y="{baseline-bh:.1f}" width="{barw}" height="{bh:.1f}" class="bar"/>')
        parts.append(f'<text x="{x+barw/2}" y="{baseline+24}" text-anchor="middle" class="b">{k} site{"s" if k>1 else ""}</text>')
        parts.append(f'<text x="{x+barw/2}" y="{baseline-bh-8:.1f}" text-anchor="middle" class="s">{val}</text>')
    parts.append(f'<text x="{x0+15}" y="{y0+h-80}" class="b">32 distinct carrier species in 48 site × carrier records</text>')
    parts.append(f'<text x="{x0+15}" y="{y0+h-55}" class="sm">20 species occur as carriers at one site only; maximum = 3 sites</text>')

    # Panel C: pairwise overlap
    x0 = 885
    parts.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" class="box"/>')
    parts.append(f'<text x="{x0+15}" y="{y0+28}" class="s">C  Carrier turnover among sites</text>')
    shared = summary["site_pairs_sharing_any_carrier"]
    total = summary["site_pair_count"]
    none = total - shared
    bx = x0+75
    scale = 260/total
    none_h = none*scale
    sh_h = shared*scale
    parts.append(f'<rect x="{bx}" y="{baseline-none_h:.1f}" width="90" height="{none_h:.1f}" class="bar"/>')
    parts.append(f'<rect x="{bx+150}" y="{baseline-sh_h:.1f}" width="90" height="{sh_h:.1f}" class="bar"/>')
    parts.append(f'<text x="{bx+45}" y="{baseline+24}" text-anchor="middle" class="b">no shared carrier</text>')
    parts.append(f'<text x="{bx+195}" y="{baseline+24}" text-anchor="middle" class="b">shared carrier</text>')
    parts.append(f'<text x="{bx+45}" y="{baseline-none_h-8:.1f}" text-anchor="middle" class="s">{none}</text>')
    parts.append(f'<text x="{bx+195}" y="{baseline-sh_h-8:.1f}" text-anchor="middle" class="s">{shared}</text>')
    parts.append(f'<text x="{x0+15}" y="{y0+h-80}" class="b">median pairwise carrier-set Jaccard = {summary["pairwise_carrier_jaccard_median"]:.1f}</text>')
    parts.append(f'<text x="{x0+15}" y="{y0+h-55}" class="sm">only {shared}/{total} site pairs share any individually sufficient species</text>')

    parts.append('<text x="45" y="690" class="sm">Exploratory frozen-summary analysis; it does not alter the preregistered confirmatory decision.</text>')
    parts.append('</svg>')
    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
