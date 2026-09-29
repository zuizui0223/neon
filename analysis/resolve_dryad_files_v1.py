from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

USER_AGENT="arches-heteromyid-dryad-resolver/1.0"
API_ROOT="https://datadryad.org/api/v2"


def get_json(url: str) -> dict:
    req=urllib.request.Request(
        url,
        headers={
            "User-Agent":USER_AGENT,
            "Accept":"application/json",
        },
    )
    with urllib.request.urlopen(req,timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def download(url: str, path: Path) -> int:
    req=urllib.request.Request(
        url,
        headers={"User-Agent":USER_AGENT},
    )
    with urllib.request.urlopen(req,timeout=180) as response:
        raw=response.read()
    if not raw:
        raise RuntimeError(f"empty download: {url}")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw)
    return len(raw)


def _href(obj: dict, rel_contains: str) -> str | None:
    links=obj.get("_links") or {}
    for rel,value in links.items():
        if rel_contains.lower() not in str(rel).lower():
            continue
        if isinstance(value,dict) and value.get("href"):
            return str(value["href"])
        if isinstance(value,str):
            return value
    return None


def _embedded_lists(obj: Any) -> list[list]:
    out=[]
    if isinstance(obj,dict):
        embedded=obj.get("_embedded")
        if isinstance(embedded,dict):
            for value in embedded.values():
                if isinstance(value,list):
                    out.append(value)
        for value in obj.values():
            out.extend(_embedded_lists(value))
    elif isinstance(obj,list):
        for value in obj:
            out.extend(_embedded_lists(value))
    return out


def _all_dicts(obj: Any) -> list[dict]:
    out=[]
    if isinstance(obj,dict):
        out.append(obj)
        for value in obj.values():
            out.extend(_all_dicts(value))
    elif isinstance(obj,list):
        for value in obj:
            out.extend(_all_dicts(value))
    return out


def _absolute(url: str) -> str:
    return urllib.parse.urljoin("https://datadryad.org",url)


def search_dataset(doi: str) -> dict:
    query=urllib.parse.quote(doi,safe="")
    search=get_json(f"{API_ROOT}/search?q={query}")
    needle=doi.lower().replace("https://doi.org/","")
    candidates=[]
    for obj in _all_dicts(search):
        blob=json.dumps(obj,sort_keys=True).lower()
        if needle in blob:
            candidates.append(obj)
    if not candidates:
        raise RuntimeError(f"Dryad API search returned no object matching {doi}")

    # Prefer the shallow dataset summary that exposes a self link.
    candidates.sort(
        key=lambda x:(
            0 if _href(x,"self") else 1,
            len(json.dumps(x,sort_keys=True)),
        )
    )
    summary=candidates[0]
    self_url=_href(summary,"self")
    if self_url:
        try:
            return get_json(_absolute(self_url))
        except Exception:
            pass
    return summary


def latest_version(dataset: dict) -> dict:
    versions_url=_href(dataset,"versions")
    if not versions_url:
        # Some API responses expose versions in embedded form directly.
        version_candidates=[]
        for rows in _embedded_lists(dataset):
            for row in rows:
                if isinstance(row,dict) and (
                    _href(row,"files")
                    or "versionNumber" in row
                    or "version" in row
                ):
                    version_candidates.append(row)
        if version_candidates:
            version_candidates.sort(
                key=lambda x:int(x.get("versionNumber",x.get("version",0)) or 0),
                reverse=True,
            )
            return version_candidates[0]
        raise RuntimeError("Dryad dataset response has no versions link")

    payload=get_json(_absolute(versions_url))
    versions=[]
    for rows in _embedded_lists(payload):
        versions.extend(row for row in rows if isinstance(row,dict))
    if not versions:
        raise RuntimeError("Dryad versions endpoint returned no versions")
    versions.sort(
        key=lambda x:int(x.get("versionNumber",x.get("version",0)) or 0),
        reverse=True,
    )
    return versions[0]


def file_records(version: dict) -> list[dict]:
    files_url=_href(version,"files")
    if not files_url:
        self_url=_href(version,"self")
        if self_url:
            version=get_json(_absolute(self_url))
            files_url=_href(version,"files")
    if not files_url:
        raise RuntimeError("Dryad version response has no files link")

    payload=get_json(_absolute(files_url))
    records=[]
    for rows in _embedded_lists(payload):
        for row in rows:
            if not isinstance(row,dict):
                continue
            name=(
                row.get("path")
                or row.get("fileName")
                or row.get("filename")
                or row.get("name")
            )
            if name:
                records.append(row)
    if not records:
        raise RuntimeError("Dryad files endpoint returned no named files")
    return records


def resolve_download_url(row: dict) -> str:
    for rel in ("download","stash:download","self"):
        url=_href(row,rel)
        if url and ("download" in url or "file_stream" in url):
            return _absolute(url)

    for key in ("downloadUrl","downloadURL","url"):
        value=row.get(key)
        if value and ("download" in str(value) or "file_stream" in str(value)):
            return _absolute(str(value))

    # If only a file self endpoint is present, retrieve it once and re-check.
    self_url=_href(row,"self")
    if self_url:
        detail=get_json(_absolute(self_url))
        for rel in ("download","stash:download"):
            url=_href(detail,rel)
            if url:
                return _absolute(url)
        for key in ("downloadUrl","downloadURL","url"):
            value=detail.get(key)
            if value and ("download" in str(value) or "file_stream" in str(value)):
                return _absolute(str(value))

    raise RuntimeError(
        "no public download URL found for Dryad file record: "
        + json.dumps(row,sort_keys=True)[:1000]
    )


def resolve_and_download(
    doi: str,
    wanted_names: list[str],
    output_dir: Path,
) -> dict:
    dataset=search_dataset(doi)
    version=latest_version(dataset)
    records=file_records(version)

    by_name={}
    for row in records:
        name=str(
            row.get("path")
            or row.get("fileName")
            or row.get("filename")
            or row.get("name")
            or ""
        ).strip()
        if name:
            by_name[name]=row

    missing=[name for name in wanted_names if name not in by_name]
    if missing:
        raise RuntimeError(
            f"Dryad API file list missing exact names: {missing}; "
            f"available={sorted(by_name)}"
        )

    outputs=[]
    for name in wanted_names:
        row=by_name[name]
        url=resolve_download_url(row)
        size=download(url,output_dir/name)
        outputs.append({
            "name":name,
            "download_url":url,
            "bytes":size,
            "api_file_record":row,
        })

    return {
        "doi":doi,
        "dataset_id":dataset.get("id"),
        "version_number":version.get("versionNumber",version.get("version")),
        "available_file_names":sorted(by_name),
        "downloads":outputs,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--doi",required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--manifest",type=Path,required=True)
    parser.add_argument("--file",action="append",dest="files",required=True)
    args=parser.parse_args()

    out=resolve_and_download(args.doi,args.files,args.output_dir)
    args.manifest.parent.mkdir(parents=True,exist_ok=True)
    args.manifest.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "doi":out["doi"],
        "dataset_id":out["dataset_id"],
        "version_number":out["version_number"],
        "downloads":[
            {"name":row["name"],"bytes":row["bytes"]}
            for row in out["downloads"]
        ],
    },indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
