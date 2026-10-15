#!/usr/bin/env python3
"""Run MOSA effect-blind tag/sex/station identity audit on verified 2023 bytes.

Author's exact 55 date deletions, one correction, first-species labels and
official 363-occasion date set are reverified. Cohort selection is **the same**
frozen conservative 153 strict within-calendar-month MN three-night periods,
not a replacement based on 363 authored occasions. No W/B spatial response
metrics or abundance-spatial association are calculated or released.
"""
from __future__ import annotations

import csv
import io
import json
import urllib.error
from collections import defaultdict
from pathlib import Path

from analysis.audit_mosa_effect_blind_identity_conflicts_v1 import (
    audit_identity_conflicts,
)
from analysis.audit_mosa_frozen_conservative_mna_support_v1 import (
    conservative_month_mna_structure,
)
from analysis.audit_mosa_author_exact_filter_v1 import (
    PROCESSING, EXPECTED_AUTHOR_REMOVALS,
    EXPECTED_CORRECTION_ORIGINAL_DATE_INDEX, EXPECTED_CORRECTION_DATE,
    parse_author_filter_commands, replay_author_schedule, source_first_species,
)
from analysis.audit_mosa_author_occasion_mask_v1 import (
    TIMEFILE, FROZEN_TOTAL, validated_author_days,
)
from analysis.audit_mosa_effect_blind_structure_v1 import (
    published_field_map,
)
from analysis.audit_mosa_encounter_toe_reconciliation_v1 import (
    _validated_download, author_matrix_species_tags,
)
from analysis.audit_mosa_zenodo_source_schema_v1 import (
    API, RECORD_ID, _get, select_datafile, validate_source_bytes,
    PublishedSourceError,
)

OUT = Path("build/mosa_effect_blind_identity_conflicts_v1.json")
FROZEN = Path("results/mosa_frozen_conservative_mna_support_receipt_20261015.json")


def must_equal(got, expected, meaning):
    if got != expected:
        raise PublishedSourceError(
            f"Frozen MOSA provenance/denominator drift: {meaning}"
        )


def run() -> dict:
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    must_equal(frozen["status"], "GO_FROZEN_CONSERVATIVE_MNA_SUPPORT_ONLY",
               "published frozen conservative support status")
    meta = json.loads(_get(API).decode("utf-8"))
    must_equal(int(meta.get("id", -1)), RECORD_ID, "Zenodo record ID")
    files = {str(z.get("key") or ""): z for z in meta["files"]}
    if PROCESSING not in files or TIMEFILE not in files:
        raise PublishedSourceError("Exact authored cleaning and time files missing")

    source = select_datafile(meta)
    raw = _validated_download(source)
    validation = validate_source_bytes(raw, source)
    must_equal(validation["verified_checksum"],
               frozen["published_original_MD5"], "source CSV digest")
    delimiter = {"SEMICOLON": ";", "COMMA": ",", "TAB": "\t"}[
        validation["delimiter_type"]
    ]
    reader = csv.DictReader(
        io.StringIO(raw.decode(validation["text_encoding"])),
        delimiter=delimiter,
    )
    rows = list(reader)
    must_equal(len(rows), FROZEN_TOTAL, "original capture row count")
    fields = validation["column_headers"]
    f = published_field_map(fields)
    if len([c for c in fields if c.upper().strip() == "SX"]) != 1:
        raise PublishedSourceError("Verified original data has no unique SX")

    rmd = _validated_download(files[PROCESSING]).decode("utf-8-sig", errors="strict")
    cmds = parse_author_filter_commands(rmd)
    must_equal(tuple(cmds["removed_original_unique_date_indices"]),
               EXPECTED_AUTHOR_REMOVALS, "author's 55 original date deletions")
    must_equal(cmds["corrected_source_date_index"],
               EXPECTED_CORRECTION_ORIGINAL_DATE_INDEX, "date correction index")
    must_equal(cmds["corrected_to_date"],
               EXPECTED_CORRECTION_DATE, "corrected date")
    must_equal(files[PROCESSING]["checksum"],
               frozen["published_authors_processing_Rmd_MD5"],
               "published author RMarkdown digest")
    must_equal(files[TIMEFILE]["checksum"],
               frozen["published_author_time_MD5"],
               "published author time table digest")

    time_rows = list(csv.DictReader(
        io.StringIO(_validated_download(files[TIMEFILE]).decode("utf-8-sig")),
        delimiter=";",
    ))
    author_days = validated_author_days(time_rows)["_author_days"]
    retained = replay_author_schedule(
        rows, f["date"], cmds, expected_author_days=author_days,
    )["retained_rows"]
    must_equal(len(author_days), 1089, "363 x 3 author retained nights")

    matrix, matrix_meta = author_matrix_species_tags(meta)
    must_equal(
        [z["MD5"] for z in matrix_meta],
        frozen["published_encounter_matrix_MD5s"],
        "original published author MN encounter matrices",
    )
    first = source_first_species(retained, f["tag"], f["species"])
    author_mn = {
        str(toe or "").strip() for sp, toe in matrix
        if str(sp or "").strip().upper() == "MN" and str(toe or "").strip()
    }
    must_equal({k for k, v in first.items() if v == "MN"}, author_mn,
               "first retained MN species roster")
    must_equal(len(author_mn), 19678, "author MN codes")
    forms = defaultdict(set)
    for sp, toe in matrix:
        if str(sp or "").strip().upper() == "MN":
            forms[str(toe or "").strip()].add(str(toe))
    collisions = {tag for tag, variants in forms.items() if len(variants) > 1}
    must_equal(len(collisions), 14, "whitespace-normalized TOE collisions")

    # Reuse the exact same frozen structural function and cohort, without
    # changing support thresholds or joining the MNA values to any position.
    structural, strict = conservative_month_mna_structure(
        retained, fields, author_mn, collisions,
    )
    must_equal(structural["status"], frozen["status"], "strict pre-effect GO")
    for key in (
        "eligible_original_conservative_months", "strict_three_night_months",
        "years_with_ge2_distinct_MNA_levels",
        "eligible_months_inside_MNA_varying_years",
        "noncolliding_author_first_MN_tag_codes",
        "source_species_MN_rows_kept_after_author_filter",
        "species_MN_rows_without_valid_lattice_position",
        "MNA_on_eligible_months",
        "eligible_months_by_year",
    ):
        must_equal(structural[key], frozen[key], key)
    months = {entry["year_month"] for entry in strict}
    must_equal(len(months), 153, "unique frozen eligible months")
    expected_m = {entry["year_month"]: entry["m"] for entry in strict}
    audit = audit_identity_conflicts(
        retained, fields, author_mn, collisions, months,
        expected_support_m=expected_m,
    )
    must_equal(audit["frozen_eligible_months"], 153, "audit cohort months")
    must_equal(audit["repeat_supported_months_scored"], 153,
               "audit repeats across frozen months")
    must_equal(audit["MN_retained_rows_without_valid_lattice_station"],
               frozen["species_MN_rows_without_valid_lattice_position"],
               "valid station source exclusions")
    result = {
        **audit,
        "source": {
            "doi": "10.5281/zenodo.10049811",
            "source_original_MD5": validation["verified_checksum"],
            "source_authored_processing_MD5": files[PROCESSING]["checksum"],
            "source_author_occasion_MD5": files[TIMEFILE]["checksum"],
            "published_matrix_MD5s": [z["MD5"] for z in matrix_meta],
            "authored_exact_1089_retained_dates_matched": True,
            "frozen_conservative_153_months_reproduced": True,
            "frozen_MNA_variation_years": 22,
            "MNA_values_joined_to_spatial_data": False,
        },
        "scientific_boundary": {
            "one_site_not_multisite_generalization": True,
            "biological_individual_identity_resolved": False,
            "published_MN_19850_individuals_reconciled": False,
            "NEON_original_6_of_8_genus_guard": "FAILED_UNCHANGED",
            "NEON_five_genus_future_confirmation": "NOT_ESTIMABLE",
            "NEON_Peromyscus_frozen_direction": "NOT_REPLICATED_IMPRECISE",
            "next": "Inspect anonymized capture-protocol causes of any same-day multiple-station records; seek author identity-code clarification and write a separate pre-effect release decision. No W/B outcomes may be computed by this run.",
        },
    }
    return result


if __name__ == "__main__":
    try:
        report = run()
    except (PublishedSourceError, RuntimeError, ValueError, UnicodeError,
            OSError, urllib.error.URLError, KeyError) as exc:
        report = {
            "schema": "neon.mosa.effect_blind_identity_conflict_summary.v2",
            "status": "STOP_SOURCE_OR_FROZEN_IDENTITY_AUDIT",
            "diagnostic": str(exc)[:600],
            "MNA_W_B_or_density_effects_opened": False,
            "ecological_effects_opened": False,
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "EFFECT_BLIND_IDENTITY_COUNTS_ECOLOGY_HOLD":
        raise SystemExit(3)
