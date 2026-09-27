from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "dist" / "oikos_anonymous_review_package.zip"

FORBIDDEN = (
    "zhang",
    "ruiqi",
    "rachel",
    "zuizui0223",
    "github.com/zuizui0223",
    "rachelzhang",
)

REQUIRED = {
    "README_ANONYMOUS.md",
    "MANIFEST.json",
    "manuscript/main_text.md",
    "data/site_metrics_v1.csv",
    "results/carrier_turnover_v1.json",
    "results/carrier_prevalence_response_v1.json",
    "results/carrier_prevalence_mechanism_summary_v1.json",
    "analysis/carrier_turnover_v1.py",
    "analysis/count_conditioned_carrier_null_v1.py",
    "analysis/build_carrier_mechanism_figure_v1.py",
    "evidence/protocol_v1.json",
    "evidence/response_lock_v1.json",
    "evidence/programme_closure_v1.json",
    "evidence/carrier_prevalence_protocol_v1.json",
    "evidence/carrier_prevalence_fresh_roster_lock_v1.json",
    "evidence/carrier_prevalence_target_pool_traits_lock_v1.json",
    "evidence/carrier_prevalence_response_protocol_v1.json",
    "tests/test_frozen_results.py",
}


def main() -> None:
    if not ZIP_PATH.is_file():
        raise SystemExit(f"missing: {ZIP_PATH}")

    with zipfile.ZipFile(ZIP_PATH) as zf:
        names = set(zf.namelist())
        missing = sorted(REQUIRED - names)
        if missing:
            raise SystemExit(f"missing required package entries: {missing}")

        manifest = json.loads(zf.read("MANIFEST.json"))
        entries = manifest["files"]

        for name in sorted(names):
            raw = zf.read(name)
            text = raw.decode("utf-8", errors="ignore").lower()
            hits = [token for token in FORBIDDEN if token in text]
            if hits:
                raise SystemExit(f"identifying token(s) in {name}: {hits}")

            if name == "MANIFEST.json":
                continue
            expected = entries.get(name)
            if expected is None:
                raise SystemExit(f"unmanifested file: {name}")
            digest = hashlib.sha256(raw).hexdigest()
            if digest != expected["sha256"] or len(raw) != expected["bytes"]:
                raise SystemExit(f"manifest mismatch: {name}")

    print(f"anonymous package verified: {len(names)} files")


if __name__ == "__main__":
    main()
