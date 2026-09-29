# Arches heteromyid cross-scale validation — source audit v1

Date: 2026-09-29

Status: source/schema audit only. No sex-specific spatial or movement outcome may be calculated.

## Frozen public source

Dryad dataset: `10.5061/dryad.pv608`

Files audited:
- `Rodent Trapping, Salt Valley.csv` (Dryad file stream 21848)
- `Rodent Trapping, Willow Flats.csv` (Dryad file stream 21850)

Published methods establish permanent trapping grids (163 stations at Salt Valley; 156 at Willow Flats), 15 m station spacing, 2–3 consecutive nights per trapping session, numbered ear tags for captured animals, and release at the recorded point of capture.

## Independence boundary

`Dipodomys ordii` is already outcome-inspected in the completed NEON/Portal programme. It may be present in the source audit, but it is prospectively excluded from any future held-out effect analysis.

Any future estimability design may use only heteromyid species whose sex-specific packing and movement outcomes were not inspected in the completed programme.

## Permitted actions now

- download and checksum the two frozen trapping files;
- inspect exact headers, row counts, delimiter, and structural coding examples;
- determine whether identity, sex, species, capture date/session/night, and trap-station information are present;
- determine whether the two files can be treated as distinct site contexts.

## Forbidden now

- species-specific sample-size counts;
- male/female counts;
- movement distances;
- sex-specific packing scores;
- sex-effect signs, coefficients, intervals or p-values.

An estimability design must be frozen in a later commit before any sex-specific sample-support counts are opened.
