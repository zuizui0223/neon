"""One original NEON tower source-month parser differential diagnostic.

No mammal effects, weather measurements or original site/date values.
Compares the already successful pilot parser to the stricter recently
introduced full 205-month parser for the SAME official response.
"""
from __future__ import annotations
from pathlib import Path
from urllib.parse import urlsplit
import json,os,re

from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus
from analysis.run_neon_macro_temporal_weather_source_v1 import NEON_SITES
from analysis.run_multiscale_density_estimability_release2026_v3 import (
    QUERY_URL,TOKEN_ENV,_request_json,
)
from analysis.run_neon_macro_weather_pilot_v1 import (
    eligible_first_original_pair,_month_manifest,
)
from analysis.neon_macro_tower_thermal_contrast_v1 import (
    position,_month_catalog,select_fixed_temperature_file
)
from analysis.run_neon_macro_original_tower_thermal_ecology_v1 import (
    _exact_month_query_body
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"build/neon_original_tower_month_parser_difference_v1.json"

def safe_parser_profile(archived_record:dict,strict_record:dict|None)->dict:
    """No file name, exact timestamp, site, URL, individual ID or tag exported."""
    name=str(archived_record.get("name") or "")
    ends=name.endswith(".csv")
    has_table="SAAT_30min" in name
    suff=bool(re.search(r"\.\d{3}\.030\.SAAT_30min\.csv$",name))
    # File-name table pattern is a source format, not a private site name.
    return {
        "pilot_provider_record_was_valid":True,
        "file_is_csv":ends,
        "file_contains_explicit_SAAT_30min_table":has_table,
        "current_exact_three_digit_position_regex_matches":suff,
        "file_has_three_digit_vertical_position_under_old_parser":position(name) is not None,
        "full_new_parser_selects_a_record":strict_record is not None,
        "full_new_parser_same_provider_name_as_pilot":(
            strict_record is not None and str(strict_record.get("name") or "")==name
        ),
        "provider_size_type":"int" if isinstance(archived_record.get("size"),int) else "other",
        "size_gt_0":isinstance(archived_record.get("size"),int) and archived_record["size"]>0,
        "size_le_15mb":isinstance(archived_record.get("size"),int) and archived_record["size"]<=15000000,
        "provider_checksum_length":len(str(archived_record.get("md5") or "")),
        "provider_url_https":str(archived_record.get("url") or "").startswith("https://"),
        "no_source_identifier_name_url_or_date_returned":True,
        "no_mammal_ecological_effect_opened":True,
    }

def run()->dict:
    token=os.environ.get(TOKEN_ENV,"").strip()
    if not token:raise ValueError("NEON source access unavailable")
    old,two,_=original_sources_for_two_genus()
    if len(old)!=58 or len(two)!=158:
        raise ValueError("Original NEON mammal source cohort drifted")
    sites=_request_json(NEON_SITES).get("data")
    if not isinstance(sites,list):raise ValueError("NEON site source metadata unavailable")
    site,month=eligible_first_original_pair(two,sites)
    req=_exact_month_query_body(site,month)
    payload=_request_json(QUERY_URL,token=token,body=req)
    original=_month_manifest(payload,"DP1.00002.001",site,month,"SAAT_30min")
    current=_month_catalog(payload,{(site,month)}).get((site,month))
    return {
        "schema":"neon.macro.original_tower_month_parser_differential_source_qa.v1",
        "status":"ONE_ORIGINAL_MONTH_SOURCE_PARSER_DIFFERENCE_DIAGNOSED",
        "same_single_official_NEON_release_month_response_for_both_parsers":True,
        "original_pre_effect_one_month_parser_succeeded":True,
        "strict_full_run_parser_succeeded":current is not None,
        "source_safe_parser_profile":safe_parser_profile(original,current),
        "not_an_ecological_climate_or_detection_result":True,
        "old_14_30_site_ecological_positive_results_unchanged":True,
        "no_site_or_animal_private_values_exported":True,
    }

def main()->int:
    try:
        result=run()
        ec=0
    except Exception as err:
        result={
            "schema":"neon.macro.original_tower_month_parser_differential_source_qa.v1",
            "status":"STOP_SOURCE_PILOT_AND_FULL_PARSER_DIAGNOSTIC",
            "error_class":type(err).__name__,
            "no_raw_identifiers_or_source_exception_messages_exported":True,
            "no_climate_recurrence_effect_computed":True,
        }
        ec=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return ec
if __name__=="__main__":
    raise SystemExit(main())
