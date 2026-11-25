"""V24: independently measured early seed fate and subsequent emergence.
OSF source-only inventory, no biological outcome counts or fit.
"""
import csv,hashlib,io,json,pathlib,re,urllib.request,urllib.parse
NODE="r9cmj"
ROOT="https://api.osf.io/v2"
CAP=15_000_000
def read(url,cap=CAP):
    if urllib.parse.urlparse(url).scheme!="https":raise ValueError("non_https")
    req=urllib.request.Request(url,headers={"User-Agent":"NEON ecological source audit/1","Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=30) as r:b=r.read(cap+1)
    if len(b)>cap:raise ValueError("byte_cap")
    return b
def api(url):return json.loads(read(url))
def pages(url):
    seen=set()
    while url:
        if url in seen or len(seen)>30:raise ValueError("page_limit")
        seen.add(url)
        x=api(url)
        yield from x["data"]
        url=x.get("links",{}).get("next")
def inventory(url,depth=0):
    if depth>4:raise ValueError("folder_depth")
    for f in pages(url):
        a=f["attributes"]
        if a["kind"]=="folder":
            yield from inventory(f["relationships"]["files"]["links"]["related"]["href"],depth+1)
        elif a["kind"]=="file":yield f
def csv_schema(b):
    txt=b.decode("utf-8-sig")
    variants=[]
    for sep in (",",";","\t"):
        rr=list(csv.reader(io.StringIO(txt,newline=""),delimiter=sep))
        if rr and len(rr[0])>1 and len(set(rr[0]))==len(rr[0]) and all(len(x)==len(rr[0]) for x in rr[1:]):
            variants.append((sep,rr))
    if len(variants)!=1:raise ValueError("unresolved_delimiter")
    sep,rr=variants[0]
    h=[x.strip() for x in rr[0]]
    # Calendar/site/treatment labels only; do not count fate or emergence.
    allowed={"year","site","plot","altitude","elevation","month","date","day","year_of_experiment","experiment","treatment","exclusion","microhabitat","location","species"}
    cols=[]
    for i,k in enumerate(h):
        vals=set(x[i].strip() for x in rr[1:])
        if k.lower() in allowed:cols.append({"name":k,"distinct":len(vals),"labels":sorted(vals) if len(vals)<=30 else None})
    return {"header":h,"rows":len(rr)-1,"delimiter":repr(sep),"context_fields":cols}
def main():
    out={"status":"STOP_SOURCE","node":NODE,"doi":"10.17605/OSF.IO/R9CMJ","paper":"10.1111/1365-2656.70101","effect_opened":False}
    try:
        root=api(f"{ROOT}/nodes/{NODE}/")["data"]
        if root["id"].lower()!=NODE or not root["attributes"]["public"]:raise ValueError("node identity/public status")
        out["title"]=root["attributes"]["title"]
        out["description"]=str(root["attributes"].get("description") or "")[:3000]
        ff=list(inventory(f"{ROOT}/nodes/{NODE}/files/osfstorage/"))
        if len(ff)>100:raise ValueError("file roster cap")
        out["files"]=[]
        for f in ff:
            a=f["attributes"]
            z={"id":f["id"],"name":a["name"],"size":a["size"],"path":a.get("materialized_path"),"hashes":a.get("extra",{}).get("hashes",{})}
            out["files"].append(z)
        # All bounded tabular files are inspected, not selected by outcome.
        for f,z in zip(ff,out["files"]):
            name=z["name"].lower()
            if not name.endswith((".csv",".tsv",".txt",".xlsx")):continue
            try:
                n=z["size"]
                if not isinstance(n,int) or n<=0 or n>CAP:raise ValueError("metadata size")
                b=read(f["links"]["download"],n)
                if len(b)!=n:raise ValueError("provider size mismatch")
                hashes=z["hashes"]
                z["sha256"]=hashlib.sha256(b).hexdigest()
                z["md5"]=hashlib.md5(b).hexdigest()
                if hashes.get("sha256") and hashes["sha256"]!=z["sha256"]:raise ValueError("provider sha256 mismatch")
                if hashes.get("md5") and hashes["md5"]!=z["md5"]:raise ValueError("provider md5 mismatch")
                if not hashes.get("sha256") and not hashes.get("md5"):raise ValueError("no provider checksum")
                if name.endswith((".csv",".tsv")):z["schema"]=csv_schema(b)
                elif name.endswith(".xlsx"):
                    import openpyxl
                    w=openpyxl.load_workbook(io.BytesIO(b),read_only=True,data_only=True)
                    z["schema"]=[{"sheet":q.title,"rows":q.max_row,"first_row":[str(v) if v is not None else "" for v in next(q.values)]} for q in w.worksheets]
                else:z["text_description"]=b.decode("utf-8-sig")[:3000] if "readme" in name else None
                z["status"]="VERIFIED_BYTES"
            except Exception as e:z["status"]="STOP_FILE";z["reason"]=type(e).__name__+": "+str(e)[:200]
        out["status"]="SOURCE_INVENTORY_COMPLETE"
    except Exception as e:out["reason"]=type(e).__name__+": "+str(e)[:250]
    out["boundary"]="Seed tracking and simulated-cache emergence are distinct experiments; no individual join assumed. Source support only, no fit."
    p=pathlib.Path("build/neon_alpine_seed_source_v24.json");p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n");print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
