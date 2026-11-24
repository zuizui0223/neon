"""Post-result standing-stock / expanding-window stress, same frozen Holt response."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from hashlib import sha256
from math import log1p
import json,re
import numpy as np
from analysis.run_neon_holt_oak_seedling_annual_v1 import (
    ROOT,YEARS,parse_rows,valid_key,plant_annual,covariates,
    PLANT_SHA,CAP_SHA,SOURCES,download_version,req)
OUT=ROOT/"build/neon_holt_seedling_stock_forecast_20261124.json"
LAMBDA=1.0
ERAS=((1999,2004),(2005,2013))

def original_panel(seed,seedling,years=YEARS):
    a=defaultdict(set);b=defaultdict(set)
    for data,by in ((seed,a),(seedling,b)):
        for row in data:
            k=valid_key(row)
            if k and k[0] in years:by[k[0]].add(k[1:])
    req(set(a)==set(years) and set(b)==set(years),"ORIGINAL_YEAR_SUPPORT_DRIFT")
    common=set.intersection(*(by[y] for by in (a,b) for y in years))
    counts=Counter()
    for row in seedling:
        k=valid_key(row)
        if k and k[0] in years and k[1:] in common and oak(row):counts[k]+=1
    return common-{k[1:] for k,n in counts.items() if n>1}

def oak(x):
    return x["FIASP"].strip()=="833" and x["SPEC"].strip()=="5"

def stock_support(seedling,panel,years=YEARS):
    observed=defaultdict(set);rows=defaultdict(list);calendar=set()
    for x in seedling:
        try:y=int(x["YEAR"]);p=int(x["PLOT"]);l=x["LINE"].strip()
        except (ValueError,KeyError):continue
        if l not in {"N","S"} or not 1<=p<=600:continue
        calendar.add(y)
        if (l,p) not in panel:continue
        observed[y].add((l,p))
        if oak(x):rows[y].append(((l,p),x["HT1"].strip()))
    def value(y):
        if observed[y]!=panel:return None,"PANEL_INCOMPLETE"
        rr=rows[y]
        if len({k for k,v in rr})!=len(rr):return None,"DUPLICATE_LITERAL_OAK"
        if any(not re.fullmatch(r"[0-9]+",v) for k,v in rr):return None,"INVALID_LITERAL_HT1"
        return 100*sum(int(v) for k,v in rr)/len(panel),None
    ans={};audit={}
    for y in years:
        earlier=[v for v in calendar if v<y]
        if not earlier:audit[str(y)]={"status":"NO_EARLIER_CENSUS"};continue
        prev=max(earlier);gap=y-prev
        if gap>3:audit[str(y)]={"status":"GAP_OVER_3","previous_year":prev};continue
        v,err=value(prev)
        audit[str(y)]={"status":err or "PRIOR_STOCK_GO","previous_year":prev,"gap":gap}
        if not err:ans[y]=(log1p(v),gap)
    return ans,audit

def matrix(x,mu,sd,aug):
    a=(x-mu)/sd
    base=np.column_stack((np.ones(len(x)),a[:,[0,1,2,3,5,6]]))
    return np.column_stack((base,a[:,4],a[:,1]*a[:,4])) if aug else base

def fit(x,y,aug):
    mu=x.mean(0);sd=x.std(0)
    sd=np.where(sd>1e-12,sd,1.)
    d=matrix(x,mu,sd,aug)
    penalty=np.eye(d.shape[1])*LAMBDA
    penalty[0,0]=0.
    b=np.linalg.solve(d.T@d+penalty,d.T@y)
    req(np.all(np.isfinite(b)),"NONFINITE_RIDGE")
    return b,mu,sd

def predict(ys,cov,stock,years=YEARS):
    use=[y for y in years if y in ys and y in cov and y in stock]
    train0=[y for y in use if y<1999]
    predyears=[y for y in use if y>=1999]
    era_counts=[sum(lo<=y<=hi for y in predyears) for lo,hi in ERAS]
    out={"eligible_years":use,"initial_training_years":train0,
         "prediction_years":predyears,"prediction_era_counts":era_counts,"effect":None}
    if len(use)<18 or len(train0)<9 or len(predyears)<8 or min(era_counts)<3:
        return {**out,"status":"STOP_PRIOR_STOCK_OR_TEMPORAL_SUPPORT"}
    x=np.array([list(cov[y])+list(stock[y]) for y in use],float)
    z=np.array([log1p(ys[y]) for y in use],float)
    req(np.all(np.isfinite(x)) and np.all(np.isfinite(z)),"NONFINITE_INPUT")
    b,_,_=fit(x,z,True)
    low=float(b[-2]-b[-1]);high=float(b[-2]+b[-1]);interaction=float(b[-1])
    errors=[]
    for y in predyears:
        j=use.index(y)
        mask=np.array([t<y for t in use])
        req(mask.sum()>=9,"INSUFFICIENT_PAST_ONLY_TRAINING")
        predictions=[]
        for aug in (False,True):
            beta,mu,sd=fit(x[mask],z[mask],aug)
            predictions.append(float(matrix(x[j:j+1],mu,sd,aug)[0]@beta))
        errors.append((y,(predictions[0]-z[j])**2,(predictions[1]-z[j])**2,(stock[y][0]-z[j])**2))
    def rms(rows,k):return float(np.sqrt(np.mean([row[k] for row in rows])))
    rm0,rm1,rmp=(rms(errors,k) for k in (1,2,3))
    era=[]
    for lo,hi in ERAS:
        ee=[row for row in errors if lo<=row[0]<=hi]
        era.append({"years":[lo,hi],"n":len(ee),"baseline_RMSE":rms(ee,1),
                    "augmented_RMSE":rms(ee,2),"persistence_RMSE":rms(ee,3)})
    gates={"low_seed_negative":low<0,"interaction_positive":interaction>0,
           "beats_stock_baseline":rm1<rm0,"beats_persistence":rm1<rmp,
           "both_eras_improve":all(e["augmented_RMSE"]<e["baseline_RMSE"] for e in era)}
    return {**out,"status":"POST_RESULT_STOCK_FORECAST_STRESS_SUPPORTED" if all(gates.values()) else "POST_RESULT_STOCK_FORECAST_STRESS_NOT_SUPPORTED",
            "effect":{"gates":gates,"ridge_lambda":LAMBDA,"mouse_low_seed_slope":low,
                      "mouse_high_seed_slope":high,"mouse_seed_interaction":interaction,
                      "baseline_past_trained_RMSE":rm0,"augmented_past_trained_RMSE":rm1,
                      "persistence_RMSE":rmp,"era_RMSE":era,"no_p_value_or_causal_claim":True}}

def run():
    from playwright.sync_api import sync_playwright
    raw={}
    with sync_playwright() as pw:
        browser=pw.chromium.launch()
        for kind,(url,n,fields) in SOURCES.items():
            page=browser.new_page(accept_downloads=True)
            try:blob=download_version(page,url)
            finally:page.close()
            req(sha256(blob).hexdigest()==PLANT_SHA[kind],"PINNED_PLANT_BYTES_DRIFT")
            raw[kind]=parse_rows(blob,n)
        browser.close()
    ys,report=plant_annual(raw["seedfall"],raw["seedling"])
    panel=original_panel(raw["seedfall"],raw["seedling"])
    req(len(panel)==report["fixed_surveyed_plots"]==116,"ORIGINAL_PANEL_DRIFT")
    stock,audit=stock_support(raw["seedling"],panel)
    out=predict(ys,covariates(),stock)
    return {**out,"prior_census_support":audit,"primary_panel":116,
            "primary_original_result_unchanged":True,"post_result_same_source_stress":True,
            "only_past_response_years_used_for_prediction":True,
            "conditional_on_observed_spring_weather_and_retrospective_panel":True,
            "not_germination_or_seed_fate":True,"submission_hold":True,
            "plant_SHA256":PLANT_SHA,"capture_SHA256":CAP_SHA}
def main():
    try:out=run()
    except Exception as exc:out={"status":"STOP_SOURCE_OR_MODEL","error_class":type(exc).__name__,
        "reason":str(exc) if type(exc) is ValueError and re.fullmatch(r"[A-Z0-9_]+",str(exc)) else "UNEXPORTED_ERROR",
        "effect":None,"submission_hold":True}
    out.update(schema="neon.holt.seedling_stock_forecast_stress.v1",retrieved_utc=datetime.now(timezone.utc).isoformat())
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=="__main__":raise SystemExit(main())
