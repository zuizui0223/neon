# Original independent 5–6cm contact logger versus rodent capture source: verified and STOP

Date: 15 November 2026. ONE integrated NEON mammal spatial ecology manuscript v0.9 PR #23. This is **published independent detector evidence** and a **new source-quality audit**, NOT a new causal ecological contact effect.

## Biological reason to seek independent proximity

The latest Finnish 2021 bank-vole reanalysis (same open original cohort) showed site-equal same-identity rank persistence of capture-centroid pair distances: +0.469 over shuffled identity (10 sites/102 dyads), while within-individual seasonal captured-centroid locations shifted. Neither model observed animal-to-animal contact. Direct contact, resource sharing, pathogen exposure and social affiliation cannot be inferred from stability of distances between baited-trap capture centroids.

Independent published 2025 prairie-vole field-enclosure study: Davidson et al., *Journal of Mammalogy* 106(4):1035–1044, DOI **10.1093/jmammal/gyaf032**. Author-deployed ProxLogs measured signals at approximately **5–6 cm**, while separately collected live-trap co-capture observations formed a second social network. The AUTHOR-PUBLISHED result for the shared 24-animal network was trapping association-versus-ProxLogs QAP Pearson **r=0.148**, **R²=0.02**, not a new result of NEON. Authors used frequency/intensity and degree and documented substantially higher logger resolution. It is a seminatual enclosure dataset involving *Microtus ochrogaster* and is NOT independent contact observations of original NEON genera, Portal *Dipodomys* or Finnish *Myodes*.

## Actual public source files, all verified from Figshare REST

Public Figshare project ID 228462. Source metadata Action #43712998261 (corrected original collar_ids and global_ids filenames); official article listing identified **nine public files**.

A separate MD5+file-size verifying original source auditor [Action #43713170444](https://github.com/zuizui0223/neon/actions/runs/43713170444) successfully downloaded the nine original files, **2,287,874 original bytes**, all checksum matched, and audited CSV headers/row counts without returning animal IDs or event pairs:
- **50,741** original close-proximity ProxLogs event rows, file prox_full_noduplicates.csv, columns c1,c2,date,datetime.
- **4,454** animal capture rows, full_voles_trap.csv, columns date,enclosure,stake.trap,tag,weight,sex,fate.
- **2,588** original trapping-network rows, rfid_trap_network_data_method.csv.
- **38** collar device-to-animal deployment rows, collar_ids.csv with date_on and date_off.
- **76** device operation summary rows, proxlog_summary.csv.
- **648** all-animal sex metadata rows, global_ids.csv.
- Original author analysis code JoM_analyses.R and two original collar recovery quality tables.

## Source namespace and chronology at original event grain

The 50,741 logger rows have **101,482 c1/c2 endpoint fields**. All match published collar DEVICE IDs; none are direct PIT TAG IDs. The 26 distinct collared-animal tags (14 M, 12 F in original global metadata) are therefore NOT recovered by a naive numeric join to the trap tag column.

The source-only 2024 Figshare device/day/date episode crosswalk [Action #43714508039](https://github.com/zuizui0223/neon/actions/runs/43714508039) used 2025 original provider-MD5 verified 6 biological source files and actual recorded dates to map device IDs to PIT tags. The deterministic diagnostic found:
- **37/38** original collar episodes had forward dated starts/ends. **ONE** had date_off earlier than date_on. No arbitrary date correction is allowed.
- One source device has **overlapping dated records assigning it to different animal IDs**; ambiguous calendar day is not manually assigned according to contact outcomes.
- **50,737/50,741 events (99.992%)** had a unique date-specific animal mapping at BOTH logger endpoints among the valid 37 episodes. **FOUR events** remain unresolved at endpoint 2. This mapping was measured for ALL source rows without effect-oriented exclusions. Successfully mapping individual contact positives does not imply that loggers captured ALL eligible contacts or zero-contact dyad-day exposures.
- Logger events occurred on **17 calendar days** and ordinary live capture on **132 calendar days** (across full original source). **10 days** have any event in both modalities; this broad day overlap is NOT evidence that the exact same dyads were monitored simultaneously or over equal exposure.
- The source has **26 original collared individual tags** also appearing somewhere in the trapping dataset. The original enclosure label takes multiple values across capture records for 15 collared tags; without source-author semantic resolution do NOT claim these are separate independent enclosure populations or actual between-enclosure animal movements.
- Original logger datetime strings are mostly time-first and original trap network TimeStart/TimeStop are numeric, thus calendar-day matching used the separately explicit date columns, NOT guessed timestamp formats or numeric time period semantics.

**Source integrity decision: FAIL CLOSED.** Pre-source-frozen rule required all 38 original collar episodes valid/noncontradictory, >=80% individually resolvable events, >=12 collared tags with trap records, >=5 logger/capture overlapping days. Original **full 38 chronology fails** even though 99.992% of event positives are one-to-one mapped in a quarantined source diagnostic. Therefore no new dyad-positive-versus-negative ecological regression, no sex-assortativity or exposure-normalized direct-contact inference was performed. Re-scoping to favorable valid episodes and treating silent devices as recorded absences would be post-result source selection and is unauthorized in this programme.

## What the mammal biology does and does not show

The original 2025 published logger-vs-trapping comparison offers real separate-hardware evidence that an association from live trapping provides extremely limited quantitative information about logger-measured proximity. A positive original QAP r with R²=0.02 does not mean 98% of ecological social relationships are random; it is a statement about their observable, unequal-resolution matrices in that original 24-vole comparison.

The new source audit verifies that raw data for a direct observation channel exist and that virtually all positive records can be mapped to the original collared animals by verified dates. However, source validity and at-risk zero-contact denominators are insufficient to claim a new longitudinal contact pattern. The Finnish original 47/10/102 paired-distance result cannot be called contact-partner persistence, nor is the original NEON 14-site Z+0.795 a social-network edge, direct habitat use or fitness outcome. Structural island results are based on mapped occurrence and geographic kNN graph, not observed dispersal. No niche-mechanism, true social ties, transmission, rescue, or universal persistence claim is established by joining these different systems.

## Reproducibility and status

- Full anonymous source receipt: results/neon_prairie_vole_direct_contact_source_receipt_20261115.json
- Project manifests: [GitHub Action #43712998261](https://github.com/zuizui0223/neon/actions/runs/43712998261)
- All 9 provider MD5-verified file headers: [Action #43713170444](https://github.com/zuizui0223/neon/actions/runs/43713170444)
- Namespace/test-only source: [Action #43713728803](https://github.com/zuizui0223/neon/actions/runs/43713728803)
- Device time crosswalk, 37/38 data-source scientific STOP: [Action #43714508039](https://github.com/zuizui0223/neon/actions/runs/43714508039)
- Original published study: https://doi.org/10.1093/jmammal/gyaf032
- Actual public source project: https://figshare.com/projects/Journal_of_Mammalogy_-_Methods_for_measuring_fine-scale_social_proximity_in_small_mammals/228462

NEXT: independent contact ecology requires a completely identified matched PIT/collar deployment and logger uptime/absence observation model in a new original source, or an author-curated corrected chronology version prospectively frozen as a NEW source. Do not silently patch the existing invalid 38-row source after the fact. One NEON macroecology manuscript stays DRAFT/SUBMISSION HOLD; no original negative gate is overwritten.
