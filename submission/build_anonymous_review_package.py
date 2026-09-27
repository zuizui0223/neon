from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
STAGE = DIST / "oikos_anonymous_review"
ZIP_PATH = DIST / "oikos_anonymous_review_package.zip"

# Keep this list explicit. The review archive is deliberately narrower than the repository.
FILES = {
    "manuscript/neon_metacommunity_redundancy/MANUSCRIPT_V6_MECHANISM_VALIDATED_DRAFT.md":
        "manuscript/main_text.md",
    "manuscript/neon_metacommunity_redundancy/CLAIM_MATRIX_V1.json":
        "evidence/confirmatory_claim_matrix.json",
    "manuscript/neon_metacommunity_redundancy/EXPLORATORY_CLAIM_MATRIX_V1.json":
        "evidence/exploratory_claim_matrix.json",
    "data/derived/site_metrics_v1.csv":
        "data/site_metrics_v1.csv",
    "data/derived/best_species_frequency_v1.csv":
        "data/best_species_frequency_v1.csv",
    "results/carrier_turnover_v1.json":
        "results/carrier_turnover_v1.json",
    "results/carrier_frequency_v1.csv":
        "results/carrier_frequency_v1.csv",
    "results/site_pair_carrier_overlap_v1.csv":
        "results/site_pair_carrier_overlap_v1.csv",
    "data/derived/combine_target_pool_traits_v1.csv":
        "data/combine_target_pool_traits_v1.csv",
    "data/external/carrier_niche_evidence_v2_all32.csv":
        "data/carrier_niche_evidence_v2_all32.csv",
    "results/carrier_niche_role_v2_all32.json":
        "results/carrier_niche_role_v2_all32.json",
    "results/combine_carrier_trait_summary_v1.json":
        "results/combine_carrier_trait_summary_v1.json",
    "results/carrier_prevalence_response_v1.json":
        "results/carrier_prevalence_response_v1.json",
    "results/carrier_prevalence_mechanism_summary_v1.json":
        "results/carrier_prevalence_mechanism_summary_v1.json",
    "analysis/carrier_turnover_v1.py":
        "analysis/carrier_turnover_v1.py",
    "analysis/build_carrier_turnover_figure_v1.py":
        "analysis/build_carrier_turnover_figure_v1.py",
    "analysis/carrier_niche_role_v2.py":
        "analysis/carrier_niche_role_v2.py",
    "analysis/analyze_combine_carrier_traits_v1.py":
        "analysis/analyze_combine_carrier_traits_v1.py",
    "analysis/count_conditioned_carrier_null_v1.py":
        "analysis/count_conditioned_carrier_null_v1.py",
    "analysis/build_carrier_mechanism_figure_v1.py":
        "analysis/build_carrier_mechanism_figure_v1.py",
    "analysis/build_paper_assets.py":
        "analysis/build_paper_assets.py",
    "tests/test_frozen_results.py":
        "tests/test_frozen_results.py",
    "tests/test_carrier_niche_role.py":
        "tests/test_carrier_niche_role.py",
    "tests/test_combine_carrier_traits.py":
        "tests/test_combine_carrier_traits.py",
    "tests/test_count_conditioned_carrier_null.py":
        "tests/test_count_conditioned_carrier_null.py",
    "validation/neon_metacommunity_connectivity_v1/analysis_implementation_v1.json":
        "evidence/analysis_implementation_v1.json",
    "validation/neon_metacommunity_connectivity_v1/fresh_roster_lock_v1.json":
        "evidence/fresh_roster_lock_v1.json",
    "validation/neon_metacommunity_connectivity_v1/protocol_v1.json":
        "evidence/protocol_v1.json",
    "validation/neon_metacommunity_connectivity_v1/response_lock_v1.json":
        "evidence/response_lock_v1.json",
    "validation/neon_metacommunity_connectivity_v1/programme_closure_v1.json":
        "evidence/programme_closure_v1.json",
    "validation/neon_metacommunity_connectivity_v1/posthoc_redundancy_audit_v1.json":
        "evidence/posthoc_redundancy_audit_v1.json",
    "validation/carrier_prevalence_mechanism_v1/protocol_v1.json":
        "evidence/carrier_prevalence_protocol_v1.json",
    "validation/carrier_prevalence_mechanism_v1/fresh_roster_lock_v1.json":
        "evidence/carrier_prevalence_fresh_roster_lock_v1.json",
    "validation/carrier_prevalence_mechanism_v1/target_pool_traits_lock_v1.json":
        "evidence/carrier_prevalence_target_pool_traits_lock_v1.json",
    "validation/carrier_prevalence_mechanism_v1/response_protocol_v1.json":
        "evidence/carrier_prevalence_response_protocol_v1.json",
    "validation/carrier_prevalence_mechanism_v1/response_authorization_v1.json":
        "evidence/carrier_prevalence_response_authorization_v1.json",
}

FORBIDDEN = (
    "zhang",
    "ruiqi",
    "rachel",
    "zuizui0223",
    "github.com/zuizui0223",
    "rachelzhang",
)

README = """# Anonymous review reproducibility package

This archive accompanies a double-anonymized ecological manuscript on local
spatial cohesion in small-mammal metacommunities.

## Contents

- `manuscript/main_text.md`: anonymous V6 manuscript source.
- `data/`: frozen derived site-level, trait and fresh-mechanism tables.
- `results/`: confirmatory, carrier-turnover, niche-role and fresh mechanism results.
- `analysis/`: deterministic analysis and figure-generation scripts.
- `evidence/`: frozen protocols, rosters, response authorization and claim boundaries.
- `tests/`: frozen-result and mechanism integrity checks.
- `MANIFEST.json`: SHA-256 hashes for every packaged file.

## Scientific boundary

The original 16-site confirmatory endpoint is closed: pooling target species did
not increase the declared local spatial-cohesion fraction beyond the best
individual species at any site.

The carrier-turnover and trophic-role extensions are post hoc. They show that
the property is redundant across species within sites while carrier identity
turns over among sites and spans contrasting trophic roles.

A separate response-blind 11-site prospective mechanism programme was then
frozen and consumed once. Its primary count-conditioned test did not support
positive spatial organization beyond prevalence (median site excess -0.0804;
4/11 positive sites; one-sided exact p=0.8867). The predeclared grid-conditioned
decomposition placed essentially all departure at the between-grid allocation
scale, with median within-grid organization component zero.

Post-response diagnostics such as positive traps per occupied grid and
carrier-state switching remain explicitly exploratory and cannot alter the
prospective mechanism decision.

## Reproduction

From the archive root, with Python 3.12 or later:

    python analysis/carrier_turnover_v1.py
    python analysis/carrier_niche_role_v2.py
    python analysis/analyze_combine_carrier_traits_v1.py
    python -m unittest discover -s tests -v
    python analysis/build_paper_assets.py
    python analysis/build_carrier_turnover_figure_v1.py
    python analysis/build_carrier_mechanism_figure_v1.py

The biological source observations are public NEON data; this archive contains
derived review data and the frozen audit trail needed to inspect the manuscript
claims without disclosing author identity.

No repository URL, author name, affiliation, email address or source-control
history is included in this archive.
"""


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def assert_anonymous(path: str, raw: bytes) -> None:
    text = raw.decode("utf-8", errors="ignore").lower()
    hits = [token for token in FORBIDDEN if token in text]
    if hits:
        raise RuntimeError(f"author-identifying token(s) in {path}: {hits}")


def stage_files() -> dict[str, dict[str, object]]:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)

    manifest: dict[str, dict[str, object]] = {}

    readme_raw = README.encode("utf-8")
    assert_anonymous("README_ANONYMOUS.md", readme_raw)
    (STAGE / "README_ANONYMOUS.md").write_bytes(readme_raw)
    manifest["README_ANONYMOUS.md"] = {
        "bytes": len(readme_raw),
        "sha256": sha256(readme_raw),
    }

    for source, target in sorted(FILES.items()):
        src = ROOT / source
        if not src.is_file():
            raise FileNotFoundError(source)
        raw = src.read_bytes()
        assert_anonymous(target, raw)
        dst = STAGE / target
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(raw)
        manifest[target] = {"bytes": len(raw), "sha256": sha256(raw)}

    manifest_raw = (
        json.dumps(
            {
                "schema": "neon.oikos_anonymous_review_package.v1",
                "files": manifest,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")
    assert_anonymous("MANIFEST.json", manifest_raw)
    (STAGE / "MANIFEST.json").write_bytes(manifest_raw)
    return manifest


def build_zip() -> None:
    DIST.mkdir(exist_ok=True)
    stage_files()
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    with zipfile.ZipFile(
        ZIP_PATH,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as zf:
        for path in sorted(p for p in STAGE.rglob("*") if p.is_file()):
            rel = path.relative_to(STAGE).as_posix()
            raw = path.read_bytes()
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, raw, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


if __name__ == "__main__":
    build_zip()
    print(f"{ZIP_PATH}: {ZIP_PATH.stat().st_size} bytes sha256={sha256(ZIP_PATH.read_bytes())}")
