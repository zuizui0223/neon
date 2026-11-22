#!/usr/bin/env python3
"""Post-result direct 14-site NEON fixed-fixed null calibration.

We REPLAY EXACTLY the archived 58 spatial units and their original
2,000-draw fixed-fixed nulls, with the SAME random seeds and the SAME
source bytes. Private null overlap arrays remain in RAM only. Then we
sample a calibrated grand 14-site statistic directly from those nulls.

This tests a *specific validity assumption* of the already-opened p from
site sign flips. It is NOT an independent new ecological dataset, and
does not re-fit the failed density W/B hypothesis or change the old p.
"""
from __future__ import annotations

import json
import math
import os
from collections import defaultdict
from pathlib import Path
from statistics import mean

from analysis.run_multiscale_density_estimability_release2026_v3 import (
    PRODUCT, RELEASE, START, END, PRODUCT_URL, QUERY_URL, TOKEN_ENV,
    MAX_DOWNLOAD_WORKERS, _request_json, _site_codes, _inventory,
    _download_many, _read_plot_rows, _read_trap_rows, _candidate_nights,
)
from analysis.audit_multiscale_density_mnka_variation_v1 import _taxonomy
from analysis.audit_neon_crossseason_genus_support_v1 import source_event_support
from analysis.run_neon_crossseason_genus_template_ecology_v1 import (
    verified_support_gate, SEED, N_DRAWS, N_BURN, SWAPS, MIN_ESS
)
from analysis.neon_crossseason_template_null_v1 import (
    fixed_fixed_null_for_unit, crossseason_template_inference
)
from analysis.neon_crossseason_direct_site_null_v1 import (
    direct_site_null_calibration
)

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SUPPORT=ROOT/"results/neon_crossseason_genus_template_support_receipt_20261019.json"
PRIMARY=ROOT/"results/neon_crossseason_genus_template_ecology_receipt_20261019.json"
OUT=ROOT/"build/neon_crossseason_direct_site_null_calibration_v1.json"

META_SEED=2026101929
META_DRAWS=20000


def require(cond,msg):
    if not cond:
        raise RuntimeError("FROZEN ORIGINAL NEON OUTCOME REPLAY STOP: "+msg)


def _original_source_units()->tuple[list[dict],dict,dict]:
    frozen=json.loads(SOURCE_SUPPORT.read_text(encoding="utf-8"))
    old=json.loads(PRIMARY.read_text(encoding="utf-8"))
    require(RELEASE=="RELEASE-2026" and START=="2015-04" and END=="2026-09",
            "original source date/version changed")
    require(old["status"]=="SUPPORT_MULTI_SITE_GENUS_TEMPLATE_REASSEMBLY" and
            old["source"]["original_pre_effect_source_gate_reproduced"],
            "original 14-site ecological receipt unavailable")
    token=os.environ.get(TOKEN_ENV,"").strip()
    require(bool(token),"original authorized immutable NEON source missing")
    all_target,genus_by_taxon,_=_taxonomy()
    sites=_site_codes(_request_json(PRODUCT_URL))
    inventory=_inventory(_request_json(
        QUERY_URL,token=token,body={
            "productCode":PRODUCT,
            "siteCodes":sites,
            "startDateMonth":START,
            "endDateMonth":END,
            "release":RELEASE,
            "package":"basic",
            "includeProvisional":False,
        },
    ))
    require(len(inventory)==3547,
            "original source manifest count changed")
    plot_files=[r for r in inventory if "mam_perplotnight" in r["name"]]
    require(len(plot_files)==1773,"original plot files changed")
    plots=[]
    for m,raw in zip(plot_files,_download_many(
        plot_files,token,max_workers=MAX_DOWNLOAD_WORKERS
    )):
        plots.extend(_read_plot_rows(raw,m["site"],m["month"]))
    nights,site_months=_candidate_nights(plots)
    trap_files=[r for r in inventory
                if "mam_pertrapnight" in r["name"]
                and (r["site"],r["month"]) in site_months]
    require(len(trap_files)==1707,"original trap files changed")
    traps=[]
    for m,raw in zip(trap_files,_download_many(
        trap_files,token,max_workers=MAX_DOWNLOAD_WORKERS
    )):
        for row in _read_trap_rows(raw,nights):
            row["_site"]=m["site"]
            traps.append(row)
    require(len(plots)==21363 and len(traps)==1505827,
            "original NEON archive row universe changed")

    private=[]
    source=source_event_support(plots,traps,genus_by_taxon,internal_units=private)
    verified_support_gate(source,frozen)
    require(len(private)==58,"original 58 seasonal units changed")
    return private,old,{
        "source_files_MD5_checked":len(inventory),
        "source_plot_rows":len(plots),
        "source_trap_rows":len(traps),
        "original_58_source_support_reproduced":True,
    }


def run()->dict:
    private,archived,src=_original_source_units()
    require(
        SEED==2026101901 and N_DRAWS==2000 and N_BURN==1000
        and SWAPS==40 and MIN_ESS==200,
        "original null model draw configuration changed"
    )
    ordered=sorted(private,key=lambda u:(
        u["site"],u["site_plot"],u["season_ordinal"],
    ))
    original_unit=archived["informative_unit_source_geometry_summary"]["unlabelled_unit_diagnostics"]
    require(len(original_unit)==len(ordered)==58,
            "Original 58 per-unit receipt length changed")

    source_null_unit=[]
    by_site=defaultdict(list)
    min_effective_null=float("inf")
    for idx,(u,old) in enumerate(zip(ordered,original_unit)):
        draws=[]
        replay=fixed_fixed_null_for_unit(
            u["A"],u["B"],seed=SEED+idx,n_draws=N_DRAWS,
            burn_in=N_BURN,swaps_per_draw=SWAPS,min_effective_draws=MIN_ESS,
            private_draws_out=draws,
        )
        require(
            replay["status"]=="INFORMATIVE_FIXED_FIXED_NULL"
            and old["status"]==replay["status"]
            and len(draws)==N_DRAWS,
            "original fixed-fixed null chain not fully informative"
        )
        for key1,key2 in [
            ("z","z"),
            ("source_genera","source_genera"),
            ("season_A_observed_genus_trap_cells",
             "observed_genus_trap_cells_season_A"),
            ("season_B_observed_genus_trap_cells",
             "observed_genus_trap_cells_season_B"),
            ("lag1_overlap_autocorrelation","lag1_overlap_autocorrelation"),
            ("approx_effective_null_draws_lag1","approx_effective_null_draws_lag1"),
            ("swap_acceptance_rate","swap_acceptance_rate"),
        ]:
            if not math.isclose(
                float(replay[key1]),float(old[key2]),rel_tol=1e-10,abs_tol=1e-10,
            ):
                raise RuntimeError("Original source unit value changed: "+key1)
        min_effective_null=min(
            min_effective_null,replay["approx_effective_null_draws_lag1"]
        )
        by_site[u["site"]].append(replay["z"])
        norm=[(x-replay["null_mean"])/replay["null_sd"] for x in draws]
        source_null_unit.append({
            "site":u["site"],
            "observed_unit_z":replay["z"],
            "null_unit_z_draws":norm,
        })

    recomputed_site=crossseason_template_inference(by_site,seed=SEED)
    archived_site=archived["independent_site_ecology"]
    require(recomputed_site["physical_sites"]==14,"original site count changed")
    require(recomputed_site["informative_seasonal_units"]==58,
            "original informative seasonal units changed")
    require(
        math.isclose(
            recomputed_site["site_mean_Z_mean"],
            archived_site["site_mean_Z_mean"],
            rel_tol=0,abs_tol=1e-10,
        )
        and math.isclose(
            recomputed_site["one_sided_site_signflip_p"],
            archived_site["one_sided_site_signflip_p"],
            rel_tol=0,abs_tol=1e-12,
        )
        and all(math.isclose(x,y,rel_tol=0,abs_tol=1e-10)
                for x,y in zip(
                    recomputed_site["site_Z_means_sorted_ascending"],
                    archived_site["site_Z_means_sorted_ascending"],
                )),
        "original exact site inference no longer reproduces"
    )
    derived=direct_site_null_calibration(
        source_null_unit,seed=META_SEED,n_replicates=META_DRAWS,
    )
    require(
        derived["source_independent_physical_sites"]==14
        and derived["source_original_seasonal_units"]==58
        and math.isclose(
            derived["observed_equal_site_weighted_mean_Z"],
            archived_site["site_mean_Z_mean"],rel_tol=0,abs_tol=1e-10,
        ),
        "direct-null source site or test statistic changed"
    )

    ind=derived["independent_unit_marginal_null"]["one_sided_p"]
    correlated=derived["comonotone_within_site_marginal_null"]["one_sided_p"]
    status=(
        "POST_RESULT_DIRECT_FIXED_FIXED_NULL_SUPPORTS_PATTERN_UNDER_BOTH_COUPLINGS"
        if ind<0.05 and correlated<0.05 else
        "POST_RESULT_DIRECT_FIXED_FIXED_NULL_WEAKENS_ORIGINAL_INFERENCE"
    )
    return {
        **derived,
        "schema":"neon.direct_nested_genus_recurring_site_null_validation.v1",
        "status":status,
        "source":src,
        "exact_original_primary_reproduction":{
            "all_58_unit_Z_and_MCMC_diagnostics_match_archived":True,
            "original_14_sorted_site_means_match_archived":True,
            "original_exact_signflip_p_unchanged":archived_site["one_sided_site_signflip_p"],
            "original_physical_site_mean_Z_unchanged":archived_site["site_mean_Z_mean"],
            "minimum_original_unit_null_lag1_ESS":min_effective_null,
        },
        "scientific_boundary":{
            "two_direct_null_couplings_are_post_result_checks":True,
            "original_signflip_p_not_an_unconditional_exact_ecological_null":True,
            "conditional_fixed_fixed_null_generating_mechanism_assumed":True,
            "same_site_reused_season_dependence_not_known":True,
            "comonotone_sensitivity_not_guaranteed_global_bound":True,
            "no_p_value_selection_or_pooled_significance":True,
            "same_original_58_pairs_and_14_sites":True,
            "no_new_animal_or_genus_ecological_response_selected":True,
            "no_competition_habitat_filtering_or_detection_causation_proven":True,
            "density_W_B_original_generalization":"FAILED_5_OF_8",
            "fixed_total_F_C_historical_direct_match":"NONE_UNDER_QUALIFIER",
            "MOSA_W_B":"SEALED",
            "species_level_and_genus_level_San_Jacinto_NEON_not_pooled":True,
            "all_original_unit_null_vectors_dropped_after_computation":True,
            "raw_tags_sites_or_trap_positions_exported":False,
        }
    }


def main() -> int:
    try:
        result=run()
    except Exception as exc:
        result={
            "schema":"neon.direct_nested_genus_recurring_site_null_validation.v1",
            "status":"STOP_REPRODUCIBILITY_OR_MCMC",
            "diagnostic":str(exc)[:650],
            "site_null_recalibration_successful":False,
            "original_eight_genus_density_generality":"FAILED_5_OF_8",
            "MOSA_W_B":"SEALED",
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                   encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 3 if result["status"]=="STOP_REPRODUCIBILITY_OR_MCMC" else 0


if __name__=="__main__":
    raise SystemExit(main())
