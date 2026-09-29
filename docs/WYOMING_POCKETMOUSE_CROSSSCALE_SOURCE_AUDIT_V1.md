# Wyoming pocket-mouse cross-scale validation — source audit v1

Date: 2026-09-29

Status: source/schema audit only. No species-specific sex effect or movement outcome may be calculated.

## Frozen public source

University of Wyoming DataCorral dataset:
- title: It's a Trap: Optimizing Detection of Rare Small Mammals
- DOI: 10.15786/n57k-sz82
- public ZIP: https://pathfinder.arcc.uwyo.edu/publications/ZooPhys/Harkins_etal_OriginalData.zip

Associated field study:
- 2015–2016 small-mammal trapping in Wyoming;
- 4 consecutive nights per site under the published field protocol;
- individually marked animals using PIT or numbered ear tags;
- species, sex, trap type, bait type and grid point recorded for captures.

## Independence boundary

`Dipodomys ordii` is already outcome-inspected in the completed NEON/Portal programme and is prospectively excluded from any future effect analysis.

The focal held-out heteromyid candidate is `Perognathus fasciatus`; no sex-specific outcome for this species has been inspected in the prior programme.

## Permitted actions now

- download and checksum the frozen ZIP;
- inventory archive members;
- inspect table headers, delimiters and total row counts;
- identify structural fields for individual identity, sex, species, site, spatial trap/grid point and temporal occasion/night/date;
- determine which archive table(s) are structurally capable of supporting a later estimability design.

## Forbidden now

- species-specific row counts;
- male/female counts;
- recapture counts by species;
- movement distances;
- sex-specific packing;
- effect signs, intervals, coefficients or p-values.

A separate estimability design must be frozen before any held-out species sample-support count is opened.
