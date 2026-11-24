"""Bounded source inventory for independently measured consumer pressure.

Only author-linked public OSF project and publisher-linked PMC supplement.
No private login, alternative mirrors, source-block rescue or effects.
OSF provider metadata hashes checked where present; SHA256 recorded otherwise.
"""
from collections import Counter
from datetime import datetime,timezone
from hashlib import md5,sha256
from io import BytesIO,StringIO
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request,urlopen
import csv,json,re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_consumer_pressure_source_20261125.json"
OSF="56m2n"
PMC="https://pmc.ncbi.nlm.nih.gov/articles/instance/13635484/bin/ECE3-16-e74453-s002.xlsx"
LIMIT=40_000_000
SUFFIXES={".csv",".tsv",".xlsx",".xls",".txt",".r",".rds",".rdata",".sav",".zip"}
def req(x,code):
    if not x:raise ValueError(code)
def get(url,limit):
    req(urlparse(url).scheme=="https","NON_HTTPS_URL")
    with urlopen(Request(url,headers={"User-Agent":"NEON academic source inventory"}),timeout=45) as f:
        data=f.read(limit+1);final=f.geturl()
    req(len(data)<=limit and urlparse(final).scheme=="https","BYTE_OR_URL_LIMIT")
    return data,final
def api(url):
    req(urlparse(url).hostname=="api.osf.io" and urlparse(url).path.startswith("/v2/"),"UNVERIFIED_OSF_API_URL")
    raw,_=get(url,2_000_000)
    return json.loads(raw)
def schema(raw,name):
    suffix=Path(name).suffix.lower()
    if suffix==".xlsx":
        from openpyxl import load_workbook
        req(raw[:2]==b"PK","NOT_XLSX_BYTES")
        from zipfile import ZipFile
        with ZipFile(BytesIO(raw)) as z:
            req(sum(i.file_size for i in z.infolist())<=100_000_000,"UNCOMPRESSED_LIMIT")
        book=load_workbook(BytesIO(raw),read_only=True,data_only=True)
        try:
            return {"sheets":[{"name":s.title,"rows_extent":s.max_row,"cols_extent":s.max_column,
                    "first_row_candidate_headers":[str(v)[:160] if isinstance(v,str) and len(v)<=160 else None for v in next(s.iter_rows(min_row=1,max_row=1,values_only=True),())]}
                    for s in book.worksheets]}
        finally:book.close()
    if suffix in {".csv",".tsv"}:
        try:txt=raw.decode("utf-8-sig")
        except UnicodeDecodeError:txt=raw.decode("latin1")
        reader=csv.reader(StringIO(txt,newline=""),delimiter="\t" if suffix==".tsv" else ",")
        first=next(reader)
        req(0<len(first)<=1000,"HEADER_LIMIT")
        valid=all(not s.strip() or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ ./()%-]*",s.strip()) for s in first)
        widths=Counter(len(r) for r in reader)
        return {"candidate_headers":first if valid else None,"row_count":sum(widths.values()),"row_width_counts":dict(widths)}
    return {"status":"BYTES_ONLY"}
def pages(url):
    seen=set()
    while url:
        req(url not in seen and len(seen)<30,"OSF_PAGINATION_LIMIT");seen.add(url)
        obj=api(url)
        req(isinstance(obj.get("data"),list),"OSF_LIST_SCHEMA")
        yield from obj["data"]
        url=obj.get("links",{}).get("next")
def osf():
    root=api(f"https://api.osf.io/v2/nodes/{OSF}/")["data"]
    req(root["id"]==OSF and root["attributes"].get("public") is True,"OSF_PUBLIC_IDENTITY")
    title=root["attributes"]["title"]
    req("scatter" in title.lower() and "burial" in title.lower(),"OSF_TITLE_MISMATCH")
    folders=[f"https://api.osf.io/v2/nodes/{OSF}/files/osfstorage/"];files=[];seen=set()
    while folders:
        u=folders.pop(0)
        req(u not in seen and len(seen)<100,"OSF_FOLDER_LIMIT");seen.add(u)
        for f in pages(u):
            a=f["attributes"]
            if a["kind"]=="folder":
                link=f["relationships"]["files"]["links"]["related"]
                folders.append(link["href"] if isinstance(link,dict) else link)
            elif a["kind"]=="file":
                files.append(f)
            else:raise ValueError("OSF_UNKNOWN_FILE_KIND")
            req(len(files)<200,"OSF_FILE_LIMIT")
    out={"title":title,"node_id":OSF,"files":[]}
    candidates=[f for f in files if Path(f["attributes"]["name"]).suffix.lower() in SUFFIXES]
    req(candidates and all(type(f["attributes"].get("size")) is int and f["attributes"]["size"]>=0 for f in candidates),"NO_BOUNDED_DATA_FILES")
    req(sum(f["attributes"]["size"] for f in candidates)<=LIMIT,"OSF_TOTAL_BUDGET")
    for f in files:
        a=f["attributes"];name=a["name"];size=a.get("size");hashes=a.get("extra",{}).get("hashes",{})
        rec={"file_id":f["id"],"name":name,"size":size,"provider_hashes":hashes,"modified":a.get("date_modified")}
        if f in candidates:
            try:
                url=f["links"]["download"]
                req(urlparse(url).hostname in {"osf.io","files.osf.io","api.osf.io"},"OSF_DOWNLOAD_LINK_HOST")
                raw,_=get(url,size)
                req(len(raw)==size,"OSF_SIZE_MISMATCH")
                m=md5(raw).hexdigest();s=sha256(raw).hexdigest()
                for alg,got in (("md5",m),("sha256",s)):
                    if hashes.get(alg):req(hashes[alg].lower()==got,"OSF_PROVIDER_HASH_MISMATCH")
                rec.update(sha256=s,verified_size=len(raw),provider_digest_available=bool(hashes.get("md5") or hashes.get("sha256")))
                try:rec["schema"]=schema(raw,name)
                except Exception as e:rec["schema_error"]=type(e).__name__
            except Exception as e:rec.update(status="FILE_STOP",error_class=type(e).__name__)
        out["files"].append(rec)
    out["status"]="SOURCE_BYTES_GO_SCHEMA_ONLY" if all("sha256" in v for v in out["files"] if Path(v["name"]).suffix.lower() in SUFFIXES) else "STOP_PARTIAL_FILES"
    return out
def qinling():
    raw,final=get(PMC,5_000_000)
    req(raw[:2]==b"PK","PUBLISHER_ATTACHMENT_NOT_XLSX")
    return {"status":"SOURCE_BYTES_GO_SCHEMA_ONLY","source_url":PMC,"bytes":len(raw),
            "sha256":sha256(raw).hexdigest(),"provider_hash_not_published":True,
            "schema":schema(raw,"ECE3-16-e74453-s002.xlsx"),
            "autumn_2016_2021_vs_spring_2022_2024_confounded_with_period":True}
def main():
    out={"schema":"neon.consumer_pressure.source_inventory.v1","no_effect_fitted":True,"submission_hold":True}
    for key,fn in (("poland_osf",osf),("qinling_publisher",qinling)):
        try:out[key]=fn()
        except Exception as e:out[key]={"status":"SOURCE_STOP","error_class":type(e).__name__,
             "reason":str(e) if type(e) is ValueError and re.fullmatch(r"[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR"}
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
