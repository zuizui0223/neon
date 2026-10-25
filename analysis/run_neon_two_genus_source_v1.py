#!/usr/bin/env python3
"""Effect-blind source audit of exactly-two-genus NEON season pairs.

Extract private source matrices but NEVER compute seasonal overlap, unit Z,
null draws, individual movement, density response or habitat coefficient.
Always reproduce original 58 three-genus primary cohort and 216 two-plus
eligible pair denominator before reporting the new disjoint 158-group.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
import json,os

from analysis.run_multiscale_density_estimability_release2026_v3 import (
    PRODUCT,RELEASE,START,END,PRODUCT_URL,QUERY_URL,TOKEN_ENV,
    MAX_DOWNLOAD_WORKERS,_request_json,_site_codes,_inventory,
    _download_many,_read_plot_rows,_read_trap_rows,_candidate_nights,
)
from analysis.audit_multiscale_density_mnka_variation_v1 import _taxonomy
from analysis.audit_neon_crossseason_genus_support_v1 import source_event_support
from analysis.run_neon_crossseason_genus_template_ecology_v1 import verified_support_gate
from analysis.neon_macro_site_selection_v1 import site_metadata_index

ROOT=Path(__file__).resolve().parents[1]
SOURCE_RECEIPT=ROOT/"results/neon_crossseason_genus_template_support_receipt_20261019.json"
OUT=ROOT/"build/neon_exactly_two_genus_source_support_v1.json"
NEON_SITE_META="https://data.neonscience.org/api/v0/sites?release=RELEASE-2026"


def check(x:bool,why:str)->None:
    if not x:raise RuntimeError("NEON_TWO_GENUS_SOURCE_STOP: "+why)


def selection_summary(exact:list[dict],known_three:list[dict],
                      site_metadata:dict[str,dict],
                      *,expected_two:int=158,expected_three:int=58)->dict:
    check(len(exact)==expected_two and len(known_three)==expected_three,
          "exact-two or original >=3 source counts changed")
    def key(u):
        return (u["site"],tuple(u["site_plot"]),u["season_ordinal"])
    keys2={key(u) for u in exact}
    keys3={key(u) for u in known_three}
    check(len(keys2)==len(exact) and len(keys3)==len(known_three)
          and not(keys2 & keys3),"source two/three original seasons overlap")
    check(all(len(u["A"])==len(u["B"])==2 and set(u["A"])==set(u["B"])
              for u in exact),"exact-two group labels incorrect")
    sites2={u["site"] for u in exact}
    sites3={u["site"] for u in known_three}
    check(all(s in site_metadata for s in sites2|sites3),
          "NEON site metadata not mapped to original source")
    domains2={site_metadata[s]["domain"] for s in sites2}
    domains3={site_metadata[s]["domain"] for s in sites3}
    cnt=Counter()
    site_periods=defaultdict(Counter)
    for u in exact:
        site=u["site"];plot=tuple(u["site_plot"]);q=u["season_ordinal"]
        cnt[site_metadata[site]["domain"]]+=1
        for edge in (q,q+1):
            site_periods[site][(plot,edge)]+=1
    reuse_sites={
        site for site,periods in site_periods.items()
        if any(count>1 for count in periods.values())
    }
    clean=[u for u in exact if u["site"] not in reuse_sites]
    check(len(exact)==sum(cnt.values()),"source two-genus region distribution invalid")
    year_counts=Counter(u["season_ordinal"]//4 for u in exact)
    clean_sites={u["site"] for u in clean}
    eligible=(len(exact)>=80 and len(sites2)>=12 and len(domains2)>=8)
    return {
        "schema":"neon.macro.exactly_two_genus_source_support.v1",
        "status":("EXACT_TWO_GENUS_SOURCE_GO_NO_EFFECT_OPENED"
                  if eligible else "STOP_EXACT_TWO_GENUS_MACRO_STRUCTURAL_COVERAGE"),
        "exact_two_source":{
            "pairs":len(exact),"physical_sites":len(sites2),
            "plots":len({tuple(u["site_plot"]) for u in exact}),
            "domains":len(domains2),
            "domains_by_original_qualifying_pair_count":dict(sorted(cnt.items())),
            "source_pair_year_counts":dict(sorted((str(k),v) for k,v in year_counts.items())),
            "source_season_reuse_physical_sites":len(reuse_sites),
            "source_whole_site_disjoint_sensitivity_pairs":len(clean),
            "source_whole_site_disjoint_sensitivity_sites":len(clean_sites),
            "disjoint_sensitivity_exclusion_all_pairs_at_affected_sites":True,
        },
        "original_strict_primary":{
            "pairs":len(known_three),"sites":len(sites3),
            "domains":len(domains3),
            "old_positive_spatial_effects_not_recomputed":True,
        },
        "macro_geographical_comparison":{
            "exact_two_sites_not_in_strict_primary":len(sites2-sites3),
            "original_strict_sites_not_in_exact_two":len(sites3-sites2),
            "sites_common_to_both_source_subsets":len(sites3 & sites2),
            "exact_two_domains_not_in_strict_primary":len(domains2-domains3),
            "strict_primary_domains_not_in_exact_two":len(domains3-domains2),
            "original_source_803_candidate_pairs":803,
            "original_source_216_ge2_genus_diagnostic_pairs":216,
            "exact_two_and_original_strict_primary_nonoverlapping":True,
        },
        "precommitted_source_gate":{
            "minimum_exact_two_pairs":80,
            "minimum_independent_sites":12,
            "minimum_ecological_domains":8,
            "passed":eligible,
            "post_result_historical_exploration_not_new_independent_replication":True,
        },
        "scientific_scope":{
            "new_genus_trap_overlap_computed":False,
            "new_null_distribution_or_Z_computed":False,
            "old_58_original_result_unchanged":True,
            "old_eight_genus_density_generality_failed":True,
            "private_original_site_plot_station_taxon_or_animal_ID_exported":False,
            "nonqualifying_site_or_domain_not_zero_recurrence":True,
            "next":("run pre-locked uniform two-row fixed-margin sampler only"
                    if eligible else "STOP biological effect; record source-only support"),
        },
    }


def original_sources_for_two_genus():
    token=os.environ.get(TOKEN_ENV,"").strip()
    check(bool(token),"NEON original release token absent")
    check((RELEASE,START,END)==("RELEASE-2026","2015-04","2026-09"),
          "original release window changed")
    all_target,genus_by_taxon,_=_taxonomy()
    check(bool(all_target) and bool(genus_by_taxon),"NEON official taxonomic concepts missing")
    sites=_site_codes(_request_json(PRODUCT_URL))
    inventory=_inventory(_request_json(QUERY_URL,token=token,body={
        "productCode":PRODUCT,"siteCodes":sites,
        "startDateMonth":START,"endDateMonth":END,
        "release":RELEASE,"package":"basic","includeProvisional":False,
    }))
    pf=[meta for meta in inventory if "mam_perplotnight" in meta["name"]]
    check((len(inventory),len(pf))==(3547,1773),"original release inventory drift")
    plot_rows=[]
    for meta,raw in zip(pf,_download_many(pf,token,max_workers=MAX_DOWNLOAD_WORKERS)):
        plot_rows.extend(_read_plot_rows(raw,meta["site"],meta["month"]))
    nights,months=_candidate_nights(plot_rows)
    tf=[meta for meta in inventory if "mam_pertrapnight" in meta["name"]
        and (meta["site"],meta["month"]) in months]
    check(len(tf)==1707,"original trap inventory drift")
    trap_rows=[]
    for meta,raw in zip(tf,_download_many(tf,token,max_workers=MAX_DOWNLOAD_WORKERS)):
        for r in _read_trap_rows(raw,nights):
            r["_site"]=meta["site"]
            trap_rows.append(r)
    check((len(plot_rows),len(trap_rows))==(21363,1505827),
          "NEON original source row totals drift")
    strict=[]
    exact=[]
    support=source_event_support(
        plot_rows,trap_rows,genus_by_taxon,
        internal_units=strict,internal_two_genus_units=exact,
    )
    frozen=json.loads(SOURCE_RECEIPT.read_text(encoding="utf-8"))
    verified_support_gate(support,frozen)
    check((len(strict),len(exact),
           support["eligible_2genus_diagnostic_pairs"])==(58,158,216),
          "original diagnostic 216 or 58/158 split changed")
    return strict,exact,{
        "manifest_files_original_verified":len(inventory),
        "downloaded_checksum_verified_capture_files":len(pf)+len(tf),
        "original_trap_rows":len(trap_rows),
        "original_plot_rows":len(plot_rows),
        "original_three_genus_source_support_verification":True,
    }


def run()->dict:
    strict,exact,source=original_sources_for_two_genus()
    token=os.environ.get(TOKEN_ENV,"").strip()
    response=_request_json(NEON_SITE_META)
    data=response.get("data")
    check(isinstance(data,list),"NEON official site/domain metadata unavailable")
    needed={u["site"] for u in strict+exact}
    selected=[r for r in data if r.get("siteCode") in needed]
    meta=site_metadata_index(selected)
    summary=selection_summary(exact,strict,meta)
    return {
        **summary,
        "source_provenance":{
            **source,
            "release":"RELEASE-2026",
            "original_Domain_metadata":"NEON GET /api/v0/sites?release=RELEASE-2026",
            "source_preregistered_original_three_genus_gate_passed":True,
            "new_exact_two_spatial_effects_not_opened":True,
        },
    }


def main()->int:
    try:
        report=run()
        exitcode=0
    except Exception as exc:
        report={
            "schema":"neon.macro.exactly_two_genus_source_support.v1",
            "status":"STOP_SOURCE_RECONSTRUCTION_OR_INVARIANT",
            "error_class":type(exc).__name__,
            "private_source_exception_values_not_exported":True,
            "original_58_ecological_result_not_modified":True,
            "any_new_ecological_effect_opened":False,
        }
        exitcode=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
    return exitcode


if __name__=="__main__":
    raise SystemExit(main())
