"""Pure, source-blind NEON tower temperature 30min weather feature logic.

Only provider MD5-verified, exact RELEASE-2026 source records may enter.
These functions never use mammal R, Z, tag IDs, trap coordinates or habitat.
"""
from __future__ import annotations
import csv,io,math,calendar,re
from statistics import mean


# Official NEON Instrumented Systems archive file naming:
# NEON.DOM.SITE.DPL.PRNUM.REV.HOR.VER.TMI.DESC.YYYY-MM.PKGTYPE.GENTIME.csv
# https://data.neonscience.org/file-naming-conventions
# Prior regex omitted .YYYY-MM.basic.GENTIME and rejected source months.
NAME=re.compile(r"\.(\d{3})\.030\.SAAT_30min\.(\d{4}-\d{2})\.basic\.(\d{8}T\d{6}Z)\.csv$")


def position(name:str)->str|None:
    m=NAME.search(str(name))
    return m.group(1) if m else None


def select_fixed_temperature_file(records:list[dict])->dict|None:
    """Lowest literal archived sensor index, no rescue by later outcomes."""
    eligible=[]
    for r in records:
        name=str(r.get("name") or "")
        pos=position(name)
        if not pos:continue
        size=r.get("size")
        url=str(r.get("url") or "")
        checksum=str(r.get("md5") or "").lower()
        if isinstance(size,bool) or not isinstance(size,int) or size<=0 or size>15000000:
            continue
        if len(checksum)!=32 or not all(c in "0123456789abcdef" for c in checksum):
            continue
        if not url.startswith("https://"):
            continue
        eligible.append({**r,"position":pos})
    return min(eligible,key=lambda x:(x["position"],x["name"])) if eligible else None


def aggregate_qc_month(raw:bytes,month:str,*,min_valid_fraction:float=.70)->dict:
    """Mean temperature using only finalQF0 finite, physically plausible rows.

    Day/month label is known *only from provider archive*, not capture date,
    and retained in RAM. Never infer weather at the rodent trapping grid.
    """
    if not isinstance(raw,bytes):
        raise ValueError("NEON weather source bytes required")
    try:
        year,mon=map(int,month.split("-"))
        expected=calendar.monthrange(year,mon)[1]*48
    except (ValueError,TypeError,IndexError):
        raise ValueError("Bad provider weather month") from None
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    names=set(reader.fieldnames or [])
    if not {"startDateTime","endDateTime","tempSingleMean","finalQF"} <= names:
        return {"status":"STOP_SOURCE_WEATHER_COLUMNS","total_rows":0,
                "finite_QF0_rows":0,"required_rows":expected}
    total=0
    values=[]
    duplicates=0
    seen=set()
    flags={"QF0":0,"QF1":0,"MISSING_OR_OTHER":0}
    for row in reader:
        total+=1
        t=str(row.get("startDateTime") or "").strip()
        if t in seen:duplicates+=1
        seen.add(t)
        f=str(row.get("finalQF") or "").strip()
        key="QF0" if f=="0" else "QF1" if f=="1" else "MISSING_OR_OTHER"
        flags[key]+=1
        if f!="0":continue
        x=str(row.get("tempSingleMean") or "").strip()
        try: val=float(x)
        except ValueError:continue
        if not math.isfinite(val) or not -90 <= val <= 65:continue
        values.append(val)
    fraction=len(values)/expected
    okay=(duplicates==0 and total>=expected*.70
          and total<=expected*1.10 and fraction>=min_valid_fraction)
    return {
        "status":"TOWER_TEMP_MONTH_QC_PASS" if okay else "STOP_TOWER_TEMP_MONTH_QC",
        "total_rows":total,
        "finite_QF0_rows":len(values),
        "expected_30min_rows":expected,
        "finite_QF0_fraction_of_expected":fraction,
        "duplicate_30min_start_time_rows":duplicates,
        "final_flag0_rows":flags["QF0"],
        "final_flag1_rows":flags["QF1"],
        "other_or_missing_flag_rows":flags["MISSING_OR_OTHER"],
        # Internal valid climate value only; the public summary only
        # includes aggregate cross-site/month distributions, never
        # source date or site-specific temperature.
        "_private_mean_celsius":mean(values) if okay else None,
    }


def source_month_selection(units:list[dict],availability:dict)->tuple[list[dict],set[tuple[str,str]]]:
    """Original cohorts only. No climate values or observed ecology scores."""
    selected=[]
    necessary=set()
    for u in units:
        datesA=u.get("capture_dates_A")
        datesB=u.get("capture_dates_B")
        if not isinstance(datesA,tuple) or not isinstance(datesB,tuple) or len(datesA)!=3 or len(datesB)!=3:
            raise ValueError("Original source three-date event missing")
        ma={z.isoformat()[:7] for z in datesA}
        mb={z.isoformat()[:7] for z in datesB}
        if len(ma)!=1 or len(mb)!=1 or ma==mb:
            continue
        one=next(iter(ma))
        two=next(iter(mb))
        site=u["site"]
        if one not in availability.get(site,set()) or two not in availability.get(site,set()):
            continue
        selected.append({"unit":u,"site":site,"monthA":one,"monthB":two})
        necessary.update(((site,one),(site,two)))
    return selected,necessary


def _month_catalog(query:dict,required:set[tuple[str,str]])->dict:
    """NEON /data/query basic packages across exact release only."""
    root=query.get("data")
    if not isinstance(root,dict):
        raise ValueError("Source release data-query schema unavailable")
    blocks=root.get("releases")
    if not isinstance(blocks,list):
        raise ValueError("Source release packages not a list")
    current=[r for r in blocks if isinstance(r,dict) and r.get("release")=="RELEASE-2026"]
    if len(current)!=1:
        raise ValueError("Original weather RELEASE-2026 block missing")
    all_files={}
    for pkg in current[0].get("packages",[]):
        if not isinstance(pkg,dict) or pkg.get("packageType")!="basic":
            continue
        site=pkg.get("siteCode")
        month=pkg.get("month")
        key=(site,month)
        if key not in required:
            continue
        opts=all_files.setdefault(key,[])
        for file in pkg.get("files",[]):
            if isinstance(file,dict) and "SAAT_30min" in str(file.get("name") or ""):
                opts.append(file)
    return {key:select_fixed_temperature_file(all_files.get(key,[]))
            for key in required}


def climate_site_model(records:list[dict],*,seed:int=2026102521,n_bootstrap:int=2000)->dict:
    """Single declared between-physical-site response with latitude/season mix."""
    import numpy as np
    from random import Random
    if not isinstance(seed,int) or n_bootstrap<100:
        raise ValueError("Bad prespecified bootstrap configuration")
    if len(records)<18 or len({r["site"] for r in records})!=len(records):
        return {"status":"STOP_TOO_FEW_UNIQUE_WEATHER_SOURCE_SITES",
                "ecological_temperature_slope_fitted":False}
    # Site fixed grain (one point/site) prevents pseudo-replicating all
    # original seasonal and station rows as independent ecosystems.
    rows=sorted(records,key=lambda r:r["site"])
    X=np.array([[1.,float(r["mean_abs_delta_C"])/5.,
                 (float(r["site_latitude"])-40.)/10.,
                 float(r["fraction_summer_to_autumn"])]
                 for r in rows],dtype=float)
    yy=np.array([float(r["site_mean_original_exact_Z"]) for r in rows])
    if not np.all(np.isfinite(X)) or not np.all(np.isfinite(yy)):
        raise ValueError("Climate-site regression fields nonfinite")
    if np.linalg.matrix_rank(X)!=4:
        return {"status":"STOP_SITE_CLIMATE_LATITUDE_SEASON_DESIGN_RANK",
                "ecological_temperature_slope_fitted":False,
                "original_physical_sites":len(records)}
    coef=np.linalg.lstsq(X,yy,rcond=None)[0]
    rng=Random(seed)
    boot=[]
    fails=0
    for k in range(n_bootstrap):
        inds=[rng.randrange(len(rows)) for _ in rows]
        bx=X[inds,:]
        if np.linalg.matrix_rank(bx)<4:
            fails+=1
        else:
            boot.append(float(np.linalg.lstsq(bx,yy[inds],rcond=None)[0][1]))
    if len(boot)/n_bootstrap <.95:
        return {"status":"STOP_SITE_WEATHER_BOOTSTRAP_UNIDENTIFIABLE",
                "ecological_temperature_slope_fitted":False,
                "original_physical_sites":len(records),
                "valid_site_bootstrap_fraction":len(boot)/n_bootstrap}
    boot.sort()
    def quantile(p):
        ix=p*(len(boot)-1)
        lo=int(ix)
        hi=min(len(boot)-1,lo+1)
        w=ix-lo
        return boot[lo]*(1-w)+boot[hi]*w
    loo=[]
    for idx in range(len(rows)):
        take=[i for i in range(len(rows)) if i!=idx]
        if np.linalg.matrix_rank(X[take,:])!=4:
            return {"status":"STOP_SITE_LOSO_CLIMATE_MODEL_RANK",
                    "ecological_temperature_slope_fitted":False}
        loo.append(float(np.linalg.lstsq(X[take,:],yy[take],rcond=None)[0][1]))
    slope=float(coef[1])
    return {
        "status":"SOURCE_QC_SUPPORTED_HISTORICAL_EXPLORATORY_THERMAL_ASSOCIATION",
        "ecological_temperature_slope_fitted":True,
        "physical_site_independent_units":len(rows),
        "beta_recurrence_Z_per_5C_abs_seasonal_monthly_tower_temp_change":slope,
        "site_bootstrap_2000_draws_requested":n_bootstrap,
        "site_bootstrap_draws_valid":len(boot),
        "site_cluster_bootstrap_95_interval":[quantile(.025),quantile(.975)],
        "latitudinal_adjustment_beta_per_10_degrees":float(coef[2]),
        "season_transition_mix_beta":float(coef[3]),
        "LOSO_beta_thermal_min":min(loo),
        "LOSO_beta_thermal_max":max(loo),
        "LOSO_fraction_same_beta_sign":sum(x*slope>0 for x in loo)/len(loo),
        "thermal_decay_hypothesis_negative_beta":slope<0,
        "bootstrap_interval_strictly_negative":quantile(.975)<0,
        "not_new_independent_observational_release":True,
        "genus_specific_detection_and_grid_habitat_unmeasured":True,
        "site_weather_monthly_tower_temperature_not_grid_microclimate":True,
        "no_site_ID_or_individual_source_climate_value_exported":True,
    }
