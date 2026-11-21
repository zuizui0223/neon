# 2026 Figshare original mouse/vole foraging and station-night observation data — source schema gate

**21 November 2026, frozen from original provider metadata inventory BEFORE downloading 2026 original ecological data values.** One NEON Draft PR #23, SUBMISSION HOLD.

## Why a separate 2026 source audit?

Merz, Record & Mortelliti (2026), *Ecology*, DOI **10.1002/ecy.70312**, published source `10.6084/m9.figshare.28207769.v2`, exact original Figshare article ID **28207769** version **2**. The 2026 article describes activity/resource finding in the **same Penobscot Experimental Forest** used in Merz, Boone & Mortelliti (2023). It is NOT an independent geographical replication of the 2023 paper; original 2016–2023 capture records may contain the **same PIT animals** from the 2018 seed experiment. Do NOT pool effect sizes or claim independent field samples without exact identity/date/grid overlap QA.

The original provider metadata check [run 44854388505](https://github.com/zuizui0223/neon/actions/runs/44854388505) discovered **9 original files** in this distinct 2026 v2 article. Filenames alone show 2016–2023 capture records and station-night & taxon-specific foraging tables; actual sampling years/effort/linked identity are **NOT yet observed**.

## EXACT five bounded source files: bytes fixed from original Figshare provider metadata

| Original name | Provider file ID | Exact original bytes | Original MD5 |
|---|---:|---:|---|
| `2016-2023 Capture Data.csv` | 51682214 | 1,224,945 | `d9b8cd69378a98c520b10172b80f2c23` |
| `All Foraging Clean.csv` | 51682217 | 792,575 | `5f823a01c8751bd360dab723f3d49faa` |
| `All Station Nights.csv` | 51682220 | 35,432 | `1cc4f0c66043c9a96955bed1c66408e3` |
| `Mouse Foraging Data Clean.csv` | 51682229 | 278,572 | `63adc6b8f232e423fefc2d802d25904d` |
| `Vole Foraging Data Clean.csv` | 51682232 | 313,588 | `e05cb082df82286672f49a39df4585b2` |

The remaining four provider-listed BLUP+R code files are not required to discover original source data grain. Do NOT download or execute those models at this stage.

## Stage B exact data provenance and source schema GO/STOP

Re-fetch official `https://api.figshare.com/v2/articles/28207769` original public metadata, require article version **2**, title matching *Intraspecific and environmental variation*, exactly **9 file entries** and all five selected files' exact published IDs/names/sizes/MD5. For each, download only official HTTPS `ndownloader.figshare.com/files/{original_ID}`; insist original byte size & MD5 reproduce exactly, reject HTML/JSON/binary, malformed UTF-8, ragged CSV rows, duplicate nonempty headers, impossible headers, zero records. Log original scientific column labels and row counts, any original **unnamed** header positions, SHA256. Do not silently assign meaning to unnamed source column, export biological values or rewrite source.

One source-only GO requires five byte/CSV schema receipts. It is **NOT** a biological field-effort GO, not a known mouse/vole foraging panel and not proof of independent data. Do not calculate identity, species, movement, risk, resource, learning, seed-choice, foraging efficiency, competition or recurrence effects. If incomplete, source STOP without dropping unfavorable cohorts or swapping another source.

The next separately frozen *support* test would verify whether original `All Station Nights.csv` is a full station×night effort denominator and whether mouse/vole foraging events, original capture IDs and actually offered resource measurements can be matched in calendar time and patch ID. Treat the original combined All Foraging table and taxon-specific data as potentially **overlapping views**, not three independent event samples. Separately quantify any original 2018 PIT×GRID overlap with verified 2023 Figshare data before calling any cross-paper biological independence. No assumptions from names.

## Biology, novelty, and previous results

Source gives a possible route toward distinguishing **actual baited seed use, opportunity/exposure and taxon/individual histories**, not direct unbaited habitat space, community turnover, biomass, conspecific competition, social contact, or experimentally demonstrated learning. Original 2026 results are PRIOR ART and no NEON novel ecological mechanism has been inferred. Original 2023 source has already verified 603 vole foraging events, 599 PIT-personality-seed linked events, 43 PIT identities, six grids, with `TREAT` forestry-management and `SITE_ID` covered/uncovered risk; do not pool with 2026 as independent sites.

Pipeline: `analysis/audit_neon_figshare_2026_original_foraging_schema_v1.py`, `tests/test_neon_figshare_2026_original_foraging_schema_v1.py`, `.github/workflows/neon-figshare-2026-original-foraging-schema.yml`; output `build/neon_figshare_2026_original_foraging_schema_v1.json`. ONE NEON ecology manuscript remains Draft/SUBMISSION HOLD.
