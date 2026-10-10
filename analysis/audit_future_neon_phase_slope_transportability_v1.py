#!/usr/bin/env python3
"""Post-result cohort-transportability audit for NEON Peromyscus slopes.

Read only two previously archived development and prospectively opened,
event-disjoint provisional-derived artifacts plus the outcome-blind 287-row
historical-MNKA predictor manifest. No NEON API calls, no subgroup discovery,
no ecological moderator fitting, and no new candidate hypothesis.

The already exposed positive development versus negative provisional future
Delta slopes are compared on 3 fully declared geography-matching scopes.
Source/site block-clustered variance allows scores from a single NEON site
to be correlated across both periods.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

# Heavy optional analysis packages are imported only within the dedicated
# transportability workflow. Core repository paper checks need no pandas.

EXPECTED_DEVELOPMENT_N=1326
EXPECTED_FUTURE_N=287
EXPECTED_DEVELOPMENT_PE=956
EXPECTED_FUTURE_PE=127
DEV_BETA=15.93005706925735
FUTURE_BETA=-7.072964939150511
TOL=1e-7

FORMULA=(
    "D_m2 ~ 0 + C(phase):C(series_id) + C(phase):C(site_month)"
    " + C(phase):C(year) + C(phase):mnka"
)


def join_new(metrics, predictors):
    def key(r):
        return (r["taxon"],r["site"],r["plot_id"],r["event_id"])
    m={key(r):r for r in metrics}
    p={key(r):r for r in predictors}
    if len(m)!=EXPECTED_FUTURE_N or len(p)!=EXPECTED_FUTURE_N or set(m)!=set(p):
        raise RuntimeError("future predictor/metric manifest drift")
    out=[]
    for k in sorted(m):
        s=m[k];v=p[k]
        if s["genus"]!=v["genus"]:
            raise RuntimeError("future genus drift")
        out.append({
            "taxon":s["taxon"],"genus":s["genus"],
            "site":s["site"],"plot_id":s["plot_id"],"event_id":s["event_id"],
            "series_id":"|".join((s["taxon"],s["site"],s["plot_id"])),
            "site_month":s["site"]+"|"+v["date"][5:7],
            "year":v["date"][:4],
            "mnka":int(v["genus_mnka"]),
            "D_m2":float(s["D_m2"]),
        })
    return out


def future_varying_cohort(rows):
    per=[r for r in rows if r["genus"]=="Peromyscus"]
    by_series=defaultdict(list)
    for r in per:by_series[r["series_id"]].append(r)
    eligible={name for name,rr in by_series.items()
              if len(rr)>=3 and len({r["mnka"] for r in rr})>=2}
    return [r for r in per if r["series_id"] in eligible]


def site_phase_difference(old,new):
    import pandas as pd
    import scipy.stats as stats
    import statsmodels.formula.api as smf
    if not old or not new:raise ValueError("empty comparison phase")
    data=pd.DataFrame([{**r,"phase":"old"} for r in old]+
                      [{**r,"phase":"new"} for r in new])
    g=data["site"].nunique()
    if g<10:raise ValueError("fewer than 10 independent site clusters")
    fit=smf.ols(FORMULA,data=data).fit(
        cov_type="cluster",
        cov_kwds={"groups":data["site"],"use_correction":True},
    )
    o="C(phase)[old]:mnka"
    n="C(phase)[new]:mnka"
    if o not in fit.params or n not in fit.params:
        raise RuntimeError("unidentified prospective phase slope")
    bo=float(fit.params[o]);bn=float(fit.params[n])
    cov=fit.cov_params()
    vv=float(cov.loc[o,o]+cov.loc[n,n]-2*cov.loc[o,n])
    if not math.isfinite(vv) or vv<0:
        raise RuntimeError("invalid site-cluster cross-phase uncertainty")
    se=math.sqrt(vv)
    diff=bn-bo
    crit=float(stats.t.ppf(0.975,g-1))
    return {
        "n_dev":len(old),"n_provisional":len(new),
        "sites":int(g),
        "dev_beta_delta":bo,"provisional_beta_delta":bn,
        "provisional_minus_dev_delta_slope":diff,
        "se_site_cluster_phase_difference":se,
        "CI95_site_cluster_t_df_sites_minus1":[diff-crit*se,diff+crit*se],
        "site_cluster_df":g-1,
        "fixed_effect_structure":"phase-specific taxon-plot, site-month and year",
        "state":"POST_RESULT_DESCRIPTIVE_NOT_REGIME_SHIFT_CONFIRMATION",
    }


def run(development,metrics,predictors):
    if len(development)!=EXPECTED_DEVELOPMENT_N:
        raise RuntimeError("frozen development 1326-session artifact drift")
    new=join_new(metrics,predictors)
    future=future_varying_cohort(new)
    dev=[r for r in development if r["genus"]=="Peromyscus"]
    if len(dev)!=EXPECTED_DEVELOPMENT_PE or len(future)!=EXPECTED_FUTURE_PE:
        raise RuntimeError("prospective Peromyscus cohort drift")
    new_sites={r["site"] for r in future}
    shared_series={r["series_id"] for r in future}&{
        r["series_id"] for r in dev}
    matched_dev=[r for r in dev if r["series_id"] in shared_series]
    matched_future=[r for r in future if r["series_id"] in shared_series]
    scopes={
        "all_development_vs_new":(dev,future),
        "same_sites_only":([r for r in dev if r["site"] in new_sites],future),
        "same_taxon_site_plot_series":(matched_dev,matched_future),
    }
    results={k:site_phase_difference(a,b) for k,(a,b) in scopes.items()}
    reference=results["all_development_vs_new"]
    if abs(reference["dev_beta_delta"]-DEV_BETA)>TOL:
        raise RuntimeError("primary development Peromyscus effect mismatch")
    if abs(reference["provisional_beta_delta"]-FUTURE_BETA)>TOL:
        raise RuntimeError("prospective Peromyscus effect mismatch")
    return {
        "schema":"neon.peromyscus_provisional_slope_transportability_v1",
        "status":"POST_RESULT_COHORT_TRANSPORTABILITY_DIAGNOSTIC",
        "source_release_dev":"RELEASE-2026",
        "source_new":"2025-2026 provisional non-overlapping event IDs, not official fixed release",
        "provenance":{
            "development_geometry_run":37793401501,
            "future_metric_only_run":38046250920,
            "future_history_pair_run":38046339017,
            "prospective_effect_run":38046615310,
        },
        "total_provisional_metric_sessions":len(new),
        "peromyscus_future_varying_sessions":len(future),
        "shared_sites_in_analysis":len(new_sites),
        "matched_taxon_site_plot_series":len(shared_series),
        "matched_dev_sessions":len(matched_dev),
        "matched_future_sessions":len(matched_future),
        "new_years":dict(sorted(Counter(r["year"] for r in future).items())),
        "dev_years":dict(sorted(Counter(str(r["year"]) for r in dev).items())),
        "mnka_range_dev":[min(r["mnka"] for r in dev),max(r["mnka"] for r in dev)],
        "mnka_range_new":[min(r["mnka"] for r in future),max(r["mnka"] for r in future)],
        "slopes":results,
        "hypothesis_boundary":(
            "A point-estimate sign reversal and failure to replicate an earlier "
            "directional prediction are observed. Difference intervals include "
            "zero and do NOT support claiming a statistically identified "
            "ecological regime switch or a novel compensatory mechanism. "
            "Scopes chosen after effects to diagnose dataset transportability; "
            "no post-hoc subgroup success may rescue the original hypothesis."
        ),
        "old_six_of_eight_genus_guard":"FAILED_UNCHANGED",
        "new_five_genus_directional_confirmation":"NOT_ESTIMABLE",
        "species_mechanism_or_territoriality_claimed":False,
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--development",required=True,type=Path)
    parser.add_argument("--future-metric",required=True,type=Path)
    parser.add_argument("--future-mnka",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    a=parser.parse_args()
    try:
        result=run(
            json.loads(a.development.read_text()),
            json.loads(a.future_metric.read_text()),
            json.loads(a.future_mnka.read_text()),
        )
    except (RuntimeError,ValueError) as ex:
        result={
            "schema":"neon.peromyscus_provisional_slope_transportability_v1",
            "status":"STOP_SOURCE_OR_ESTIMATOR_DRIFT",
            "error":str(ex),
            "positive_ecological_claim_authorized":False,
        }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    if result["status"]!="POST_RESULT_COHORT_TRANSPORTABILITY_DIAGNOSTIC":
        raise SystemExit(3)
