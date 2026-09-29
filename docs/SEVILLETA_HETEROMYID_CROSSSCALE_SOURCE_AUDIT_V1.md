# Sevilleta heteromyid cross-scale validation — source audit v1

Date: 2026-09-29

Status: source/schema audit only. No sex-specific ecological outcome may be calculated.

## Source

Sevilleta LTER Small Mammal Mark-Recapture Population Dynamics at Core Research Sites at the Sevilleta National Wildlife Refuge, New Mexico.

Frozen source package:
- KNB package: knb-lter-sev.8.297972
- DOI: 10.6073/pasta/142d2a1c7a1a6397fb56a47b5817bf1d
- public UNM mirror data file: sev008_rodentpopns_20151022.txt

Published design metadata state that the file contains mark-recapture data from permanently established web arrays at 8 sites; each site has 3 webs sampled for 3 consecutive nights in spring and fall; each web contains 145 stakes and 148 traps.

## Why this source is being audited

The completed NEON/Portal sex-packing programme and the held-out-NEON validation are closed. The latter stopped before effects because no uninspected NEON species had enough site-matched N>=5/sex support.

Sevilleta is a genuinely independent trapping programme with a multi-night spatial design and therefore may support an external cross-scale validation.

## Current permitted actions

Permitted:
- download the frozen public source;
- checksum it;
- detect delimiter/header;
- count rows;
- identify structural columns and candidate identity/sex/species/site/web/stake/night/date fields;
- inspect coding dictionaries needed to reconstruct sampling sessions.

Not permitted:
- calculate male/female movement distances;
- calculate sex-specific packing;
- compare male and female spatial endpoints;
- fit ecological effect models;
- choose species based on effect direction.

## Next gate

Only after a source-schema receipt is frozen may a separate estimability design be written. The estimability design must be committed before sex-specific sample-support counts are opened.
