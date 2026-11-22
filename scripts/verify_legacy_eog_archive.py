#!/usr/bin/env python3
"""Verify archived EOG small-mammal files against original Git blob SHA and size."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"archive/eog_legacy_neon_20261122/SOURCE_MANIFEST.json"

def git_blob_sha(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode()+payload).hexdigest()

def main() -> None:
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if len(data["files"]) != 80:
        raise SystemExit("Unexpected EOG legacy file count")
    for item in data["files"]:
        path=ROOT/item["target"]
        if not path.is_file():
            raise SystemExit(f"MISSING: {path}")
        payload=path.read_bytes()
        if len(payload)!=item["size_bytes"] or git_blob_sha(payload)!=item["blob_sha"]:
            raise SystemExit(f"SHA OR SIZE MISMATCH: {path}")
    print(f"PASS: {len(data['files'])} immutable archived EOG NEON files verified")

if __name__=="__main__":
    main()
