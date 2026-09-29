# Jornada SMES heteromyid cross-scale validation — source audit v1

Date: 2026-09-29

Status: source/schema audit only. No sex-specific sample-support count or ecological outcome may be calculated.

## Candidate source

Dataset: `Rodent data from trapping webs in the long-term Small Mammal Exclusion Study (SMES) at Jornada Basin LTER, 1995-2007`.

Published source records identify this dataset as Jornada LTER / USDA and preserve a legacy raw CSV path:

`JornadaStudy_086_smes_rodent_trapping_data_0.csv`

Data.gov continues to list the dataset with CSV resources.

## Why it matters

A trapping-web dataset can potentially provide both:
- one-night spatial configuration from trap/station locations; and
- repeated-night individual movement from marked recaptures.

## Independence boundary

Any later held-out effect analysis must exclude species whose sex-specific outcomes were already inspected in the completed NEON/Portal programme:
- Chaetodipus baileyi
- Chaetodipus penicillatus
- Dipodomys merriami
- Dipodomys ordii

Source auditing may list file headers containing those taxa only indirectly; no species-specific counts or effects are permitted.

## Permitted source-audit actions

- resolve current public CSV resources through the legacy Jornada URL and/or Data.gov CKAN metadata;
- checksum downloaded CSV files;
- record row counts and exact headers;
- classify structural columns for individual identity, sex, species, site/web, trap/station, session/night/date.

## Forbidden at this stage

- counts stratified by sex or species;
- movement distances;
- packing scores;
- sex-effect signs or estimates;
- ecological models.

If a structurally adequate raw capture table is found, a separate estimability design must be frozen before any sex-specific sample-support counts are opened.
