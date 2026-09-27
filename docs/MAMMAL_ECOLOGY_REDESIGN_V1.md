# Mammal ecology redesign — V1

## New primary goal

Move the project from a coarse occurrence-geometry paper to a **small-mammal population and space-use study** that uses the native strengths of NEON's mark-recapture design.

Primary question:

> **Within the same small-mammal species, how does within-grid space use vary across sites, years and habitats after capture effort and local population size are accounted for?**

This retains the useful intuition behind the former “context-dependent carrier” idea but replaces the carrier endpoint with mammal-scale quantities.

## Scientific object

The new object is **within-grid space use**, not site-level graph connectivity.

The important contrasts are:

- the same species across sites;
- the same species across years;
- the same species across sampling bouts;
- populations in different habitat classes;
- changes in spatial spread conditional on abundance / capture effort.

This design avoids treating continental species-pool turnover as the ecological result.

## Data policy

### Development data

RELEASE-2026 is already response-consumed at the product level by the previous programmes.

It may be used for:

- retrospective model development;
- data-quality diagnostics;
- estimability checks;
- choosing among prespecified biologically interpretable models.

Any ecological result estimated from these already-accessed records is **exploratory/developmental**, regardless of whether a particular column was previously parsed.

### Confirmatory data

No RELEASE-2026 result may be relabelled confirmatory.

After the development model is frozen, confirmatory validation must use the first future NEON small-mammal records not contained in the consumed RELEASE-2026 response. Site or species eligibility rules must be frozen before those observations are opened.

## Sampling unit hierarchy

Retain the native hierarchy rather than collapsing across the release:

1. site;
2. mammal grid / plotID;
3. year;
4. sampling bout / eventID;
5. trapping night / nightuid;
6. trap coordinate;
7. individualID / tag-derived individual;
8. capture event.

## Spatial scales

Primary within-grid scales are fixed in advance from the NEON grid design:

- **10 m** — orthogonal nearest-neighbour trap spacing;
- **14.14 m** — diagonal nearest neighbours;
- **20 m**;
- **30 m**.

These are evaluation scales, not assumed home-range radii.

The analysis must not derive its primary threshold by requiring a large fraction of the *site-wide* graph to connect.

Site-level distances among grids may be analysed separately as a landscape context variable, but they may not be mixed into the within-grid endpoint.

## Effort and completeness

Use the actual sampling effort.

Required inputs include:

- `mam_perplotnight`;
- `mam_pertrapnight`;
- `nightuid`;
- `eventID`;
- `mammalGridSamplingType`;
- `gridCompletion`;
- trap status / whether a trap-night was available for capture.

The denominator for a trap-level response is an **active trap-night**, not a trap that existed somewhere in the release.

Diversity, pathogen and historical recapture grids must not be treated as if they had identical nightly effort.

## Taxonomic rule

Before ecological analysis:

1. use the current corrected taxonomy in the released product;
2. inspect `identificationQualifier`;
3. inspect `mam_identificationHistory` where present;
4. reject or aggregate uncertain cryptic identifications according to a frozen rule;
5. run a sensitivity analysis in which problematic cryptic complexes are analysed at genus / pair level.

The *Peromyscus maniculatus–leucopus* complex is an explicit required sensitivity case.

Do not choose which taxa to aggregate after seeing ecological effect sizes.

## Population size / abundance

Do not use total capture count as if it were population size.

Development analysis should compare:

- minimum number known alive (unique `individualID` / resolved tag identities per population-session);
- effort-standardized capture rate;
- where estimable, closed or spatial capture-recapture abundance/density.

The final confirmatory abundance metric and its estimability gate must be frozen after RELEASE-2026 development and before future response access.

## Primary spatial response

### Development target

For each eligible species × grid × sampling session, estimate the spatial spread of capture activity within the grid.

The primary candidate representation is a **multi-scale neighbour statistic** at 10, 14.14, 20 and 30 m, calculated on effort-standardized trap-level capture/individual-use data.

Its null conditions on:

- active trap set;
- sampling effort;
- local abundance / number of unique individuals;
- the number of capture/use events.

This asks whether captures are more spatially concentrated or dispersed than expected merely because there were more animals or more sampling effort.

### Individual movement secondary

Where repeated captures of the same individual make the comparison estimable, calculate:

- successive recapture displacement;
- within-session displacement distribution;
- individual capture-location radius / spread.

For suitable sessions, evaluate spatial capture-recapture movement-scale parameters as a mammal-specific secondary endpoint.

A separate estimability gate is required for recapture-based inference.

## Habitat

Use `nlcdClass` as the first frozen habitat covariate because it is part of the NEON spatial sampling design.

Primary habitat questions:

- Does within-grid spatial spread differ among habitat classes within the same species?
- Does local abundance modify that relationship?
- Is site-to-site variation reduced after habitat is included?

Additional environmental covariates may be added only in a declared second layer and must not be selected from response correlations.

## Candidate biological hypotheses

### H1 — abundance-conditioned context dependence

Within a species, populations with similar abundance and effort can nevertheless differ in within-grid spatial concentration among sites or years.

Evidence requires repeatability of the species × context effect; a single rare capture cannot define the state.

### H2 — habitat modulation

Within a species, habitat class explains some between-grid or between-site variation in spatial concentration after abundance and effort are controlled.

### H3 — density-dependent spatial expansion

As local population size increases, capture locations occupy a broader part of the grid rather than merely accumulating repeated captures at the same traps.

The sign and functional form should be finalized during consumed-data development and then frozen before future validation.

### H4 — individual movement correspondence

Where recapture data are estimable, population-level spatial concentration should correspond to independently observed individual displacement / movement scale.

This provides a biological validation of any trap-level spatial metric.

## Required negative controls

- shuffle capture locations among active trap-nights while preserving effort and session abundance;
- preserve individual capture frequency when testing spatial arrangement;
- repeat analyses with ambiguous taxa removed / aggregated;
- compare diversity versus pathogen/recapture grid sampling types;
- ensure results are not driven by one trapping night, one individual, or one rare peripheral capture.

## Success criteria for a mammal ecology paper

The paper should not be advanced on a method-only result.

A publishable ecological result needs at least one of:

1. a replicated within-species habitat or abundance relationship;
2. repeatable site/year shifts in mammal-scale space use after effort and abundance adjustment;
3. agreement between population-level spatial concentration and individual recapture movement;
4. a clear, replicated contrast among ecological strategies that remains after local species-pool composition and sampling design are controlled.

## Relationship to V6

V6 is retained as a coarse-scale negative precursor:

> The former site-level structural thresholds were overwhelmingly larger than within-grid trap geometry, so the resulting no-isolated-occurrence endpoint collapsed to grid allocation and did not resolve mammal-scale space use.

The redesign does **not** retune the closed V6 endpoint. It asks a new ecological question with a new response scale.
