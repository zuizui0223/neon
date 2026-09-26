from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAITS = ROOT / "data" / "external" / "carrier_niche_evidence_v2_all32.csv"
SITES = ROOT / "data" / "derived" / "site_metrics_v1.csv"
OUT = ROOT / "results" / "carrier_niche_role_recomputed_v2.json"


def load_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    traits = load_csv(TRAITS)
    sites = load_csv(SITES)

    by_species = {r["species_name"]: r for r in traits}
    if len(by_species) != 32:
        raise RuntimeError(f"expected 32 coded carrier species, got {len(by_species)}")

    carrier_species = {
        species
        for site in sites
        for species in site["best_species_names"].split(";")
        if species
    }
    if set(by_species) != carrier_species:
        missing = sorted(carrier_species - set(by_species))
        extra = sorted(set(by_species) - carrier_species)
        raise RuntimeError(f"trait coverage mismatch missing={missing} extra={extra}")

    group_counts = Counter(r["primary_trophic_group"] for r in traits)
    recurrent = sorted(
        (
            r["species_name"],
            int(r["carrier_site_count"]),
            r["primary_trophic_group"],
        )
        for r in traits
        if int(r["carrier_site_count"]) >= 3
    )

    site_groups = {}
    multi_carrier_sites = []
    cross_trophic_multi = []
    all_four = []

    for site in sites:
        carriers = [x for x in site["best_species_names"].split(";") if x]
        groups = sorted({by_species[x]["primary_trophic_group"] for x in carriers})
        site_groups[site["site_code"]] = groups
        if len(carriers) >= 2:
            multi_carrier_sites.append(site["site_code"])
            if len(groups) >= 2:
                cross_trophic_multi.append(site["site_code"])
        if len(groups) == 4:
            all_four.append(site["site_code"])

    payload = {
        "schema": "neon.carrier_niche_role.recomputed.v2",
        "status": "posthoc_literature_backed_all_carrier_trait_audit",
        "carrier_species_count": len(carrier_species),
        "primary_trophic_group_counts": dict(sorted(group_counts.items())),
        "recurrently_observed_carriers": [
            {
                "species": species,
                "carrier_site_count": site_count,
                "primary_trophic_group": group,
            }
            for species, site_count, group in recurrent
        ],
        "recurrent_carrier_primary_trophic_groups": sorted(
            {group for _, _, group in recurrent}
        ),
        "multi_carrier_site_count": len(multi_carrier_sites),
        "multi_carrier_sites_spanning_multiple_trophic_groups": len(cross_trophic_multi),
        "multi_carrier_cross_trophic_fraction": (
            len(cross_trophic_multi) / len(multi_carrier_sites)
        ),
        "within_guild_only_multi_carrier_sites": sorted(
            set(multi_carrier_sites) - set(cross_trophic_multi)
        ),
        "sites_spanning_all_four_primary_trophic_groups": sorted(all_four),
        "site_primary_trophic_groups": dict(sorted(site_groups.items())),
        "interpretation": (
            "Carrier redundancy is usually cross-trophic rather than confined to one "
            "feeding guild. Different ecosystem-effect roles converge on the same local "
            "spatial-continuity response property."
        ),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
