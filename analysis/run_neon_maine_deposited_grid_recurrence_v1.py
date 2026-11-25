"""Independent regional comparison, Brehm & Mortelliti deposited records.
Separate all-deposited-eight-grid estimand, not a replication of the paper's
600-point cohort. No extrapolation of one region or causal habitat inference.
"""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from hashlib import sha256,md5
from io import BytesIO,StringIO
from pathlib import Path
from zipfile import ZipFile
from statistics import mean
import csv,json,math,re
from analysis.audit_neon_maine_groundcover_capture_schema_v1 import (
    ARTICLE,FILE,SIZE,MD5,SHA,bounded,require
)
from analysis.neon_exact_two_row_fixedmargin_v1 import (
    two_row_exact_marginal,observed_exact_unit
)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_maine_deposited_grid_recurrence_20261125.json"
COUNTS={"microhabitat.csv":800,"16_19_GRID_occup.csv":47200,"GRID_trap_dist.csv":80000,"mg.csv":1688,"pm.csv":1970}
WINDOWS=((1,2),(3,4))  # June->July and August->September; no reused session
TARGET=("MG","PM")
MIN_PAIRS=12
MIN_GRIDS=4
def read(z,name,columns):
    raw=z.read("DataS1/"+name)
    try:s=raw.decode("utf-8-sig")
    except UnicodeError:s=raw.decode("cp1252")
    it=csv.DictReader(StringIO(s,newline=""))
    require(it.fieldnames and columns<=set(it.fieldnames) and len(it.fieldnames)==len(set(it.fieldnames)),"DOCUMENTED_HEADER_DRIFT")
    rows=list(it)
    require(len(rows)==COUNTS[name] and all(None not in v and None not in v.values() for v in rows),"SOURCE_ROW_COUNT_OR_SHAPE_DRIFT")
    return rows
def clean(x):
    x=str(x).strip()
    return x if x.lower() not in {"","na","nan","null","n/a"} else None
def source():
    m=json.loads(bounded("https://api.figshare.com/v2/articles/"+str(ARTICLE)+"/versions/1",2_000_000))
    require(m.get("id")==ARTICLE and m.get("version")==1,"SOURCE_ARTICLE_DRIFT")
    files=[x for x in m.get("files",[]) if x.get("id")==FILE]
    require(len(files)==1,"SOURCE_FILE_ROSTER_DRIFT")
    f=files[0]
    require(f.get("name")=="DataS1.zip" and f.get("size")==SIZE and (f.get("computed_md5") or f.get("supplied_md5"))==MD5,"SOURCE_FILE_METADATA_DRIFT")
    b=bounded(f["download_url"],SIZE)
    require(len(b)==SIZE and md5(b).hexdigest()==MD5 and sha256(b).hexdigest()==SHA,"SOURCE_BYTES_DRIFT")
    return b
def reconcile(raw):
    with ZipFile(BytesIO(raw)) as z:
        require(sum(v.file_size for v in z.infolist())<10_000_000,"ZIP_SIZE")
        micro=read(z,"microhabitat.csv",{"SITE","GRID","TRT"})
        occ=read(z,"16_19_GRID_occup.csv",{"SITE","UNIQUE_OCC","OCCUP"})
        dist=read(z,"GRID_trap_dist.csv",{"SITE1","SITE2","DISTANCE"})
        captures=[(label,x) for name,label in (("mg.csv","MG"),("pm.csv","PM"))
                  for x in read(z,name,{"SITE","GRID","TRT","PIT","SPP","SEASON","YEAR","SESSION","UNIQUE_OCC"})]
    issues=Counter();sites={};grids=defaultdict(set)
    for x in micro:
        s,g,t=(clean(x[k]) for k in ("SITE","GRID","TRT"))
        require(s and g and t and s not in sites,"MICRO_SITE_KEY_INVALID")
        sites[s]=(g,t);grids[g].add(s)
    require(len(grids)==8 and all(len(v)==100 for v in grids.values()),"EIGHT_GRID_ROSTER_DRIFT")
    # Verify all distance pairs are within the documented grid, including
    # reciprocal distances and diagonal zeros. No location exported.
    dd={}
    for x in dist:
        a,b=clean(x["SITE1"]),clean(x["SITE2"])
        try:v=float(x["DISTANCE"])
        except ValueError:v=float("nan")
        require(a in sites and b in sites and sites[a][0]==sites[b][0] and math.isfinite(v) and v>=0 and (a,b) not in dd,"DISTANCE_KEY_OR_VALUE_INVALID")
        require((a==b)==(v==0),"DISTANCE_ZERO_IDENTITY_CONFLICT")
        dd[a,b]=v
    require(len(dd)==80000 and all(abs(v-dd.get((b,a),float("inf")))<1e-8 for (a,b),v in dd.items()),"DISTANCE_MATRIX_INCOMPLETE")
    oo={};occasion=set()
    for x in occ:
        s,o,v=(clean(x[k]) for k in ("SITE","UNIQUE_OCC","OCCUP"))
        require(s in sites and o and v in {"0","1"} and (s,o) not in oo,"OCCUPANCY_KEY_INVALID")
        oo[s,o]=int(v);occasion.add(o)
    require(len(occasion)==59 and len(oo)==len(sites)*len(occasion),"OCCUPANCY_CARTESIAN_SUPPORT_DRIFT")
    byocc=defaultdict(set);obs=set();pits=defaultdict(set);tagocc=defaultdict(set)
    for expected,x in captures:
        s,g,t,tag,sp,o=(clean(x[k]) for k in ("SITE","GRID","TRT","PIT","SPP","UNIQUE_OCC"))
        require(s in sites and sites[s]==(g,t),"CAPTURE_SITE_GRID_TREATMENT_MISMATCH")
        require(tag and sp==expected and o in occasion,"CAPTURE_TAG_OR_SPECIES_INVALID")
        try:y=int(x["YEAR"]);m=int(x["SESSION"])
        except ValueError:raise ValueError("CAPTURE_CALENDAR_INVALID")
        require(y in range(16,20) and m in range(1,6) and clean(x["SEASON"])==f"{y}_{m}","CAPTURE_CALENDAR_INCONSISTENT")
        byocc[o].add((y,m))
        # The published OCCUP variable denotes occupied/unoccupied,
        # NOT independently documented trap functionality.
        if oo[s,o]!=1:issues["capture_on_nonoccupied_source_cell"]+=1
        pits[tag].add(sp);tagocc[tag,o].add((s,sp))
        key=(g,s,o,y,m,tag,sp)
        if key in obs:issues["duplicate_capture_key_rows"]+=1
        obs.add(key)
    require(set(byocc)==occasion and all(len(v)==1 for v in byocc.values()),"OCCASION_CALENDAR_CROSSWALK_INVALID")
    require(not issues["capture_on_nonoccupied_source_cell"],"CAPTURE_OCCUPANCY_CONFLICT")
    conflict={t for t,v in pits.items() if len(v)!=1}
    ambig={t for (t,o),v in tagocc.items() if len(v)!=1}
    excluded=conflict|ambig
    issues["cross_species_tag_conflicts"]=len(conflict);issues["same_occasion_multistation_tags"]=len(ambig)
    # Conservative exclusion of entire conflicting tag histories. A
    # cross-grid recapture alone is not a contradiction.
    obs={v for v in obs if v[5] not in excluded}
    month_occ=defaultdict(set)
    for o,v in byocc.items():month_occ[next(iter(v))].add(o)
    source_diag={"grids":len(grids),"microhabitat_sites":len(sites),"complete_distance_cells":len(dd),
        "occupied_source_cells":sum(oo.values()),"occupancy_cells":len(oo),"unique_occasions":len(occasion),
        "calendar_sessions":len(month_occ),"occasion_count_per_session_histogram":dict(Counter(map(len,month_occ.values()))),
        "raw_capture_rows":len(captures),"eligible_distinct_capture_keys":len(obs),"issues":dict(issues),
        "regional_study_count":1,"occupancy_not_operability":True,
        "eight_deposited_grids_not_original_six_grid_roster":True}
    return grids,obs,month_occ,source_diag
def build_pairs(grids,obs,month_occ):
    # Exact-overlap score is invariant to a one-to-one station relabeling.
    # Use arbitrary sorted labels in existing null code; this is not a
    # coordinate reconstruction and never used for neighbor distances.
    tags=defaultdict(set);pos=defaultdict(set);month_tags=defaultdict(set)
    for g,s,o,y,m,t,sp in obs:
        tags[g,y,m,sp].add(t);pos[g,y,m,sp,t].add(s);month_tags[y,m].add(t)
    diag=Counter();pairs=[]
    for g,ss in sorted(grids.items()):
        station={v:f"{chr(65+j//10)}{j%10+1}" for j,v in enumerate(sorted(ss))}
        for y in range(16,20):
            for a,b in WINDOWS:
                diag["prespecified_grid_month_pairs"]+=1
                if len(month_occ[y,a])!=3 or len(month_occ[y,b])!=3:
                    diag["not_three_documented_occasions"]+=1;continue
                shared=month_tags[y,a]&month_tags[y,b]  # across all deposited grids
                mat=[]
                for m in (a,b):
                    mm={}
                    for sp in TARGET:
                        tt=tags[g,y,m,sp]-shared
                        if len(tt)<2:break
                        pp=set().union(*(pos[g,y,m,sp,t] for t in tt))
                        if len(pp)<2:break
                        mm[sp]={station[s] for s in pp}
                    mat.append(mm)
                if any(len(v)!=2 for v in mat):
                    diag["insufficient_nonshared_tag_station_support"]+=1;continue
                A,B=mat
                mar=two_row_exact_marginal(A,B)
                if mar["status"]!="EXACT_NONDEGENERATE":
                    diag["exact_null_zero_variance"]+=1;continue
                pairs.append((g,y,a,A,B,mar));diag["informative_pairs"]+=1
    return pairs,dict(diag)
def summarize(pairs):
    by=defaultdict(list)
    for g,y,a,A,B,m in pairs:
        score=observed_exact_unit(A,B,m)
        excess=(sum(len(A[k]&B[k]) for k in A)-m["null_mean"])/sum(map(len,B.values()))
        by[g].append((score["z"],excess))
    zz=[mean(v[0] for v in x) for x in by.values()]
    ef={"equal_grid_mean_Z":mean(zz),"positive_grid_means":sum(v>0 for v in zz),
        "anonymous_grid_means_sorted":sorted(zz),"equal_grid_excess_B_station_cell_fraction":mean(mean(v[1] for v in x) for x in by.values()),
        "no_regional_inference_or_pooled_p":True}
    if len(zz)>1:ef["leave_one_grid_out_mean_range"]=[min(mean(v for j,v in enumerate(zz) if j!=i) for i in range(len(zz))),max(mean(v for j,v in enumerate(zz) if j!=i) for i in range(len(zz)))]
    return ef
def run():
    grids,obs,month_occ,source_diag=reconcile(source())
    pairs,diag=build_pairs(grids,obs,month_occ)
    support={"informative_pairs":len(pairs),"grids":len({v[0] for v in pairs}),"minimum_pairs":MIN_PAIRS,"minimum_grids":MIN_GRIDS}
    out={"source_checks":source_diag,"pair_support":diag,"effect_support":support,"effect":None}
    if support["informative_pairs"]<MIN_PAIRS or support["grids"]<MIN_GRIDS:
        return {**out,"status":"STOP_REGIONAL_PAIR_SUPPORT"}
    ef=summarize(pairs)
    ok=ef["equal_grid_mean_Z"]>0 and ef["positive_grid_means"]>=math.ceil(.75*support["grids"]) and ef["leave_one_grid_out_mean_range"][0]>0
    return {**out,"status":"REGIONAL_DESCRIPTIVE_DIRECTION_SUPPORTED" if ok else "REGIONAL_DESCRIPTIVE_DIRECTION_NOT_SUPPORTED","effect":ef}
def main():
    out={"schema":"neon.maine.deposited_grid_recurrence.v1","submission_hold":True,
        "archive_doi":"10.6084/m9.figshare.14488626.v1","original_paper_doi":"10.1002/eap.2443",
        "eight_grid_deposited_record_exploration_not_original_paper_cohort":True,
        "no_habitat_or_causal_fit":True}
    try:out.update(run())
    except Exception as e:out.update(status="STOP_SOURCE_OR_ONTOLOGY",effect=None,error_class=type(e).__name__,reason=str(e) if type(e) is ValueError and re.fullmatch("[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR")
    out["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
