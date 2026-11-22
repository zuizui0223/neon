"""Describe rows of the pinned Gu et al. Figshare v2 archive. Requires openpyxl.

Run with --source-dir pointing to the three published files and a copy of the
Figshare v2 metadata response named Gu_v2_metadata.json, and --output FILE.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


DOI = "10.6084/m9.figshare.29815622.v2"
METADATA_URL = "https://api.figshare.com/v2/articles/29815622/versions/2"
FILES = {
    "Raw data.xlsx": (56869019, 51056, "d6fca6133f60fdd0971557f8ab4c9b7e"),
    "Gu_code.R": (57701641, 8533, "5de4b92c120a8c35b072737d9344185c"),
    "README.txt": (57701638, 1413, "da65fb22331ee45f1bb7d50feec1002b"),
}
SPECIES = {"Apodemus draco", "Niviventer confucianus", "Niviventer fulvescens"}
# Terms in the pinned README; blank cells remain a separate archive category.
FATES = {"IIS": "intact in situ", "EIS": "eaten in situ", "EAR": "eaten after removal",
         "SHI": "scatter-hoarded during primary dispersal", "M": "missing"}


def check_file(path, size, md5):
    data = path.read_bytes()
    if len(data) != size or hashlib.md5(data).hexdigest() != md5:
        raise ValueError(f"Size or MD5 differs from pinned provider file: {path.name}")
    return hashlib.sha256(data).hexdigest()


def source_manifest(directory):
    metadata_path = directory / "Gu_v2_metadata.json"
    data = metadata_path.read_bytes()
    meta = json.loads(data)
    if (meta.get("id"), meta.get("version"), meta.get("doi")) != (29815622, 2, DOI):
        raise ValueError("Expected the Gu et al. Figshare version 2 record")
    entries = meta["files"]
    by_name = {entry["name"]: entry for entry in entries}
    if set(by_name) != set(FILES) or len(entries) != len(FILES):
        raise ValueError("Published file list differs from pinned version 2")
    files = []
    for name, (file_id, size, md5) in FILES.items():
        entry = by_name[name]
        if (entry["id"], entry["size"], entry["computed_md5"]) != (file_id, size, md5):
            raise ValueError(f"Figshare metadata differs from pinned file: {name}")
        sha256 = check_file(directory / name, size, md5)
        files.append({"name": name, "id": file_id, "size_bytes": size, "md5": md5,
                      "sha256": sha256, "download_url": entry["download_url"]})
    return {"provider": "Figshare", "doi": DOI, "version": 2, "license": meta["license"]["name"],
            "metadata": {"url": METADATA_URL, "name": metadata_path.name, "size_bytes": len(data),
                         "sha256": hashlib.sha256(data).hexdigest()}, "files": files}


def describe_rows(rows):
    class_fates = {key: Counter() for key in ("species_assigned", "literal_not_triggered", "blank", "other")}
    species_fates = defaultdict(Counter)
    histories = defaultdict(list)
    fate_counts = Counter()
    for row in rows:
        code = row["Code"]
        if code in (None, ""):
            raise ValueError("Dispersal row without a seed code")
        actor = row["Dispersers"]
        fate = row["Fate"] or "blank"
        if actor in SPECIES:
            category = "species_assigned"
            species_fates[actor][fate] += 1
        elif actor == "Not triggered":
            category = "literal_not_triggered"
        elif actor in (None, ""):
            category = "blank"
        else:
            category = "other"
        histories[code].append(tuple(sorted(row.items())))
        class_fates[category][fate] += 1
        fate_counts[fate] += 1
    repeated = [records for records in histories.values() if len(records) > 1]
    return {
        "archive_rows": sum(fate_counts.values()),
        "distinct_seed_codes": len(histories),
        "repeated_code_groups": len(repeated),
        "nonidentical_repeated_code_groups": sum(len(set(records)) > 1 for records in repeated),
        "rows_by_fate": dict(fate_counts),
        "rows_by_disperser_class_and_fate": class_fates,
        "rows_by_assigned_species_and_fate": dict(species_fates),
    }


def inspect(directory):
    from openpyxl import load_workbook

    manifest = source_manifest(directory)
    workbook = load_workbook(directory / "Raw data.xlsx", read_only=True, data_only=True)
    try:
        seed_rows = iter(workbook["Dispersal"].values)
        columns = next(seed_rows)
        rodent_columns = next(workbook["Rodent survey"].values)
        counts = describe_rows(dict(zip(columns, values, strict=True)) for values in seed_rows)
        sheets = workbook.sheetnames
    finally:
        workbook.close()
    return {
        "status": "ARCHIVE_ROW_DESCRIPTION_ONLY", "manifest": manifest,
        "sheets": sheets, "columns": {"Dispersal": columns, "Rodent survey": rodent_columns},
        "fate_definitions_from_readme": FATES,
        "pit_column_present": {"Dispersal": "PIT" in columns, "Rodent survey": "PIT" in rodent_columns},
        "rodent_individual_join_performed": False,
        "interpretation": [
            "All cell counts describe Dispersal worksheet rows. Repeated seed codes are retained.",
            "Not triggered is the literal Dispersers value. Its sensor channel is unspecified. "
            "It does not establish the absence of an animal.",
            "M denotes an unknown seed fate. Blank denotes an empty cell. "
            "An assigned disperser species does not resolve a missing fate.",
            "The published study describes 736 seeds. The archive contains nonidentical rows sharing seed codes. "
            "The published R script uses explicit count vectors. Its mapping from workbook rows "
            "to the article's analysis population is undocumented in these files.",
        ],
        **counts,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    for name in (*FILES, "Gu_v2_metadata.json"):
        source = args.source_dir / name
        if output == source.resolve() or (output.exists() and source.exists() and output.samefile(source)):
            parser.error(f"--output would overwrite source file: {name}")
    result = inspect(args.source_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
