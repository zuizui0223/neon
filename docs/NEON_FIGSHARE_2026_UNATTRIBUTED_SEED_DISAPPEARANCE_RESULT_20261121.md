# Unattributed seed disappearance at baited field stations without deposited video events — original descriptive result

> **22 November 2026 correction.** The three trailing keyless records have now been verified as totals, differences and rounded fractions, matching the 288 actual station-nights and the published paper. The old all-291-observation gate failure remains historical; it is not evidence for three missing station observations. Moreover, 53 of the 152 nights absent from All Foraging are labeled Visitors in the station file and account for 556 of the 806 missing seed units. Absence from the deposited event table does not establish absence of footage. See the [current reconciliation, independent seed-fate comparison and reproducible results](NEON_SEED_EVENT_FATE_RECONCILIATION_20261122.md). The material below preserves the 21 November interpretation for provenance.


**Date: 21 November 2026. POST-RESULT, one NEON ecology manuscript Draft/SUBMISSION HOLD.**
This is a direct original-source descriptive quantification of **experimental seed disappearance** not paired with **recorded video foraging events**, *not* a novel, replicated, causal mammal process. The original Merz, Record & Mortelliti (2026) *Ecology* paper (DOI `10.1002/ecy.70312`) already acknowledged that seeds may go missing from stations without supporting video footage and included these missing seeds in their community-level response. **This study and basic observation type are PRIOR ART.** We make no new article-level claim about seed dispersal or animal causation.

## Original data and exactly fixed estimand

Original provider article Figshare `28207769 v2`; all five original source files MD5/size verified. Station-night source `All Station Nights.csv` original file ID 51682220, MD5 `1cc4f0c66043c9a96955bed1c66408e3`; video-event source `All Foraging Clean.csv` original file ID 51682217, MD5 `5f823a01c8751bd360dab723f3d49faa`. The previously frozen 291-row strict source gate **FAILED** at three final original rows that lacked every `Grid,Site,Session,Night` key but still had 2–4 nonempty seed count fields. These rows were NOT silently discarded to pass the old gate: original `SOURCE STOP` remains. For a newly precommitted separate, **retrospective descriptive-only** population, use the 288 uniquely keyed source station-night observations with full seed `WP/RO.seeds.set/left` fields; 136 have an exact matching source station-night in the All Foraging video-event ledger, 152 have no matched event key. Original three source rows remain in provenance, unassigned to any station.

Our [fixed descriptive source design](NEON_FIGSHARE_2026_SEED_LOSS_WITHOUT_VIDEO_FROZEN_DESCRIPTIVE_20261121.md) was committed **before source seed count outcomes** were evaluated. Original checks included 4 numeric nonnegative integer fields per station-night, both `Night.set`/ `Morning.check` nonmissing, no `seeds.left > seeds.set` in either seed type, >=100 valid source station-night observations in each camera-event class. The original [GitHub Actions run 44901631224](https://github.com/zuizui0223/neon/actions/runs/44901631224) passed four synthetic tests and original provider MD5s, returned **all 288** precommitted station-night records eligible, **no source quality exclusions**, and preserved the previous strict source STOP separately.

A seed recorded as missing means **number of seeds set out minus number remaining when field workers checked the station**, which can include eaten, moved, unrecorded or otherwise lost seeds. No original video event recorded is not a verified camera-on negative and not true animal absence. The published data represent deliberately provisioned white pine seeds and red oak acorns, NOT site-wide naturally available rodent food, edible energy/biomass or seed production.

## Descriptive ecological source result

| Original source station-night category | Nights with complete seed counts | Nights with ≥1 seed missing | Fraction nights | White pine seeds missing | Red oak acorns missing | Total seeds missing |
|---|---:|---:|---:|---:|---:|---:|
| At least one deposited `All Foraging` video event | **136** | **131** | **96.32%** | **1,564** | **211** | **1,775** |
| **No deposited video foraging event** | **152** | **120** | **78.95%** | **667** | **139** | **806** |
| Combined station-night observations | **288** | **251** | **87.15%** | **2,231** | **350** | **2,581** |

Original seeds offered: camera-event-positive nights WP 1,962 + RO 440 = 2,402; no-event nights WP 2,318 + RO 515 = 2,833; **5,235 individual offered seed/acorn units** overall. The **806 missing units on no-video-event nights represent 31.23% of all 2,581 source missing seed units** (do NOT convert this count to seed *mass*, since pine seeds and acorns differ greatly). Within the original no-event group, 120 of 152 station-nights (78.95%) were missing at least one offered seed/acorn.

This is a valid **source-discrepancy between deposited camera-positive foraging ledger and independent seed fate observations**, consistent with the published paper's discussion of unfilmed loss. It does NOT say that **31.23% of rodent consumption/dispersal was unobserved**, nor establish insects, rodents, tree squirrels, wind, video annotation failures, night camera uptime, visit frequency or competitive/learned behavior. Do not interpret 288 spatially correlated source station-nights as independent landscapes or genuine NEON trap occupancy data.

## Scientific decision

- **Concrete observation:** substantial experimental seed disappearance occurred even on original baited station-nights without any deposited video foraging event; source-level community seed fate is not perfectly described by the available positive-event animal interaction ledger.
- **Prior art and limits:** Original paper already analyzes community-level seeds missing, including non-video seed losses. Our cross-tab is a transparent magnitude/boundary audit of a known data-generating discrepancy, not a new mechanistic ecological principle; no animal-to-seed causal attribution.
- **Consequences for NEON:** A recorded trapping/camera event cannot be assumed to enumerate all resource use. But neither this seed-tray study nor source-level loss can identify what produces NEON's 14-site conditional genus×trap recurrence, or whether interspecific competition, true patch biomass, animal learning or true use underlie it.
- **Next independently falsifiable biological study design:** paired **true on/off detector exposure** AND identifiable individual interactions AND independent patch-specific natural food biomass, at multiple landscapes/times. Only such data would allow resource and interaction-mediated spatial organization to be separated from observation effects. More historical Portal/NEON/PEF post-result effect fishing is not warranted.

## Exact persistent evidence

`analysis/audit_neon_figshare_2026_seed_loss_without_video_v1.py`; `tests/test_neon_figshare_2026_seed_loss_without_video_v1.py`; frozen protocol `docs/NEON_FIGSHARE_2026_SEED_LOSS_WITHOUT_VIDEO_FROZEN_DESCRIPTIVE_20261121.md`; original aggregated result `results/neon_figshare_2026_seed_disappearance_without_video_20261121.json`; [verified GitHub Action 44901631224](https://github.com/zuizui0223/neon/actions/runs/44901631224). No original individual PIT, video, geographic coordinates, field site keys or original CSV source file was re-exported to the repo. Previous NEON, Portal, Finland and Structural mammal original effects unchanged. Draft/SUBMISSION HOLD.
