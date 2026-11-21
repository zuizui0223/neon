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
