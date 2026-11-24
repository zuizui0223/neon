"""Two pinned public experimental seed-fate archives: metadata/headers only."""
from datetime import datetime,timezone
from hashlib import md5,sha256
from pathlib import Path
from io import BytesIO,StringIO
from zipfile import ZipFile,is_zipfile
import csv,json,re
from analysis.audit_neon_direct_resource_groundcover_source_v1 import bounded,safe_provider
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_direct_seed_fate_stage_sources_20261124.json"
SOURCES={
    3189775:{"version":1,"keywords":("indirect","seed"),"paper":"10.1111/1365-2656.12542","role":"primary_mixed_seed_neighbourhood"},
    1256359:{"version":None,"keywords":("scatter","hoarding"),"paper":"10.1371/journal.pone.0124932","role":"secondary_life_stage_inventory_only"},
}
MAX_BYTES=100_000_000
MAX_METADATA=2_000_000
SUFFIXES={".csv",".tsv",".txt",".xls",".xlsx",".rds",".rdata",".rda",".zip",".parquet"}
def require(ok,code):
    if not ok:raise ValueError(code)
def metadata(raw,ident,expected):
    obj=json.loads(raw)
    require(isinstance(obj,dict) and obj.get("id")==ident,"ARTICLE_ID")
    title=obj.get("title","")
    require(isinstance(title,str) and all(k in title.lower() for k in expected["keywords"]),"ARTICLE_TITLE")
    version=obj.get("version")
    require(type(version) is int and version>=1 and (expected["version"] is None or version==expected["version"]),"ARTICLE_VERSION")
    doi=obj.get("doi","")
    require(isinstance(doi,str) and doi.lower() in {f"10.6084/m9.figshare.{ident}",f"10.6084/m9.figshare.{ident}.v{version}"},"ARTICLE_DOI")
    files=obj.get("files")
    require(isinstance(files,list) and 0<len(files)<=80,"FILE_COUNT")
    seen_id=set();seen_name=set();out=[]
    for f in files:
        fid,name,size=f.get("id"),f.get("name"),f.get("size")
        require(type(fid) is int and fid>0 and fid not in seen_id,"FILE_ID")
        require(isinstance(name,str) and 0<len(name)<=256 and "/" not in name and "\\" not in name and name not in seen_name,"FILE_NAME")
        require(type(size) is int and size>=0,"FILE_SIZE")
        checksum=f.get("computed_md5") or f.get("supplied_md5")
        require(checksum is None or isinstance(checksum,str) and re.fullmatch("[a-fA-F0-9]{32}",checksum),"FILE_MD5")
        seen_id.add(fid);seen_name.add(name)
        out.append({"id":fid,"name":name,"size":size,"md5":checksum.lower() if checksum else None,"href":f.get("download_url"),"candidate":Path(name).suffix.lower() in SUFFIXES})
    return obj,version,out

def header(raw,name):
    try:txt=raw.decode("utf-8-sig")
    except UnicodeDecodeError:txt=raw.decode("latin1")
    reader=csv.reader(StringIO(txt,newline=""),delimiter="\t" if name.lower().endswith(".tsv") else ",")
    row=next(reader)
    require(0<len(row)<=500 and all(len(v)<=200 for v in row),"HEADER_BOUNDS")
    # Report candidate column labels only when all nonblank cells look like
    # identifiers or human-readable header text. Headerless raw values redacted.
    valid=all(not v.strip() or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ .()/\-:%?+]*",v.strip()) for v in row)
    return {"column_count":len(row),"candidate_headers":row if valid else None,
            "header_not_confirmed_as_semantic_definition":True}
def schema(raw,name):
    suffix=Path(name).suffix.lower()
    if suffix==".zip" and is_zipfile(BytesIO(raw)):
        with ZipFile(BytesIO(raw)) as z:
            info=z.infolist()
            require(len(info)<=2000 and len({i.filename for i in info})==len(info),"ARCHIVE_MEMBER_GUARD")
            require(sum(i.file_size for i in info)<=MAX_BYTES,"ARCHIVE_UNCOMPRESSED_LIMIT")
            members=[]
            for i in info:
                item={"name":i.filename,"size":i.file_size}
                if not i.is_dir() and Path(i.filename).suffix.lower() in {".csv",".tsv",".xlsx",".xls"}:
                    try:item["schema"]=schema(z.read(i),i.filename)
                    except Exception as e:item["schema_stop"]=type(e).__name__
                members.append(item)
            return {"members":members}
    if suffix in {".csv",".tsv"}:return header(raw,name)
    if suffix==".xlsx":
        from openpyxl import load_workbook
        book=load_workbook(BytesIO(raw),read_only=True,data_only=False)
        try:
            sheets=[]
            for s in book.worksheets:
                first=next(s.iter_rows(min_row=1,max_row=1,values_only=True),())
                valid=all(v is None or isinstance(v,str) and len(v)<=200 and not v.startswith("=") and bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ .()/\-:%?+]*",v.strip())) for v in first)
                sheets.append({"sheet":s.title,"rows":s.max_row,"columns":s.max_column,"candidate_headers":list(first) if valid else None})
            return {"sheets":sheets}
        finally:book.close()
    if suffix==".xls":
        import xlrd
        book=xlrd.open_workbook(file_contents=raw,on_demand=True)
        try:
            sheets=[]
            for s in book.sheets():
                first=s.row_values(0) if s.nrows else []
                valid=all(isinstance(v,str) and len(v)<=200 and (not v.strip() or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ .()/\-:%?+]*",v.strip())) for v in first)
                sheets.append({"sheet":s.name,"rows":s.nrows,"columns":s.ncols,"candidate_headers":first if valid else None})
            return {"sheets":sheets}
        finally:book.release_resources()
    return {"status":"BYTES_ONLY_SCHEMA_NOT_PARSED"}
def audit(ident,expected,fetch=bounded):
    base=f"https://api.figshare.com/v2/articles/{ident}"
    url=base+(f"/versions/{expected['version']}" if expected["version"] is not None else "")
    raw=fetch(url,MAX_METADATA)
    obj,version,files=metadata(raw,ident,expected)
    if expected["version"] is None:
        # Version-specific refetch must confirm exactly the same DOI and file roster.
        pinned=fetch(base+f"/versions/{version}",MAX_METADATA)
        obj2,version2,files2=metadata(pinned,ident,{**expected,"version":version})
        require(version2==version and [(f["id"],f["name"],f["size"],f["md5"]) for f in files]==[(f["id"],f["name"],f["size"],f["md5"]) for f in files2],"PUBLIC_VERSION_ROSTER_DRIFT")
        raw,obj,files=pinned,obj2,files2
    result={"article_id":ident,"article_title":obj["title"],"doi":obj["doi"],"version":version,"paper":expected["paper"],"role":expected["role"],"metadata_sha256":sha256(raw).hexdigest(),"files":[]}
    candidates=[f for f in files if f["candidate"]]
    for f in files:result["files"].append({k:v for k,v in f.items() if k!="href"})
    if not candidates or sum(f["size"] for f in candidates)>MAX_BYTES or any(not f["md5"] or not safe_provider(f["href"]) for f in candidates):
        return {**result,"status":"STOP_NO_BOUNDED_CHECKSUM_SOURCE"}
    receipts=[]
    for f in candidates:
        row={"file_id":f["id"],"name":f["name"]}
        try:
            raw=fetch(f["href"],f["size"])
            require(len(raw)==f["size"] and md5(raw).hexdigest()==f["md5"],"SOURCE_BYTES_DRIFT")
            row.update(verified_size=len(raw),verified_md5=f["md5"],sha256=sha256(raw).hexdigest())
            try:row["schema"]=schema(raw,f["name"])
            except Exception as e:row["schema_stop"]=type(e).__name__
        except Exception as e:row.update(status="FILE_SOURCE_STOP",error_class=type(e).__name__)
        receipts.append(row)
    return {**result,"status":"CHECKSUM_SOURCE_GO_SCHEMA_ONLY" if all("sha256" in x for x in receipts) else "STOP_INCOMPLETE_SOURCE_BYTES","source_receipts":receipts}
def main():
    out={"schema":"neon.direct_seed_fate_stage_sources.v1","source_results":{},"no_biological_effect_fitted":True,"no_seasonal_effect_estimated":True,"Holt_annual_forecast_lane_closed":True,"submission_hold":True}
    for ident,expected in SOURCES.items():
        try:out["source_results"][str(ident)]=audit(ident,expected)
        except Exception as e:out["source_results"][str(ident)]={"status":"STOP_METADATA_OR_PROVIDER","error_class":type(e).__name__}
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
