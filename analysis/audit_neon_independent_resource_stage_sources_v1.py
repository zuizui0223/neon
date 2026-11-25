"""New independent sources. No further Polish session reconstruction.

Retrieve author/publisher linked public data with bounded provider APIs.
Annual Huang source: metadata and literal six-year table; no cross-year
interpolation or individual seed-fate claim. Lichti: collection inventory
only; actual dataset vs supplement explicitly distinguished.
"""
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256,md5
from io import StringIO,BytesIO
from pathlib import Path
from urllib.parse import quote,urlparse
from urllib.request import Request,urlopen
import csv,json,re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_independent_resource_stage_sources_20261125.json"
HDOI="10.5061/dryad.4qrfj6q9m"
HNAME="Masting_and_seed_fate_data_for_Castanopsis_fargesii.csv"
HFILE=758390
COLL=3306858
LIMIT=12_000_000
def req(x,code):
    if not x:raise ValueError(code)
def get(url,limit=LIMIT):
    req(urlparse(url).scheme=="https","NON_HTTPS_URL")
    with urlopen(Request(url,headers={"User-Agent":"NEON academic public-data inventory","Accept":"*/*"}),timeout=35) as response:
        b=response.read(limit+1);final=response.geturl()
    req(len(b)<=limit and urlparse(final).scheme=="https","BYTE_OR_URL_LIMIT")
    return b
def jget(url,limit=2_000_000):
    return json.loads(get(url,limit))
def dryad_api(path):
    req(path.startswith("/api/v2/"),"DRYAD_PATH_NOT_API")
    return jget("https://datadryad.org"+path)
def sha(b):return sha256(b).hexdigest()
def csv_table(b,maxrows=20000):
    s=b.decode("utf-8-sig")
    candidates=[]
    for sep in (",",";","\t"):
        v=list(csv.reader(StringIO(s,newline=""),delimiter=sep))
        if v and 1<len(v[0])<=100 and all(len(x)==len(v[0]) for x in v):
            candidates.append((sep,v))
    req(len(candidates)==1,"CSV_DIALECT_UNRESOLVED")
    sep,rows=candidates[0]
    req(len(rows)-1<=maxrows,"CSV_ROW_LIMIT")
    return sep,rows[0],rows[1:]
def huang():
    meta=dryad_api("/api/v2/datasets/"+quote("doi:"+HDOI,safe=""))
    req(str(meta.get("identifier","")).lower().removeprefix("doi:")==HDOI,"DRYAD_DOI_MISMATCH")
    title=meta.get("title","")
    req("masting" in title.lower() and "castanopsis" in title.lower(),"DRYAD_TITLE_MISMATCH")
    f=dryad_api("/api/v2/files/"+str(HFILE))
    name=f.get("path",f.get("filename",f.get("name","")))
    req(Path(str(name)).name==HNAME,"DRYAD_FILE_NAME_MISMATCH")
    size=f.get("size")
    req(type(size) is int and 0<size<5000,"ANNUAL_FILE_SIZE_DRIFT")
    raw=get("https://datadryad.org/api/v2/files/"+str(HFILE)+"/download",size)
    req(len(raw)==size,"ANNUAL_FILE_BYTE_SIZE_MISMATCH")
    # Dryad may expose digest as a scalar or dict. Verify recognized
    # provider digests; no assertion of provider validation otherwise.
    verified=[]
    digest=f.get("digest")
    alg=str(f.get("digestType",f.get("digest_type",""))).lower().replace("-","")
    for typ,val in (("sha256",sha(raw)),("md5",md5(raw).hexdigest())):
        expected=f.get(typ)
        if alg==typ and isinstance(digest,str):expected=digest
        if isinstance(digest,dict):expected=digest.get(typ,expected)
        if expected:
            req(str(expected).lower()==val,"DRYAD_PROVIDER_DIGEST_MISMATCH")
            verified.append(typ)
    sep,h,rows=csv_table(raw,20)
    # The public annual summary is tiny. Export only if six annual
    # numeric rows, with explicit 2013–2018 year field and no other text.
    out={"status":"SOURCE_BYTES_GO_SCHEMA_ONLY","doi":HDOI,"title":title,
         "file_id":HFILE,"name":name,"bytes":len(raw),"sha256":sha(raw),
         "verified_provider_digests":verified,"header":h,"data_rows":len(rows),"delimiter":repr(sep)}
    year=[i for i,x in enumerate(h) if x.strip().lower() in {"year","yr"}]
    if len(rows)==6 and len(year)==1 and {x[year[0]].strip() for x in rows}=={str(y) for y in range(2013,2019)} and all(re.fullmatch(r"-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?|NA|",v.strip()) for x in rows for v in x):
        out["literal_annual_numeric_summary"]=rows
        out["status"]="SOURCE_NUMERIC_ANNUAL_SUMMARY_GO_SEMANTICS_PENDING"
    return out
def figshare():
    root=jget(f"https://api.figshare.com/v2/collections/{COLL}")
    req(root.get("id")==COLL and "mast species composition" in root.get("title","").lower(),"COLLECTION_IDENTITY_MISMATCH")
    articles=jget(f"https://api.figshare.com/v2/collections/{COLL}/articles?page_size=100")
    req(isinstance(articles,list) and 0<len(articles)<100,"COLLECTION_ARTICLE_ROSTER_LIMIT")
    items=[];total=0
    for item in articles:
        aid=item["id"]
        req(type(aid) is int,"INVALID_ARTICLE_ID")
        art=jget(f"https://api.figshare.com/v2/articles/{aid}")
        req(art.get("id")==aid,"ARTICLE_IDENTITY_MISMATCH")
        rec={"id":aid,"title":art.get("title"),"doi":art.get("doi"),"version":art.get("version"),"files":[]}
        for f in art.get("files",[]):
            name=f.get("name","");size=f.get("size");fid=f.get("id")
            info={"id":fid,"name":name,"size":size}
            suffix=Path(name).suffix.lower()
            # Download bounded tabular files; leave documents and
            # archives as inventory, not presumed underlying seed data.
            if suffix in {".csv",".tsv",".txt",".xlsx",".xls",".r",".rdata",".rds"}:
                try:
                    req(type(fid) is int and type(size) is int and 0<size<=LIMIT and total+size<=LIMIT,"FILE_BUDGET")
                    raw=get("https://api.figshare.com/v2/file/download/"+str(fid),size)
                    total+=len(raw)
                    req(len(raw)==size,"FIGSHARE_SIZE_MISMATCH")
                    expected=f.get("computed_md5") or f.get("supplied_md5")
                    req(bool(expected) and md5(raw).hexdigest()==expected.lower(),"FIGSHARE_MD5_MISMATCH")
                    info.update(sha256=sha(raw),verified_md5=expected,verified_size=len(raw))
                    if suffix in {".csv",".tsv"}:
                        sep,h,rows=csv_table(raw)
                        info["schema"]={"header":h,"data_rows":len(rows),"delimiter":repr(sep)}
                    elif suffix==".xlsx":
                        from openpyxl import load_workbook
                        from zipfile import ZipFile
                        with ZipFile(BytesIO(raw)) as z:
                            req(sum(v.file_size for v in z.infolist())<100_000_000,"XLSX_EXPANSION_LIMIT")
                        w=load_workbook(BytesIO(raw),read_only=True,data_only=True)
                        try:info["schema"]={"sheets":[{"name":s.title,"rows_extent":s.max_row,"cols_extent":s.max_column,"header":[str(x)[:100] if x is not None else None for x in next(s.iter_rows(min_row=1,max_row=1,values_only=True),())]} for s in w.worksheets]}
                        finally:w.close()
                except Exception as e:info["status"]="FILE_OR_SCHEMA_STOP";info["error_class"]=type(e).__name__;info["reason"]=str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR"
            rec["files"].append(info)
        items.append(rec)
    return {"status":"PUBLISHER_LINKED_COLLECTION_INVENTORY_ONLY","collection_id":COLL,"title":root["title"],"articles":items,"seed_cohort_data_verified":False}
def main():
    out={"schema":"neon.independent.resource_stage.source_inventory.v1","poland_session_lane_closed":True,"submission_hold":True,"no_new_individual_effect":True}
    for k,fn in (("huang_dryad",huang),("lichti_figshare",figshare)):
        try:out[k]=fn()
        except Exception as e:out[k]={"status":"SOURCE_STOP","error_class":type(e).__name__,"reason":str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR"}
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
