# Mammal ecology validity audit — V1

## Decision

**Oikos V6 is on SUBMISSION HOLD.**

The pre-audit submission snapshot remains preserved at:

`submission/oikos-v6-2026-09-27` → `d7c24907bd6bb3f64905c0052141e537706d1792`

That snapshot is retained for provenance. It is **not recommended for submission** after the validity audit below.

The problem is not the response firewall, one-time authorization, frozen site denominator or reproducibility machinery. Those remain strong. The problem is that the ecological measurement scale and the interpretation attached to it do not support the mammal-ecology claims made in V6.

## 1. Geometry audit: the within-grid result is nearly predetermined

The audit reopened **no biological response**. It used only frozen node IDs, NEON location metadata and the already-frozen world definitions.

Across the original 16 sites plus the independent fresh 11 sites:

- 27 sites;
- 94 distinct canonical adjacency worlds;
- **93/94 worlds (98.94%) connect every pair of traps within the same mammal grid**;
- **26/27 sites** already have complete within-grid adjacency at their *smallest* canonical threshold;
- all 27 sites have at least 95% of same-grid trap pairs adjacent at the smallest threshold.

Observed within-grid maximum trap separations were 126.94–127.52 m. Minimum canonical thresholds ranged from 112.62 to 1569.74 m.

The sole exception was TOOL:

- minimum threshold = 112.62 m;
- maximum within-grid distance = 126.94 m;
- nevertheless 99.394% of same-grid trap pairs were adjacent.

For the original 16-site programme, all reconstructed adjacency fingerprints were compared against the frozen response-blind source artifact and matched exactly at all 16 sites.

### Consequence

The V6 statement that the median within-grid organization component was zero is not an independent ecological discovery. With these thresholds, within-grid trap geometry has almost entirely been collapsed before the biological response is evaluated.

Similarly, the finding that the grid-conditioned null reproduced 66/68 carrier states is largely expected from the declared geometry. Once positive counts by grid are fixed, almost no within-grid arrangement remains visible to the endpoint.

The correct retained statement is narrower:

> At the coarse structural thresholds selected by the site-level LCC ladder, the no-isolated-occurrence endpoint is determined almost entirely by allocation among mammal grids.

That is a property of the measurement design. It should not be presented as evidence that fine-scale small-mammal spatial organization is weak or absent.

## 2. Carrier turnover does not exceed species-pool turnover in the independent fresh panel

The fresh 11-site frozen response retains complete identities for all eligible species, allowing a direct comparison between carrier turnover and ordinary biogeographic turnover.

Across 55 site pairs:

- eligible species-pool Jaccard: median 0, mean 0.07677;
- species-pool Jaccard = 0 for 35/55 pairs;
- carrier Jaccard: median 0, mean 0.03985;
- carrier Jaccard = 0 for 50/55 pairs;
- Spearman association between species-pool Jaccard and carrier Jaccard = 0.492.

A pool-conditioned null was then run with 20,000 deterministic replicates. Within each site, the observed number of carriers was fixed and carrier identities were sampled uniformly from that site's frozen eligible species pool.

- observed mean carrier Jaccard = 0.03985;
- null mean = 0.03102;
- null median = 0.02835;
- null 95% interval = 0.00835–0.06948;
- one-sided p for observed carrier overlap being **lower** than the species-pool-conditioned null = **0.7568**.

### Consequence

The raw result “median carrier-set Jaccard = 0” cannot be used as evidence that the carrier role is unusually taxonomically replaceable. In the independent fresh panel, ordinary site species-pool turnover is sufficient to explain that pattern.

The original 16-site response summary did not retain complete non-carrier species identities. Those biological responses are closed and are not reopened to rescue this claim. Therefore the carrier-specific turnover claim is withdrawn from the manuscript-facing interpretation.

## 3. The spatial scale is generally larger than species-level space-use scales

As a supporting sanity check only, fresh-panel minimum thresholds were compared with equivalent circular diameters derived from the pre-frozen COMBINE `home_range_km2` values.

Among 41 species × site records with nonmissing home-range estimates:

- median threshold / equivalent home-range diameter = **7.61**;
- Q25 = 3.13;
- Q75 = 19.53;
- 97.6% exceeded one equivalent home-range diameter;
- 90.2% exceeded two;
- 53.7% exceeded five.

These external home-range values are coarse species-level traits and are not local movement estimates. They are therefore not a formal biological calibration. They nevertheless reinforce the geometry audit: the existing endpoint is not naturally interpreted as individual-scale movement or within-grid space use.

## 4. V6 discards major mammal-specific information in DP1.10072.001

The NEON Small Mammal Box Trapping product is explicitly a **mark-recapture** product. The official user guide describes unique individual identifiers, repeated sampling bouts, one- versus three-night grid protocols, and standard 10 m trap spacing. NEON also provides `mammalGridSamplingType`, `gridCompletion`, `eventID`, and the `nightuid` join between grid-night and trap-night tables.

V6 instead reduces the response to:

> species × trap = ever captured at least once anywhere in RELEASE-2026.

This removes:

- capture effort;
- sampling-bout identity;
- year;
- seasonal/bout variation;
- individual identity and recapture histories;
- abundance / minimum-known-alive information;
- movement between recapture locations.

For a mammal ecology paper, these are not minor omitted covariates. They are central information carried by the data product.

## 5. Taxonomic uncertainty is material

NEON's Small Mammal Sampling protocol explicitly states that *Peromyscus* species can be difficult to distinguish in the field, especially *P. maniculatus* and *P. leucopus*. It instructs technicians to use `identificationQualifier`, cryptic-species-pair codes or genus-level codes when uncertain.

The data product also provides identification history for later taxonomic corrections.

A species-level state such as carrier/non-carrier can therefore be sensitive to uncertain field identification. Future mammal-ecology analysis must predeclare a taxonomic uncertainty rule rather than treating every species label as equally certain.

## 6. “Grid allocation” is not a habitat mechanism

NEON mammal grids are spatial sampling strata. In the standard design, grids are usually 10 × 10 traps with 10 m spacing and are distributed among the site's NLCD classes, with most of a grid required to lie in its target class. Grid identity can therefore correlate with habitat, but it is not itself an environmental variable.

The current decomposition shows only that the endpoint is largely determined by **which grid receives positive captures**. It does not establish why those grids differ.

A habitat mechanism requires independently measured habitat information, beginning with `nlcdClass` and, where justified, additional vegetation, topographic, moisture or soil covariates.

## 7. What remains valid from the old programme

Retain:

- the full audit trail;
- the frozen 16-site and 11-site negative results as historical results;
- the demonstration that the chosen site-level structural ladder is overwhelmingly coarse relative to within-grid trap geometry;
- ORNL as an example of the mathematical weakest-link property of an all-positive endpoint;
- the general lesson that a response-blind workflow can still freeze an ecologically uninformative estimand.

Do not retain as headline ecological conclusions:

- within-grid organization is biologically negligible;
- carrier identity has unusually high turnover beyond biogeography;
- cross-trophic carrier composition establishes ecological convergence;
- carrier switching is a mammal ecological state change rather than potentially capture/detection structure;
- the existing endpoint measures mammal-scale connectivity or movement.

## 8. Current status

**V6: HOLD — do not submit.**

The next active scientific programme is defined in:

`docs/MAMMAL_ECOLOGY_REDESIGN_V1.md`

The old submission package remains reproducible and archived, but it is no longer the active scientific endpoint.
