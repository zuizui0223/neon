"""One bounded independent, paper-linked ecological source inventory.
Pruvot et al. 2024, One Earth, doi:10.1016/j.oneear.2023.11.003.
No code execution from the archive, no response analysis or inferred station joins.
"""
from collections import Counter
from datetime import datetime,timezone
from hashlib import md5,sha256
from pathlib import Path,PurePosixPath
from urllib.parse import urlparse
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from io import BytesIO,StringIO
from zipfile import ZipFile
import csv,json,re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_cambodia_independent_source_20261125.json"
RECORD=10042694
DOI="10.5281/zenodo.10042694"
API=f"https://zenodo.org/api/records/{RECORD}"
BYTE_CAP=40_000_000
EXPANSION_CAP=100_000_000
TABLE={".csv",".tsv",".txt",".xlsx",".xls",".rds",".rdata",".rda"}
ARCHIVE={".zip"}
CODE={".r",".rmd",".md",".pdf"}
def req(v,code):
    if not v:raise ValueError(code)
def get(url,cap):
    u=urlparse(url)
    req(u.scheme=="https" and u.hostname in {"zenodo.org","www.zenodo.org"},"UNVERIFIED_PROVIDER_URL")
    with urlopen(Request(url,headers={"User-Agent":"NEON academic source inventory","Accept":"*/*"}),timeout=60) as f:
        raw=f.read(cap+1);final=urlparse(f.geturl())
    req(final.scheme=="https" and len(raw)<=cap,"SOURCE_BUDGET_OR_REDIRECT")
    return raw
def verify(raw,size,checksum):
    req(type(size) is int and len(raw)==size,"FILE_SIZE_MISMATCH")
    req(isinstance(checksum,str) and re.fullmatch(r"md5:[0-9a-fA-F]{32}",checksum),"PROVIDER_MD5_MISSING")
    req(md5(raw).hexdigest()==checksum[4:].lower(),"PROVIDER_MD5_MISMATCH")
    return {"bytes":len(raw),"md5":md5(raw).hexdigest(),"sha256":sha256(raw).hexdigest()}
def tabular(name,raw):
    # No source row values or coordinates exported; only schema/shape.
    ext=Path(name).suffix.lower()
    if ext in {".csv",".tsv",".txt"}:
        try:s=raw.decode("utf-8-sig")
        except UnicodeDecodeError:s=raw.decode("latin1")
        choices=[]
        for sep in (",",";","\t"):
            rr=list(csv.reader(StringIO(s,newline=""),delimiter=sep))
            if rr and 1<len(rr[0])<=500 and all(len(x)==len(rr[0]) for x in rr if any(x)):
                choices.append((sep,rr))
        if len(choices)!=1:return {"status":"UNRESOLVED_TABLE_DIALECT"}
        sep,rr=choices[0];header=rr[0]
        return {"status":"TABLE_SCHEMA_ONLY","delimiter":repr(sep),"header":header,"nonblank_data_rows":sum(any(x) for x in rr[1:])}
    if ext==".xlsx":
        from openpyxl import load_workbook
        with ZipFile(BytesIO(raw)) as z:
            req(sum(x.file_size for x in z.infolist())<=EXPANSION_CAP,"XLSX_EXPANSION_LIMIT")
        w=load_workbook(BytesIO(raw),read_only=True,data_only=True)
        try:
            return {"status":"WORKBOOK_SCHEMA_ONLY","sheets":[{"name":s.title,"rows_extent":s.max_row,"cols_extent":s.max_column,"header":[str(x)[:160] if x is not None else None for x in next(s.iter_rows(min_row=1,max_row=1,values_only=True),())]} for s in w.worksheets]}
        finally:w.close()
    return {"status":"BYTES_ONLY_NOT_EXECUTED"}
def archive(raw):
    with ZipFile(BytesIO(raw)) as z:
        members=z.infolist()
        req(len(members)<=1000 and sum(x.file_size for x in members)<=EXPANSION_CAP,"ZIP_EXPANSION_LIMIT")
        out=[]
        for x in members:
            path=PurePosixPath(x.filename)
            req(not path.is_absolute() and ".." not in path.parts,"ZIP_UNSAFE_MEMBER")
            rec={"name":x.filename,"bytes":x.file_size}
            # Exclude infection/test-focused data from ecological inspection.
            if not x.is_dir() and Path(x.filename).suffix.lower() in TABLE and not re.search(r"pathogen|virus|pcr|serolog|infection|rna|lepto|hanta",x.filename,re.I):
                if x.file_size<=10_000_000:
                    data=z.read(x);rec["sha256"]=sha256(data).hexdigest()
                    rec["schema"]=tabular(x.filename,data)
                else:rec["status"]="TABLE_SIZE_LIMIT"
            out.append(rec)
        return out
def run():
    payload=get(API,4_000_000);obj=json.loads(payload)
    md=obj.get("metadata",{})
    req(obj.get("id")==RECORD and DOI in {obj.get("doi"),obj.get("conceptdoi"),md.get("doi")},"RECORD_ID_DOI_MISMATCH")
    title=str(md.get("title",""));creators=[str(x.get("name","")) for x in md.get("creators",[])]
    # Do not accept a different publication's collection merely because
    # its species names or size look suitable.
    req(any("pruvot" in x.lower() for x in creators) and any(w in title.lower() for w in ("cambodia","deforestation","small mammal","rodent")),"AUTHOR_TITLE_IDENTITY_UNRESOLVED")
    files=obj.get("files",[]);req(isinstance(files,list) and 0<len(files)<=100,"FILE_ROSTER_INVALID")
    inventory=[];total=0
    for f in files:
        name=f.get("key");size=f.get("size");digest=f.get("checksum")
        req(isinstance(name,str) and type(size) is int and size>=0,"FILE_METADATA_INVALID")
        rec={"name":name,"size":size,"checksum":digest}
        ext=Path(name).suffix.lower()
        if ext in TABLE|ARCHIVE and not re.search(r"pathogen|virus|pcr|serolog|infection|rna|lepto|hanta",name,re.I):
            if size>0 and total+size<=BYTE_CAP:
                try:
                    links=f.get("links",{})
                    url=links.get("content") or links.get("self")
                    req(isinstance(url,str),"NO_PROVIDER_DOWNLOAD_LINK")
                    raw=get(url,size);total+=len(raw)
                    rec["verified"]=verify(raw,size,digest)
                    if ext in ARCHIVE:rec["members"]=archive(raw)
                    else:rec["schema"]=tabular(name,raw)
                except Exception as e:
                    rec.update(status="FILE_OR_SCHEMA_STOP",error_class=type(e).__name__,reason=str(e) if type(e) is ValueError and re.fullmatch(r"[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR")
                    if isinstance(e,HTTPError):rec["http_status"]=e.code
            else:rec["status"]="SOURCE_FILE_BUDGET_STOP"
        else:rec["status"]="INVENTORY_ONLY"
        inventory.append(rec)
    return {"status":"PAPER_LINKED_RECORD_INVENTORY","record_id":RECORD,"doi":DOI,"title":title,"metadata_sha256":sha256(payload).hexdigest(),"files":inventory,"verified_file_count":sum("verified" in f for f in inventory),"downloaded_bytes":total,
        "verified_crossseason_individual_station_vegetation_join":False,"ecological_effect":None}
def main():
    out={"schema":"neon.cambodia.independent.source.v1","submission_hold":True,"no_new_effect":True}
    try:out.update(run())
    except Exception as e:
        out.update(status="SOURCE_STOP",error_class=type(e).__name__,reason=str(e) if type(e) is ValueError and re.fullmatch(r"[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR")
        if isinstance(e,HTTPError):out["http_status"]=e.code
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
