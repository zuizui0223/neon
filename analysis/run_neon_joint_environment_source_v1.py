#!/usr/bin/env python3
"""Original 58-pair exact crosswalk of two independently sampled sources.

Do not read or refit any old mammal genus-station ecological effect.
Only original capture days and the CHM / nearby field-plant source support.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import os

from analysis.run_neon_habitat_source_link_v1 import (
    BASE, TOKEN_ENV, reconstruct, _request_json, digest
)
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    QUERY_URL, _download_many
)
from analysis.run_neon_nearby_baseplant_source_v1 import plant_manifest
from analysis.neon_field_plant_source_support_v1 import (
    parse_1m2_source, plant_source_events, summarize_nearby_plant_bouts
)
from analysis.run_neon_aop_historical_flight_month_v1 import (
    PRODUCT as AOP_PRODUCT, RELEASE as AOP_RELEASE, MONTH_RE,
    audit_flight_month_availability
)
from analysis.neon_joint_environment_source_crosswalk_v1 import (
    joint_source_crosswalk
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_joint_chm_plant_exact_pairs_source_20261028.json"
PLANT_RECEIPT=ROOT/"results/neon_baseplot_cover_time_source_receipt_20261028.json"
CHM_RECEIPT=ROOT/"results/neon_historical_chm_actual_pixel_source_receipt_20261028.json"
AOP_RECEIPT=ROOT/"results/neon_aop_multiyear_month_coverage_receipt_20261028.json"
STAGE="CHECK_PRIOR_SOURCE_RECEIPTS"
STAGES={"CHECK_PRIOR_SOURCE_RECEIPTS","REBUILD_FROZEN_MAMMAL_SOURCE",
        "VERIFY_FROZEN_AOP_AVAILABLE_MONTHS","VERIFY_FROZEN_PLANT_SOURCE",
        "DOWNLOAD_PUBLISHED_ORIGINAL_PLANT_FILES",
        "EXACT_JOINT_PAIR_CROSSWALK"}

def must(ok,why):
    if not ok:
        raise ValueError("Original environmental source invariant failed: "+why)

def run():
    global STAGE
    token=os.environ.get(TOKEN_ENV,"").strip()
    must(bool(token),"NEON source authorization")
    plant=json.loads(PLANT_RECEIPT.read_text(encoding="utf-8"))
    chm=json.loads(CHM_RECEIPT.read_text(encoding="utf-8"))
    aop_old=json.loads(AOP_RECEIPT.read_text(encoding="utf-8"))
    must(
        plant.get("status")=="SOURCE_BASE_PLANT_NEARBY_TIME_MATCH_GO_NOT_TRAP_HABITAT"
        and plant.get("provider_verified_plant_files")==326
        and plant["matched_plant_field_bout_support"]["source_period_support_counts"]["numeric_365_distinct"]==51
        and plant["matched_plant_field_bout_support"]["source_period_support_counts"]["numeric_90_distinct"]==16,
        "original base-plant verified receipt")
    must(
        chm.get("status")=="HISTORIC_CHM_SOURCE_SUPPORT_GO_NOT_BIOLOGICAL_EFFECT"
        and chm.get("provider_checksum_size_verified_tiles")==51
        and chm["actual_historical_CHM_1m_pixel_support"]["within12_actually_qualified_pairs"]==36
        and chm["actual_historical_CHM_1m_pixel_support"]["within3_actually_qualified_pairs"]==22
        and chm["actual_historical_CHM_1m_pixel_support"]["prior12_actually_qualified_pairs"]==18
        and chm["actual_1m_pixel_status_counts"]["VALID_REFERENCE_PIXEL"]==24600,
        "original 51-tile 24600-pixel historical AOP receipt")
    must(
        aop_old.get("status")=="MULTIYEAR_OFFICIAL_AOP_MONTH_AVAILABILITY_AUDITED_NOT_HABITAT_EFFECT"
        and aop_old.get("total_unique_site_flight_month_pairs")==97,
        "original AOP 97 source site-month visits")

    STAGE="REBUILD_FROZEN_MAMMAL_SOURCE"
    units,plots,sites,names,mammal_source=reconstruct(token)
    must((len(units),len(plots),len(sites))==(58,30,14),
         "frozen 58 season comparisons in 30 plots and 14 sites")

    STAGE="VERIFY_FROZEN_AOP_AVAILABLE_MONTHS"
    aop=_request_json(BASE+"products/"+AOP_PRODUCT+"?release="+AOP_RELEASE,token=token)
    must(digest(aop)==aop_old["source_provenance"]["official_product_metadata_digest"],
         "official AOP release metadata digest")
    site_rows=aop.get("data",{}).get("siteCodes",[])
    must(isinstance(site_rows,list),"official AOP site source listing")
    bysite={r["siteCode"]:r for r in site_rows if isinstance(r,dict) and
            isinstance(r.get("siteCode"),str)}
    months={s:sorted({m for m in bysite.get(s,{}).get("availableMonths",[])
                       if isinstance(m,str) and MONTH_RE.fullmatch(m)}) for s in sites}
    coverage=audit_flight_month_availability(units,months)
    must(
        (coverage["total_unique_site_flight_month_pairs"],
         coverage["pairs_all_six_days_within_12_months"],
         coverage["pairs_all_six_days_within_3_months"],
         coverage["pairs_all_six_days_within_12_months_only_not_later_acquisition"],
         coverage["pairs_all_six_days_within_3_months_only_not_later_acquisition"])
        ==(97,36,22,18,10),
        "actual historical AOP source month support")

    STAGE="VERIFY_FROZEN_PLANT_SOURCE"
    query=_request_json(QUERY_URL,token=token,body={
        "productCode":"DP1.10058.001","siteCodes":sorted(sites),
        "startDateMonth":"2015-04","endDateMonth":"2025-12",
        "release":"RELEASE-2026","package":"basic","includeProvisional":False,
    })
    must(digest(query)==plant["official_plant_manifest_digest"],
         "published original base-plant file manifest digest")
    files=plant_manifest(query,sites)
    must(len(files)==326 and sum(x["size"] for x in files)==131730791,
         "original 326 MD5-verified plant source files")

    STAGE="DOWNLOAD_PUBLISHED_ORIGINAL_PLANT_FILES"
    verified=[]
    for row,raw in zip(files,_download_many(files,token,max_workers=6)):
        data,n=parse_1m2_source(raw)
        verified.append((row["site"],data,n))
    must(len(verified)==326,"source field plant file count")
    byplot,plant_counts=plant_source_events(verified,plots)
    old_support=summarize_nearby_plant_bouts(units,byplot)
    must(
        old_support["source_period_support_counts"]["numeric_365_distinct"]==51
        and old_support["source_period_support_counts"]["numeric_90_distinct"]==16
        and old_support["plots_with_exact_ID_matched_base_plant_survey"]==30,
        "reproduced old 51 and 16 original plant source pair counts")

    STAGE="EXACT_JOINT_PAIR_CROSSWALK"
    result=joint_source_crosswalk(units,months,byplot)
    must(
        result["frozen_actual_CHM_raster_eligible_pair_counts"]==
        {"within12":36,"within3":22,"prior12":18,"prior3":10}
        and result["frozen_nearby_plant_numeric_two_event_pair_counts"]==
        {"numeric365":51,"numeric90":16},
        "original two source-pair cohorts changed")
    return {
        **result,
        "source_provenance":{
            "original_mammal_source":mammal_source,
            "original_AOP_source_sha256":digest(aop),
            "original_plant_source_sha256":digest(query),
            "original_plant_provider_MD5_verified_files":len(verified),
            "original_CHM_51_rasters_24600_pixels_attested_by_immutable_receipt":True,
            "CHM_rasters_not_reselected_or_redownloaded_using_old_mammal_Z":True,
            "new_genus_spatial_effect_or_habitat_coefficient_opened":False,
            "source_retrieved_utc":datetime.now(timezone.utc).isoformat(),
        },
        "interpretation":{
            "exact_source_overlap_not_animal_ecological_effect":True,
            "base_plot_ground_cover_not_at_mammal_trap":True,
            "old_catchability_habitat_identifiability_UNRESOLVED":True,
            "original_negative_source_gates_unchanged":True,
            "single_macro_paper_submission_HOLD":True,
        },
    }

def main():
    global STAGE
    try:
        result=run()
        code=0
    except Exception as exc:
        result={
            "schema":"neon.mammal.two_environment_sources_exact_pair_crosswalk.v1",
            "status":"STOP_ORIGINAL_JOINT_SOURCE_RECONSTRUCTION",
            "failed_stage":STAGE if STAGE in STAGES else "UNKNOWN",
            "error_class":type(exc).__name__,
            "original_mammal_ecological_responses_unopened":True,
            "private_site_plot_animal_station_dates_or_cover_not_exported":True,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
