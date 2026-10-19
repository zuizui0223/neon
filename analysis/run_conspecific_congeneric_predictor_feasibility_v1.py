#!/usr/bin/env python3
"""One-time, effect-BLIND species vs congener MNKA feasibility, RELEASE-2026.

Independently reproduces the original complete 3-night NEON structural
response universe, source taxon histories and genus MNKA definition without
reading W, B, centroid locations, spatial distances or ecological slopes.
All outputs are aggregated by genus. This cannot confirm the previously
FAILED multigenus packing hypothesis or refit previously viewed outcomes.
"""
from __future__ import annotations

import csv
import io
import json
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from analysis.audit_multiscale_density_estimability_v1 import audit
from analysis.audit_multiscale_density_mnka_variation_v1 import (
    _capture_status, _taxonomy, TAXONOMY_URL, SATURATION_MAX, MIN_REPEAT, COMPLETE
)
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    PRODUCT, RELEASE, START, END, PRODUCT_URL, QUERY_URL, TOKEN_ENV,
    MAX_DOWNLOAD_WORKERS,
    _request_json, _site_codes, _inventory, _download_many,
    _read_plot_rows, _read_trap_rows, _candidate_nights, _write_csv,
)
from analysis.conspecific_congeneric_predictor_support_v1 import (
    GROUP_TAXON_IDS, event_predictors, response_predictor_rows,
    genus_support,
)
from analysis.audit_neon_u_adjusted_fixed_total_support_v1 import (
    fixed_total_genus_support,
)
from analysis.audit_neon_fixed_total_observed_pairs_v1 import (
    observed_fixed_total_pairs,
)

ROOT=Path(__file__).resolve().parents[1]
LOCK=ROOT/"results/multiscale_density_target_taxon_lock_v1.json"
OLD=ROOT/"results/multiscale_density_mnka_variation_decision_v1.json"
OUT=ROOT/"build/conspecific_congeneric_predictor_feasibility_v1.json"


def require(condition: bool, message: str):
    if not condition:
        raise RuntimeError("SOURCE-INVARIANT STOP: "+message)


def run() -> dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    if not token:
        raise RuntimeError("NEON_API_TOKEN is required for versioned NEON data")
    frozen=json.loads(OLD.read_text(encoding="utf-8"))
    lock=json.loads(LOCK.read_text(encoding="utf-8"))
    require(RELEASE=="RELEASE-2026","unexpected historical release")
    require(frozen["status"]=="GENUS_MNKA_STRUCTURE_GO","prior frozen genus MNKA")
    all_target, genus_by_taxon, names_by_taxon=_taxonomy()
    original_target=set(lock["target_taxon_ids"])
    require(original_target.issubset(all_target),"frozen taxonomy target roster unavailable")
    require(GROUP_TAXON_IDS.issubset(original_target),"four original species-group taxa missing")
    require(len(GROUP_TAXON_IDS)==4,"species-group set drift")
    # The original source may contain target species not in the 44-concept
    # analysis-response roster. They are still valid OTHER congeners when
    # taxonomy confirms species rank; do not mislabel them unresolved.
    rank_payload=_request_json(TAXONOMY_URL)
    taxon_ranks=defaultdict(set)
    for z in rank_payload["data"]:
        tid=str(z.get("taxonID") or "").strip()
        if tid in all_target and str(z.get("taxonProtocolCategory") or "").strip().lower()=="target":
            taxon_ranks[tid].add(str(z.get("dwc:taxonRank") or "").strip())
    require(all(len(taxon_ranks[t])==1 for t in all_target),
            "missing or conflicting target taxon ranks")
    rank_by_taxon={tid:next(iter(taxon_ranks[tid])) for tid in all_target}
    species_ids={tid for tid,rnk in rank_by_taxon.items() if rnk=="species"}
    require(len(original_target & species_ids)==31,
            "frozen roster no longer has 31 explicitly species-ranked targets")
    require(all(rank_by_taxon[t]=="speciesGroup" for t in GROUP_TAXON_IDS),
            "frozen published species-group rank changed")

    site_codes=_site_codes(_request_json(PRODUCT_URL))
    release_query=_request_json(
        QUERY_URL,token=token,
        body={
            "productCode":PRODUCT,"siteCodes":site_codes,
            "startDateMonth":START,"endDateMonth":END,
            "release":RELEASE,"package":"basic","includeProvisional":False,
        },
    )
    inventory=_inventory(release_query)

    pfiles=[row for row in inventory if "mam_perplotnight" in row["name"]]
    prows=[]
    for meta, raw in zip(pfiles,_download_many(pfiles,token,max_workers=MAX_DOWNLOAD_WORKERS)):
        prows.extend(_read_plot_rows(raw,meta["site"],meta["month"]))
    nights,site_months=_candidate_nights(prows)
    require(bool(nights),"no original exact-3-night events")
    tfiles=[row for row in inventory
            if "mam_pertrapnight" in row["name"]
            and (row["site"],row["month"]) in site_months]
    trows=[]
    qualifier_headers_checked=0
    for meta,raw in zip(tfiles,_download_many(tfiles,token,max_workers=MAX_DOWNLOAD_WORKERS)):
        fieldnames=next(csv.reader(io.StringIO(raw.decode("utf-8-sig").splitlines()[0])),[])
        if not {"identificationQualifier","identification_qualifier"}.intersection(fieldnames):
            raise RuntimeError("NEON source pertrapnight lacks identificationQualifier")
        qualifier_headers_checked+=1
        for row in _read_trap_rows(raw,nights):
            row["_site"]=meta["site"]
            trows.append(row)

    pp=[
        {k:r[k] for k in (
            "nightuid","eventID","plotID","siteID",
            "mammalGridSamplingType","gridCompletion","collectDate",
        )}
        for r in prows if r["nightuid"] in nights
    ]
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        pf=root/"plots.csv";tf=root/"traps.csv"
        _write_csv(pf,pp,[
            "nightuid","eventID","plotID","siteID","mammalGridSamplingType",
            "gridCompletion","collectDate",
        ])
        _write_csv(tf,trows,[
            "nightuid","plotID","trapCoordinate","trapStatus","tagID",
            "taxonID","scientificName","identificationQualifier","taxonRank",
        ])
        structural=audit(pf,tf)

    sessions=[
        s for s in structural["support"]["sessions"]
        if s.get("primary_complete_session")
        and int(s.get("n_repeat_coordinate_supported_tagged_individuals",0))>=MIN_REPEAT
        and str(s.get("taxon","")) in original_target
        and float(s.get("all_capture_trap_night_fraction_of_observed",1.0))<=SATURATION_MAX
    ]
    require(len(sessions)==frozen["frozen_response_support"]["observed_target_guarded_sessions"],
            "original target response-session count")

    plot_groups=defaultdict(list)
    for r in pp:
        plot_groups[(str(r["siteID"]),str(r["plotID"]),str(r["eventID"]))].append(r)
    complete={}
    night_to_event={}
    for key,rows in plot_groups.items():
        unique_nights={str(r["nightuid"]) for r in rows}
        completion={str(r["gridCompletion"]) for r in rows if r["gridCompletion"]}
        ordered_dates=sorted({str(r["collectDate"]) for r in rows if r["collectDate"]})
        site,plot,event=key
        if site!="SRER" and len(unique_nights)==3 and completion=={COMPLETE}:
            require(bool(ordered_dates),"complete event missing capture date")
            complete[key]=ordered_dates[0]
            for night in unique_nights:
                if night in night_to_event and night_to_event[night]!=key:
                    raise RuntimeError("Night appears in multiple plot events")
                night_to_event[night]=key

    ordered_events={}
    by_plot=defaultdict(list)
    for key,first in complete.items():
        by_plot[(key[0],key[1])].append((first,key[2]))
    for siteplot,items in by_plot.items():
        ordered_events[siteplot]=[
            event for _date,event in sorted(items,key=lambda x:(x[0],x[1]))
        ]

    tag_taxa=defaultdict(set)
    tag_events=defaultdict(set)
    qualifier_warning_histories=set()
    qualifier_warning_capture_rows=0
    target_capture_rows=0
    for r in trows:
        if not _capture_status(r.get("trapStatus","")):continue
        taxon=str(r.get("taxonID","")).strip()
        tag=str(r.get("tagID","")).strip()
        if taxon not in all_target or not tag:continue
        event_key=night_to_event.get(str(r.get("nightuid","")).strip())
        if event_key is None:continue
        site,plot,_event=event_key
        hkey=(site,plot,tag)
        tag_taxa[hkey].add(taxon)
        tag_events[hkey].add(str(event_key[2]))
        qualifier=str(r.get("identificationQualifier") or "").strip().upper()
        if qualifier not in {"", "NA", "N/A", "NULL"}:
            qualifier_warning_histories.add(hkey)
            qualifier_warning_capture_rows+=1
        target_capture_rows+=1

    require(len(tag_taxa)==frozen["taxonomy_history"]["target_tag_histories"],
            "original target tagged histories")
    require(target_capture_rows==frozen["taxonomy_history"]["target_capture_rows_used_for_history"],
            "original target capture records")

    histories=[
        {"site":key[0],"plot_id":key[1],
         "taxon_ids":sorted(taxa),"event_ids":sorted(tag_events[key]),
         "qualifier_warning":key in qualifier_warning_histories}
        for key,taxa in tag_taxa.items()
    ]
    maps,history_types=event_predictors(
        ordered_events=ordered_events,
        histories=histories,
        genus_by_taxon=genus_by_taxon,
        resolved_species_ids=species_ids,
    )
    maps_qualifier,history_types_qualifier=event_predictors(
        ordered_events=ordered_events,histories=histories,
        genus_by_taxon=genus_by_taxon,
        resolved_species_ids=species_ids,
        respect_qualifier_warning=True,
    )
    require(set(maps_qualifier)==set(maps),
            "identity sensitivity changed original event keys")
    require(all(maps[k]["N"]==maps_qualifier[k]["N"] for k in maps),
            "identity sensitivity changed the original genus MNKA")
    require(history_types_qualifier.get("CROSS_GENUS",0)==
            history_types.get("CROSS_GENUS",0),
            "identity sensitivity changed cross-genus exclusions")
    require(history_types_qualifier.get("RESOLVED_SPECIES",0)<=
            history_types.get("RESOLVED_SPECIES",0),
            "qualifier warning created newly resolved species")
    require(history_types_qualifier.get("UNRESOLVED_IN_GENUS",0)>=
            history_types.get("UNRESOLVED_IN_GENUS",0),
            "qualifier warning removed unresolved histories")

    require(history_types.get("CROSS_GENUS",0)==
            frozen["taxonomy_history"]["cross_genus_histories_excluded"],
            "cross-genus identity count")
    require(history_types.get("RESOLVED_SPECIES",0)+
            history_types.get("UNRESOLVED_IN_GENUS",0)+
            history_types.get("CROSS_GENUS",0)==len(tag_taxa),
            "genus identity classification total")

    indexed_sessions=[]
    for s in sessions:
        site_ids=s.get("site_ids",[])
        genera=s.get("genus_labels",[])
        require(len(site_ids)==1 and len(genera)==1,
                "frozen structurally supported site/genus not unambiguous")
        site,plot,event=site_ids[0],s["plot_id"],s["event_id"]
        dt=complete.get((site,plot,event))
        require(bool(dt),"frozen response session lacks exact complete event")
        genus=genera[0]
        indexed_sessions.append({
            "site":site,"plot_id":plot,"event_id":event,
            "taxon":s["taxon"],"genus":genus,
            "year":str(dt[:4]),"month":str(dt[5:7]),
        })
    report_rows,row_counts=response_predictor_rows(
        indexed_sessions,maps,resolved_species_ids=species_ids
    )
    require(row_counts["target_structural_sessions"]==1536,
            "source target sessions not 1536")

    # Original effect-blind MNKA series diagnostics must still match, without
    # accessing any W/B or refitting the old response model.
    by_series=defaultdict(list)
    for row in report_rows:
        by_series[row["series_id"]].append(row)
    require(len(by_series)==frozen["mnka_variation"]["taxon_plot_series_total"],
            "original response taxon × plot series count")
    varying=[
        vals for vals in by_series.values()
        if len(vals)>=3 and len({v["N"] for v in vals})>=2
    ]
    require(len(varying)==frozen["mnka_variation"]["series_with_at_least_3_sessions_and_2_mnka_values"],
            "original genus MNKA varying-series count")
    require(sum(map(len,varying))==
            frozen["mnka_variation"]["response_sessions_in_varying_series"],
            "original genus MNKA varied sessions")

    all_target_genera={genus_by_taxon[t] for t in original_target}
    per_genus=genus_support(report_rows,all_genera=all_target_genera)
    candidate=[genus for genus,info in per_genus.items()
               if info["state"]=="PREDICTOR_ONLY_POTENTIALLY_IDENTIFIABLE"]
    qual_rows,qual_row_counts=response_predictor_rows(
        indexed_sessions,maps_qualifier,resolved_species_ids=species_ids
    )
    require(qual_row_counts==row_counts,
            "Qualifier sensitivity changed fixed response session classification")
    require(all(o["N"]==q["N"] for o,q in zip(report_rows,qual_rows)),
            "Qualifier sensitivity changed any known-alive N in fixed cohort")
    qual_per_genus=genus_support(qual_rows,all_genera=all_target_genera)
    qual_candidate=[g for g,meta in qual_per_genus.items()
                    if meta["state"]=="PREDICTOR_ONLY_POTENTIALLY_IDENTIFIABLE"]

    # Frozen subsequent ecological question: at fixed genus N and unknown
    # U, can replacing one congener by one conspecific be *identified*
    # after the same original site-month/year/series controls?
    # Only the previously selected Peromyscus candidate receives this
    # additional source-only check, NEVER a W/B or ecological response fit.
    fixed_total_priority="Peromyscus"
    require(fixed_total_priority in candidate and fixed_total_priority in qual_candidate,
            "original source-only Peromyscus F/C structural candidate status drifted")
    original_frozen_receipt=json.loads(
        (ROOT/"results/conspecific_congeneric_predictor_feasibility_receipt_20261018.json").read_text(encoding="utf-8")
    )
    qualifier_frozen_receipt=json.loads(
        (ROOT/"results/conspecific_congeneric_qualifier_sensitivity_receipt_20261018.json").read_text(encoding="utf-8")
    )
    expected_baseline=original_frozen_receipt["per_genus"][fixed_total_priority]
    expected_qualifier=qualifier_frozen_receipt["qualifier_sensitivity"]["per_genus"][fixed_total_priority]
    for actual,expected,phase in (
        (per_genus[fixed_total_priority],expected_baseline,"baseline"),
        (qual_per_genus[fixed_total_priority],expected_qualifier,"qualifier"),
    ):
        for key in ("species_sessions_in_3plus_series",
                    "species_sessions_all",
                    "sites_in_3plus_series",
                    "species_series_with_3plus_sessions",
                    "series_joint_F_C_variation",
                    "unresolved_abundance_sum",
                    "genus_abundance_sum",
                    "event_sessions_with_resolved_other_congener_C"):
            require(actual[key]==expected[key],
                    "pre-existing original Peromyscus F/C "+phase+" "+key+" drifted")
    baseline_fixed_total=fixed_total_genus_support(
        report_rows,genus=fixed_total_priority,
        previous_frozen_support=per_genus[fixed_total_priority],
    )
    qualifier_fixed_total=fixed_total_genus_support(
        qual_rows,genus=fixed_total_priority,
        previous_frozen_support=qual_per_genus[fixed_total_priority],
    )
    require(
        baseline_fixed_total["strictly_species_labelled_source_sessions"]==
        qualifier_fixed_total["strictly_species_labelled_source_sessions"]==948,
        "same frozen 948 structural sessions required before U-adjusted support"
    )
    require(baseline_fixed_total["original_physical_sites"]==
            qualifier_fixed_total["original_physical_sites"]==33,
            "original 33 physical Peromyscus sites drifted")
    require(baseline_fixed_total["rank_FC_after_nuisance"]==2 and
            qualifier_fixed_total["rank_FC_after_nuisance"]==2,
            "original two-predictor rank drifted")

    # Literal matched observations at identical genus N and unresolved U:
    # this distinguishes direct ecological source overlap from model-only
    # regression extrapolation. Do not relax equality or access W/B.
    literal_baseline=observed_fixed_total_pairs(
        report_rows,genus=fixed_total_priority,
        previous_frozen_support=per_genus[fixed_total_priority],
    )
    literal_qualifier=observed_fixed_total_pairs(
        qual_rows,genus=fixed_total_priority,
        previous_frozen_support=qual_per_genus[fixed_total_priority],
    )
    for literal in (literal_baseline,literal_qualifier):
        require(literal["original_frozen_3plus_series_sessions"]==948,
                "literal fixed-total session denominator drifted")
        require(literal["original_physical_sites"]==33 and
                literal["original_focal_series"]==109,
                "literal fixed-total physical-site/series denominator drifted")
        require(not literal["ecological_W_B_effects_opened"],
                "literal source audit unexpectedly opened spatial outcomes")

    return {
        "schema":"neon.conspecific_congeneric_predictor_feasibility_v1",
        "status":"EFFECT_BLIND_SPECIES_CONGENER_FEASIBILITY_SCORED_NOT_ECOLOGICAL_EFFECT",
        "created_at":"2026-10-18",
        "source":{
            "release":RELEASE,
            "product":PRODUCT,"product_date_start":START,"product_date_end":END,
            "provenance":"NEON API manifest size/MD5 verified with original RELEASE-2026 reader",
            "history_definition":"site × plot × tag; first-last complete event index, as original genus MNKA",
            "taxonomy_source":"NEON SMALL_MAMMAL target taxonomy and frozen target lock",
            "files_checked":len(inventory),
            "perplot_files":len(pfiles),"pertrap_files":len(tfiles),
            "qualifier_source_columns_verified":qualifier_headers_checked,
            "data_policy":"No raw code, animal ID, location, or W/B outcomes in output",
        },
        "invariants":{
            "original_source_target_sessions":len(sessions),
            "original_target_histories":len(tag_taxa),
            "original_target_capture_rows":target_capture_rows,
            "original_genus_mnka_varying_series":len(varying),
            "original_genus_mnka_varying_sessions":sum(map(len,varying)),
            "original_response_series":len(by_series),
            "taxonomy_histories":history_types,
            "target_species_ids_in_original_roster":len(original_target & species_ids),
            "target_species_group_ids_in_original_roster":len(GROUP_TAXON_IDS),
            "all_public_target_species_ids":len(species_ids),
            **row_counts,
        },
        "fixed_feasibility_thresholds":{
            "minimum_species_sessions":60,"minimum_sites":6,
            "minimum_threeplus_series":8,"minimum_jointly_varying_series":5,
            "residual_rank":2,"maximum_condition_number":30.0,
        },
        "priority_genus":"Peromyscus",
        "per_genus":per_genus,
        "candidate_genera_predictor_only":candidate,
        "fixed_total_U_adjusted_predictor_only":{
            "schema":"neon.fixed_total.U_adjusted_historical_FE_design.v1",
            "status":"ORIGINAL_SOURCE_VERIFIED_NO_W_B_SPATIAL_OUTCOMES",
            "primary_genus_precommitted":"Peromyscus",
            "baseline":baseline_fixed_total,
            "qualifier_conservative":qualifier_fixed_total,
            "literal_same_total_and_U_observation_support":{
                "schema":"neon.fixed_total.same_N_U_matched_source_observations.v1",
                "original_same_948_focal_sessions":True,
                "baseline":literal_baseline,
                "qualifier_conservative":literal_qualifier,
                "no_spatial_response_or_species_mechanism_opened":True,
            },
            "other_genera_original_F_C_structural_results_preserved":{
                g:v["state"] for g,v in per_genus.items() if g!="Peromyscus"
            },
            "minimum_original_species_sessions":60,
            "minimum_original_physical_sites":6,
            "minimum_original_3plus_series":8,
            "minimum_original_joint_FC_varying_series":5,
            "conditional_FC_rank_required":2,
            "maximum_conditional_FC_condition_number":30.0,
            "the_same_observed_original_N_and_structural_cohort":True,
            "rank_identifiability_does_not_establish_field_species_truth":True,
            "observational_effect_not_fitted":True,
            "independent_new_NEON_events_not_accessed":True,
            "ecological_paper_publication_still_DRAFT_HOLD":True,
        },
        "qualifier_conservative_sensitivity":{
            "classification_rule":"Any nonblank identificationQualifier except NA/N/A/NULL converts a single-species taxon history to same-genus unresolved U",
            "original_genus_N_invariant_every_event":True,
            "strict_structural_response_session_universe_unchanged":True,
            "warning_capture_rows":qualifier_warning_capture_rows,
            "warning_tag_histories":len(qualifier_warning_histories),
            "newly_unresolved_formerly_resolved_histories":(
                history_types["RESOLVED_SPECIES"]-
                history_types_qualifier.get("RESOLVED_SPECIES",0)
            ),
            "qualifier_sensitive_taxonomy_histories":history_types_qualifier,
            "per_genus":qual_per_genus,
            "candidate_genera_qualifier_conservative":qual_candidate,
            "no_W_B_spatial_ecological_effects":True,
            "explicit_qualifier_warning_is_not_proof_of_wrong_species":True,
        },
        "hypothesis_scope":"NEW post-development species-vs-congener question, not retrospective original hypothesis confirmation",
        "biological_caution":{
            "F_C_U_not_true_density":True,
            "species_groups_never_assigned_to_species":True,
            "same_genus_multitaxon_histories_not_assigned_to_a_specific_species":True,
            "cross_genus_histories_excluded":True,
            "this_is_predictor_only_historical_response_consumed_data":True,
            "future_outcome_event_ids_must_be_unopened":True,
            "original_8_genus_guard":"FAILED_5_OF_8",
            "original_provisional_future_five_genus":"NOT_ESTIMABLE",
            "MOSA_spatial_effects_opened":False,
            "W_B_or_density_spatial_effects_computed":False,
            "new_mammal_spatial_ecological_claim":False,
        },
    }


def main() -> int:
    try:
        result=run()
    except Exception as exc:
        result={
            "schema":"neon.conspecific_congeneric_predictor_feasibility_v1",
            "status":"STOP_SOURCE_OR_PREDICTOR_FEASIBILITY",
            "diagnostic":str(exc)[:700],
            "W_B_or_density_spatial_effects_computed":False,
        }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if result["status"].startswith("EFFECT_BLIND") else 3

if __name__=="__main__":
    raise SystemExit(main())
