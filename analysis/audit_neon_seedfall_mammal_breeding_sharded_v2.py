"""Bounded full-source replay: disjoint site shards, unchanged support audit.

No seed mass or pregnancy association, no site or animal identifiers in
receipts. Sharding changes only transport and memory budget.
"""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,os,re
from analysis.audit_neon_seedfall_mammal_breeding_support_v1 import (
    ROOT,RELEASE,START,END,LITTER,MAMMAL,LITTER_TABLES,MAMMAL_TABLES,
    TOKEN_ENV,_request_json,_site_codes,inventory,manifest_info,audit,req,LIMIT,
)
N_SHARDS=4
PIN_PATH=ROOT/"results/neon_seedfall_mammal_breeding_v1_budget_stop_20261125.json"
BUILD=ROOT/"build"
SCHEMA="neon.seedfall.mammal.breeding.shard.v1"
ALL_SCHEMA="neon.seedfall.mammal.breeding.sharded_support.v1"

def expected():
    a=json.loads(PIN_PATH.read_text())["original_stdout_json"]
    req(a["status"]=="STOP_SOURCE_FILE_BUDGET_OR_EMPTY","PIN_NOT_ORIGINAL_BUDGET_STOP")
    return {k:a[k] for k in ("release","window","common_product_site_count","litter_product_site_count",
        "mammal_product_site_count","litter_manifest","mammal_manifest_all","mammal_manifest_selected")}

def partition(sites):
    sites=sorted(sites)
    req(len(sites)==32 and len(set(sites))==32,"ORIGINAL_SITE_ROSTER_DRIFT")
    return [set(sites[j::N_SHARDS]) for j in range(N_SHARDS)]

def manifest_pin_digest(pin):
    return sha256(json.dumps(pin,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def source(token):
    req(RELEASE=="RELEASE-2026" and START=="2017-01" and END=="2025-12","SOURCE_WINDOW_DRIFT")
    def sites(product):
        return set(_site_codes(_request_json("https://data.neonscience.org/api/v0/products/"+product+"?release="+RELEASE)))
    a,b=sites(LITTER),sites(MAMMAL);common=sorted(a&b)
    parts=partition(common)
    lf=inventory(LITTER,common,LITTER_TABLES,token)
    mf0=inventory(MAMMAL,common,MAMMAL_TABLES,token)
    mf=[v for v in mf0 if int(v["month"][-2:]) in {2,3,4,5,6,8,9,10,11,12}]
    mf.sort(key=lambda v:(v["table"]!="mam_perplotnight",v["site"],v["month"],v["name"]))
    pin={"release":RELEASE,"window":[START,END],"litter_product_site_count":len(a),
        "mammal_product_site_count":len(b),"common_product_site_count":len(common),
        "litter_manifest":manifest_info(lf),"mammal_manifest_all":manifest_info(mf0),
        "mammal_manifest_selected":manifest_info(mf)}
    req(pin==expected(),"FULL_PINNED_MANIFEST_DRIFT")
    return parts,lf,mf,pin

def shard(index):
    token=os.environ.get(TOKEN_ENV,"").strip()
    req(token,"NEON_TOKEN_UNAVAILABLE")
    parts,lf,mf,pin=source(token)
    ss=parts[index]
    ls=[x for x in lf if x["site"] in ss];ms=[x for x in mf if x["site"] in ss]
    req(len(ss)==8 and ls and ms,"EMPTY_OR_DRIFTED_SHARD")
    req(sum(x["size"] for x in ls+ms)<=LIMIT,"SHARD_EXCEEDS_EXISTING_BUDGET")
    out={"source_pin_sha256":manifest_pin_digest(pin),"shard_index":index,
         "site_count":len(ss),"litter_manifest":manifest_info(ls),"mammal_manifest_selected":manifest_info(ms),
         "site_partition_sha256":sha256(json.dumps(sorted(ss),separators=(",",":")).encode()).hexdigest()}
    # Exact inherited v1 audit. Site-local joins and support counts are
    # additive across disjoint whole-site shards; no row-based splits.
    out["audit"]=audit(ls,ms,token)
    out["status"]="SOURCE_SUPPORT_ONLY_NO_EFFECT"
    out["all_downloaded_files_size_md5_verified"]=len(ls)+len(ms)
    return out

def merge_numeric(items):
    """Add nonnegative source counts; require identical boolean semantics.

    Nested dictionaries may have different observed category keys.
    No averaging rates or treating booleans as integers.
    """
    out={}
    for m in items:
        for k,v in m.items():
            if isinstance(v,bool):
                req(k not in out or (isinstance(out[k],bool) and out[k]==v),"BOOLEAN_SEMANTICS_DRIFT")
                out[k]=v
            elif isinstance(v,int) and v>=0:
                req(k not in out or (type(out[k]) is int),"COUNT_TYPE_DRIFT")
                out[k]=out.get(k,0)+v
            elif isinstance(v,dict):
                req(k not in out or isinstance(out[k],dict),"NESTED_TYPE_DRIFT")
                out[k]=merge_numeric([out.get(k,{}),v])
            else:
                raise ValueError("UNMERGEABLE_SOURCE_COUNT")
    return out

def merge_headers(items):
    all_headers=defaultdict(Counter)
    for value in items:
        for tab,records in value.items():
            for row in records:
                all_headers[tab][tuple(row["header"])]+=row["files"]
    return {tab:[{"header":list(h),"files":n} for h,n in sorted(c.items())] for tab,c in sorted(all_headers.items())}

def merge_manifest(items):
    return merge_numeric([{k:v for k,v in x.items() if k!="md5_manifest_sha256"} for x in items])

def combined(data,pin):
    req(len(data)==N_SHARDS and {x.get("shard_index") for x in data}==set(range(N_SHARDS)),"INCOMPLETE_SHARD_ROSTER")
    req(all(x.get("status")=="SOURCE_SUPPORT_ONLY_NO_EFFECT" for x in data),"ONE_OR_MORE_SHARD_SOURCE_STOP")
    req(all(x.get("source_pin_sha256")==manifest_pin_digest(pin) and x.get("site_count")==8 for x in data),"SHARD_PIN_DRIFT")
    req(len({x["site_partition_sha256"] for x in data})==N_SHARDS,"DUPLICATE_SHARD_PARTITION")
    for table in ("litter_manifest","mammal_manifest_selected"):
        expect={k:v for k,v in pin[table].items() if k!="md5_manifest_sha256"}
        req(merge_manifest([x[table] for x in data])==expect,"TOTAL_MANIFEST_COUNT_MISMATCH")
    audited=[x["audit"] for x in data]
    req(all(a["ecological_effect"] is None and a["complete_resource_intervals_verified"] is False and a["individual_identity_history_verified"] is False for a in audited),"AUDIT_OUTCOME_OPENED")
    nverified=sum(x["all_downloaded_files_size_md5_verified"] for x in data)
    req(nverified==7009,"TOTAL_FILE_COUNT_MISMATCH")
    result={"status":"ALL_32_SITES_SOURCE_SUPPORT_ONLY_NO_EFFECT","original_full_manifest":pin,
         "source_pin_sha256":manifest_pin_digest(pin),"shard_count":len(data),
         "all_downloaded_files_size_md5_verified":nverified,
         "litter_source":merge_numeric([a["litter_source"] for a in audited]),
         "mammal_source":merge_numeric([a["mammal_source"] for a in audited]),
         "necessary_calendar_support":merge_numeric([a["necessary_calendar_support"] for a in audited]),
         "headers":merge_headers([a["headers"] for a in audited]),
         "complete_resource_intervals_verified":False,"individual_identity_history_verified":False,
         "ecological_effect":None,
         "shards":[{k:x[k] for k in ("shard_index","site_count","source_pin_sha256","site_partition_sha256",
           "litter_manifest","mammal_manifest_selected","all_downloaded_files_size_md5_verified","status")} for x in sorted(data,key=lambda x:x["shard_index"])]}
    # The support histogram is the number of physical sites by count of
    # candidate years; it must reconcile with total candidate site-years.
    s=result["necessary_calendar_support"];h=s["site_year_support_histogram"]
    req(sum(h.values())==s["candidate_sites"] and sum(int(k)*n for k,n in h.items())==s["candidate_site_years"],"CANDIDATE_HISTOGRAM_MISMATCH")
    req(s["candidate_sites"]<=32 and s["candidate_site_years"]<=32*9,"CANDIDATE_SUPPORT_OUT_OF_BOUNDS")
    req(sum(n for k,n in h.items() if int(k)>=4)==s["sites_with_at_least_four_candidate_years"],"CANDIDATE_REPEAT_SUPPORT_MISMATCH")
    return result

def emit(path,out):
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="mode",required=True)
    s=sub.add_parser("shard");s.add_argument("index",type=int,choices=range(N_SHARDS))
    c=sub.add_parser("combine");c.add_argument("directory",type=Path)
    a=parser.parse_args()
    out={"schema":SCHEMA if a.mode=="shard" else ALL_SCHEMA,
         "submission_hold":True,"no_new_ecological_effect":True,"original_budget_stop_preserved":True}
    path=BUILD/(f"neon_seedfall_mammal_support_shard_{a.index}.json" if a.mode=="shard" else "neon_seedfall_mammal_breeding_sharded_support_20261125.json")
    if a.mode=="shard":out["shard_index"]=a.index
    try:
        if a.mode=="shard":out.update(shard(a.index))
        else:
            files=sorted(a.directory.rglob("neon_seedfall_mammal_support_shard_*.json"))
            data=[json.loads(f.read_text()) for f in files]
            req(all(x.get("schema")==SCHEMA for x in data),"SHARD_SCHEMA_MISMATCH")
            out["received_shard_statuses"]=[{"index":x.get("shard_index"),"status":x.get("status"),"reason":x.get("reason")} for x in data]
            out.update(combined(data,expected()))
    except Exception as e:
        out.update(status="STOP_SHARD_OR_COMBINE_SOURCE",ecological_effect=None,
                   error_class=type(e).__name__,reason=str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR")
    emit(path,out)
    # A STOP receipt is preserved, but the job is non-successful. The
    # aggregator uses always() and never accepts incomplete successful shards.
    return 0 if out["status"] in {"SOURCE_SUPPORT_ONLY_NO_EFFECT","ALL_32_SITES_SOURCE_SUPPORT_ONLY_NO_EFFECT"} else 2
if __name__=="__main__":raise SystemExit(main())
