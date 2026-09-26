from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "derived" / "combine_carrier_traits_v1.csv"
OUT = ROOT / "results" / "combine_carrier_trait_summary_recomputed_v1.json"
TRAITS = [
    "adult_mass_g",
    "dispersal_km",
    "habitat_breadth_n",
    "det_diet_breadth_n",
    "home_range_km2",
    "density_n_km2",
    "trophic_level",
]

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
    mx, my = statistics.mean(x), statistics.mean(y)
    dx = math.sqrt(sum((v-mx)**2 for v in x))
    dy = math.sqrt(sum((v-my)**2 for v in y))
    if dx == 0 or dy == 0:
        return None
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/(dx*dy)

def spearman(x,y):
    if len(x) < 3:
        return None
    return pearson(rank_average(x), rank_average(y))

def cliffs_delta(a,b):
    if not a or not b:
        return None
    gt=sum(x>y for x in a for y in b)
    lt=sum(x<y for x in a for y in b)
    return (gt-lt)/(len(a)*len(b))

def fnum(x):
    if x is None or x == "":
        return None
    return float(x)

def main():
    with DATA.open(newline="",encoding="utf-8") as fh:
        rows=list(csv.DictReader(fh))
    if len(rows)!=32:
        raise RuntimeError(f"expected 32 carrier species, got {len(rows)}")

    results={}
    for trait in TRAITS:
        pairs=[(int(r["carrier_site_count"]),fnum(r[trait])) for r in rows]
        pairs=[x for x in pairs if x[1] is not None]
        singleton=[v for n,v in pairs if n==1]
        recurrent=[v for n,v in pairs if n>=2]
        results[trait]={
            "n":len(pairs),
            "spearman_recurrence":spearman([float(n) for n,v in pairs],[v for n,v in pairs]),
            "singleton_n":len(singleton),
            "recurrent_n":len(recurrent),
            "singleton_median":statistics.median(singleton) if singleton else None,
            "recurrent_median":statistics.median(recurrent) if recurrent else None,
            "cliffs_delta_recurrent_vs_singleton":cliffs_delta(recurrent,singleton),
        }

    payload={
        "schema":"neon.combine_carrier_traits.recomputed.v1",
        "scope":"carrier-only posthoc diagnostic of recurrence across 1-3 sites",
        "carrier_species_n":len(rows),
        "traits":results,
        "interpretation":(
            "Broad niche and movement traits show little association with carrier recurrence. "
            "Species-level population density has the largest positive effect among tested traits, "
            "motivating a fresh count-conditioned spatial-null test of prevalence versus spatial organization."
        ),
        "limitations":[
            "COMBINE density is not local NEON density",
            "carrier-only sample cannot test carrier versus non-carrier status",
            "posthoc exploratory analysis",
            "no phylogenetic correction",
        ],
    }
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
