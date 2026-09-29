# San Jacinto heteromyid cross-scale validation — source audit v1

Date: 2026-09-29

Status: source/schema audit only. No sex-specific packing or movement effect may be calculated.

## Public source

Figshare article: 18295520 v1
DOI: 10.6084/m9.figshare.18295520.v1
Associated study: Chock, Shier & Grether (2022), Oecologia.

Published methods describe eight 7 x 7 trap grids, 49 traps per grid, 6.25 m spacing, monthly trapping for three consecutive nights, unique individual identification, sex, and trap location recorded.

## Independence

The focal heteromyids in this dataset are not among the four species whose sex-specific outcomes were inspected in the completed Portal/NEON programme.

Candidate held-out taxa include:
- Los Angeles pocket mouse (Perognathus longimembris brevinasus)
- Chaetodipus fallax
- Dipodomys simulans
- Dipodomys stephensi

## Permitted now

- query anonymous Figshare API metadata;
- freeze exact file IDs, sizes, checksums and names;
- download public tabular files;
- inspect table/sheet names, headers and row counts;
- determine whether identity, sex, species, grid, trap location and temporal fields are structurally present.

## Forbidden now

- species-specific support counts;
- male/female sample counts;
- movement distances;
- sex-specific packing;
- effect signs, intervals or p-values.

If a structurally adequate raw capture table exists, a separate estimability design must be committed before any sex-stratified support count is opened.
