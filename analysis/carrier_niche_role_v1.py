from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAITS = ROOT / "data" / "external" / "carrier_niche_evidence_v1.csv"
SITES = ROOT / "data" / "derived" / "site_metrics_v1.csv"
OUT = ROOT / "results" / "carrier_niche_role_v1.json"


def main() -> None:
    with TRAITS.open(newline="", encoding="utf-8") as fh:
        trait_rows = list(csv.DictReader(fh))
    with SITES.open(newline="", encoding="utf-8") as fh:
        site_rows = list(csv.DictReader(fh))

    trait_by_species = {r["species_name"]: r for r in trait_rows}
    group_counts = defaultdict(int)
    recurring = []
    for r in trait_rows:
        group_counts[r["primary_trophic_group"]] += 1
        if int(r["carrier_site_count"]) >= 3:
            recurring.append(r)

    site_role_diversity = {}
    for row in site_rows:
        carriers = [x for x in row["best_species_names"].split(";") if x]
        coded = [trait_by_species[x] for x in carriers if x in trait_by_species]
        groups = sorted({r["primary_trophic_group"] for r in coded})
        site_role_diversity[row["site_code"]] = {
            "all_carrier_count": len(carriers),
            "coded_carrier_count": len(coded),
            "coded_primary_trophic_groups": groups,
            "coded_trophic_group_count": len(groups),
            "coded_carriers": [
                {
                    "species": r["species_name"],
                    "primary_trophic_group": r["primary_trophic_group"],
                    "trophic_niche": r["trophic_niche"],
                }
                for r in coded
            ],
        }

    recurring_groups = sorted({r["primary_trophic_group"] for r in recurring})
    multi_role_sites = sorted(
        site for site, x in site_role_diversity.items()
        if x["coded_trophic_group_count"] >= 2
    )
    three_role_sites = sorted(
        site for site, x in site_role_diversity.items()
        if x["coded_trophic_group_count"] >= 3
    )

    payload = {
        "schema": "neon.carrier_niche_role.exploratory.v1",
        "status": "posthoc_literature_backed_representative_trait_audit",
        "coded_carrier_species": len(trait_rows),
        "coded_primary_trophic_group_counts": dict(sorted(group_counts.items())),
        "recurrently_observed_carriers": [
            {
                "species": r["species_name"],
                "carrier_site_count": int(r["carrier_site_count"]),
                "primary_trophic_group": r["primary_trophic_group"],
                "habitat_niche": r["habitat_niche"],
            }
            for r in recurring
        ],
        "recurrent_carrier_primary_trophic_groups": recurring_groups,
        "recurrent_carrier_trophic_group_count": len(recurring_groups),
        "sites_with_at_least_two_coded_carrier_trophic_groups": multi_role_sites,
        "sites_with_at_least_three_coded_carrier_trophic_groups": three_role_sites,
        "site_role_diversity": site_role_diversity,
        "interpretation": (
            "Continuity-carrier status is not confined to one trophic or ecosystem-effect "
            "guild. Recurrent carriers already span omnivory, granivory and herbivory, "
            "and some sites contain independently sufficient carriers from multiple trophic "
            "guilds. This supports treating continuity carrier status as a site-scale spatial "
            "response property rather than as an ecosystem functional role."
        ),
        "claim_boundary": {
            "supported_by_current_audit": [
                "literature-backed representative carriers span multiple trophic niches",
                "all four three-site recurrent carriers are represented and span three primary trophic groups",
                "some sites contain coded carriers from multiple trophic groups",
            ],
            "not_yet_supported": [
                "carrier status is caused by habitat breadth",
                "carrier status is caused by mobility or home-range size",
                "carrier status predicts ecosystem functioning",
                "carrier species are functionally redundant in the classical biodiversity-ecosystem-function sense",
                "the 17-species representative trait audit estimates trait frequencies for all 32 carrier species",
            ],
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
