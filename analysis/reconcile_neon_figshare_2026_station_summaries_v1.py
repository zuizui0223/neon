"""Reconcile the Merz et al. Figshare v2 field inventory and event-table coverage."""
import argparse
import csv
import hashlib
import json
from decimal import Decimal, InvalidOperation
from io import StringIO
from pathlib import Path
from urllib.request import urlopen

METADATA_URL = "https://api.figshare.com/v2/articles/28207769/versions/2"
DOI = "10.6084/m9.figshare.28207769.v2"
FILES = {
    "All Station Nights.csv": (51682220, "1cc4f0c66043c9a96955bed1c66408e3"),
    "All Foraging Clean.csv": (51682217, "5f823a01c8751bd360dab723f3d49faa"),
    "Main Analysis - Clean.R": (51823913, "b5f99bfd6b800cdecb435dfb23f6e6b9"),
}
# Other public files in the fixed v2 deposit also need protection from output writes.
PROTECTED_INPUTS = (
    *FILES, "metadata.json", "2016-2023 Capture Data.csv", "BLUPS_MG 2016-2023.csv",
    "BLUPS_PM 2016-2023.csv", "Mouse Foraging Data Clean.csv",
    "Vole Foraging Data Clean.csv", "Repeatability.R",
)
KEY = ("Grid", "Site", "Session", "Night")
SPECIES = ("WP", "RO")
COUNTS = tuple(f"{s}.seeds.{kind}" for s in SPECIES for kind in ("set", "left"))
LABELS = ("Visitors", "None", "NA")
TOLERANCE = Decimal("0.000000001")


def seed_count(value):
    """Field counts must be nonnegative whole units. A blank is missing."""
    if isinstance(value, bool) or not str(value).isascii() or not str(value).isdigit():
        raise ValueError("Expected a nonnegative integer seed count")
    return int(value)


def station_key(row):
    values = tuple(row.get(column) for column in KEY)
    if any(value is None or not str(value).strip() for value in values):
        raise ValueError("Incomplete station key")
    return values


def verify_summaries(rows, totals):
    # Only this full sequence is a validated footer. Its position is significant.
    summary_checks = []
    for index, name in enumerate(("set_and_left_totals", "differences", "fractions")):
        row = rows[index]
        allowed = COUNTS if index == 0 else COUNTS[::2]
        if any(value != "" for column, value in row.items() if column not in allowed):
            raise ValueError("Nonblank content outside the expected summary cells")
        values = {}
        for column in allowed:
            species = column[:2]
            offered = totals[f"{species}.seeds.set"]
            missing = offered - totals[f"{species}.seeds.left"]
            if index < 2:
                value = seed_count(row.get(column))
                if value != (totals[column] if index == 0 else missing):
                    raise ValueError("Summary count does not match the keyed station rows")
            else:
                try:
                    value = Decimal(str(row.get(column)))
                except InvalidOperation as exc:
                    raise ValueError("Invalid summary fraction") from exc
                if not offered or not value.is_finite() or abs(value - Decimal(missing) / offered) > TOLERANCE:
                    raise ValueError("Summary fraction does not match the keyed station rows")
            values[column] = str(value) if index == 2 else value
        summary_checks.append({"summary_type": name, "source_values": values})
    return summary_checks


def reconcile(stations, events):
    if len(stations) < 4:
        raise ValueError("Expected station rows followed by three summary rows")
    event_keys = {station_key(row) for row in events}
    seen = set()
    totals = dict.fromkeys(COUNTS, 0)
    groups = {
        (present, label): {"event_row_present": present, "station_visitor_label": label,
                           "station_nights": 0, "WP_offered": 0, "WP_missing": 0,
                           "RO_offered": 0, "RO_missing": 0, "nights_with_any_missing": 0}
        for present in (True, False) for label in LABELS
    }
    for row in stations[:-3]:
        key = station_key(row)
        if key in seen:
            raise ValueError("Duplicate keyed station row")
        seen.add(key)
        label = row.get("Visitors?")
        if label not in LABELS:
            raise ValueError("Unexpected Visitors? label")
        group = groups[key in event_keys, label]
        group["station_nights"] += 1
        any_missing = False
        for species in SPECIES:
            set_column, left_column = (f"{species}.seeds.{kind}" for kind in ("set", "left"))
            offered, left = seed_count(row.get(set_column)), seed_count(row.get(left_column))
            if left > offered:
                raise ValueError("Seeds left exceed seeds offered")
            totals[set_column] += offered
            totals[left_column] += left
            group[f"{species}_offered"] += offered
            group[f"{species}_missing"] += offered - left
            any_missing |= offered > left
        group["nights_with_any_missing"] += int(any_missing)
    if not event_keys <= seen:
        raise ValueError("An event key is absent from the station inventory")
    summaries = verify_summaries(stations[-3:], totals)
    return {"station_source_rows": len(stations), "station_nights": len(seen),
            "verified_tail_summaries": summaries, "event_rows": len(events),
            "station_nights_with_event_rows": len(event_keys),
            "coverage": list(groups.values())}


def fetch(url):
    with urlopen(url, timeout=60) as response:
        return response.read()


def run(source_dir, download=False):
    metadata_path = source_dir / "metadata.json"
    if download:
        source_dir.mkdir(parents=True, exist_ok=True)
    raw_metadata = (fetch(METADATA_URL) if download and not metadata_path.exists()
                    else metadata_path.read_bytes())
    metadata = json.loads(raw_metadata)
    if (metadata["id"], metadata["version"], metadata["doi"]) != (28207769, 2, DOI):
        raise ValueError("Unexpected Figshare article version")
    if download and not metadata_path.exists():
        metadata_path.write_bytes(raw_metadata)
    manifest = {f["name"]: f for f in metadata["files"]}
    tables, sources = {}, []
    for name, (file_id, md5) in FILES.items():
        url = f"https://ndownloader.figshare.com/files/{file_id}"
        entry = manifest[name]
        if (entry["id"], entry["computed_md5"], entry["download_url"]) != (file_id, md5, url):
            raise ValueError(f"Source manifest mismatch for {name}")
        path = source_dir / name
        content = fetch(url) if download and not path.exists() else path.read_bytes()
        if hashlib.md5(content).hexdigest() != md5 or len(content) != entry["size"]:
            raise ValueError(f"Source file verification failed for {name}")
        if download and not path.exists():
            path.write_bytes(content)
        sources.append({"file": name, "file_id": file_id, "md5": md5,
                        "sha256": hashlib.sha256(content).hexdigest(), "download_url": url})
        if name.endswith(".csv"):
            tables[name] = list(csv.DictReader(StringIO(content.decode("utf-8-sig"))))
    result = reconcile(tables["All Station Nights.csv"], tables["All Foraging Clean.csv"])
    result.update({"source_doi": DOI, "source_metadata_url": METADATA_URL, "sources": sources,
                   "historical_all_291_station_rows_gate": "FAILED",
                   "historical_gate_diagnosis": "The strict gate treated three verified summary records as station-nights."})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True,
                        help="Directory containing metadata.json and the three pinned Figshare files")
    parser.add_argument("--download", action="store_true", help="Retrieve missing public source files")
    parser.add_argument("--output", type=Path, required=True, help="Aggregate-only JSON destination")
    args = parser.parse_args()
    for name in PROTECTED_INPUTS:
        source = args.source_dir / name
        if (args.output.resolve() == source.resolve()
                or (args.output.exists() and source.exists() and args.output.samefile(source))):
            parser.error("Choose an output path different from the source files")
    report = run(args.source_dir, args.download)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
