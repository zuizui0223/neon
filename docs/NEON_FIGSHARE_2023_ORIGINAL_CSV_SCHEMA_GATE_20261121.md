# Original 2023 Figshare seed/RFID source bytes — effect-blind schema admission
Date 21 November 2026, after official provider metadata inventory [run 44854388505](https://github.com/zuizui0223/neon/actions/runs/44854388505), **before any original CSV rows have been read**.

**Primary study fixed:** Merz, Boone & Mortelliti 2023 `Ecosphere` (DOI 10.1002/ecs2.4377); original Figshare article **21512436**, provider article version **1**, `10.6084/m9.figshare.21512436.v1`. Original dataset contains five source files, NOT 2026 study files. Original provider metadata receipt `results/neon_figshare_foraging_original_metadata_20261121.json`.

## Exact 2023 original file selection from published provider metadata

Only THREE original small CSVs, downloaded unchanged from official HTTPS `download_url` (do not guess a file URL or scrape the landing page):

| Original published filename | Original Figshare file ID | Provider published exact bytes | Published MD5 |
|---|---:|---:|---|
| `2018 Vole Seed Data.csv` | 38217891 | 66667 | `5c58051b71eaa55cd888c87b6494a00c` |
| `Vole BLUPS.csv` | 38217897 | 108786 | `ddfb7c7a7e6472dd064bc3e4edda7d81` |
| `Vole Personality Data.csv` | 38217900 | 343858 | `f0d2310389cc1c02cbeabf352b0b131c` |

The original R analysis scripts are in the verified metadata but **not** downloaded or executed in this source-byte gate. The separate 2026 Figshare article **28207769 v2** remains untouched at original-data stage.

## Source-only code and stage

Re-fetch exact article **21512436** metadata from `https://api.figshare.com/v2/articles/21512436` and independently check the provider `id`, published version **1**, file IDs/names/bytes/md5 matches the above exact lock (including consistent figure/article provenance). For each locked file, require official metadata HTTPS `download_url` on exact provider `ndownloader.figshare.com` (or `figshare.com`), path ending `/files/{pinned_original_id}`. GET with a timeout and published source size +1 maximum; reject non-200/HTML/JSON/ZIP, wrong byte size or MD5, malformed UTF8 or duplicate CSV columns, empty CSV, ragged row, duplicate source headers. Calculate exact original SHA256 for future integrity audit, count original rows, report header columns only. Do not copy raw rows or identity tags into artifacts or commit them. Source GO here means `source CSV header/bytes verified`, **not** the source-level ecological join is possible.

**No new ecological model or inference:** Do not calculate selection proportions, seed consumption, behavior, risk preference, per-individual memory, fitness, learning, or a cross-study mammal spatial recurrence statistic. Original article already published an association of predator-risk/cover and individual personality with voles' seed choices; it is **prior art**. Source is a mechanism-oriented behavioral calibration candidate, not NEON/Portal/Finland macroecological replication.

After byte/schema GO, a separately fixed join feasibility design may inspect only structural categories/ID support and event dates; no arbitrary recoding after observing biological effects. Code `analysis/audit_neon_figshare_2023_original_csv_schema_v1.py`; tests `tests/test_neon_figshare_2023_original_csv_schema_v1.py`; CI `.github/workflows/neon-figshare-2023-original-csv-schema.yml`. Output source receipt `build/neon_figshare_2023_original_csv_schema_v1.json`. One NEON Draft PR #23 remains **SUBMISSION HOLD**.

## Original header diagnosis and narrowly scoped correction (after source-format STOP)

The first original MD5-verified file run [Action 44854592523](https://github.com/zuizui0223/neon/actions/runs/44854592523) passed source-identity tests but source STOPPED with `SOURCE_EMPTY_HEADER_LABEL`. Rather than rename arbitrary fields, a separate effect-blind header-only [Action 44854666315](https://github.com/zuizui0223/neon/actions/runs/44854666315) verified the exact original provider MD5 for all THREE CSVs and reported original column names, row widths and counts **without opening biological effects or raw individual data**:

- `2018 Vole Seed Data.csv`: original **603 rows × 26 named columns** including `PIT, SESSION, GRID, Moon, TREAT, SITE_ID, SPP, Seed_Choice, Choice_YN, Amt_Consumed, WP, BF, PercWP, PercBF, PropWP, PropBF, Dispersed, MG_ABUND, PRED_PRES`. No empty headers. These header labels suggest source for original per-event animal/patch/treatment/seed-access variables; no ecological association or verified join yet.
- `Vole BLUPS.csv`: original **1,069 rows × 9 columns**, exactly **ONE unnamed first column at index 0** plus eight named `PIT,bl_ms,bl_rr,bl_groom,bl_prop_center,bl_handling,bl_latency_em,bl_time_tunnel`. The unlabeled field's semantic meaning is unknown and is excluded from scientific covariates; original bytes and raw schema remain intact.
- `Vole Personality Data.csv`: original **3,712 rows × 22 named columns**, including `PIT,SESSION,SEASON.x,YEAR,SPP.x,GRID.x,HANDLING,Mean.speed,Rear...rate,Prop.time.center`. No empty headers.

Repaired the parser to accept **only the exact original 2023 Figshare `Vole BLUPS.csv` with the single empty first column**, never general empty headers or invented values, and to preserve both original and scientific-name headers. The original biological/source selection rules, exact original MD5/byte counts, 2023 article v1 and previous NEON findings did not change. New workflow must verify complete three-file source GO before any join feasibility is attempted. Stage-B source GO is NOT an ecological effect.
