"""Resolve primary Figshare identity using author-cited workbook name.

No biological effects or raw seed values are analyzed here. Archive v1 STOP
unchanged. Secondary source documentation only, not a substitute endpoint.
"""
from collections import Counter
from datetime import datetime,timezone
from hashlib import md5,sha256
from io import BytesIO
from pathlib import Path
import json,re
from analysis.audit_neon_direct_seed_fate_stage_sources_v1 import (
    metadata,bounded,safe_provider,require,MAX_METADATA,MAX_BYTES)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_seed_fate_stage_ontology_v2_20261124.json"
PRIMARY=3189775
AUTHOR_CITED="QCSsquirelindirecteffctFigshare.xlsx"
SECONDARY=1256359
SECONDARY_READMES={
 3250772:("ReadME_hoardingdata.rtf",4140,"3e9500e098e5e6d26c7a1c135d90ec55"),
 3250778:("ReadME_seedlingheightdata.rtf",2451,"3d3a17262a2629a50ef6de9bd627b47d"),
 3250790:("ReadME_seedlingsurvivaldata.rtf",2818,"f3bab8b606dabda3011d65afe45df653"),
}

def primary_identity(raw):
    # DOI/version/size/file rules from v1; replace only the title-keyword rule
    # with the original paper's exact cited dataset name.
    obj,version,files=metadata(raw,PRIMARY,{"version":1,"keywords":()})
    require(obj["doi"].lower()==f"10.6084/m9.figshare.{PRIMARY}.v1","EXACT_VERSION_DOI_MISMATCH")
    candidates=[f for f in files if f["name"].lower()==AUTHOR_CITED.lower()]
    title_is_citation=obj["title"].strip().lower()==AUTHOR_CITED.lower()
    require(len(candidates)==1 or (title_is_citation and len(files)==1 and Path(files[0]["name"]).suffix.lower()==".xlsx"),"AUTHOR_CITED_WORKBOOK_NOT_IDENTIFIED")
    f=candidates[0] if len(candidates)==1 else files[0]
    require(f["md5"] and safe_provider(f["href"]) and 0<f["size"]<=MAX_BYTES,"CHECKSUM_OR_BUDGET")
    return obj,f

def heading(v):
    if v is None:return None
    if isinstance(v,str) and len(v)<=160 and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ .()/\-:%?+]*",v.strip()):
        return v.strip()
    return "<nonheader-value>"

def primary(fetch=bounded):
    raw=fetch("https://api.figshare.com/v2/articles/3189775/versions/1",MAX_METADATA)
    try:obj,f=primary_identity(raw)
    except ValueError as e:
        # Public provider metadata only, to diagnose identity mismatch.
        a=json.loads(raw)
        return {"status":"STOP_METADATA_IDENTITY","reason":str(e),
                "provider_id":a.get("id"),"provider_version":a.get("version"),
                "provider_doi":a.get("doi"),"provider_title":a.get("title"),
                "provider_file_names":[x.get("name") for x in a.get("files",[])]}
    data=fetch(f["href"],f["size"])
    require(len(data)==f["size"] and md5(data).hexdigest()==f["md5"],"SOURCE_BYTES_DRIFT")
    from openpyxl import load_workbook
    book=load_workbook(BytesIO(data),read_only=True,data_only=True)
    try:
        sheets=[]
        for s in book.worksheets:
            first=next(s.iter_rows(min_row=1,max_row=1,values_only=True),())
            shapes=Counter()
            # Row-width/blank support only; never emit responses or actor IDs.
            for row in s.iter_rows(min_row=2,values_only=True):
                shapes[sum(v is not None and str(v).strip()!="" for v in row)]+=1
            sheets.append({"sheet":s.title,"max_rows":s.max_row,"max_columns":s.max_column,
                           "candidate_first_row_headers":[heading(v) for v in first],
                           "nonblank_cell_counts_by_row":dict(sorted(shapes.items()))})
        return {"status":"AUTHOR_CITED_WORKBOOK_SOURCE_GO_SCHEMA_ONLY",
                "title":obj["title"],"doi":obj["doi"],"file_id":f["id"],"filename":f["name"],
                "provider_md5":f["md5"],"verified_size":len(data),"sha256":sha256(data).hexdigest(),
                "metadata_sha256":sha256(raw).hexdigest(),"sheets":sheets}
    finally:book.close()

def secondary(fetch=bounded):
    raw=fetch("https://api.figshare.com/v2/articles/1256359/versions/1",MAX_METADATA)
    obj,version,files=metadata(raw,SECONDARY,{"version":1,"keywords":("scatter","hoarding")})
    byid={f["id"]:f for f in files}
    result={}
    for fid,(name,size,digest) in SECONDARY_READMES.items():
        f=byid[fid]
        require((f["name"],f["size"],f["md5"])==(name,size,digest) and safe_provider(f["href"]),"README_SOURCE_DRIFT")
        data=fetch(f["href"],size)
        require(len(data)==size and md5(data).hexdigest()==digest,"README_BYTES_DRIFT")
        # RTF is original author documentation, not biological table values.
        from striprtf.striprtf import rtf_to_text
        desc=rtf_to_text(data.decode("latin1",errors="strict"))
        result[name]={"file_id":fid,"sha256":sha256(data).hexdigest(),
                      "provider_md5":digest,"text":desc[:12000]}
    return {"status":"ORIGINAL_DOCUMENTATION_GO","doi":obj["doi"],"documentation":result,
            "not_same_seed_cohort_join_established":True}

def main():
    out={"schema":"neon.seed_fate_stage_ontology.v2","source_results":{},
         "v1_stop_preserved":True,"no_effect_fitted":True,"submission_hold":True}
    for name,fn in (("primary",primary),("secondary_documentation",secondary)):
        try:out["source_results"][name]=fn()
        except Exception as e:
            out["source_results"][name]={"status":"SOURCE_STOP","error_class":type(e).__name__,
              "reason":str(e) if type(e) is ValueError and re.fullmatch(r"[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR"}
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
