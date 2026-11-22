# Historical NEON files migrated from EOG

**Archive only — not an active NEON manuscript or a validated biological conclusion.**

These are the exact files of the former EOG 16-site small-mammal metacommunity/continuity analysis, statistical protocol, frozen response receipt, historical Oikos manuscript proposals, editorial checks, and associated tests. They were archived here on 2026-11-22 before removal of the biological manuscript lane from EOG.

- Original EOG commit: [methods repository snapshot](https://github.com/zuizui0223/eog/tree/91240104f9816459cd9555a63555664aff60760b).
- Manifest: [source Git blobs and destination map](SOURCE_MANIFEST.json).
- Verify without executing archived experiments: `python scripts/verify_legacy_eog_archive.py`.
- Archived `.github/workflows` files are **not active**; scripts under this folder are historical only.

## Why this must not become the current Oikos submission

EOG's original 16-site endpoint had **0/16 positive null-adjusted turnover-gain sites** and **13/16 sites with multiple species independently passing the originally declared continuity metric**. These figures are reproduced historical endpoint observations, not robust functional redundancy or demonstrated metacommunity movement.

The later EOG ceiling audit found full best-species saturation at 16/16 sites, which algebraically constrains the primary statistic and null p-value. Crucially, the canonical NEON repository's mammal-ecology validity audit established that 93/94 original adjacency worlds connected every trap pair in a grid, and 26/27 sites were already saturated at the smallest threshold; the raw carrier-turnover conclusion also failed a species-pool-conditioned test (p=0.7568). This weakens the historical biological interpretation.

**Current NEON canonical status:** [README](../../README.md) — SUBMISSION HOLD; the new mainline is individual-based mammal-scale space use accounting for sampling effort, density/abundance, capture–recapture and habitat. Do not submit the legacy V6 or the legacy EOG manuscript as a new paper. Do not promote the old 13/16 result as a general ecological discovery.

The complete preserved EOG frozen method results still exist in EOG commit history, but NEON is the biological interpretation owner. EOG remains the methodological/finite-world benchmark owner. This migration does not add an EOG-WF predictive endpoint or rescore original biological results.
