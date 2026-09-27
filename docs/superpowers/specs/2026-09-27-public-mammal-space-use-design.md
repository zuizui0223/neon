# Public small-mammal data study — design v1

Date: 2026-09-27

Status: design for review; implementation has not started.

## 1. Purpose

Build a mammal-ecology paper entirely from **already public small-mammal capture data**, without waiting for future NEON releases and without reusing the coarse V6 carrier/cohesion endpoint.

The biological question is:

> **Does ecological context alter how a small-mammal population is spatially packed within a trapping grid, independently of how many individuals were captured?**

The study will use two complementary public data systems:

1. **Portal Project** — long-term experimental manipulation of rodent competitors in fixed plots;
2. **NSF NEON DP1.10072.001 RELEASE-2026** — geographically broad capture–mark–recapture monitoring across many habitats.

Portal supplies the causal competition contrast. NEON supplies broad replication across species, sites and habitat classes.

The intended product is a mammal ecology paper, not a methods paper and not a continuation of the V6 carrier analysis.

## 2. Why this design

### Option A — NEON only

Strengths:
- many species and sites;
- standardized 10 m grid;
- repeated sampling bouts;
- tag IDs, effort and habitat metadata.

Weakness:
- habitat contrasts are observational;
- no direct manipulation of competitor access.

### Option B — Portal only

Strengths:
- monthly data since 1977;
- permanent 7 × 7 trapping grids;
- individual IDs;
- long-running control and kangaroo-rat exclusion treatments.

Weakness:
- one desert system;
- a Portal-only result may be difficult to generalize.

### Option C — Portal causal test + NEON broad replication — selected

Portal tests whether dominant-competitor removal changes spatial packing at matched local abundance.

NEON asks whether abundance-conditioned spatial packing is context dependent across habitats and sites.

The datasets are not pooled as if they had identical sampling designs. They use one common dimensionless response statistic, then are modeled separately and synthesized at the biological-question level.

## 3. Source data

### 3.1 Portal Project

Research source:
- repository: `weecology/PortalData`
- living archive/data paper: DOI 10.5281/zenodo.1215988
- methods: `SiteandMethods/Methods.md`

Relevant public tables:

- `Rodents/Portal_rodent.csv`
  - individual capture records;
  - species;
  - plot;
  - stake;
  - sex;
  - reproductive state;
  - body mass;
  - long-term individual `id`;
  - `pit_tag` reliability indicator.

- `Rodents/Portal_rodent_trapping.csv`
  - period;
  - plot;
  - sampled;
  - effort;
  - qcflag.

- `SiteandMethods/Portal_plots.csv`
  - time-specific rodent treatment;
  - resource treatment;
  - ant treatment.

- `SiteandMethods/Portal_UTMCoords.csv`
  - plot/stake UTM coordinates.

Portal plots are 50 × 50 m. The rodent grid has 49 permanent stakes in a 7 × 7 layout, approximately 6.25 m apart. Normal trapping records use positive period codes. Negative period codes are excluded.

### 3.2 NEON small-mammal box trapping

Source:
- data product: DP1.10072.001
- release: RELEASE-2026
- DOI: 10.48443/A83H-TB34

Relevant tables:

- `mam_perplotnight`
  - one record per plotID × collectDate;
  - `nightuid`;
  - `eventID` for sampling bout;
  - `mammalGridSamplingType`;
  - `gridCompletion`.

- `mam_pertrapnight`
  - trapCoordinate;
  - plotID;
  - collectDate/nightuid;
  - tagID;
  - taxon identity;
  - identificationQualifier;
  - capture and animal measurements.

- `mam_identificationHistory`
  - published taxonomic revisions.

Trap-specific coordinates are recovered from NEON geolocation using
`plotID + "." + trapCoordinate`.

Most NEON mammal grids are 10 × 10 traps with 10 m spacing and approximately 90 × 90 m extent. Diversity grids are sampled one night per bout; pathogen grids are normally sampled three nights per bout. Mammal grids are distributed among site land-cover classes and spatial metadata include NLCD information.

## 4. Core response: abundance-conditioned population spatial packing

The two datasets have different absolute grid dimensions. They therefore will not be compared with one absolute distance threshold.

The common primary response is a **dimensionless effort- and abundance-conditioned spatial packing score**.

### 4.1 Session

Portal primary session:

`species × plot × positive census period`

NEON primary session:

`species × site × diversity-grid plotID × eventID`

For the NEON primary analysis, only one-night diversity-grid bouts are used. Multi-night pathogen grids are reserved for secondary validation.

### 4.2 One location per individual

Each individual contributes at most one spatial point per session.

Portal:
- use the unique `id`;
- each normal plot census provides one capture position per captured individual.

NEON:
- use `tagID`;
- primary diversity-grid sessions are one-night sessions, so a marked individual contributes its capture trap once.

This prevents an individual with many recaptures from mechanically receiving more spatial weight.

### 4.3 Observed statistic

For each eligible session with N captured unique individuals of one species, calculate:

`MPD_obs = mean pairwise Euclidean distance among individual capture locations`.

### 4.4 Geometry- and abundance-conditioned null

For the same session:

1. retain the exact available trapping locations;
2. retain N, the observed number of unique individuals;
3. sample N active trap locations without replacement;
4. calculate mean pairwise distance;
5. repeat 999 times, or enumerate all combinations when smaller.

The primary response is:

`Packing_z = (MPD_obs - mean(MPD_null)) / sd(MPD_null)`.

Interpretation:

- `Packing_z < 0`: individuals are more spatially concentrated than expected from grid geometry and N;
- `Packing_z ≈ 0`: spatial arrangement is consistent with random placement of N individuals among available traps;
- `Packing_z > 0`: individuals are more spatially dispersed than expected.

Because N and the available trap geometry are conditioned on, the response is not the old occupied-trap-count effect in another form.

### 4.5 Primary eligibility

A session enters the primary packing analysis only when:

- N >= 5 unique target individuals;
- valid spatial coordinate exists for every retained capture;
- the primary effort/completeness rule for that dataset is satisfied;
- no excluded taxonomic ambiguity applies.

Sensitivity analyses repeat with N >= 3 and N >= 8.

## 5. Portal primary causal analysis

### 5.1 Clean experimental window

Primary Portal causal window:

**August 2009 through March 2015.**

Reason:
- long-standing resource manipulations had ended;
- ant treatments were discontinued after July 2009;
- the broad rodent-treatment reassignment occurred on 31 March 2015.

Within this window, use plot-months whose current `Portal_plots` treatment is:

- `control`, or
- `exclosure` (kangaroo rats excluded).

Exclude:
- all-rodent removal plots;
- negative period codes;
- `sampled != 1`;
- `effort != 49`;
- records failing the recommended QC rule;
- non-target rodents.

### 5.2 Biological contrast

Primary Portal model:

`Packing_z ~ log(N) * kangaroo_rat_exclosure + species + seasonal_time + plot + year`

implemented as a hierarchical mixed model with:

- fixed effect of centered log N;
- fixed treatment effect;
- N × treatment interaction;
- species-specific intercepts and N slopes;
- plot random intercept;
- year effect;
- cyclic month or new-moon-period seasonal structure.

The primary ecological parameter is the **treatment modification of the abundance–packing relationship**.

Interpretation:

- treatment effect at matched N: dominant-competitor exclusion changes spatial packing independently of local captured abundance;
- N × treatment interaction: competitor environment changes how populations spatially reorganize as crowding changes.

The analysis does not claim that stake-level capture location is an individual's home range.

## 6. NEON broad replication analysis

### 6.1 Primary sampling subset

Use only diversity-grid bouts for the primary cross-site analysis because these grids are sampled for one night per bout and therefore most closely match Portal's one-night census unit.

A NEON session requires:

- `mammalGridSamplingType = diversity`;
- a valid eventID;
- acceptable gridCompletion;
- at least 90 usable trap locations unless the official grid has fewer design locations;
- unambiguous target-species identification under the frozen taxonomy rule;
- N >= 5 unique tagIDs.

Actual active-trap geometry, rather than an assumed 10 × 10 square, is used by the null.

### 6.2 Habitat context

Use the published NEON `nlcdClass` spatial metadata.

Raw NLCD classes are grouped before outcome analysis into a small ecological set:

- forest;
- shrub/scrub;
- grassland/herbaceous;
- cropland/pasture;
- wetland;
- other/rare.

The exact code-to-group lookup is stored as a frozen table before model fitting.

### 6.3 Model

Primary NEON model:

`Packing_z ~ log(N) * habitat_group + seasonal_time + species + site + year`

with:

- species random intercepts;
- species random slopes for log N where estimable;
- site random intercept;
- year effect;
- habitat-group main effect and N interaction.

The primary NEON question is whether **within-species abundance-conditioned packing varies among ecological contexts**, not whether species occupy different continents or regional species pools.

## 7. Cross-dataset synthesis

NEON and Portal are not merged row-wise.

Synthesis uses three levels.

### 7.1 General density–packing relationship

Compare the distribution of species-specific log(N) slopes in:

- Portal controls;
- Portal kangaroo-rat exclosures;
- NEON habitat groups.

### 7.2 Shared species

For species represented with sufficient sessions in both datasets, compare the sign and magnitude of abundance-conditioned packing slopes.

No minimum number of shared species is assumed in advance. This layer is reported only when at least three shared species meet the frozen estimability rule in both datasets.

### 7.3 Experimental interpretation

Portal is the only source used for causal statements about kangaroo-rat competitor exclusion.

NEON habitat effects remain observational.

A positive result is not required to match exactly across the two datasets. The intended synthesis is whether population spatial packing is a fixed species property or is modified by ecological context after N and sampling geometry are controlled.

## 8. Secondary mammal-specific validation

### 8.1 NEON pathogen grids

Multi-night pathogen grids are excluded from the primary packing model but used to validate the biological meaning of the population packing statistic.

For species × grid × bout units with adequate recapture data, calculate:

- successive within-bout recapture displacement;
- individual capture-location spread;
- where estimable, an SECR movement/detection scale.

Test whether session-level `Packing_z` is associated with these independent individual-level movement quantities.

### 8.2 Portal individual history

Portal `id` allows month-to-month re-encounter displacement among stakes and plots.

This is secondary because the temporal interval is longer than the within-bout NEON recapture interval.

Use it only to test whether populations with persistently high or low packing scores also show systematic differences in individual spatial displacement/residency.

## 9. Taxonomic uncertainty

### NEON

Before outcome fitting:

1. use current released taxonID/scientificName;
2. inspect `identificationQualifier`;
3. inspect `mam_identificationHistory`;
4. exclude uncertain species-level assignments from the primary analysis;
5. run a sensitivity analysis with cryptic complexes aggregated at genus/pair level.

The *Peromyscus maniculatus–P. leucopus* complex is a mandatory sensitivity case.

### Portal

Use target-rodent species codes from the research dataset.

Use the long-term unique `id`, preferring records whose individual identity is PIT-tag based where sensitivity to identity quality matters.

Portal species/identity data flags are retained and summarized before modeling.

## 10. Effort and data-quality controls

### Portal

Primary analysis requires:
- positive period;
- sampled = 1;
- effort = 49;
- recommended qcflag;
- valid stake;
- no off-plot trapping.

### NEON

Primary analysis requires:
- diversity grid;
- one-night event;
- acceptable gridCompletion;
- valid trap geolocation;
- valid tagID;
- target species;
- taxonomic certainty rule satisfied.

The actual trap set is reconstructed from `mam_pertrapnight`.

## 11. Robustness and non-independence

Required sensitivity analyses:

1. N threshold: 3 / 5 / 8;
2. first-capture / unique-individual position rule;
3. remove sessions dominated by one trap or one individual-history anomaly;
4. Portal PIT-tag-reliable subset;
5. Portal control versus exclosure using only long-term treatment plots;
6. NEON leave-one-site-out;
7. NEON leave-one-year-out;
8. ambiguous taxa removed versus aggregated;
9. NEON pathogen-grid secondary replication;
10. alternative spatial response:
   - null-standardized radius of gyration;
   - null-standardized nearest-neighbour distance.

The headline result may not depend on selecting one of these alternatives after inspecting significance.

## 12. Main hypotheses

### H1 — abundance-conditioned spatial packing is not a fixed species property

Within species, `Packing_z` varies among ecological contexts after N and sampling geometry are controlled.

### H2 — dominant-competitor exclusion modifies spatial packing

At Portal, kangaroo-rat exclosure changes mean `Packing_z` and/or the log(N)–Packing_z slope of non-kangaroo-rat rodents relative to controls.

### H3 — habitat modifies density-dependent packing across NEON

Within species, the relationship between N and `Packing_z` differs among broad NLCD habitat groups.

### H4 — population packing has mammal-biological meaning

Where repeated individual captures are available, `Packing_z` covaries with an independently estimated individual movement/recapture spatial scale.

## 13. Claim boundaries

The study may claim:

- context dependence of the spatial distribution of captured individuals within standardized trapping grids;
- treatment effects at Portal where the experimental contrast is valid;
- habitat associations at NEON;
- abundance-conditioned spatial packing.

The study may not automatically claim:

- home-range size from a one-night capture distribution;
- dispersal;
- connectivity;
- territory size;
- latent abundance unless estimated with an explicit capture–recapture model;
- causal habitat effects from NEON;
- causal competition effects outside Portal.

## 14. Novelty boundary

Existing work already includes:

- NEON-wide abundance and capture-probability estimation;
- extensive Portal competition and community-dynamics research;
- a Portal study of *Chaetodipus penicillatus* habitat-patch use in relation to *C. baileyi*.

The intended contribution is therefore **not** “competitors affect habitat use” or “NEON can estimate abundance.”

The new contribution must be the joint demonstration, across multiple species and two public mammal systems, that:

> the spatial packing of individuals within a population can change independently of local captured abundance, and that this abundance-conditioned packing is modified by ecological context, with experimental competitor exclusion providing the causal anchor.

If Portal treatment does not affect abundance-conditioned packing, the paper can still succeed if NEON shows repeatable within-species context dependence and Portal provides a strong negative experimental boundary. The result must remain ecological rather than method-centric.

## 15. Validation strategy for an all-public-data paper

Because all data are already public, the paper will not use “fresh response” language.

Robustness is established with:

- predefined analysis before the main model run;
- leave-site/year-out prediction;
- Portal plot-level treatment replication;
- separate NEON and Portal models;
- cross-dataset agreement where taxa overlap;
- fixed sensitivity analyses;
- complete reporting of null and negative results.

This is a public-data observational/experimental synthesis, not a preregistered prospective study.

## 16. Implementation boundary

Implementation starts only after this design is approved.

First implementation phase:

1. build immutable source manifests for NEON RELEASE-2026 and the current PortalData commit;
2. audit exact fields and data-quality codes;
3. build harmonized session tables without fitting ecological models;
4. quantify how many species × sessions pass N >= 3, 5 and 8;
5. report shared-species overlap and Portal treatment replication;
6. only then freeze the estimability-aware model specification.

No ecological coefficient will be selected or interpreted during the data-ingestion phase.

## 17. Source references

- NEON Small Mammal Box Trapping DP1.10072.001, RELEASE-2026, DOI 10.48443/A83H-TB34.
- NEON Small Mammal Box Trapping User Guide and Quick Start Guide.
- Portal Project public data repository: https://github.com/weecology/PortalData
- Portal living data archive: DOI 10.5281/zenodo.1215988
- Portal data paper: Ernest et al., The Portal Project: a long-term study of a Chihuahuan desert ecosystem.
- Bledsoe et al. 2019, *Ecology*, DOI 10.1002/ecy.2869.
- NEON abundance-index evaluation: *Journal of Mammalogy* 104:292–302, DOI 10.1093/jmammal/gyac096.
