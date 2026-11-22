# Direct prairie vole logging vs trapping: source admission STOP (15 November 2026)

One unified NEON mammal ecology manuscript PR #23, DRAFT/SUBMISSION HOLD; no new biological direct-contact effect opened.

## What original data were verified

Published Davidson et al. 2025 (DOI 10.1093/jmammal/gyaf032) compared live-trapping and ProxLogs at 5–6cm within a single ~0.1ha prairie-vole enclosure. Their already-published 24-animal network association had QAP r≈0.148 and MRQAP R²≈0.02. This is prior art, not a new result of NEON.

The author-specified original Figshare project 228462 has NINE original file entries. Original independent stage confirmed MD5/byte integrity and schema of SEVEN published CSVs:
- prox_full_noduplicates.csv: 50,741 original raw logger event records;
- full_voles_trap.csv: 4,454 original trapping records;
- rfid_trap_network_data_method.csv: 2,588 preconstructed trap-network records;
- collar_ids.csv: 38 original collar assignments (PIT-tag/collar start/end);
- proxlog_summary.csv: 76 logger administrative records;
- global_ids.csv: 648 ID-sex records;
- collar_success_long.csv: 48 device-success records.

These checks prove original source and columns exist, NOT that any individual dyad was observed by both devices in a trustworthy simultaneous period. Original nine-file manifest: results/neon_prairie_vole_figshare_source_manifest_20261115.json. Seven-file verified header/source receipt: results/neon_prairie_vole_verified_raw_schema_20261115.json.

## Actual strict source integrity outcome

Before opening logger dyad contacts, the separately run original collar-interval date audit read all 38 source collar assignment rows with unchanged provider MD5. **Exactly ONE source collar assignment has date_on AFTER date_off**; zero had identical start/end dates. This violates the prospectively declared requirement that every original source collar-on/off record have coherent temporal ordering before constructing a single joint animal×sensor×date exposure denominator.

Result **STOP_ORIGINAL_COLLAR_INTERVALS_SOURCE_INTEGRITY**, not a direct-contact biological negative and not a demonstrated zero simultaneous event. Do not discard the invalid collar assignment after seeing the problem, treat the animal as a contact-free dyad, or invent source correction. Do not join all 50,741 sensor event records to all 4,454 trapping rows while the collar working risk set is undefined. Other missing/invalid original contact observation intervals remain UNTESTED because the first strict source check stopped.

GitHub [original calendar source Action #43696359435](https://github.com/zuizui0223/neon/actions/runs/43696359435) completed technically SUCCESS and preserved anonymous STOP artifact #14154313086 digest SHA256 06abbbce5c3a262dd222406b3dee94450a6e888a7c870c5bf6ad9013d8fa3e94. Machine-reproducible anonymized source result is in results/neon_prairie_vole_collar_original_calendar_STOP_receipt_20261115.json. It includes neither collar/tag identities nor source dates.

## Implication for actual mammal ecology

The already-published independent benchmark implies recorded within-trap co-occurrence explains very little of high-resolution 5–6cm recorded proximity in this single enclosure, but cannot validate the 2021 Finnish 47-vole within-site dyad ranks or the NEON original 14-site genus capture-station recurrence. This remains the important distinction:

1. capture station/niche opportunities,
2. relative space among individual animals,
3. actually observed co-location within the sensor's field range,
4. biological interaction such as resource competition, stable pair bond, pathogen infection.

Results at levels 1–2 are NOT evidence of 3–4. A new ecological test must measure physical co-location plus known sensor uptime and independently dated station/trap operation within the same population, with confidence that the detector records zeroes rather than missing observations. The high concentration of contacts among a few individuals documented in independent 2025 Mastomys work (DOI 10.1002/ece3.72367) provides a biologically plausible social-avoidance/contact-filter mechanism, but that work is previously published and in another mammal system.

A later original author-supplied, provider-versioned correction that makes collar risk sets well defined could be independently admitted under a newly frozen source audit, but a post-outcome deletion of exactly one bad row is not a legitimate confirmatory test. No effects from already inspected NEON/Portal/Finnish vole/Structural were recalculated. No additional standalone methods paper or fake quantitative validation was created.
