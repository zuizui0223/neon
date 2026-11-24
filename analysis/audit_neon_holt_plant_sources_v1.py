"""Anonymous FEMC versioned download via the published UI; source support only.

No response values or raw files published. Stop on any provider access block.
"""
from collections import Counter
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from io import BytesIO,StringIO
from zipfile import ZipFile,is_zipfile
import csv,json,re,tempfile
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_holt_plant_sources_20261124.json"
SOURCES={
 "seedfall":("https://www.uvm.edu/femc/data/archive/project/hrfseeds/dataset/seedtrapss1/version/859",7012,{"YEAR","LINE","PLOT","FIASP","COUNT"}),
 "seedling":("https://www.uvm.edu/femc/data/archive/project/hrfSeedlings/dataset/s1seedling/version/1074",16021,{"YEAR","LINE","PLOT","FIASP","HT1","HT2","HT3","HT4"})}
MAX_BYTES=25_000_000

def parse_csv(raw,expected,needed):
    try:s=raw.decode("utf-8-sig")
    except UnicodeError:s=raw.decode("latin1")
    rows=csv.DictReader(StringIO(s,newline=""))
    if not rows.fieldnames or not needed<=set(rows.fieldnames):return None
    count=0;bad=0;keys=set();year_counts=Counter();sp=set()
    for row in rows:
        count+=1
        try:
            y=int(row["YEAR"]);line=row["LINE"].strip();p=int(row["PLOT"])
            if line not in {"N","S"} or not 1<=p<=600:raise ValueError()
            keys.add((y,line,p));year_counts[y]+=1;sp.add(row["FIASP"].strip())
        except (ValueError,TypeError,AttributeError):bad+=1
    return {"record_count":count,"expected_records":expected,"original_columns":rows.fieldnames,
            "valid_year_line_plot_keys":len(keys),"invalid_key_rows":bad,"row_counts_by_year":dict(sorted(year_counts.items())),
            "distinct_nominal_plots":len({(l,p) for y,l,p in keys}),"distinct_FIASP_codes":len(sp),
            "status":"SOURCE_SCHEMA_GO" if count==expected and bad==0 else "STOP_SOURCE_COUNT_OR_KEYS"},keys

def parse_download(raw,expected,needed):
    if len(raw)>MAX_BYTES:raise ValueError("BYTE_LIMIT")
    members=[]
    if is_zipfile(BytesIO(raw)):
        with ZipFile(BytesIO(raw)) as z:
            if sum(i.file_size for i in z.infolist())>MAX_BYTES:raise ValueError("UNCOMPRESSED_LIMIT")
            for i in z.infolist():
                if not i.is_dir() and i.filename.lower().endswith(".csv"):
                    members.append((Path(i.filename).name,z.read(i)))
    else:members=[("download.csv",raw)]
    matched=[]
    for name,data in members:
        v=parse_csv(data,expected,needed)
        if v is not None:matched.append((name,v))
    if len(matched)!=1:raise ValueError("NO_UNIQUE_ORIGINAL_SCHEMA")
    name,(report,keys)=matched[0];report.update({"member_name":name,"download_SHA256":sha256(raw).hexdigest(),"download_bytes":len(raw)})
    return report,keys

def download_version(page,url):
    # The provider explicitly permits anonymous download. Do not enter personal details.
    page.goto(url,wait_until="domcontentloaded",timeout=60000)
    with page.expect_download(timeout=45000) as ev:
        page.get_by_role("button",name="Download This Version",exact=True).click(timeout=12000)
        # Some versions show an optional details modal with a separate Download button.
        try:
            b=page.get_by_role("button",name="Download",exact=True)
            if b.count()==1 and b.is_visible(timeout=3000):b.click(timeout=3000)
        except Exception:pass
    d=ev.value
    with tempfile.TemporaryDirectory() as tmp:
        target=Path(tmp)/"source"
        d.save_as(target)
        if target.stat().st_size>MAX_BYTES:raise ValueError("BYTE_LIMIT")
        return target.read_bytes()

def figshare_inventory():
    url="https://api.figshare.com/v2/articles/27152484"
    with urlopen(Request(url,headers={"User-Agent":"NEON academic source inventory"}),timeout=45) as f:
        raw=f.read(2_000_001)
    if len(raw)>2_000_000:raise ValueError("METADATA_LIMIT")
    x=json.loads(raw)
    if x.get("id")!=27152484:raise ValueError("ARTICLE_ID")
    return {"status":"METADATA_ONLY","article":x.get("title"),"version":x.get("version"),
            "doi":x.get("doi"),"metadata_SHA256":sha256(raw).hexdigest(),
            "files":[{k:f.get(k) for k in ("id","name","size","computed_md5")} for f in x["files"]]}

def main():
    out={"schema":"neon.holt.plant_census_source.v1","source_results":{},"no_plant_or_animal_effect_fitted":True,
         "license":"CC BY-NC-SA 4.0 for FEMC; source audit only, no raw redistribution","submission_hold":True}
    keysets={}
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            for label,(url,n,fields) in SOURCES.items():
                page=browser.new_page(accept_downloads=True)
                try:
                    report,keys=parse_download(download_version(page,url),n,fields)
                    out["source_results"][label]=report
                    if report["status"]=="SOURCE_SCHEMA_GO":keysets[label]=keys
                except Exception as exc:
                    out["source_results"][label]={"status":"STOP_OFFICIAL_VERSION_DOWNLOAD_OR_SCHEMA","error_class":type(exc).__name__}
                finally:page.close()
            browser.close()
    except Exception as exc:out["browser_source_stop"]=type(exc).__name__
    if set(keysets)==set(SOURCES):
        # Nominal same S1 plot and year/next-year support only; no biology values.
        a,b=keysets["seedfall"],keysets["seedling"]
        out["exact_S1_key_support"]={"same_year":len(a&b),"following_year":sum((y+1,l,p) in b for y,l,p in a),
          "nominal_spatial_overlap":len({(l,p) for y,l,p in a}&{(l,p) for y,l,p in b}),
          "note":"Observed rows only; annual crop-label, census effort and absent species zero semantics not yet verified"}
    try:out["same_forest_2025_source"]=figshare_inventory()
    except Exception as exc:out["same_forest_2025_source"]={"status":"SOURCE_STOP","error_class":type(exc).__name__}
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
