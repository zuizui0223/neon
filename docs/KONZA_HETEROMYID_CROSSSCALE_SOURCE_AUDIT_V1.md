# Konza heteromyid cross-scale validation — source audit v1

Date: 2026-09-29

Status: source/schema audit only. No sex-specific ecological outcome or sex-specific sample-support count may be calculated.

## Frozen public source

Public GitHub mirror of Konza LTER CSM01 small-mammal data:
- repository: `sarahsupp/KNZ-incidence`
- source commit: `c354a2fb8a034e254365f0ffbe0e0ce82bdfea66`
- raw individual file: `Datasets/Raw_data/Small_mammals/CSM012.csv`
- metadata: `Datasets/Raw_data/Small_mammals/CSM01_metadata.txt`

Underlying Konza/EDI dataset metadata identify CSM012 as individual small-mammal capture records. Sampling is by permanent traplines with 20 stations at 15 m spacing, trapped for 4 consecutive nights in spring and autumn. The metadata state that sex and capture location are recorded at each capture.

## Structural fields expected from metadata

- `Recyear`, `Season`, `RecMonth`, `Recday` — sampling date/context
- `TrapDay` — within-period trapping night
- `Watershed`, `Line` — trapline context
- `Sta` — numbered station
- `Species` — species code
- `Sex` — M/F
- `ToeClip`, `HairClip`, `REarTag`, `LEarTag` — individual-mark fields
- `Status` — capture/mark status

## Current permitted actions

- download the pinned raw CSM012 file;
- checksum and count rows;
- verify exact column names;
- inspect non-stratified coding examples for trap day, station and mark fields;
- verify that the metadata-required structural fields exist.

## Current forbidden actions

- count records by species or sex;
- count males or females;
- reconstruct species-specific individual histories;
- calculate movement distances;
- calculate sex-specific packing;
- fit any ecological effect model.

## Next gate

Only if the source audit passes may a separate estimability design be committed. That design must freeze:
1. the prospective heteromyid taxon set;
2. individual identity reconstruction;
3. session and independent spatial-unit definitions;
4. N-per-sex thresholds;
5. packing and movement estimability gates;
before any species-by-sex sample-support counts are opened.
