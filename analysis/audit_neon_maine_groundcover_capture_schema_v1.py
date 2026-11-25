"""Read the actual codebook and capture schemas of an already verified source.
Brehm & Mortelliti 2021 (10.1002/eap.2443), Figshare 14488626 v1.
No external code execution, no raw animal/location rows exported.
"""
from collections import Counter
from datetime import datetime,timezone
from hashlib import md5,sha256
from io import BytesIO,StringIO
from pathlib import Path,PurePosixPath
from zipfile import ZipFile
import csv,json,re
from analysis.audit_neon_direct_resource_groundcover_source_v1 import bounded,require
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_maine_groundcover_capture_schema_20261125.json"
ARTICLE=14488626
FILE=27847659
SIZE=692526
MD5="0a240dff244d72b41ecb3789b339abb6"
SHA="d043fd84be754d77deb8397124f635ec6e301a4d0a5490360274e4e0b42a0705"
TABLES=("16_19_GRID_occup.csv","GRID_trap_dist.csv","microhabitat.csv","mg.csv","pm.csv")
DOC="Metadata.txt"
R="calculating_selection_variables.R"
MISSING={"","na","nan","null","n/a"}
def norm(s):return re.sub(r"[^a-z0-9]","",str(s).lower())
def profile_table(raw):
    try:s=raw.decode("utf-8-sig")
    except UnicodeError:s=raw.decode("cp1252")
    candidates=[]
    for delim in (",",";","\t"):
        rows=[x for x in csv.reader(StringIO(s,newline=""),delimiter=delim) if any(v.strip() for v in x)]
        if rows and 1<len(rows[0])<=300 and all(len(r)==len(rows[0]) for r in rows):
            candidates.append((delim,rows))
    require(len(candidates)==1,"CSV_DIALECT_UNRESOLVED")
    delim,rows=candidates[0];h=rows[0];data=rows[1:]
    require(len(data)>0 and len(h)==len(set(h)),"TABLE_HEADER_OR_BODY_INVALID")
    # Return only aggregate profiles. Categorical values allowed for
    # unambiguous protocol/context fields; no coordinates, tags or rows.
    labels={"year","season","month","species","sp","sex","age","treatment","habitat","foresttype","trapstatus","status","captured","capture","session","round","occasion","trappingoccasion","recapture","traptype"}
    cols=[]
    for j,k in enumerate(h):
        v=[r[j].strip() for r in data];obs=[x for x in v if x.lower() not in MISSING];cnt=Counter(obs)
        d={"name":k,"missing":len(v)-len(obs),"distinct_nonmissing":len(cnt)}
        if norm(k) in labels and len(cnt)<=32 and all(len(x)<=80 for x in cnt):
            d["literal_counts"]=dict(sorted(cnt.items()))
        cols.append(d)
    # Candidate-key counts do not establish semantics. Only columns named
    # for site/grid/year/session/animal/station are included, not outcomes.
    groups={
       "grid": {"grid","site","plot","gridid","siteid","plotid","gridname"},
       "year": {"year","yr","trappingyear"},
       "session": {"session","trappingsession","month","round","occasion","trappingoccasion","date","capturedate"},
       "station": {"station","trap","trapid","stationid","trapnumber","trapsite","traplocation","point"},
       "individual": {"id","animalid","individual","individualid","tag","tagid","eartag","pittag","pit","animal","animalnumber"}
    }
    aliases={k:[h[j] for j,v in enumerate(h) if norm(v) in names] for k,names in groups.items()}
    keys={}
    for roles in (("grid","station"),("grid","year","session","station"),("grid","individual"),("grid","year","session","individual","station")):
        if all(len(aliases[k])==1 for k in roles):
            ids=[h.index(aliases[k][0]) for k in roles]
            keys["+".join(roles)]=dict(columns=[h[j] for j in ids],
                 complete_rows=sum(all(r[j].strip().lower() not in MISSING for j in ids) for r in data),
                 distinct_complete_keys=len({tuple(r[j].strip() for j in ids) for r in data if all(r[j].strip().lower() not in MISSING for j in ids)}))
    return {"header":h,"data_rows":len(data),"delimiter":repr(delim),"column_profiles":cols,
            "candidate_roles_not_validated":aliases,"candidate_key_counts":keys}
def source_notes(raw):
    try:s=raw.decode("utf-8-sig")
    except UnicodeError:s=raw.decode("cp1252")
    # Original author public codebook, not a capture table. Retain
    # column definitions and line numbers; omit e-mail/address contact.
    out=[]
    for n,line in enumerate(s.splitlines(),1):
        line=line.strip()
        if not line or "@" in line or re.search(r"^\s*(email|phone|contact)\s*[:=]",line,re.I):continue
        out.append({"line":n,"definition":line[:350]})
    return out
def code_notes(raw):
    s=raw.decode("utf-8-sig")
    # Do not execute the R file. Record only source read/join/group
    # statements and explanatory comments relevant to sample identity.
    return [{"line":n,"statement":line.strip()[:250]} for n,line in enumerate(s.splitlines(),1)
            if re.search(r"read[._]csv|read\\.table|merge\\(|join\\(|group_by\\(|aggregate\\(|unique\\(|subset\\(|filter\\(|trap|grid|session|capture|animal",line,re.I) and len(line)<500 and "@" not in line][:90]
def inspect(raw):
    require(len(raw)==SIZE and md5(raw).hexdigest()==MD5 and sha256(raw).hexdigest()==SHA,"ORIGINAL_SOURCE_BYTE_MISMATCH")
    with ZipFile(BytesIO(raw)) as z:
        info=z.infolist()
        require(len(info)<=50 and sum(x.file_size for x in info)<=10_000_000,"ZIP_BUDGET")
        require(all(not PurePosixPath(x.filename).is_absolute() and ".." not in PurePosixPath(x.filename).parts for x in info),"UNSAFE_MEMBER")
        names={x.filename for x in info};needed={"DataS1/"+k for k in TABLES+(DOC,R)}
        require(needed<=names and len(names)==len(info),"MEMBER_ROSTER_DRIFT")
        docs=z.read("DataS1/"+DOC);code=z.read("DataS1/"+R)
        tables={}
        for n in TABLES:
            v=z.read("DataS1/"+n)
            try:tables[n]={"sha256":sha256(v).hexdigest(),**profile_table(v)}
            except Exception as e:tables[n]={"sha256":sha256(v).hexdigest(),"status":"SCHEMA_STOP","error_class":type(e).__name__,"reason":str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR"}
        return {"status":"VERIFIED_CODEBOOK_AND_SOURCE_PROFILE","verified_bytes":len(raw),"verified_md5":MD5,"verified_sha256":SHA,
                "metadata_sha256":sha256(docs).hexdigest(),"author_codebook_definitions":source_notes(docs),
                "author_R_sha256":sha256(code).hexdigest(),"author_R_selected_statements_not_executed":code_notes(code),
                "tables":tables,"station_season_individual_join_verified":False,"effect":None}
def run():
    meta=json.loads(bounded("https://api.figshare.com/v2/articles/"+str(ARTICLE)+"/versions/1",2_000_000))
    require(meta.get("id")==ARTICLE and meta.get("version")==1 and "microhabitat selection" in meta.get("title","").lower(),"SOURCE_ARTICLE_DRIFT")
    files=[x for x in meta.get("files",[]) if x.get("id")==FILE]
    require(len(files)==1,"SOURCE_FILE_ROSTER_DRIFT")
    f=files[0]
    require(f.get("name")=="DataS1.zip" and f.get("size")==SIZE and (f.get("computed_md5") or f.get("supplied_md5"))==MD5,"SOURCE_FILE_METADATA_DRIFT")
    return inspect(bounded(f["download_url"],SIZE))
def main():
    out={"schema":"neon.maine.groundcover.capture_schema.v1","submission_hold":True,"paper_doi":"10.1002/eap.2443","archive_doi":"10.6084/m9.figshare.14488626.v1","cambodia_access_stop_preserved":True}
    try:out.update(run())
    except Exception as e:out.update(status="STOP_SOURCE_OR_SCHEMA",effect=None,error_class=type(e).__name__,reason=str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR")
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
