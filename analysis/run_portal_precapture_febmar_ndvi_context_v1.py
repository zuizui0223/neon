#!/usr/bin/env python3
"""Portal precapture February-March site-greenness context (post-result).

The 43 Portal spring 2023 mammal capture comparisons predate 2023 summer NDVI.
Original February–March Landsat8 is chronologically prior, but is not edible
biomass, a plot-specific environmental treatment or a mammal response.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from hashlib import sha1, sha256
from io import StringIO
from math import isfinite
from pathlib import Path
from statistics import mean
from urllib.request import Request, urlopen
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/neon_portal_precapture_febmar_ndvi_context_20261121.json"
SOURCE_REPO = "weecology/PortalData"
SOURCE_COMMIT = "afd75933249ae60f3a5e9dab00b354f219e5e045"
FILE = "NDVI/ndvi.csv"
GIT_BLOB_SHA = "0a55a926712210ee786660517a1ae12285bb6303"
BYTES_MAX = 1_000_000
YEARS = (2021, 2022, 2023, 2024)
MONTHS = (2, 3)
SENSOR = "Landsat8"
PROVIDER = "USGS"
MAX_CLOUD_PERCENT = 30.0
PROTOCOL = "docs/NEON_PORTAL_PRECAPTURE_FEBMAR_NDVI_CONTEXT_FROZEN_20261121.md"

def require(condition: bool, label: str) -> None:
    if not condition:
        raise ValueError("PORTAL_PRECAPTURE_NDVI_STOP_" + label)

def fetch_original():
    url = "https://raw.githubusercontent.com/" + SOURCE_REPO + "/" + SOURCE_COMMIT + "/" + FILE
    req = Request(url, headers={"Accept": "text/csv", "User-Agent": "NEON-original-source/1"})
    with urlopen(req, timeout=90) as resp:
        require(getattr(resp, "status", 200) == 200, "SOURCE_HTTP_STATUS")
        raw = resp.read(BYTES_MAX + 1)
    require(0 < len(raw) <= BYTES_MAX, "SOURCE_EMPTY_OR_OVER_CAP")
    low = raw[:512].lstrip().lower()
    require(not low.startswith((b"<!doctype", b"<html", b"{", b"pk\x03\x04")),
            "SOURCE_HTML_JSON_OR_ZIP")
    got = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    require(got == GIT_BLOB_SHA, "IMMUTABLE_SOURCE_HASH_MISMATCH")
    return raw

def original_records(raw):
    try:
        decoded = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("PORTAL_PRECAPTURE_NDVI_STOP_INVALID_UTF8") from None
    reader = csv.DictReader(StringIO(decoded))
    names = reader.fieldnames or []
    req = {"date", "sensor", "source", "ndvi", "cloud_cover"}
    require(len(names) == len(set(names)) and req.issubset(names),
            "ORIGINAL_REQUIRED_HEADERS_OR_DUPLICATES")
    for item in reader:
        require(None not in item and all(v is not None for v in item.values()),
                "RAGGED_ORIGINAL_CSV")
        yield item

def source_only_and_context(records):
    """Check complete four-year/two-month support before emitting any means."""
    accepted = defaultdict(list)
    found = defaultdict(Counter)
    original_days = set()
    excluded = Counter()
    for item in records:
        try:
            d = date.fromisoformat((item["date"] or "").strip())
        except (ValueError, TypeError):
            excluded["original_unparseable_date"] += 1
            continue
        if d.year not in YEARS or d.month not in MONTHS:
            continue
        found[(d.year, d.month)]["all_original_sensors"] += 1
        if item["sensor"] != SENSOR or item["source"] != PROVIDER:
            found[(d.year, d.month)]["other_sensor_or_provider"] += 1
            continue
        key = (d.isoformat(), SENSOR, PROVIDER)
        require(key not in original_days, "DUPLICATE_SOURCE_DATE_SENSOR_PROVIDER")
        original_days.add(key)
        found[(d.year, d.month)]["original_Landsat8_USGS_rows"] += 1
        raw_n, raw_cloud = (item["ndvi"] or "").strip(), (item["cloud_cover"] or "").strip()
        if not raw_n or not raw_cloud:
            excluded["missing_NDVI_or_cloud"] += 1
            continue
        try:
            n = float(raw_n)
            c = float(raw_cloud)
        except ValueError:
            excluded["non_numeric_NDVI_or_cloud"] += 1
            continue
        require(isfinite(n) and isfinite(c) and -1 <= n <= 1 and 0 <= c <= 100,
                "IMPOSSIBLE_NDVI_OR_CLOUD")
        if c > MAX_CLOUD_PERCENT:
            excluded["cloud_above_30pct"] += 1
            continue
        accepted[(d.year, d.month)].append(n)
    census = {
        str(y): {
            str(m): {
                **dict(found[(y, m)]),
                "qualifying_source_images":len(accepted[(y, m)]),
                "one_or_more_image_gate":len(accepted[(y, m)]) >= 1,
            } for m in MONTHS
        } for y in YEARS
    }
    quality = all(len(accepted[(y,m)]) >= 1 for y in YEARS for m in MONTHS)
    base = {
        "schema":"neon.portal_postresult_precapture_febmar_ndvi_context.v1",
        "original_source":{
            "repository":SOURCE_REPO,
            "git_commit":SOURCE_COMMIT,
            "file":FILE,
            "git_blob_SHA_verified":GIT_BLOB_SHA,
            "original_sensor":SENSOR,
            "original_provider":PROVIDER,
            "cloud_threshold_percent":MAX_CLOUD_PERCENT,
            "source_window_months":list(MONTHS),
            "original_years":list(YEARS),
        },
        "pre_effect_source_support":{
            "original_image_counts_by_month":census,
            "excluded_original_image_metadata_counts":dict(sorted(excluded.items())),
            "all_four_years_have_at_least_one_Feb_and_one_Mar_image":quality,
            "support_checked_before_any_mean_was_emitted":True,
        },
        "ecological_limits":{
            "this_window_chosen_after_mammal_and_satellite_results_and_source_coverage":True,
            "all_2023_Feb_and_Mar_images_precede_April_June_2023_rodent_captures":True,
            "prior_43_of_65_original_spring_mammal_comparisons_not_refit":True,
            "site_wide_greenness_1km_not_plot_biomass_seed_or_food":True,
            "one_site_series_shared_by_all_competitor_treatments":True,
            "three_transitions_do_not_demonstrate_a_general_law":True,
            "no_rodent_composition_plant_count_weather_or_learning_source_read":True,
            "no_redefinition_of_original_114_mammal_estimates":True,
            "single_NEON_draft_submission_HOLD":True,
        },
        "protocol":PROTOCOL
    }
    if not quality:
        base["status"]="SOURCE_STOP_ORIGINAL_FEBMAR_NDVI_COVERAGE"
        base["annual_NDVI"]=None
        base["all_original_adjacent_year_differences"]=None
        return base

    month_means={y:{m:mean(accepted[(y,m)]) for m in MONTHS} for y in YEARS}
    balanced={y:mean([month_means[y][m] for m in MONTHS]) for y in YEARS}
    transitions={}
    for year in YEARS[:-1]:
        d=balanced[year+1]-balanced[year]
        transitions[f"{year}_to_{year+1}"]={"signed":d,"absolute":abs(d)}
    target=transitions["2022_to_2023"]["absolute"]
    ranked=1+sum(v["absolute"]>target for v in transitions.values())
    base["status"]="SOURCE_GO_EARLY_GREENNESS_CONTEXT_ONLY_NOT_MAMMAL_MECHANISM"
    base["annual_NDVI"]={
        str(y):{
            "February_NDVI":month_means[y][2],
            "March_NDVI":month_means[y][3],
            "February_March_equal_month_mean":balanced[y],
            "number_of_qualifying_images_February":len(accepted[(y,2)]),
            "number_of_qualifying_images_March":len(accepted[(y,3)]),
        } for y in YEARS
    }
    base["all_original_adjacent_year_differences"]=transitions
    base["2022_to_2023_change_direction"]=(
        "decline" if transitions["2022_to_2023"]["signed"]<0 else
        "increase" if transitions["2022_to_2023"]["signed"]>0 else "zero"
    )
    base["2022_to_2023_absolute_change_rank_largest_first"]=ranked
    base["2022_to_2023_absolute_change_has_tied_rank"]=(
        sum(v["absolute"]==target for v in transitions.values())>1
    )
    base["not_an_inferential_p_value_or_biomass_test"]=True
    return base

def main():
    try:
        raw=fetch_original()
        result=source_only_and_context(original_records(raw))
        result["original_source"]["raw_SHA256"]=sha256(raw).hexdigest()
        result["original_source"]["original_size_bytes"]=len(raw)
        result["retrieved_utc"]=datetime.now(timezone.utc).isoformat()
        code=0
    except Exception as exc:
        result={
            "schema":"neon.portal_postresult_precapture_febmar_ndvi_context.v1",
            "status":"STOP_PINNED_SOURCE_OR_ORIGINAL_SCHEMA",
            "stop_error_class":type(exc).__name__,
            "stop_code":str(exc)[:160],
            "no_mammal_or_plant_effect_read":True,
        }
        code=3
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    return code

if __name__=="__main__":
    raise SystemExit(main())
