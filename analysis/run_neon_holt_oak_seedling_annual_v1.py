"""Frozen exploratory Holt annual seed-to-small-seedling prediction.

Exactly one primary contrast: does adding the previous August recorded mouse
count and its interaction with previous-label oak crop improve time-blocked
prediction, and have the sign expected from delayed consumer pressure?
No causal dispersal, germination, exact crop-date or geographic inference.
"""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from hashlib import sha256
from io import BytesIO,StringIO
from math import isfinite,log1p
from pathlib import Path
from zipfile import ZipFile
import csv,json,re
import numpy as np
from analysis.audit_neon_holt_annual_bridge_v1 import PLANT_SHA,CAP_SHA,explicit_august
from analysis.audit_neon_holt_plant_sources_v1 import SOURCES,download_version
from analysis.audit_neon_seasonal_seed_role_source_v1 import verified_file
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_holt_oak_seedling_annual_v1_20261124.json"
YEARS=(1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1999,2001,2004,2005,2006,2007,2008,2009,2010,2011,2013)
BLOCKS=((1988,1995),(1996,2004),(2005,2013))
MIN_PLOTS=100
MIN_YEARS=18
def req(ok,code):
    if not ok:raise ValueError(code)
def parse_rows(raw,expected):
    try:txt=raw.decode("utf-8-sig")
    except UnicodeError:txt=raw.decode("latin1")
    reader=csv.DictReader(StringIO(txt,newline=""))
    req(reader.fieldnames and len(set(reader.fieldnames))==len(reader.fieldnames),"HEADER_DUPLICATE")
    rows=list(reader)
    req(len(rows)==expected and all(None not in x and all(v is not None for v in x.values()) for x in rows),"SOURCE_ROW_OR_WIDTH_DRIFT")
    return rows

def valid_key(x):
    try:y=int(x["YEAR"]);p=int(x["PLOT"]);l=x["LINE"].strip()
    except (ValueError,KeyError):return None
    return (y,l,p) if y in YEARS and l in {"N","S"} and 1<=p<=600 and p%10==1 else None

def plant_annual(seed,seedling,years=YEARS,min_plots=MIN_PLOTS):
    # Fixed support: plots with a record in both original inventories in
    # EVERY source-supported year, before consulting recorded oak counts.
    keys={}
    for name,rows in (("seed",seed),("seedling",seedling)):
        by=defaultdict(set)
        for x in rows:
            k=valid_key(x)
            if k is not None and k[0] in years:by[k[0]].add(k[1:])
        req(set(by)==set(years),"FROZEN_PLANT_YEARS_DRIFT")
        keys[name]=by
    common=set.intersection(*(keys[name][y] for name in keys for y in years))
    count_keys=Counter()
    alt=Counter()
    for x in seedling:
        k=valid_key(x)
        if k is None or k[0] not in years or k[1:] not in common:continue
        if x["FIASP"].strip()=="833":
            if x["SPEC"].strip()=="5":count_keys[k]+=1
            else:alt[x["SPEC"].strip()]+=1
    # Exclude an entire spatial unit, not one response year, if duplicate
    # exact oak keys occur; no selection by count magnitude.
    dup={k[1:] for k,n in count_keys.items() if n>1}
    kept=common-dup
    req(len(kept)>=min_plots,"INSUFFICIENT_FIXED_COMMON_PLOTS")
    values=defaultdict(int);explicit=Counter()
    for x in seedling:
        k=valid_key(x)
        if k is None or k[0] not in years or k[1:] not in kept:continue
        if x["FIASP"].strip()!="833" or x["SPEC"].strip()!="5":continue
        v=x["HT1"].strip()
        req(bool(re.fullmatch(r"[0-9]+",v)),"INVALID_OR_MISSING_EXPLICIT_OAK_HT1")
        values[k[0]]+=int(v);explicit[k[0]]+=1
    # This is a sum of RECORDED HT1 values per surveyed plot. Not an
    # imputation of observed species absence at each individual plot.
    ys={y:100*values[y]/len(kept) for y in years}
    return ys,{"fixed_common_plots_before_duplicate_guard":len(common),"excluded_entire_plots_duplicate_oak_key":len(dup),
               "fixed_surveyed_plots":len(kept),"explicit_oak_rows_by_year":dict(sorted(explicit.items())),
               "alternative_SPEC_rows_with_FIASP_833":dict(alt),
               "outcome_definition":"recorded literal SPEC 5 FIASP 833 HT1 counts per 100 fixed surveyed nominal plots",
               "unlisted_species_not_asserted_true_absent":True,"not_new_germinants_or_seed_fate":True}

def read_zip(z,name,n):
    return parse_rows(z.read("Data and code/Data/"+name),n)

def finite_nonnegative(v,code):
    try:x=float(v)
    except (TypeError,ValueError):raise ValueError(code) from None
    req(isfinite(x) and x>=0,code)
    return x

def unique_year(rows,k):
    out={}
    for row in rows:
        y=int(row[k]);req(y not in out,"DUPLICATE_ANNUAL_SOURCE_YEAR");out[y]=row
    return out

def covariates():
    raw=verified_file(27152484,2,50529696,131218,"750f8d669a890e3450c4a61a2794c223",CAP_SHA)
    with ZipFile(BytesIO(raw)) as z:
        c=read_zip(z,"mice83_21_tr_aug.csv",11549)
        n=unique_year(read_zip(z,"mice83_21_tr_bm_aug.csv",39),"year")
        s=unique_year(read_zip(z,"seeds83_20_year_sp_wide2.csv",37),"year")
        w=unique_year(read_zip(z,"weather82_21.csv",40),"YEAR")
    ids=defaultdict(set)
    for row in c:
        req(explicit_august(row["month"]) and bool(row["id_new"].strip()),"ORIGINAL_CAPTURE_MONTH_OR_ID_DRIFT")
        ids[int(row["year"])].add(row["id_new"].strip())
    req(set(ids)==set(n) and len(ids)==39,"ANNUAL_CAPTURE_YEAR_DRIFT")
    for y,row in n.items():
        req(explicit_august(row["month"]) and int(row["nind"])==len(ids[y]),"ANNUAL_NIND_DRIFT")
    out={}
    for y in YEARS:
        if y-1 not in n or y-1 not in s or y not in w:continue
        seed=finite_nonnegative(s[y-1]["RO"],"INVALID_PRIOR_OAK_RESOURCE")
        m=finite_nonnegative(n[y-1]["nind"],"INVALID_PRIOR_MOUSE_COUNT")
        temp=float(w[y]["Min.Temp_C.AVG.SPRING"]);prec=finite_nonnegative(w[y]["Prec_mm.AVG.SPRING"],"INVALID_SPRING_PREC")
        req(isfinite(temp),"INVALID_SPRING_TEMP")
        out[y]=[float(y),log1p(seed),temp,log1p(prec),log1p(m)]
    return out

def design(x,mu,sd,augmented):
    a=(x-mu)/sd
    base=np.column_stack([np.ones(len(a)),a[:,:4]])
    if not augmented:return base
    return np.column_stack([base,a[:,4],a[:,1]*a[:,4]])

def fit(x,y,augmented):
    mu=x.mean(axis=0);sd=x.std(axis=0,ddof=0)
    req(np.all(sd>0),"CONSTANT_PREDICTOR")
    d=design(x,mu,sd,augmented)
    req(len(y)>d.shape[1] and np.linalg.matrix_rank(d)==d.shape[1] and np.linalg.cond(d)<1000,"INSUFFICIENT_OR_ILL_CONDITIONED_MODEL")
    beta=np.linalg.lstsq(d,y,rcond=None)[0]
    return beta,mu,sd

def analyze(ys,cov,years=YEARS,blocks=BLOCKS,min_years=MIN_YEARS):
    selected=[y for y in years if y in ys and y in cov]
    out={"predeclared_years":list(years),"eligible_years":selected,"eligible_years_n":len(selected),"effect":None}
    if len(selected)<min_years:
        return {**out,"status":"STOP_ANNUAL_SOURCE_SUPPORT"}
    x=np.array([cov[y] for y in selected],float);y=np.array([log1p(ys[t]) for t in selected],float)
    req(np.all(np.isfinite(x)) and np.all(np.isfinite(y)),"NONFINITE_MODEL_INPUT")
    b,mu,sd=fit(x,y,True)
    folds=[];pred0=np.full(len(y),np.nan);pred1=np.full(len(y),np.nan)
    for lo,hi in blocks:
        test=np.array([lo<=t<=hi for t in selected]);train=~test
        req(test.sum()>=3,"INSUFFICIENT_TEST_BLOCK")
        for aug,pred in ((False,pred0),(True,pred1)):
            beta,m,s=fit(x[train],y[train],aug)
            pred[test]=design(x[test],m,s,aug)@beta
        mse0=float(np.mean((pred0[test]-y[test])**2));mse1=float(np.mean((pred1[test]-y[test])**2))
        folds.append({"test_year_interval":[lo,hi],"test_n":int(test.sum()),"baseline_mse":mse0,"mouse_interaction_mse":mse1})
    req(np.all(np.isfinite(pred0)) and np.all(np.isfinite(pred1)),"INCOMPLETE_BLOCKED_PREDICTIONS")
    r0=float(np.sqrt(np.mean((pred0-y)**2)));r1=float(np.sqrt(np.mean((pred1-y)**2)))
    low=float(b[5]-b[6]);high=float(b[5]+b[6]);interaction=float(b[6])
    loo=[]
    for i in range(len(y)):
        k=np.arange(len(y))!=i
        z,_,_=fit(x[k],y[k],True)
        loo.append((float(z[6]),float(z[5]-z[6])))
    wins=sum(f["mouse_interaction_mse"]<f["baseline_mse"] for f in folds)
    # All three lines of evidence must agree; no isolated significant term.
    supported=(low<0 and interaction>0 and r1<r0 and wins>=2
               and all(a>0 and l<0 for a,l in loo))
    out.update(status="DESCRIPTIVE_DELAYED_CONSUMER_PATTERN_SUPPORTED" if supported else "DESCRIPTIVE_DELAYED_CONSUMER_PATTERN_NOT_SUPPORTED",
               effect={"low_seed_mouse_slope_at_minus_1SD":low,"high_seed_mouse_slope_at_plus_1SD":high,
                       "mouse_by_seed_interaction":interaction,"baseline_blocked_RMSE":r0,
                       "mouse_interaction_blocked_RMSE":r1,"improved_time_blocks":wins,"time_blocks":folds,
                       "loo_interaction_range":[min(a for a,l in loo),max(a for a,l in loo)],
                       "loo_low_seed_mouse_slope_range":[min(l for a,l in loo),max(l for a,l in loo)],
                       "all_coefficients_log1p_recorded_count_scale":b.tolist(),
                       "no_p_value_or_causal_claim":True})
    return out

def run():
    from playwright.sync_api import sync_playwright
    raw={}
    with sync_playwright() as pw:
        browser=pw.chromium.launch()
        for kind,(url,n,fields) in SOURCES.items():
            page=browser.new_page(accept_downloads=True)
            try:blob=download_version(page,url)
            finally:page.close()
            req(sha256(blob).hexdigest()==PLANT_SHA[kind],"PINNED_PLANT_SOURCE_BYTES_DRIFT")
            raw[kind]=parse_rows(blob,n)
        browser.close()
    ys,plant=plant_annual(raw["seedfall"],raw["seedling"])
    cov=covariates()
    result=analyze(ys,cov)
    result.update(plant_source=plant,plant_SHA256=PLANT_SHA,capture_SHA256=CAP_SHA,
                  source_crop_label_used="author RO annual label t-1; exact field collection calendar not asserted",
                  mouse_predictor="observed unique tagged mice in August t-1",
                  outcome="July t recorded oak HT1 on fixed S1 plots",
                  climate_controls="calendar year, spring minimum temperature and spring precipitation",
                  not_independent_geographic_replication=True,not_net_seed_dispersal_or_causal_predation=True,
                  same_year_august_not_used=True,submission_hold=True)
    return result
def main():
    try:out=run()
    except Exception as e:out={"status":"STOP_SOURCE_OR_MODEL_SUPPORT","error_class":type(e).__name__,
        "reason":str(e) if type(e) is ValueError and re.fullmatch(r"[A-Z0-9_]+",str(e)) else "UNEXPORTED_ERROR",
        "effect":None,"submission_hold":True}
    out.update(schema="neon.holt.oak_seedling.annual_consumer_bridge.v1",retrieved_utc=datetime.now(timezone.utc).isoformat())
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
