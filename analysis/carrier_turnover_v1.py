from __future__ import annotations

import csv
import itertools
import json
import math
from collections import Counter
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[1]
SITE_CSV = ROOT / "data" / "derived" / "site_metrics_v1.csv"
OUT = ROOT / "results"


def load_rows():
    with SITE_CSV.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def rank_average(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        r = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[order[k]] = r
        i = j
    return ranks


def pearson(x, y):
    mx, my = mean(x), mean(y)
    num = sum((a-mx)*(b-my) for a,b in zip(x,y))
    denx = math.sqrt(sum((a-mx)**2 for a in x))
    deny = math.sqrt(sum((b-my)**2 for b in y))
    return num / (denx * deny)


def spearman(x, y):
    return pearson(rank_average(x), rank_average(y))


def main():
    rows = load_rows()
    carrier_sets = {
        r["site_code"]: {x for x in r["best_species_names"].split(";") if x}
        for r in rows
    }

    freq = Counter()
    for species in carrier_sets.values():
        freq.update(species)

    pair_rows = []
    jaccards = []
    overlap_pairs = 0
    for a, b in itertools.combinations(sorted(carrier_sets), 2):
        sa, sb = carrier_sets[a], carrier_sets[b]
        inter = sa & sb
        union = sa | sb
        jac = len(inter) / len(union)
        if inter:
            overlap_pairs += 1
        jaccards.append(jac)
        pair_rows.append({
            "site_a": a,
            "site_b": b,
            "shared_carrier_count": len(inter),
            "union_carrier_count": len(union),
            "jaccard": jac,
            "shared_carriers": ";".join(sorted(inter)),
        })

    richness = [int(r["observed_target_species_count"]) for r in rows]
    eligible = [int(r["species_with_two_positive_nodes"]) for r in rows]
    depth = [int(r["best_species_count"]) for r in rows]
    dominance = [float(r["dominance_coverage"]) for r in rows]
    rescue = [float(r["cross_species_rescue_fraction"]) for r in rows]
    fraction = [d/e for d,e in zip(depth, eligible)]

    summary = {
        "schema": "neon.carrier_turnover.exploratory.v1",
        "status": "posthoc_exploratory_frozen_site_summaries_only",
        "site_count": len(rows),
        "site_carrier_records": sum(depth),
        "distinct_continuity_carrier_species": len(freq),
        "carrier_frequency_distribution": {
            str(k): sum(1 for v in freq.values() if v == k)
            for k in sorted(set(freq.values()))
        },
        "max_sites_per_carrier_species": max(freq.values()),
        "singleton_carrier_species": sum(v == 1 for v in freq.values()),
        "site_pair_count": len(pair_rows),
        "site_pairs_sharing_any_carrier": overlap_pairs,
        "site_pair_shared_carrier_fraction": overlap_pairs / len(pair_rows),
        "pairwise_carrier_jaccard_median": median(jaccards),
        "pairwise_carrier_jaccard_mean": mean(jaccards),
        "pairwise_carrier_jaccard_max": max(jaccards),
        "redundancy_depth_median": median(depth),
        "redundancy_depth_range": [min(depth), max(depth)],
        "eligible_species_individually_sufficient_fraction_median": median(fraction),
        "exploratory_rank_associations": {
            "richness_vs_redundancy_depth_rho": spearman(richness, depth),
            "richness_vs_redundancy_fraction_rho": spearman(richness, fraction),
            "richness_vs_dominance_coverage_rho": spearman(richness, dominance),
            "richness_vs_cross_species_rescue_rho": spearman(richness, rescue),
        },
        "interpretation": (
            "Spatial continuity is locally redundant but carried by taxonomically "
            "different species across sites. Richer sites contain more individually "
            "sufficient species while dominance weakens, without an increasing "
            "fraction of eligible species becoming sufficient."
        ),
        "claim_boundary": {
            "supported_descriptive": [
                "continuity-carrier identity turns over strongly among sites",
                "multiple species are individually sufficient at many sites",
                "no single species is a continent-wide continuity carrier",
            ],
            "not_supported": [
                "carrier turnover causes metacommunity stability",
                "the carrier role is a conserved functional trait",
                "taxonomic turnover among sites is itself surprising given geographic separation",
                "exploratory rank associations are confirmatory",
            ],
        },
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "carrier_turnover_v1.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with (OUT / "carrier_frequency_v1.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["species_name", "sites_as_continuity_carrier"])
        for species, count in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0])):
            w.writerow([species, count])

    with (OUT / "site_pair_carrier_overlap_v1.csv").open("w", newline="", encoding="utf-8") as fh:
        fields = [
            "site_a", "site_b", "shared_carrier_count",
            "union_carrier_count", "jaccard", "shared_carriers",
        ]
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(pair_rows)


if __name__ == "__main__":
    main()
