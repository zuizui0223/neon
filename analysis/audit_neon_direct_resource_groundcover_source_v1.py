"""Public Figshare source audit; inspect metadata, checksums and schemas only."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import md5, sha256
from io import BytesIO, StringIO
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import csv
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/neon_direct_resource_groundcover_source_20261124.json"
SOURCES = {
    15029247: ("pulsed resources", "10.1111/oik.09551", "primary_measured_food_resource"),
    14488626: ("microhabitat selection", "10.1002/eap.2443", "secondary_groundcover_inventory_only"),
}
MAX_BYTES = 100_000_000
MAX_META = 2_000_000
MAX_FILES = 80
SUFFIXES = {".csv",".tsv",".txt",".xls",".xlsx",".rds",".rdata",".rda",".zip",".parquet"}
HOSTS = {"figshare.com","api.figshare.com","ndownloader.figshare.com","s3-eu-west-1.amazonaws.com"}

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def safe_provider(url):
    if not isinstance(url,str):
        return False
    u=urlsplit(url)
    return u.scheme=="https" and u.hostname in HOSTS and not u.username and not u.password and not u.fragment

def bounded(url,limit):
    require(safe_provider(url),"UNAPPROVED_PROVIDER_URL")
    req=Request(url,headers={"User-Agent":"NEON-public-resource-source-audit/1.0","Accept":"*/*"})
    with urlopen(req,timeout=90) as response:
        require(response.status==200,"NON200_SOURCE_RESPONSE")
        raw=response.read(limit+1)
    require(len(raw)<=limit,"SOURCE_BYTE_BUDGET_EXCEEDED")
    return raw

def inventory(meta,ident):
    title_key,paper,role=SOURCES[ident]
    require(isinstance(meta,dict) and meta.get("id")==ident,"ARTICLE_ID_MISMATCH")
    title=meta.get("title")
    require(isinstance(title,str) and title_key in title.lower(),"ARTICLE_TITLE_MISMATCH")
    doi=meta.get("doi")
    require(isinstance(doi,str) and re.fullmatch(r"10\.6084/m9\.figshare\."+str(ident)+r"(?:\.v\d+)?",doi,re.I),"ARTICLE_DOI_MISMATCH")
    version=meta.get("version")
    require(type(version) is int and version>=1,"PUBLIC_VERSION_UNKNOWN")
    files=meta.get("files")
    require(isinstance(files,list) and 0<len(files)<=MAX_FILES,"INVALID_FILE_INVENTORY")
    ids=set();names=set(); rows=[]
    for f in files:
        fid,name,size=f.get("id"),f.get("name"),f.get("size")
        require(type(fid) is int and fid>0 and fid not in ids,"DUPLICATE_FILE_ID")
        require(isinstance(name,str) and 0<len(name)<=256 and "/" not in name and "\\" not in name and name not in names,"INVALID_OR_DUPLICATE_FILENAME")
        require(type(size) is int and size>=0,"INVALID_FILE_SIZE")
        check=f.get("computed_md5") or f.get("supplied_md5")
        require(check is None or (isinstance(check,str) and re.fullmatch("[0-9a-fA-F]{32}",check)),"INVALID_MD5")
        href=f.get("download_url")
        if href is not None:
            require(safe_provider(href),"UNAPPROVED_FILE_URL")
        ids.add(fid);names.add(name)
        rows.append({"file_id":fid,"name":name,"size":size,"md5":check.lower() if check else None,
                     "href":href,"candidate_data_file":Path(name).suffix.lower() in SUFFIXES})
    return title,doi,version,paper,role,rows

def plausible_header(row):
    # Avoid echoing headerless numerical or individual-record data.
    return (isinstance(row,list) and 1<=len(row)<=250
            and all(isinstance(x,str) and len(x)<=100 for x in row)
            and sum(bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ .()/%%+\-]*",x.strip())) for x in row)>=max(1,len(row)-1)
            and not any(re.fullmatch(r"[A-Fa-f0-9]{12,}",x.strip()) for x in row))

def schema(raw,name):
    suffix=Path(name).suffix.lower()
    if suffix in {".csv",".tsv"}:
        try:
            row=next(csv.reader(StringIO(raw.decode("utf-8-sig"),newline=""),
                                delimiter="\t" if suffix==".tsv" else ","))
        except (UnicodeError,StopIteration,csv.Error):
            return {"schema_status":"HEADER_NOT_READABLE"}
        if not plausible_header(row):
            return {"schema_status":"HEADER_NOT_CONFIDENT_NO_VALUES_EXPORTED","field_count":len(row)}
        return {"schema_status":"CANDIDATE_FIRST_HEADER_ROW_ONLY","field_count":len(row),
                "headers":row,"empty_headers":sum(not x.strip() for x in row),
                "duplicate_nonempty_header_count":sum(n-1 for x,n in Counter(row).items() if x.strip() and n>1)}
    if suffix==".xlsx":
        from openpyxl import load_workbook
        book=load_workbook(BytesIO(raw),read_only=True,data_only=False)
        try:
            return {"schema_status":"WORKBOOK_SHEET_NAMES_DIMENSIONS_ONLY",
                    "worksheets":[{"name":s.title,"rows":s.max_row,"columns":s.max_column} for s in book.worksheets]}
        finally:
            book.close()
    if suffix==".zip":
        with zipfile.ZipFile(BytesIO(raw)) as z:
            members=z.infolist()
            require(len(members)<=2000,"ZIP_MEMBER_COUNT_LIMIT")
            return {"schema_status":"ZIP_CENTRAL_DIRECTORY_ONLY_NO_EXTRACTION",
                    "members":[{"name":x.filename,"uncompressed_bytes":x.file_size} for x in members]}
    return {"schema_status":"FORMAT_NOT_PARSED_BYTES_VERIFIED_ONLY"}

def audit_one(ident,fetch=bounded):
    meta_raw=fetch("https://api.figshare.com/v2/articles/"+str(ident),MAX_META)
    title,doi,version,paper,role,rows=inventory(json.loads(meta_raw),ident)
    out={"article_id":ident,"article_title":title,"provider_doi":doi,"public_version":version,
         "paper_doi":paper,"role":role,"metadata_sha256":sha256(meta_raw).hexdigest(),
         "files":[{k:v for k,v in f.items() if k!="href"} for f in rows]}
    cand=[f for f in rows if f["candidate_data_file"]]
    total=sum(f["size"] for f in cand)
    out["candidate_total_bytes"]=total
    if not cand or total>MAX_BYTES or any(not f["md5"] or not f["href"] for f in cand):
        out.update(status="STOP_NO_COMPLETE_BOUNDED_CHECKSUM_SOURCE",schema_receipts=[])
        return out
    receipts=[]
    for f in cand:
        try:
            raw=fetch(f["href"],f["size"])
            require(len(raw)==f["size"],"ORIGINAL_FILE_SIZE_MISMATCH")
            require(md5(raw).hexdigest()==f["md5"],"ORIGINAL_MD5_MISMATCH")
            info={"file_id":f["file_id"],"name":f["name"],"verified_size":len(raw),"verified_md5":f["md5"],"sha256":sha256(raw).hexdigest()}
            try:
                info.update(schema(raw,f["name"]))
            except Exception as exc:
                info.update(schema_status="SCHEMA_PARSE_STOP",schema_error_class=type(exc).__name__)
            receipts.append(info)
        except Exception as exc:
            receipts.append({"file_id":f["file_id"],"name":f["name"],"status":"FILE_SOURCE_STOP","error_class":type(exc).__name__})
    out["schema_receipts"]=receipts
    out["status"]="CHECKSUM_SOURCE_GO_SCHEMA_ONLY" if all("sha256" in q for q in receipts) else "STOP_INCOMPLETE_ORIGINAL_BYTES"
    return out

def main():
    result={}
    for ident in SOURCES:
        try:
            result[str(ident)]=audit_one(ident)
        except Exception as exc:
            result[str(ident)]={"article_id":ident,"status":"STOP_PROVIDER_METADATA_OR_IDENTITY","error_class":type(exc).__name__}
    out={"schema":"neon.external.direct_measured_resource_groundcover.source_inventory.v1",
         "source_results":result,"primary_article":15029247,"secondary_inventory_only":14488626,
         "biological_response_rows_not_analyzed":True,"no_ecological_effects_fitted":True,
         "source_GO_does_not_establish_patch_time_or_ID_join":True,"no_NEON_reanalysis":True,
         "manuscript_SUBMISSION_HOLD":True,"retrieved_utc":datetime.now(timezone.utc).isoformat()}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
