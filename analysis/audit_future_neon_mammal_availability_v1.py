#!/usr/bin/env python3
"""Effect-blind future NEON product availability audit.

Read only the public /products/DP1.10072.001 metadata endpoint. This does NOT
download captures, infer novel individuals, calculate W/B, or open held-out
response values. A new month in provisional availability is ONLY a candidate;
record-level non-overlap and the pre-registered response support gates must
still be verified separately.
"""
from __future__ import annotations

import argparse
import json
import urllib.request
from datetime import date
from pathlib import Path

URL = "https://data.neonscience.org/api/v0/products/DP1.10072.001"
RELEASE = "RELEASE-2026"
TARGET_PRODUCT = "DP1.10072.001"
OUT = Path("build/future_neon_mammal_availability_v1.json")


def audit(payload: dict, as_of: str = "2026-10-10") -> dict:
    meta = payload.get("data")
    if not isinstance(meta, dict):
        raise ValueError("no data product metadata")
    sites = meta.get("siteCodes")
    if not isinstance(sites, list) or not sites:
        raise ValueError("empty product site inventory")
    asof_month=as_of[:7]
    all_sites=[]
    site_months=[]
    n_with_release=0
    missing_release_metadata=[]
    for item in sites:
        if not isinstance(item,dict):
            raise ValueError("unexpected site record")
        code=str(item.get("siteCode") or "").strip()
        if len(code)!=4:
            raise ValueError("invalid NEON site code")
        months=item.get("availableMonths")
        releases=item.get("availableReleases")
        if not isinstance(months,list) or not isinstance(releases,list):
            missing_release_metadata.append(code)
            continue
        avail={str(v) for v in months if isinstance(v,str) and len(v)==7 and v[4]=="-"}
        release_months=set()
        found=False
        for row in releases:
            if row.get("release")==RELEASE:
                found=True
                release_months |= {
                    str(v) for v in row.get("availableMonths",[])
                    if isinstance(v,str) and len(v)==7 and v[4]=="-"
                }
        if found: n_with_release+=1
        # Only entire months NOT represented by RELEASE-2026 are eligible
        # even as possible new-data months. Same-month new records ignored.
        candidate=sorted(m for m in avail-release_months if m<=asof_month)
        all_sites.append(code)
        for month in candidate:
            site_months.append({"site":code,"month":month})
    if missing_release_metadata:
        return {
            "schema":"neon.future_small_mammal_availability.v1",
            "status":"STRUCTURAL_METADATA_STOP",
            "reason":"Missing per-site release comparison metadata",
            "missing_sites":missing_release_metadata,
            "captures_downloaded":False,
            "W_B_effects_opened":False,
        }
    if n_with_release==0:
        raise ValueError("release metadata contains no RELEASE-2026 entries")
    site_months.sort(key=lambda v:(v["month"],v["site"]))
    return {
        "schema":"neon.future_small_mammal_availability.v1",
        "status":"INVENTORY_ONLY_CANDIDATE_MONTHS" if site_months
            else "NO_FULLY_NEW_SITE_MONTHS_IN_INVENTORY",
        "as_of":as_of,
        "product":TARGET_PRODUCT,
        "comparison_release":RELEASE,
        "sites_with_comparable_metadata":len(all_sites),
        "sites_with_release_2026":n_with_release,
        "new_site_month_candidates":len(site_months),
        "candidate_sites":len({x["site"] for x in site_months}),
        "candidate_months":sorted({x["month"] for x in site_months}),
        "site_month_candidates":site_months,
        "captures_downloaded":False,
        "individuals_or_nights_extracted":False,
        "W_B_effects_opened":False,
        "eligible_three_night_events_confirmed":False,
        "future_independent_replication_confirmed":False,
        "claim_boundary":"Public availability metadata are not trap-event data. Future candidate months can contain provisional, incomplete or invalid trapping; no independent confirmation is implied.",
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=OUT)
    p.add_argument("--as-of",default="2026-10-10")
    args=p.parse_args()
    if date.fromisoformat(args.as_of)>date(2026,10,10):
        raise ValueError("as-of cannot be future relative to this audit")
    req=urllib.request.Request(URL,headers={"User-Agent":"neon-future-availability-audit/1.0"})
    with urllib.request.urlopen(req,timeout=100) as resp:
        raw=resp.read()
    data=json.loads(raw)
    result=audit(data,args.as_of)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if result["status"]!="STRUCTURAL_METADATA_STOP" else 3


if __name__=="__main__":
    raise SystemExit(main())
