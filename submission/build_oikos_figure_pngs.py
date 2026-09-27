from __future__ import annotations

from pathlib import Path
import cairosvg

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "manuscript" / "neon_metacommunity_redundancy" / "generated"
OUT = ROOT / "dist" / "figures"

FIGURES = {
    GEN / "figure_1_conceptual_outcomes.svg": OUT / "Figure_1.png",
    GEN / "figure_2_community_vs_species.svg": OUT / "Figure_2.png",
    GEN / "figure_3_two_scale_redundancy.svg": OUT / "Figure_3.png",
    GEN / "figure_4_ornl_weakest_link.svg": OUT / "Figure_4.png",
    GEN / "figure_5_fresh_mechanism.svg": OUT / "Figure_5.png",
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for src, dst in FIGURES.items():
        if not src.is_file():
            raise FileNotFoundError(src)
        cairosvg.svg2png(
            bytestring=src.read_bytes(),
            write_to=str(dst),
            output_width=1800,
        )
        print(dst)


if __name__ == "__main__":
    main()
