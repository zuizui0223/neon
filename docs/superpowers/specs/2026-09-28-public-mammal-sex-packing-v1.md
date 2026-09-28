# Public small-mammal sex-specific spatial packing — design v1

Date: 2026-09-28

Status: design frozen before sex-specific outcome extraction.

## 1. Motivation

The preceding public-data Phase-2 programme established that the abundance-conditioned population Packing_z metric is mechanically well behaved, but its prespecified competition and habitat hypotheses did not produce replicated ecological support.

The next study asks a different mammal-biological question, motivated independently by long-standing heteromyid natural history:

> **Within the same population session, are male heteromyid rodents spatially more dispersed than females after the number of captured males, the number of captured females, and trap geometry are each conditioned out?**

Classical heteromyid work reports sex differences in home-range size and more frequent excursions by males, especially during reproductive periods. This study does not estimate home ranges from one-night captures. It tests whether the **population configuration of simultaneously captured males versus females** differs within the same trapping grid.

## 2. Public datasets

### Portal Project

Pinned source:
- repository: `weecology/PortalData`
- commit: `72d7ff8568052763bf6899dc462e285684cf20f6`

Use:
- `Rodents/Portal_rodent.csv`
- `Rodents/Portal_rodent_trapping.csv`
- `Rodents/Portal_rodent_species.csv`

Portal provides sex, unique long-term individual `id`, plot, stake, period, PIT-tag reliability, effort and QC.

Primary Portal period:
- all positive census periods available at the pinned commit;
- `sampled = 1`;
- `effort = 49`;
- `qcflag = 1`;
- valid 7 × 7 stakes only.

Because the comparison is male versus female **within the same plot-period**, treatment, weather and broad habitat are shared by the two sex-specific responses and are not primary confounders.

### NSF NEON

Product:
- DP1.10072.001
- RELEASE-2026
- DOI 10.48443/A83H-TB34

Primary NEON sessions:
- diversity grid;
- one-night event;
- acceptable gridCompletion;
- actual active-trap geometry;
- valid unique tagID;
- target species;
- unambiguous species identification under the frozen taxonomy rules.

The product contains `sex`, `lifeStage`, `pregnancyStatus`, individual identifiers and capture locations. This study uses sex only in the primary analysis.

## 3. Taxonomic scope

Primary taxonomic family:

**Heteromyidae**

Operational genera:
- `Chaetodipus`
- `Dipodomys`
- `Perognathus`
- `Microdipodops` if present and target-sampled.

Species-level ambiguous/genus-only records are excluded from the primary analysis.

The family is frozen before estimability counts are inspected.

Reason:
- heteromyids have a strong prior literature on sex-specific space use and excursions;
- both Portal and NEON contain multiple heteromyid species;
- the restriction avoids the Peromyscus cryptic-species problem that complicated prior work.

## 4. Session and individual rules

Portal session:
`species × plot × positive census period`.

NEON session:
`species × site × diversity-grid plotID × eventID`.

Each resolved individual contributes at most one spatial point per session.

If duplicate same-individual records occur within a session, retain the deterministic first record under the already-defined source-specific ordering rule.

Only known male and female records enter sex-specific analysis.

Unknown/ambiguous sex records are counted for QC but excluded from male/female Packing_z.

## 5. Primary response

For each eligible session, compute the existing Phase-1 abundance-conditioned packing score separately by sex.

### Male response

`Packing_z_male`

calculated from male capture locations, conditioning on:
- exact active trap geometry;
- exact number of unique captured males, `N_male`.

### Female response

`Packing_z_female`

calculated from female capture locations, conditioning on:
- the same exact active trap geometry;
- exact number of unique captured females, `N_female`.

### Paired sex contrast

`Delta_sex_packing = Packing_z_male - Packing_z_female`.

Interpretation:
- positive: males are more dispersed relative to their sex-specific conditioned expectation than females;
- zero: no sex difference in conditioned population packing;
- negative: males are more clustered than females.

The response compares sexes within the same population session. It is not a home-range estimate.

## 6. Primary eligibility

A session is primary-eligible when:
- `N_male >= 3`;
- `N_female >= 3`;
- both sex-specific nulls have nonzero variance;
- both sex-specific Packing_z values are estimable;
- all source-specific primary effort/taxonomy/geometry rules pass.

Sensitivity thresholds:
- at least 2 per sex;
- at least 5 per sex.

The N>=3 primary threshold is chosen before counts are inspected because requiring N>=5 for each sex would imply at least 10 individuals per session and may unnecessarily discard paired information. N>=5/sex remains the stricter sensitivity.

## 7. Phase A — estimability only

Before any sex-effect model is fit, report separately for Portal and NEON:

- total heteromyid sessions;
- sessions with known-sex individuals;
- primary paired sessions (>=3 males and >=3 females);
- sensitivity paired sessions (>=2/sex and >=5/sex);
- paired sessions per species;
- independent Portal plots per species;
- independent NEON sites per species;
- years/periods represented;
- fraction of captured individuals with known sex;
- PIT-reliable fraction in Portal;
- species shared between Portal and NEON that meet the same paired-session gate.

No `Delta_sex_packing` mean, coefficient, sign, confidence interval or p-value is inspected during this phase.

## 8. Advance gate

The study advances to effect modeling only if:

### Portal family gate
At least:
- 3 heteromyid species;
- each with >=10 primary paired sessions;
- each represented on >=2 plots.

### NEON family gate
At least:
- 3 heteromyid species;
- each with >=10 primary paired sessions;
- each represented at >=2 sites.

### Cross-dataset gate
At least one species has:
- >=10 primary paired sessions in Portal;
- >=10 primary paired sessions in NEON.

If the family gate fails in either dataset, no family-wide cross-dataset claim is made.

If the cross-dataset gate fails, the two datasets may still be analyzed independently but cannot be presented as same-species replication.

The gate is frozen before effects are inspected.

## 9. Planned effect model if gate passes

This section is prospective and is not implemented before the estimability gate.

### Within-dataset family model

Primary quantity:
overall mean `Delta_sex_packing`.

Model skeleton:
`Delta_sex_packing ~ 1 + season + (1 | species) + source-specific repeated-unit effects`.

Portal repeated-unit effects:
- plot;
- census year/period structure.

NEON repeated-unit effects:
- site;
- year.

Species-specific sex effects are always reported.

### Directional biological hypothesis

Primary directional hypothesis:

> **Male heteromyids have higher conditioned spatial packing than females (`Delta_sex_packing > 0`).**

This direction is justified by prior heteromyid literature reporting sex differences in home-range size and more frequent long-distance excursions by males.

A two-sided confidence interval is still reported.

## 10. Independent movement validation

NEON pathogen-grid recaptures provide a prespecified biological validation.

For eligible heteromyid individuals with repeated locations within an event:
- calculate successive displacement separately for males and females;
- compare sex-specific displacement distributions after species/site control.

The validation question is whether any population-level sex difference in Packing_z is directionally concordant with independently observed sex differences in recapture displacement.

No movement result can redefine the primary population-packing endpoint.

## 11. Mechanical null validation

Before ecological inference, simulate male and female random placements over representative Portal and NEON geometries while varying:
- N_male;
- N_female;
- sex ratio.

Required property:
expected `Delta_sex_packing` remains approximately zero and has no strong monotonic relationship with sex ratio under random placement.

Frozen warning threshold:
absolute Spearman rho between simulated sex ratio and Delta_sex_packing > 0.2.

If this fails, the ecological analysis stops.

## 12. Sensitivity analyses

Prespecified:
- >=2 per sex;
- >=5 per sex;
- Portal PIT-reliable subset;
- Portal leave-one-species-out;
- Portal leave-one-plot-out;
- NEON leave-one-species-out;
- NEON leave-one-site-out;
- exclude sessions with >20% unknown sex;
- sex-specific nearest-neighbour and radius-of-gyration alternatives;
- NEON recapture displacement validation.

No sensitivity replaces the primary N>=3 paired result.

## 13. Claim boundaries

Allowed:
- sex-specific difference in the spatial arrangement of captured individuals within the same grid/session;
- replication across public trapping systems if the frozen gate is met;
- heteromyid family-level inference only when >=3 species per source pass the gate.

Not allowed:
- male/female home-range size from one-night Packing_z;
- sex-biased dispersal;
- territory size;
- mating movement without recapture validation;
- causal explanation by reproduction unless explicitly tested later.

## 14. Novelty boundary

Existing literature already shows:
- sex differences in heteromyid home-range/movement;
- sex-specific individual home-range effects in other small mammals;
- NEON Peromyscus space-use variation.

The intended contribution is narrower:

> **a replicated public-data test of sex-specific population spatial packing within the same trapping session, explicitly standardized for sex-specific sample size and trap geometry, across multiple heteromyid species and two independent long-term trapping systems.**

If the effect is absent, the null result is retained; species or thresholds are not searched post hoc for a positive pattern.

## 15. References motivating the directional hypothesis

- Maza, B.G., French, N.R. & Aschwanden, A.P. 1973. Home Range Dynamics in a Population of Heteromyid Rodents. *Journal of Mammalogy* 54:405–425. DOI 10.2307/1379127.
- Ernest, S.K.M. et al. Portal Project public rodent data and methods, DOI 10.5281/zenodo.1215988.
- NSF NEON Small Mammal Box Trapping DP1.10072.001, RELEASE-2026.
