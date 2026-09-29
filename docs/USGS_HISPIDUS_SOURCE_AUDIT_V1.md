# USGS hispid pocket mouse mark–recapture — source audit v1

Date: 2026-09-29

Status: public-source/schema audit only. No sex-specific ecological outcome may be calculated.

## Candidate source

USGS Science Data Catalog record:
`USGS:f36fdaba-fe3d-4e59-a68f-fdc034219816`

Title:
`Data associated with: To ear tag or to PIT tag? A comparison of mark loss rates for eight rodent species`

Publication date: 2026.

The release includes *Chaetodipus hispidus* among eight rodent species and is marked public by USGS.

## Why it is only a candidate

The published purpose is tag-loss estimation, not spatial ecology. The source is useful for the present programme only if the public files retain:
- a persistent individual identifier;
- sex;
- species identity;
- repeated capture dates/occasions;
- trap/station or spatial coordinates sufficient to reconstruct capture location.

If the public files omit capture location, the candidate is rejected before any sex-specific effect is opened.

## Permitted actions

- query the public Data.gov CKAN metadata;
- download public XML metadata resources;
- resolve public ScienceBase item metadata;
- list public file names and checksums/sizes when exposed;
- download text-like public data files solely to inspect headers and structural columns;
- count total rows for file-integrity purposes.

## Forbidden actions

- species-specific row counts;
- male/female counts;
- movement distances;
- sex-specific spatial packing;
- effect signs, coefficients, intervals or p-values.

Any estimability design must be frozen after this source audit and before sex-specific sample-support counts are opened.
