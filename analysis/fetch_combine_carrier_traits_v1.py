from __future__ import annotations

import csv
import io
import json
import math
import statistics
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARRIERS = ROOT / "data" / "external" / "carrier_niche_evidence_v2_all32.csv"
OUT_DIR = ROOT / "results" / "generated"
OUT_CSV = OUT_DIR / "combine_carrier_traits_v1.csv"
OUT_JSON = OUT_DIR / "combine_carrier_trait_summary_v1.json"

REPORTED_URL = "https://ndownloader.figshare.com/files/27703263"
IMPUTED_URL = "https://ndownloader.figshare.com/files/27703266"

TRAITS = [
    "adult_mass_g",
    "dispersal_km",
    "habitat_breadth_n",
    "det_diet_breadth_n",
    "home_range_km2",
    "density_n_km2",
    "trophic_level",
    "dphy_invertebrate",
    "dphy_vertebrate",
    "dphy_plant",
    "det_inv",
    "det_vend",
    "det_vect",
    "det_vfish",
    "det_vunk",
    "det_scav",
    "det_fruit",
    "det_nect",
    "det_seed",
    "det_plantother",
    "fossoriality",
    "social_group_n",
    "activity_cycle",
]

def download_csv(url: str) -> list[dict[str, str]]:
    req = urllib.request.Request(url, headers={"User-Agent": "neon-carrier-traits/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read()
    text = raw.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))

def canonical_name(row: dict[str, str]) -> str:
    name = (row.get("iucn2020_binomial") or "").strip()
    if name and name not in {"NA", "Not recognised"}:
        return name
    return " ".join(
        x.strip() for x in (row.get("genus", ""), row.get("species", "")) if x.strip()
    )

def num(value: str | None):
    if value is None:
        return None
    x = value.strip()
    if not x or x in {"NA", "NaN", "nan", "Not recognised"}:
        return None
    try:
        v = float(x)
    except ValueError:
        return None
    return v if math.isfinite(v) else None

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
    if len(x) < 3:
        return None
    mx, my = statistics.mean(x), statistics.mean(y)
    dx = math.sqrt(sum((v-mx)**2 for v in x))
    dy = math.sqrt(sum((v-my)**2 for v in y))
    if dx == 0 or dy == 0:
        return None
    return sum((a-mx)*(b-my) for a,b in zip(x,y)) / (dx*dy)

def spearman(x, y):
    return pearson(rank_average(x), rank_average(y))

def main():
    with CARRIERS.open(newline="", encoding="utf-8") as fh:
        carriers = list(csv.DictReader(fh))
    wanted = {r["species_name"]: int(r["carrier_site_count"]) for r in carriers}

    reported_rows = download_csv(REPORTED_URL)
    imputed_rows = download_csv(IMPUTED_URL)
    reported = {canonical_name(r): r for r in reported_rows if canonical_name(r)}
    imputed = {canonical_name(r): r for r in imputed_rows if canonical_name(r)}

    print("COMBINE_REPORTED_COLUMNS " + json.dumps(list(reported_rows[0].keys())))
    missing = sorted(set(wanted) - (set(reported) | set(imputed)))
    if missing:
        raise RuntimeError(f"COMBINE taxon match missing: {missing}")

    out = []
    for species in sorted(wanted):
        rr = reported.get(species, {})
        ir = imputed.get(species, {})
        row = {
            "species_name": species,
            "carrier_site_count": wanted[species],
        }
        for trait in TRAITS:
            rv = num(rr.get(trait))
            iv = num(ir.get(trait))
            value = rv if rv is not None else iv
            row[trait] = value
            row[trait + "_provenance"] = (
                "reported" if rv is not None else
                "imputed" if iv is not None else
                "missing"
            )
        out.append(row)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fields = ["species_name", "carrier_site_count"]
    for trait in TRAITS:
        fields += [trait, trait + "_provenance"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(out)

    associations = {}
    group_summaries = {}
    for trait in TRAITS:
        pairs = [(r["carrier_site_count"], r[trait]) for r in out if r[trait] is not None]
        associations[trait] = {
            "n": len(pairs),
            "spearman_recurrence": spearman(
                [float(a) for a,b in pairs],
                [float(b) for a,b in pairs],
            ) if len(pairs) >= 3 else None,
            "reported_n": sum(r[trait + "_provenance"] == "reported" for r in out),
            "imputed_n": sum(r[trait + "_provenance"] == "imputed" for r in out),
            "missing_n": sum(r[trait + "_provenance"] == "missing" for r in out),
        }
        singleton = [float(r[trait]) for r in out if r["carrier_site_count"] == 1 and r[trait] is not None]
        recurrent = [float(r[trait]) for r in out if r["carrier_site_count"] >= 2 and r[trait] is not None]
        group_summaries[trait] = {
            "singleton_n": len(singleton),
            "recurrent_n": len(recurrent),
            "singleton_median": statistics.median(singleton) if singleton else None,
            "recurrent_median": statistics.median(recurrent) if recurrent else None,
        }

    summary = {
        "schema": "neon.combine_carrier_traits.v1",
        "source": {
            "database": "COMBINE",
            "doi": "10.1002/ecy.3344",
            "figshare": "10.6084/m9.figshare.13028255.v4",
            "reported_file_id": "27703263",
            "imputed_file_id": "27703266",
            "rule": "reported value preferred; imputed used only when reported is missing",
        },
        "scope": "32 species that are already continuity carriers; tests recurrence among carrier species, not carrier-vs-noncarrier probability",
        "carrier_species_n": len(out),
        "associations": associations,
        "singleton_vs_recurrent": group_summaries,
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("COMBINE_SUMMARY " + json.dumps(summary, sort_keys=True))
    for row in out:
        print("COMBINE_ROW " + json.dumps(row, sort_keys=True))

if __name__ == "__main__":
    main()
