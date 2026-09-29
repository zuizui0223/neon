# Powdermill cross-scale validation — source audit v1

Date: 2026-09-29

Status: source/schema audit only. No sex-specific ecological outcome may be calculated.

## Candidate source

Long Term Mammal Data from Powdermill Biological Station 1979–1999.

Known package series:
- legacy package: `knb-lter-vcr.67.17`
- current cited EDI DOI/version: `10.6073/pasta/086fda03bd91ce9c2331e3a6fdd9bcd1`, version 21 (2022).

Public documentation states that the raw `database.txt` is read after 21 metadata lines with the following 16 columns:

`animal_id, is_new, species_code, period, time, date, quadrat, sex, sex_unknown, weight, sex_shrew, scrotal_male, inguinal_male, pregnant, open_vulva, large_nipples`.

Published protocol: one 1-ha 10 x 10 station grid with 10-m spacing; two Sherman live traps per station; trapping twice per month from 1979–1999. First captures recorded individual number, grid location, mass, sex and reproductive state; recaptures within the same period recorded number, location and mass.

## Why this source matters

It is independent of the stopped Portal/NEON heteromyid programme and, if the raw object matches the documented schema, contains the three ingredients needed for a direct cross-scale test:
- persistent individual identity;
- sex-specific capture position;
- repeated capture occasions within trapping periods.

## Geometry caveat frozen now

There are **two trap slots per station**. Any later one-night packing null must represent station capacity correctly; it may not reuse the one-animal-per-station finite-population null from Portal/NEON without modification.

At source-audit stage no null model is implemented and no spatial effect is calculated.

## Permitted actions

- query the anonymous DataONE CN index for the `knb-lter-vcr.67` package series;
- select the highest package version before reading biological values;
- resolve candidate data objects anonymously through the DataONE CN resolver;
- checksum source bytes;
- identify the raw record block and verify its structural field count against the documented 16-column schema;
- count total rows only for integrity.

## Forbidden actions

- species-specific row counts;
- male/female counts;
- movement distances;
- sex-specific packing;
- effect signs, coefficients, intervals or p-values.

If source structure is adequate, a separate estimability design must be committed before any sex-specific sample-support counts are opened.
