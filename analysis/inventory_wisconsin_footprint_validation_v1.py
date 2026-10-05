from __future__ import annotations

import argparse
import csv
import io
import json
import re
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

DOI = "10.5061/dryad.zpc866thw"
API_BASE = "https://datadryad.org/api/v2"
TARGET_FILE = "CaptureMaster.csv"


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "neon-wisconsin-footprint-stage0/1.0"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode("utf-8"))


def get_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "neon-wisconsin-footprint-stage0/1.0"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def href(obj: dict, keys: tuple[str, ...]) -> str | None:
    links = obj.get("_links", {})
    for k in keys:
        v = links.get(k)
        if isinstance(v, dict) and v.get("href"):
            return str(v["href"])
    return None


def absolute(url: str) -> str:
    return urllib.parse.urljoin("https://datadryad.org", url)


def discover_files() -> tuple[dict, list[dict]]:
    encoded = urllib.parse.quote("doi:" + DOI, safe="")
    dataset = get_json(f"{API_BASE}/datasets/{encoded}")

    versions_url = href(dataset, ("stash:versions", "versions"))
    if not versions_url:
        raise RuntimeError(f"Dryad dataset response lacks versions link; keys={list(dataset.get('_links',{}))}")
    versions = get_json(absolute(versions_url))
    embedded = versions.get("_embedded", {})
    version_list = embedded.get("stash:versions") or embedded.get("versions") or []
    if not version_list:
        raise RuntimeError("Dryad versions response contains no versions")

    def version_number(v: dict) -> int:
        raw = v.get("version")
        try:
            return int(raw)
        except Exception:
            return -1

    latest = sorted(version_list, key=version_number)[-1]
    files_url = href(latest, ("stash:files", "files"))
    if not files_url:
        # Some API responses require fetching the version resource first.
        self_url = href(latest, ("self",))
        if not self_url:
            raise RuntimeError("Dryad version lacks files/self link")
        latest = get_json(absolute(self_url))
        files_url = href(latest, ("stash:files", "files"))
    if not files_url:
        raise RuntimeError("Dryad latest version lacks files link")

    files_doc = get_json(absolute(files_url))
    fembed = files_doc.get("_embedded", {})
    files = fembed.get("stash:files") or fembed.get("files") or []
    if not files:
        raise RuntimeError("Dryad files response contains no files")
    return dataset, files


def file_download_url(f: dict) -> str:
    # Dryad's HAL API may expose an authenticated API download link even for
    # public datasets. Public browser downloads use file_stream by file id.
    fid = f.get("id")
    if fid is not None:
        return f"https://datadryad.org/stash/downloads/file_stream/{fid}"
    u = href(f, ("stash:download", "download"))
    if u:
        return absolute(u)
    raise RuntimeError(f"file lacks public download id/link: {f}")


def clean(x: object) -> str:
    return str(x or "").strip()


def parse_date(x: object) -> datetime | None:
    s = clean(x)
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None


def recap_columns(columns: list[str]) -> list[tuple[str, str]]:
    out = []
    for c in columns:
        m = re.fullmatch(r"Recap Date\s*(\d+)", c, flags=re.I)
        if not m:
            continue
        n = m.group(1)
        trap = next((x for x in columns if re.fullmatch(rf"Recap Trap\s*{re.escape(n)}", x, flags=re.I)), None)
        if trap:
            out.append((c, trap))
    return sorted(out, key=lambda z: int(re.search(r"\d+", z[0]).group()))


def event_inventory(rows: list[dict]) -> dict:
    if not rows:
        raise RuntimeError("empty capture table")
    columns = list(rows[0].keys())
    pairs = recap_columns(columns)
    if not pairs:
        raise RuntimeError("no Recap Date/Trap pairs detected")

    unit_species_multinight = defaultdict(lambda: defaultdict(int))
    species_rows = Counter()
    species_events = Counter()
    species_multinight = Counter()
    species_multitrap = Counter()
    night_hist = Counter()
    trap_hist = Counter()
    sites = set()
    seasons = set()
    sessions = set()
    reconstructed_events = 0
    usable_rows = 0
    removed_rows = 0

    for i, row in enumerate(rows):
        sp = clean(row.get("Species")).upper()
        site = clean(row.get("Site"))
        season = clean(row.get("Season"))
        session = clean(row.get("Session"))
        if sp:
            species_rows[sp] += 1
        if site:
            sites.add(site)
        if season:
            seasons.add(season)
        if session:
            sessions.add(session)

        remove = clean(row.get("Remove"))
        if remove in {"1", "1.0", "TRUE", "True", "true"}:
            removed_rows += 1
            continue

        initial_date = parse_date(row.get("Capture Date"))
        initial_trap = clean(row.get("Trap ID"))
        if not sp or not site or not season or initial_date is None or not initial_trap:
            continue

        events = [(initial_date.date().isoformat(), initial_trap)]
        for dc, tc in pairs:
            d = parse_date(row.get(dc))
            t = clean(row.get(tc))
            if d is None or not t:
                continue
            events.append((d.date().isoformat(), t))

        # deduplicate exact duplicate date/trap records while preserving dates/traps.
        events = sorted(set(events))
        usable_rows += 1
        reconstructed_events += len(events)
        species_events[sp] += len(events)
        nights = {d for d, _ in events}
        traps = {t for _, t in events}
        night_hist[len(nights)] += 1
        trap_hist[len(traps)] += 1
        if len(nights) >= 2:
            species_multinight[sp] += 1
            unit = (site, season, session)
            unit_species_multinight[unit][sp] += 1
        if len(traps) >= 2:
            species_multitrap[sp] += 1

    units = []
    for (site, season, session), spp in sorted(unit_species_multinight.items()):
        positive_species = {sp:n for sp,n in sorted(spp.items()) if n > 0}
        units.append({
            "site": site,
            "season": season,
            "session": session,
            "multi_night_individuals_by_species": positive_species,
            "species_with_multi_night_individuals": len(positive_species),
            "multi_night_individuals_total": sum(positive_species.values()),
        })

    return {
        "columns": columns,
        "recapture_column_pairs": pairs,
        "raw_rows": len(rows),
        "removed_rows": removed_rows,
        "usable_initial_capture_rows": usable_rows,
        "reconstructed_capture_events": reconstructed_events,
        "sites": sorted(sites),
        "seasons": sorted(seasons),
        "sessions": sorted(sessions),
        "species_raw_rows": dict(sorted(species_rows.items())),
        "species_reconstructed_events": dict(sorted(species_events.items())),
        "species_multi_night_individuals": dict(sorted(species_multinight.items())),
        "species_multi_trap_individuals": dict(sorted(species_multitrap.items())),
        "distinct_night_count_histogram": {str(k):v for k,v in sorted(night_hist.items())},
        "distinct_trap_count_histogram": {str(k):v for k,v in sorted(trap_hist.items())},
        "unit_support": units,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    dataset, files = discover_files()
    inventory = []
    target = None
    for f in files:
        rec = {
            "id": f.get("id"),
            "path": f.get("path") or f.get("name"),
            "size": f.get("size"),
            "mime_type": f.get("mimeType") or f.get("mime_type"),
            "digest": f.get("digest"),
        }
        inventory.append(rec)
        name = clean(rec["path"]).split("/")[-1]
        if name == TARGET_FILE:
            target = f

    if target is None:
        raise RuntimeError(f"{TARGET_FILE} absent; files={[x['path'] for x in inventory]}")

    raw = get_bytes(file_download_url(target))
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    summary = event_inventory(rows)

    result = {
        "schema": "neon.wisconsin_footprint_validation_inventory.v1",
        "status": "stage0_feasibility_only_no_footprint_outcomes_opened",
        "source": {
            "doi": DOI,
            "dataset_title": dataset.get("title"),
            "publication_date": dataset.get("publicationDate"),
        },
        "files": inventory,
        "capture_file": {
            "name": TARGET_FILE,
            "bytes_downloaded": len(raw),
            **summary,
        },
        "claim_boundary": {
            "footprint_overlap_opened": False,
            "conspecific_assortativity_opened": False,
            "community_cscore_opened": False,
            "temporal_persistence_opened": False,
            "turnover_persistence_opened": False,
            "species_pair_outcomes_opened": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
