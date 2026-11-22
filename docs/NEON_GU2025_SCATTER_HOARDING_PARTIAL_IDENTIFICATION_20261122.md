# Recorded seed consumption dominates the maximal possible primary caching under unknown fates — Gu 2025, retrospective source bounds

**22 November 2026 · Analytical source boundary, NOT a new mammal macroecological mechanism, and NOT evidence from geographically replicated source populations.** One NEON ecological paper `PR #23` remains DRAFT / SUBMISSION HOLD. No historical NEON, Portal, Finland, Structural, or density/space effects have been refitted. Original Gu et al. Figshare 29815622 v2 raw data were previously verified against original byte length, MD5, SHA256 and fixed source version; this new independent arithmetic only reads the archived source-verified aggregate receipt.

## Primary scientific question and source grain

Given that many originally tracked seeds have fate coded `M` (*missing / fate unknown*), **what ecological conclusions about eating versus primary scatter-hoarding survive if we assign every unknown outcome to whichever category makes the claim hardest to support?**

Gu et al. (2025), *Ecology and Evolution* DOI [10.1002/ece3.72409](https://doi.org/10.1002/ece3.72409), public source [Figshare 29815622 v2](https://doi.org/10.6084/m9.figshare.29815622.v2). Prior article already establishes functional-trait matching, individual rodent body size versus tree seed size and species-associated pilfering. Those are **PRIOR ART** and no new interaction, competition, learning or trait effect is inferred here.

The source `Dispersal` worksheet contains **738 original RECORD ROWS**, but only **735 literal seed codes** (three codes have two non-identical rows each). The seed outcome table does NOT include actor-individual PIT despite the separate `Rodent survey` PIT table. Nothing here justifies treating 738 rows or the 536 species-labelled rows as independent animals, seed fates, or PIT-matched events. The publication discusses 736 seeds; no undocumented de-duplication or arbitrary row selection has been made. All estimates below describe **the 536 original rows with literal actor species assigned**, not the 119 blank-disperser rows or the 83 `Not triggered` rows.

Original fate codes: `EAR` eaten after removal, `EIS` eaten in situ, `SHI` primary scatter-hoarded, `M` seed fate missing. Let `n_s` be assigned-species original row count, `h_s=SHI`, `e_s=EAR+EIS`, `m_s=M`. Only for the source-defined binary categorization of these rows (confirmed eating versus primary cache, where M may belong to either):

```text
known-fate SHI fraction  = h_s / (n_s - m_s)       [descriptive complete cases]
all-row SHI lower bound  = h_s / n_s
all-row SHI upper bound  = (h_s + m_s) / n_s
confirmed eating count  = e_s
maximum SHI count       = h_s + m_s
```

These are **logical, sharp record-level partial-identification bounds** under the SOURCE categories. They are not statistical intervals or biological missing-at-random estimates. They do NOT identify final recruitment success: a primary cache might be pilfered or eventually eaten; naturally occurring mast biomass was not measured.

## Fully audited result (exact recorded counts, no imputation)

| Actor species (original row labels) | Source species-labelled rows `n` | Confirmed EAR+EIS `e` | Confirmed SHI `h` | M unknown `m` | SHI among only known fates | SHI possible fraction of all rows | Confirmed eaten vs MAX possible SHI |
|---|---:|---:|---:|---:|---:|---:|---|
| *Apodemus draco* | 373 | **227** | 28 | 118 | 28/255=10.98% | **7.51%–39.14%** | **227 > 146** (positive margin 81) |
| *Niviventer confucianus* | 159 | **104** | 18 | 37 | 18/122=14.75% | **11.32%–34.59%** | **104 > 55** (positive margin 49) |
| *Niviventer fulvescens* | 4 | 2 | 0 | 2 | 0/2=0% | 0–50% | **2 = 2** (no positive dominance) |
| **All three assigned-species source row labels** | **536** | **333** | **46** | **157** | Not a pooled independent animal/seed rate | 46/536–203/536 | **333 > 203** (positive margin 130) |

**Robust positive ecological-description bound:** across the TWO dominant actor labels, the number of recorded eaten-seed outcomes exceeds even the number of primary scatter-hoarding records possible if **ALL fate-unknown M** were primary caches. Across all 536 named-actor ROWS, 333 (62.13%) are confirmed EAR/EIS and at most 203 (37.87%) could be SHI in this binary source coding. The difference of **130 rows** survives even a maximally adverse arbitrary removal of one row from each of the **three duplicated seed codes** (a purely arithmetic lower bound of **127**). This is not a reconstruction of uniquely tagged biological seeds, much less independent animal-site replication.

**But the apparent species-level SHI preference difference is NOT robust:** A naive complete-case comparison suggests `N. confucianus minus A. draco = 18/122 - 28/255 = +3.77 percentage points`. The **sharp cross-species difference bounds** span `18/159 - 146/373 = −27.82 percentage points` to `55/159 - 28/373 = +27.08 points`. They include both signs. If, solely as a demonstration, both species' unknown `M` records were assigned the **same hypothetical** probability `p` of SHI, the direction reverses at `p = 2262/4961 ≈ 45.60%`. No source evidence licenses equal p, missing at random or independence, and the original article's seed-trait-specific tests are DISTINCT estimands from this unadjusted row-level species contrast.

## Why this advances ecology but cannot yet explain NEON

The source supports one **bounded biological observation**: among identified seed-handler rows in this subtropical system, confirmed eating outnumbers even maximally possible PRIMARY caching (within the exact source fate vocabulary), whereas a simple body-size/rodent-species ordering of caching fractions does **not** withstand unknown outcomes. Species composition, seed size/traits, repeated handling of the same seed and behavior-specific observation all remain possible drivers of the original biology; this calculation cannot isolate them.

This is materially different from NEON's genus-specific seasonal **capture-station** recurrence over physical sites. The Gu experiment did not measure any NEON trap station, and the workbook's seed-fate table lacks actor PIT identity; no individual experience, true territorial interaction, repeated patch exploitation or replacement mechanism is estimable. Consumption-versus-caching is a **seed-fate outcome**, not a proxy for tree seed biomass, forest production, plant recruitment or animal spatial niche. Keep this as a **separate, supplementary source-bounded ecological example**, never as an extra independent NEON site, a replicated mechanism or a new headline result.

## Reproducible and anti-leakage execution

Script: `analysis/gu2025_scatter_hoarding_partial_ID_v1.py`, no XLSX rewriting and no new original data rows opened. Upstream fixed receipt `results/neon_gu2025_seed_fate_archive_20261122.json` (original workbook SHA256 `9424cc40bab0ad1d498abb91c0a961ff6aa81a1a04946d1515a14b4d6baadfcb`), synthetic tests `tests/test_gu2025_scatter_hoarding_partial_ID_v1.py`; workflow `.github/workflows/neon-gu2025-scatter-hoarding-partial-ID.yml`; result `results/neon_gu2025_scatter_hoarding_partial_ID_20261122.json`. No individual tags, seed codes, source dates or source spatial coordinates emitted. Historic pre-source outcome selection and all failed NEON validation rules remain unchanged. **ONE Draft/SUBMISSION HOLD**.
