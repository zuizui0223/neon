"""Source-only audit of the 2025 Holt paper's public Figshare v2 archive.

The published study concerns August capture abundance/body weight, not a
seasonal or dispersal experiment. Inspect checksums, archive membership and
CSV headers/counts only. No capture or plant response effects are opened.
"""
from collections import Counter
from datetime import datetime,timezone
from hashlib import md5,sha256
from io import BytesIO,StringIO
from pathlib import Path
from zipfile import ZipFile,is_zipfile
import csv,json,re
from analysis.audit_neon_direct_resource_groundcover_source_v1 import bounded,require,safe_provider
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_holt_2025_capture_source_20261124.json"
ARTICLE=27152484
VERSION=2
BUDGET=100_000_000
SUFFIX={".zip",".csv",".tsv",".xlsx",".xls",".rds",".rdata",".rda",".txt",".parquet"}
def csv_schema(raw,name):
    text=raw.decode("utf-8-sig")
    it=csv.reader(StringIO(text,newline=""),delimiter="\t" if name.lower().endswith(".tsv") else ",")
    h=next(it)
    require(0<len(h)<=5000 and all(len(x)<=160 for x in h),"INVALID_COLUMN_HEADER")
    widths=Counter();year_fields={i:Counter() for i,x in enumerate(h) if x.strip().lower() in {"year","yr","captureyear","capture_year"}}
    for row in it:
        widths[len(row)]+=1
        if len(row)!=len(h):continue
        for i,c in year_fields.items():
            x=row[i].strip()
            c[x if re.fullmatch(r"(19|20)\d{2}",x) else "unresolved"]+=1
    return {"columns":h,"rows":sum(widths.values()),"row_width_counts":dict(widths),
            "year_counts_by_column_index":{str(i):dict(sorted(c.items())) for i,c in year_fields.items()}}
def inspect_bytes(raw,name):
    if is_zipfile(BytesIO(raw)):
        with ZipFile(BytesIO(raw)) as z:
            info=z.infolist()
            require(len(info)<=2000 and len({x.filename for x in info})==len(info),"ZIP_MEMBER_LIMIT_OR_DUPLICATE")
            require(sum(x.file_size for x in info)<=BUDGET,"UNCOMPRESSED_BUDGET")
            result={"members":[{"name":x.filename,"size":x.file_size} for x in info],"csv_schema":{}}
            for x in info:
                if x.is_dir() or Path(x.filename).suffix.lower() not in {".csv",".tsv"}:continue
                try:result["csv_schema"][x.filename]=csv_schema(z.read(x),x.filename)
                except (UnicodeError,StopIteration,csv.Error,ValueError) as e:result["csv_schema"][x.filename]={"status":"SCHEMA_PARSE_STOP","error_class":type(e).__name__}
            return result
    if Path(name).suffix.lower() in {".csv",".tsv"}:return {"csv_schema":csv_schema(raw,name)}
    return {"schema_status":"OTHER_FORMAT_BYTES_VERIFIED_ONLY"}
def audit(fetch=bounded):
    meta_raw=fetch(f"https://api.figshare.com/v2/articles/{ARTICLE}/versions/{VERSION}",2_000_000)
    x=json.loads(meta_raw)
    require(x.get("id")==ARTICLE and x.get("version")==VERSION,"VERSION_ID_MISMATCH")
    require("coupled effects of forest growth and climate change" in x.get("title","").lower(),"TITLE_MISMATCH")
    require(x.get("doi","").lower()==f"10.6084/m9.figshare.{ARTICLE}.v{VERSION}","DOI_MISMATCH")
    files=x.get("files")
    require(isinstance(files,list) and 0<len(files)<=80,"FILE_INVENTORY_LIMIT")
    out={"article":x["title"],"doi":x["doi"],"version":VERSION,"metadata_sha256":sha256(meta_raw).hexdigest(),"files":[]}
    ids=set();names=set();cand=[]
    for f in files:
        fid,name,size=f["id"],f["name"],f["size"]
        require(type(fid) is int and fid>0 and fid not in ids,"FILE_ID_DUPLICATE")
        require(isinstance(name,str) and 0<len(name)<=256 and "/" not in name and "\\" not in name and name not in names,"BAD_FILE_NAME")
        require(type(size) is int and size>=0,"BAD_FILE_SIZE")
        digest=f.get("computed_md5") or f.get("supplied_md5")
        ids.add(fid);names.add(name)
        rec={"id":fid,"name":name,"size":size,"provider_md5":digest}
        out["files"].append(rec)
        if Path(name).suffix.lower() in SUFFIX:cand.append((f,rec))
    require(cand and sum(f["size"] for f,_ in cand)<=BUDGET,"NO_BOUNDED_CANDIDATE_ARCHIVE")
    require(all(isinstance(rec["provider_md5"],str) and re.fullmatch("[a-fA-F0-9]{32}",rec["provider_md5"]) and safe_provider(f.get("download_url")) for f,rec in cand),"MISSING_CHECKSUM_OR_PROVIDER_URL")
    for f,rec in cand:
        try:
            raw=fetch(f["download_url"],f["size"])
            require(len(raw)==f["size"] and md5(raw).hexdigest()==rec["provider_md5"].lower(),"SOURCE_BYTES_MISMATCH")
            rec["sha256"]=sha256(raw).hexdigest()
            rec["verified_size"]=len(raw)
            try:rec["schema"]=inspect_bytes(raw,f["name"])
            except Exception as e:rec["schema"]={"status":"SCHEMA_STOP","error_class":type(e).__name__}
        except Exception as e:rec["status"]="SOURCE_STOP";rec["error_class"]=type(e).__name__
    out["status"]="CHECKSUM_SOURCE_GO_SCHEMA_ONLY" if all("sha256" in rec for _,rec in cand) else "STOP_INCOMPLETE_SOURCE_BYTES"
    return out
def main():
    try:out=audit()
    except Exception as e:out={"status":"STOP_PROVIDER_OR_SOURCE","error_class":type(e).__name__}
    out.update(schema="neon.holt.2025.capture_source.v1",retrieved_utc=datetime.now(timezone.utc).isoformat(),
               no_ecological_effect_fitted=True,same_forest_not_independent_replication=True,
               historical_2022_date_code_stop_unchanged=True,submission_hold=True)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
