# Public Small-Mammal Spatial Packing — Phase 2 Amended Design

Date: 2026-09-27

Status: amended design required by `validation/public_mammal_space_use_v1/estimability_gate_v1.json`.

**No ecological model has been fit before this amendment.**

## 1. Why Phase 1 changed the design

The Phase-1 estimability audit produced three decisive constraints.

### Portal

Only one species satisfies the frozen primary replication gate in both experimental contexts:

**Chaetodipus penicillatus**

N >= 5 sessions:
- control: 194 sessions across 10 plots;
- kangaroo-rat exclosure: 196 sessions across 8 plots.

The planned multispecies Portal treatment hierarchy is therefore not estimable and is removed.

### NEON

Six species have a frozen habitat-identifiability path, but the structure differs among them.

Within-site habitat contrast:
- `Chaetodipus hispidus`;
- `Myodes rutilus`;
- `Perognathus parvus`;
- `Peromyscus boylii`.

Cross-site replicated habitat structure:
- `Myodes rutilus`;
- `Peromyscus maniculatus`;
- `Sigmodon hispidus`.

No species satisfies the original source-specific primary gate in **both** Portal and NEON.

Therefore the paper will not claim same-species replication across the two datasets.

## 2. Novelty correction after current literature review

Two relevant published results constrain the claim.

### Bledsoe & Ernest 2019 — Portal

Bledsoe & Ernest used Portal data to show that *C. penicillatus* changed treatment/patch use as *C. baileyi* established. They analyzed treatment-level abundance, residency, movement between treatments and arrival of new individuals.

The present study must therefore **not** claim novelty for showing that competition changes which Portal plots or treatments *C. penicillatus* uses.

The new Portal question is finer scale:

> At the same captured population size, does exclusion of dominant kangaroo rats alter how *C. penicillatus* individuals are spatially arranged **within** a 50 × 50 m plot?

This is a within-patch population-spacing question rather than patch selection.

### O'Fallon, Pinter-Wollman & Mabry 2025 — NEON

O'Fallon et al. analyzed individual Peromyscus space use across NEON. They estimated 50% KDE home-range area from individuals with at least five adult captures at at least three unique locations and tested sex, body condition, habitat, latitude and mean MNKA. They already showed habitat- and density-dependent variation in individual home-range area.

The present study therefore must **not** claim novelty for “NEON shows density and habitat affect small-mammal space use.”

Our response is biologically and statistically different:

- one-night population snapshot rather than multi-capture individual home range;
- unique individuals within a grid/session rather than repeated locations of one animal;
- mean pairwise distance standardized against the exact N and active trap geometry;
- a population-level spacing state after the mechanical effect of N is conditioned out.

Peromyscus is not a headline NEON taxon in the amended design.

## 3. Central biological question

> **Can ecological context reorganize the spatial packing of a small-mammal population within a habitat patch independently of the number of individuals present?**

The primary ecological interpretation concerns **population spatial packing**, not home-range size, dispersal or connectivity.

A population is “more clustered” when captured individuals lie closer together than expected for N individuals placed among the exact available trapping locations.

A population is “more dispersed” when their locations are farther apart than the same conditioned expectation.

## 4. Frozen response

The Phase-1 response remains unchanged:

`Packing_z = (MPD_obs - mean(MPD_null)) / sd(MPD_null)`

where the null preserves:
- exact available trap geometry;
- exact N unique captured individuals;
- sampling session.

Negative values = more concentrated than the conditioned random expectation.

Positive values = more dispersed.

This metric is not changed after the Phase-1 estimability audit.

## 5. Portal — primary causal analysis

### 5.1 Species and time window

Primary species:

**Chaetodipus penicillatus**

Primary period:

**August 2009 through March 2015**

Use:
- control plots;
- kangaroo-rat exclosures;
- positive normal census periods;
- sampled = 1;
- effort = 49;
- recommended QC;
- valid 7 × 7 stake positions;
- N >= 5 unique individuals.

All-rodent removals are excluded.

### 5.2 Experimental unit

Observation:

`plot × census period`

Independent treatment replication is at the **plot** level:
- 10 controls;
- 8 kangaroo-rat exclosures.

Repeated monthly observations are not treated as independent treatment replicates.

### 5.3 Primary model

Gaussian crossed mixed model:

`Packing_z ~ treatment * z_logN`

with:
- plot random intercept;
- census-period random intercept.

Definitions:
- control is the treatment reference;
- `z_logN` is log(N) standardized over the retained primary Portal sessions;
- census period is the monthly Portal period identifier.

The period random intercept controls environmental conditions shared by plots during the same census.

### 5.4 Primary Portal parameters

**P1 — treatment main effect**

Difference in expected `Packing_z` between kangaroo-rat exclosures and controls at mean log(N).

**P2 — treatment × log(N)**

Difference between treatments in the abundance–packing relationship.

No directional sign is declared.

### 5.5 Portal robustness

Mandatory:
1. N >= 3;
2. N >= 8;
3. long-term treatment plots only;
4. PIT-reliable-identity sensitivity;
5. leave-one-plot-out;
6. leave-one-census-period-out;
7. alternative null-standardized radius of gyration;
8. alternative null-standardized nearest-neighbour distance.

The primary conclusion must not reverse solely because one plot or one census period is removed.

## 6. NEON — primary ecological generalization

NEON is not used to repeat the Portal treatment effect.

Its role is to ask whether abundance-conditioned population packing responds to habitat context in an independent mammal system using standardized public monitoring.

### 6.1 Primary NEON species

**Myodes rutilus**

Reason:
- it has the strongest replicated within-site habitat design;
- the same forest-versus-shrub contrast occurs at two sites;
- it avoids the Peromyscus home-range literature overlap and the primary cryptic-complex concern.

Frozen N >= 5 sessions:

BONA:
- forest: 15;
- shrub/scrub: 6.

DEJU:
- forest: 13;
- shrub/scrub: 5.

Only BONA and DEJU enter the primary Myodes habitat model.

HEAL shrub-only sessions do not identify the within-site habitat contrast and are excluded from the primary model.

### 6.2 Primary NEON model

Gaussian model:

`Packing_z ~ habitat + z_logN + site`

where:
- forest is the reference habitat;
- shrub/scrub is the comparison;
- site is a fixed blocking factor (BONA versus DEJU);
- `z_logN` is standardized within the retained *M. rutilus* primary sessions.

The primary ecological parameter is the shrub/scrub versus forest difference after N and site are controlled.

A `habitat × site` interaction is **not** included in the primary model because shrub sample size is limited. Site-specific habitat effects are reported descriptively and in sensitivity analysis.

### 6.3 NEON generalization set

The following within-site contrasts are secondary planned generalizations:

- *Chaetodipus hispidus*, OAES:
  - grassland/herbaceous = 9;
  - shrub/scrub = 6.

- *Perognathus parvus*, ONAQ:
  - forest = 13;
  - shrub/scrub = 25.

- *Peromyscus boylii*, SJER:
  - forest = 9;
  - grassland/herbaceous = 19.

Each is fit separately with:

`Packing_z ~ habitat + z_logN`

because each contrast occurs at one site.

These analyses may support generality but are not pooled as if “habitat” has one universal directional effect across taxa.

### 6.4 Cross-site observational secondary analyses

Secondary only:
- *Sigmodon hispidus*;
- *Peromyscus maniculatus*;
- *Myodes rutilus* additional site structure.

Cross-site habitat comparisons cannot be interpreted as within-site habitat effects.

They use site blocking/random effects and are labelled observational.

## 7. Peromyscus boundary

### 7.1 Novelty boundary

Peromyscus is excluded from the headline NEON result because O'Fallon et al. 2025 already analyzed NEON Peromyscus individual home-range responses to density and habitat.

### 7.2 Taxonomic boundary

Species-level *P. maniculatus* and *P. leucopus* results are not primary.

If they are shown in secondary analyses:
- current released identifications must be used;
- uncertain `identificationQualifier` rows remain excluded;
- identification history must be applied;
- the mandatory cryptic-complex sensitivity aggregates/removes the *maniculatus–leucopus* complex.

No Peromyscus secondary result can rescue a failed Portal or *Myodes rutilus* primary result.

## 8. Cross-dataset synthesis

The same-species Portal–NEON synthesis is deleted.

The two datasets address the same **process-level** question using the same Packing_z definition:

- Portal: does experimental competitor exclusion reorganize population packing?
- NEON: does habitat context reorganize population packing within the same species and site system?

Synthesis is qualitative/process-level unless a later prespecified meta-analytic effect scale is justified.

The paper does not claim that *C. penicillatus* and *M. rutilus* have the same ecological response.

## 9. Individual-movement validation

NEON pathogen-grid recapture data remain a prespecified secondary validation.

Phase 1 found 30 species with an estimable recapture pathway.

The validation asks:

> Do population sessions with different Packing_z also differ in independently observed individual recapture displacement?

This is a validation of biological meaning, not a replacement primary endpoint.

The exact recapture eligibility and displacement statistic must be implemented and tested before those outcomes are inspected.

## 10. Hypotheses

### H1 — experimental competition changes within-patch population packing

In *C. penicillatus*, kangaroo-rat exclosure changes mean Packing_z and/or its relationship with N relative to control plots.

Evidence source: Portal experiment.

### H2 — habitat changes abundance-conditioned population packing

In *Myodes rutilus*, Packing_z differs between forest and shrub/scrub after N and site are controlled.

Evidence source: within-site replicated NEON habitat design at BONA and DEJU.

### H3 — context dependence generalizes beyond one species

At least one of the three prespecified additional within-site NEON species contrasts shows a habitat-associated packing difference in the same population-level metric.

This is secondary/generalization evidence and is reported with full multiplicity transparency.

### H4 — Packing_z reflects mammal spatial behavior

Where recapture data are estimable, population Packing_z covaries with individual recapture displacement.

This is secondary validation.

## 11. What would make the paper biologically interesting

The manuscript should advance only if the result concerns mammal ecology, not merely the new metric.

Strong positive outcome:
- experimental competitor exclusion changes within-plot packing at matched N; and
- an independent NEON habitat contrast demonstrates that population packing is context dependent outside Portal.

Still publishable boundary result:
- strong experimental Portal effect but little NEON habitat generalization;
- or a clear null Portal treatment effect that constrains the mechanism already suggested by prior Portal patch-use studies, alongside strong replicated Myodes habitat structure.

Weak/non-paper outcome:
- Packing_z varies only with N;
- all effects vanish under plot/session influence checks;
- results depend on Peromyscus;
- the main conclusion is only that the statistic can be computed.

## 12. Statistical reporting

For every primary coefficient report:
- estimate;
- standard error;
- 95% confidence interval;
- standardized effect where interpretable;
- sample sessions;
- independent plots/sites;
- marginal predictions over observed N range.

P-values may be reported but do not determine whether null results are shown.

No model selection over a large candidate set is used for the primary models.

## 13. Multiplicity boundary

Primary family:
- Portal P1 treatment effect;
- Portal P2 treatment × N;
- NEON Myodes habitat effect.

These are all reported regardless of significance.

Secondary species-specific habitat contrasts are clearly separated from the primary family.

No secondary result is promoted because it is the smallest p-value.

## 14. Relationship to existing literature

The manuscript must explicitly distinguish:

**Bledsoe & Ernest 2019**
- patch/treatment use;
- abundance;
- residency;
- between-treatment movement;
- response to *C. baileyi* establishment.

This study:
- within-plot locations of contemporaneously captured individuals;
- N-conditioned population spatial packing;
- direct kangaroo-rat treatment comparison in the clean 2009–2015 window.

**O'Fallon et al. 2025**
- individual Peromyscus home ranges;
- repeated captures per individual;
- KDE area;
- sex, body condition, density, habitat and latitude.

This study:
- population snapshot;
- one location per unique individual per session;
- exact N- and grid-conditioned spacing;
- non-Peromyscus headline NEON taxon.

## 15. Implementation authorization

This amended design supersedes the Phase-1 model specification sections but does not alter:
- source manifests;
- session construction;
- Packing_z;
- N eligibility flags;
- frozen Phase-1 estimability report.

Phase-2 ecological model implementation remains blocked until this amended design is reviewed and approved.

After approval, a separate Phase-2 implementation plan must be written before model code is created.

## References added by amendment

- Bledsoe, E. K. & Ernest, S. K. M. 2019. Temporal changes in species composition affect a ubiquitous species' use of habitat patches. *Ecology* 100:e02869. DOI 10.1002/ecy.2869.
- O'Fallon, S., Pinter-Wollman, N. & Mabry, K. E. 2025. Uncovering multiple influences on space use by deer mice using large ecological networks. *Oecologia* 207:98. DOI 10.1007/s00442-025-05731-2.
