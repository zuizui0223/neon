from __future__ import annotations

import argparse, csv, hashlib, io, json, os, urllib.request
from collections import Counter, defaultdict
from pathlib import Path

QUERY_URL="https://data.neonscience.org/api/v0/data/query"
TOKEN_ENV="NEON_API_TOKEN"
PRODUCT="DP1.10072.001"
RELEASE="RELEASE-2026"
SITES=("SRER","STEI","STER","TALL","TEAK","TOOL","TREE","UKFS","WOOD","WREF","YELL")
UA="neon-footprint-validation-stage0/1.0"

def post_query(token:str)->dict:
    body={
      "productCode":PRODUCT,
      "siteCodes":list(SITES),
      "startDateMonth":"2010-01",
      "endDateMonth":"2026-09",
      "includeProvisional":False,
      "package":"basic",
      "release":RELEASE,
    }
    req=urllib.request.Request(
      QUERY_URL,
      data=json.dumps(body,separators=(",",":"),sort_keys=True).encode(),
      method="POST",
      headers={"Content-Type":"application/json","X-API-Token":token,"User-Agent":UA},
    )
    with urllib.request.urlopen(req,timeout=180) as r:
        return json.loads(r.read().decode())

def inventory(payload:dict)->list[dict]:
    data=payload.get("data",{})
    if data.get("productCode")!=PRODUCT: raise RuntimeError("product drift")
    blocks=[x for x in data.get("releases",[]) if x.get("release")==RELEASE]
    if len(blocks)!=1: raise RuntimeError("release block mismatch")
    out={}
    for pkg in blocks[0].get("packages",[]):
        site=str(pkg.get("siteCode",""))
        if site not in SITES: raise RuntimeError(f"unexpected site {site}")
        month=str(pkg.get("month",""))
        for f in pkg.get("files",[]):
            name=str(f.get("name",""))
            low=name.lower()
            table=None
            if "mam_perplotnight" in low and low.endswith(".csv"): table="mam_perplotnight"
            elif "mam_pertrapnight" in low and low.endswith(".csv"): table="mam_pertrapnight"
            else: continue
            row={"site":site,"month":month,"name":name,"table":table,
                 "url":str(f.get("url","")),"size":int(f.get("size",0)),
                 "md5":str(f.get("md5","")).lower()}
            if not row["url"].startswith("https://") or len(row["md5"])!=32:
                raise RuntimeError(f"bad inventory row {name}")
            out[(site,month,name)]=row
    rows=[out[k] for k in sorted(out)]
    if not rows: raise RuntimeError("no mammal files")
    return rows

def download(row:dict,token:str)->bytes:
    req=urllib.request.Request(row["url"],headers={"X-API-Token":token,"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=240) as r: raw=r.read()
    if len(raw)!=row["size"]: raise RuntimeError(f"size mismatch {row['name']}")
    if hashlib.md5(raw).hexdigest()!=row["md5"]: raise RuntimeError(f"md5 mismatch {row['name']}")
    return raw

def rows(raw:bytes)->tuple[list[str],list[dict]]:
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    return list(reader.fieldnames or []),list(reader)

def clean(x): return str(x or "").strip()

def is_capture(status:str)->bool:
    s=clean(status).lower()
    return "capture" in s and "no capture" not in s

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    token=os.environ.get(TOKEN_ENV,"").strip()
    if not token: raise RuntimeError("NEON_API_TOKEN missing")

    payload=post_query(token)
    files=inventory(payload)
    file_receipts=[]
    headers={"mam_perplotnight":set(),"mam_pertrapnight":set()}

    # nightuid -> bout metadata
    night={}
    plot_rows=0
    for f in [x for x in files if x["table"]=="mam_perplotnight"]:
        raw=download(f,token)
        hdr, rr=rows(raw)
        headers["mam_perplotnight"].update(hdr)
        plot_rows += len(rr)
        file_receipts.append({k:f[k] for k in ("site","month","name","table","size","md5")})
        for r in rr:
            uid=clean(r.get("nightuid"))
            if not uid: continue
            meta={
              "site":f["site"],
              "plotID":clean(r.get("plotID")),
              "collectDate":clean(r.get("collectDate")),
              "eventID":clean(r.get("eventID")),
              "mammalGridSamplingType":clean(r.get("mammalGridSamplingType") or r.get("mammalGridSampleType")),
              "gridCompletion":clean(r.get("gridCompletion")),
            }
            if uid in night and night[uid]!=meta:
                raise RuntimeError(f"nightuid metadata conflict {uid}")
            night[uid]=meta

    captures=[]
    trap_rows=0
    x_capture_rows=0
    capture_no_tag=0
    capture_no_taxon=0
    capture_no_event=0
    unknown_nightuid=0
    taxon_rows=Counter()
    for f in [x for x in files if x["table"]=="mam_pertrapnight"]:
        raw=download(f,token)
        hdr, rr=rows(raw)
        headers["mam_pertrapnight"].update(hdr)
        trap_rows += len(rr)
        file_receipts.append({k:f[k] for k in ("site","month","name","table","size","md5")})
        for r in rr:
            if not is_capture(r.get("trapStatus","")): continue
            tag=clean(r.get("tagID"))
            tax=clean(r.get("taxonID"))
            coord=clean(r.get("trapCoordinate"))
            nuid=clean(r.get("nightuid"))
            if not tag:
                capture_no_tag+=1; continue
            if not tax:
                capture_no_taxon+=1; continue
            if "X" in coord.upper() or not coord:
                x_capture_rows+=1; continue
            meta=night.get(nuid)
            if meta is None:
                unknown_nightuid+=1; continue
            event=clean(meta["eventID"])
            if not event:
                capture_no_event+=1; continue
            date=clean(meta["collectDate"]) or clean(r.get("collectDate"))
            plot=clean(meta["plotID"]) or clean(r.get("plotID"))
            if not date or not plot: continue
            captures.append({
              "site":f["site"],"plotID":plot,"eventID":event,"date":date,
              "tagID":tag,"taxonID":tax,"trapCoordinate":coord,
              "samplingType":meta["mammalGridSamplingType"],
              "gridCompletion":meta["gridCompletion"],
            })
            taxon_rows[tax]+=1

    grouped=defaultdict(list)
    for r in captures:
        grouped[(r["site"],r["plotID"],r["eventID"],r["tagID"])].append(r)

    unit_species=defaultdict(Counter)
    night_hist=Counter(); trap_hist=Counter()
    inconsistent=[]
    multi=0
    for key, rr in grouped.items():
        dates={x["date"] for x in rr}
        traps={x["trapCoordinate"] for x in rr}
        taxa={x["taxonID"] for x in rr}
        night_hist[len(dates)]+=1
        trap_hist[len(traps)]+=1
        if len(taxa)>1:
            inconsistent.append({"site":key[0],"plotID":key[1],"eventID":key[2],"tagID":key[3],
                                 "taxa":sorted(taxa),"nights":len(dates)})
            continue
        if len(dates)>=2:
            multi+=1
            unit_species[(key[0],key[1],key[2])][next(iter(taxa))]+=1

    units=[]
    for (site,plot,event), spp in sorted(unit_species.items()):
        units.append({
          "site":site,"plotID":plot,"eventID":event,
          "multi_night_individuals_by_taxon":dict(sorted(spp.items())),
          "taxa_with_multi_night_individuals":len(spp),
          "multi_night_individuals_total":sum(spp.values()),
        })

    result={
      "schema":"neon.independent_footprint_validation.inventory.v1",
      "status":"stage0_support_only_no_footprint_outcomes_opened",
      "source":{"product":PRODUCT,"release":RELEASE,"fixed_sites":list(SITES)},
      "files":{"count":len(file_receipts),"total_bytes":sum(x["size"] for x in file_receipts),
               "receipts":file_receipts},
      "schemas":{k:sorted(v) for k,v in headers.items()},
      "support":{
        "perplotnight_rows":plot_rows,"pertrapnight_rows":trap_rows,
        "joined_tagged_capture_rows":len(captures),
        "capture_rows_excluded_missing_tag":capture_no_tag,
        "capture_rows_excluded_missing_taxon":capture_no_taxon,
        "capture_rows_excluded_x_or_missing_coordinate":x_capture_rows,
        "capture_rows_excluded_missing_eventID":capture_no_event,
        "capture_rows_unknown_nightuid":unknown_nightuid,
        "tagged_individual_unit_histogram_distinct_nights":{str(k):v for k,v in sorted(night_hist.items())},
        "tagged_individual_unit_histogram_distinct_traps":{str(k):v for k,v in sorted(trap_hist.items())},
        "multi_night_individuals":multi,
        "taxon_capture_rows":dict(sorted(taxon_rows.items())),
        "taxonomically_inconsistent_tag_units":len(inconsistent),
        "taxonomic_inconsistency_examples":inconsistent[:20],
        "units_with_any_multi_night_individual":len(units),
        "units_with_at_least_two_taxa_multi_night":sum(u["taxa_with_multi_night_individuals"]>=2 for u in units),
        "units_with_at_least_three_taxa_multi_night":sum(u["taxa_with_multi_night_individuals"]>=3 for u in units),
        "unit_support":units,
      },
      "claim_boundary":{
        "footprint_overlap_opened":False,
        "conspecific_assortativity_opened":False,
        "community_cscore_opened":False,
        "habitat_effect_opened":False,
        "species_pair_outcomes_opened":False,
      }
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "status":result["status"],
      "file_count":result["files"]["count"],
      "total_bytes":result["files"]["total_bytes"],
      "multi_night_individuals":multi,
      "units_2plus_taxa":result["support"]["units_with_at_least_two_taxa_multi_night"],
      "units_3plus_taxa":result["support"]["units_with_at_least_three_taxa_multi_night"],
      "taxonomic_inconsistent":len(inconsistent)
    },indent=2))
    return 0

if __name__=="__main__": raise SystemExit(main())
