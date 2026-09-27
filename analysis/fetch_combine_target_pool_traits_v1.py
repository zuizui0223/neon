from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"validation"/"carrier_prevalence_mechanism_v1"/"protocol_v1.json"
OUT_DIR=ROOT/"results"/"generated"
OUT_CSV=OUT_DIR/"combine_target_pool_traits_v1.csv"
OUT_JSON=OUT_DIR/"combine_target_pool_traits_summary_v1.json"

TAXONOMY_URL=(
    "https://data.neonscience.org/api/v0/taxonomy?"
    "taxonTypeCode=SMALL_MAMMAL&verbose=true&offset=0&limit=1000"
)
REPORTED_URL="https://ndownloader.figshare.com/files/27703263"
IMPUTED_URL="https://ndownloader.figshare.com/files/27703266"
TRAITS=[
    "adult_mass_g","dispersal_km","habitat_breadth_n","det_diet_breadth_n",
    "home_range_km2","density_n_km2","trophic_level",
    "dphy_invertebrate","dphy_vertebrate","dphy_plant",
    "det_inv","det_vend","det_vect","det_vfish","det_vunk","det_scav",
    "det_fruit","det_nect","det_seed","det_plantother",
    "fossoriality","social_group_n","activity_cycle"
]

def sha_bytes(raw: bytes)->str:
    return hashlib.sha256(raw).hexdigest()

def canonical_sha(value: object)->str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()).hexdigest()

def download(url:str)->bytes:
    req=urllib.request.Request(url,headers={"User-Agent":"neon-carrier-mechanism-traits/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def rows_from(raw:bytes):
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))

def canonical_name(row):
    name=(row.get("iucn2020_binomial") or "").strip()
    if name and name not in {"NA","Not recognised"}:
        return name
    return " ".join(x.strip() for x in (row.get("genus",""),row.get("species","")) if x.strip())

def num(x):
    if x is None:return None
    x=x.strip()
    if not x or x in {"NA","NaN","nan","Not recognised"}:return None
    try:v=float(x)
    except ValueError:return None
    return v if math.isfinite(v) else None

def main():
    protocol=json.loads(PROTOCOL.read_text())
    excluded={x["scientific_name"] for x in protocol["target_taxa"]["design_contamination_exclusions"]}

    tax_raw=download(TAXONOMY_URL)
    tax_payload=json.loads(tax_raw.decode("utf-8"))
    taxa=[]
    for row in tax_payload.get("data",[]):
        if str(row.get("dwc:taxonRank","")).lower()!="species":continue
        if str(row.get("taxonProtocolCategory","")).lower()!="target":continue
        tid=str(row.get("taxonID","")).strip()
        name=str(row.get("dwc:scientificName","")).strip()
        if tid and name and name not in excluded:
            taxa.append((name,tid))
    taxa=sorted(set(taxa))

    rep_raw=download(REPORTED_URL)
    imp_raw=download(IMPUTED_URL)
    rep_rows=rows_from(rep_raw); imp_rows=rows_from(imp_raw)
    reported={canonical_name(r):r for r in rep_rows if canonical_name(r)}
    imputed={canonical_name(r):r for r in imp_rows if canonical_name(r)}

    out=[]
    for name,tid in taxa:
        rr=reported.get(name,{})
        ir=imputed.get(name,{})
        row={"species_name":name,"taxon_id":tid,"combine_match":bool(rr or ir)}
        for trait in TRAITS:
            rv=num(rr.get(trait)); iv=num(ir.get(trait))
            row[trait]=rv if rv is not None else iv
            row[trait+"_provenance"]="reported" if rv is not None else "imputed" if iv is not None else "missing"
        out.append(row)

    OUT_DIR.mkdir(parents=True,exist_ok=True)
    fields=["species_name","taxon_id","combine_match"]
    for trait in TRAITS:fields += [trait,trait+"_provenance"]
    with OUT_CSV.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields)
        w.writeheader();w.writerows(out)

    summary={
        "schema":"neon.combine_target_pool_traits.v1",
        "status":"response_blind_trait_pool_frozen_candidate",
        "neon_taxonomy_fingerprint":canonical_sha(tax_payload),
        "neon_target_taxon_count":len(out),
        "combine_exact_match_count":sum(bool(r["combine_match"]) for r in out),
        "combine_unmatched_species":[r["species_name"] for r in out if not r["combine_match"]],
        "source":{
            "database":"COMBINE",
            "publication_doi":"10.1002/ecy.3344",
            "figshare_doi":"10.6084/m9.figshare.13028255.v4",
            "reported_file_id":"27703263",
            "reported_sha256":sha_bytes(rep_raw),
            "imputed_file_id":"27703266",
            "imputed_sha256":sha_bytes(imp_raw),
            "rule":"exact IUCN-2020 binomial match; reported preferred; imputed used only when reported is missing; unmatched taxa remain unmatched"
        },
        "trait_coverage":{
            trait:{
                "nonmissing":sum(r[trait] is not None for r in out),
                "reported":sum(r[trait+"_provenance"]=="reported" for r in out),
                "imputed":sum(r[trait+"_provenance"]=="imputed" for r in out),
                "missing":sum(r[trait+"_provenance"]=="missing" for r in out)
            }
            for trait in TRAITS
        },
        "response_endpoint_requests":0,
        "biological_response_bytes_opened":0
    }
    summary["fingerprint"]=canonical_sha(summary)
    OUT_JSON.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("TARGET_TRAIT_SUMMARY "+json.dumps(summary,sort_keys=True))

if __name__=="__main__":
    main()
