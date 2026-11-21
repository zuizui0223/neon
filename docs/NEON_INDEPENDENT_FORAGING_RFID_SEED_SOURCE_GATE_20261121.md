# Direct foraging and resource observations: independent Figshare source gate (2026-11-21)

**One integrated NEON mammal ecology PR #23, Draft / SUBMISSION HOLD. Source inventory BEFORE raw response files.**

## Exact new candidate and scientific usefulness

Merz, Boone & Mortelliti (2023), *Ecosphere*, **DOI 10.1002/ecs2.4377**, `https://doi.org/10.6084/m9.figshare.21512436` original Figshare article ID **21512436**. Original study: six Maine trapping grids, original known `Myodes gapperi` individual identity and personality, paired 2018 forest-floor seed trays with controlled preferred *Pinus strobus* (5g) and less-preferred *Abies balsamea* (5g), predator-risk refuge manipulation (cover vs no cover), original RFID antennas and cameras at feeding patches, measured actual seed availability, seed choices, removal/consumption. Original published result: ~603 wild vole site visits including 306 seed selection events by **16** identified animals with usable original personality data. Individual personality, predator risk and seed-selection effects are **already in the article, not new NEON ecology**. Passive RFID at baited food stations does NOT document all movement or general habitat-space use. Fewer than ~16 individually identifiable decision-making voles prohibits large-scale generality.

The article's Figshare repository is a **potential independent behavioral and use-sensor calibration** to establish what data actually identify resource use rather than capture-space recurrence. The candidate is not an NEON/Portal replication and will not be quantitatively pooled across estimands. Individual-level learning is NOT directly randomized in the original study. Resource quantities are *offered* seed supply, not naturally available standing biomass; risk treatment is cover (predation risk proxy), not direct species competition.

## Secondary disjoint candidate (source-only, no outcomes)

Merz, Record & Mortelliti (2026), *Ecology* (DOI 10.1002/ecy.70312), “Intraspecific and environmental variation mediate seed finding effectiveness among scatter-hoarding small mammals”, official article data statement `https://doi.org/10.6084/m9.figshare.28207769` **article ID 28207769**. This source was identified during the 2026-11-21 literature screening. It is a distinct publication potentially containing original encounter/seed-finding data, but no schema, rows, sample size, download availability or biological effects have been verified by our source audit. Merely naming it is not a validation; do not combine with 2023 data by assumed shared individuals or protocols.

The 2023 dataset is the **primary candidate**. Secondary candidate is inventory-only for now and cannot replace a primary download/source gate failure, or be opportunistically selected for a favorable result.

## Strict two-step public-source gate

**Stage A — provider metadata only, no original biological data rows.**

From official `https://api.figshare.com/v2/articles/21512436` and `https://api.figshare.com/v2/articles/28207769`: require HTTP 200, JSON object with exact id, authoritative title, DOI and version/date if present, list of file metadata records (nonzero unique numerical file IDs, original filenames, original sizes, original content-checksum md5 if published, official file download URL). Cap JSON metadata to 1MB and original files to 50 entries. A redirect, HTML challenge, invalid file listing, unexpected article ID, oversize, duplicate ID/name or unexpected source status is **SOURCE_STOP** and never an ecological null. Only public static file names, IDs, sizes, hashes, provider type and aggregate candidate status may be recorded. No private credentials, animal identities, GPS coordinates, tracking/movement or response outcomes.

**Stage B — source bytes, only after separate explicit file selection by verified metadata, no frozen biological effect yet.**

For 2023 source, choose original files by provider names and data descriptions, pin the exact source file ID, size and MD5 (if present), then download *only the minimum modest sized original tabular text required* through a public `download_url` issued by Figshare. No guessing ZIP data structure, no substituting article PDFs/figures, no scraping website, no switching to a different study or source version on failure. Validate byte count and checksum, UTF-8 CSV schema, unique original individual and patch keys, shared timestamps and offered seed availability fields. A first GO requires verified jointly matchable (1) identity or anonymized individual tag, (2) independent camera/RFID foraging event, (3) resource quantity by patch/event, (4) cover/risk treatment, (5) original sampling exposure; otherwise STOP. The ecological sample's actual size is not established by published summary alone.

**No effect unsealing:** do not fit an interaction, seed preference, risk/learning effect, spatial fidelity or competitor slope in this source inventory. Original effects are prior art. A later protocol would need a genuinely new *conditional* question (e.g., how detector-independent food-patch visit templates alter interpretation of capture-derived space use) but must not be reverse engineered after opening 2023 data.

## Mechanism boundaries and prior NEON status

The existing source-verified NEON 14-site genus×capture-station Z+0.795 and 30-site exploratory two-genus Z+0.615 remain conditional observations. Independent Portal site-stake R1 non-support, Finland own-location stationary null −0.2426, NEON density 5/8 guard failure, and Portal plant-count/competitor temporal instability plus spring-site NDVI non-decline are untouched. No new true species niche or learning result. The single manuscript remains **SUBMISSION HOLD**.

Stage-A artifacts:
- `analysis/audit_neon_figshare_foraging_source_inventory_v1.py`
- `tests/test_neon_figshare_foraging_source_inventory_v1.py`
- `.github/workflows/neon-figshare-foraging-source-inventory.yml`
- `build/neon_figshare_foraging_source_inventory_v1.json` (provider metadata/STOP only)
