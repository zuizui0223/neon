# San Jacinto transition-niche ecology exploration v1

**Status:** exploratory ecological extension, isolated from the frozen MEE temporal-aliasing programme  
**Parent commit:** `265b338521da52d8379f851ca6383dde96e7812c`  
**Branch:** `ecology/san-jacinto-transition-niche-v1`

## Biological question

The parent study showed that six granivorous rodent species can overlap strongly in nightly activity while remaining spatially segregated, with species-specific microhabitat associations. The new question is:

> **How can spatial niche partitioning persist when individuals move among multiple trap locations within the same night?**

The working ecological hypothesis is not that rodents move little. It is that **movement direction is constrained relative to environmental structure**, so substantial movement can occur without erasing spatial niche segregation.

This branch must not retroactively alter, rescue or reclassify any frozen claim in the MEE live-trap-aliasing paper.

## Stage 0 — feasibility inventory only

Before opening any new movement-direction or habitat-transition outcome, inspect only:

1. Figshare file inventory and file names;
2. CSV column names;
3. species roster;
4. row counts, individual counts and counts of valid same-night repeated captures;
5. counts of consecutive within-night transitions;
6. date coverage, including May–July 2016, the period used for published resource-selection analyses;
7. whether environmental data can be joined to trap locations by grid and trap/flag identity.

Stage 0 must **not** calculate or display:

- transition distances;
- transition directions;
- origin-to-destination habitat differences;
- species-specific transition kernels;
- C-score changes under observed or randomized movement.

Those quantities stay unopened until the Stage-1 design is frozen from the feasibility information alone.

## Candidate Stage 1 if trap-level environmental data are joinable

The primary ecological test will ask whether observed within-night moves retain environmental similarity more strongly than expected from their spatial length alone.

For each consecutive same-individual, same-night recapture transition in the published resource-selection season (May–July 2016):

- retain the observed origin trap;
- retain the observed Euclidean displacement length;
- construct the set of within-grid destinations at the same grid displacement length;
- compare the observed destination with random valid destinations from that distance-matched set.

The primary response will be environmental distance between origin and destination in the published vegetation/soil habitat space. The distance-matched null controls for ordinary spatial autocorrelation, grid-edge geometry and the fact that short moves necessarily encounter similar habitat more often.

**Primary biological prediction:** observed transitions cross less environmental distance than distance-matched alternative moves.

Species eligibility, the minimum transition count, the exact habitat variables/PC construction, the number of randomizations and the pooled-vs-species decision rule will be frozen **after Stage 0 counts are known but before any Stage-1 transition outcome is computed**.

## Candidate Stage 2 only if Stage 1 supports habitat retention

A later, separately frozen test may ask whether observed transition directions preserve community-level spatial segregation more strongly than distance-matched rewiring of the same moves.

This is deliberately conditional. A null Stage-1 result stops the route; it does not trigger a search across alternative movement metrics.

## Claim boundary

Even a positive result would show that recorded capture-to-recapture transitions preserve habitat structure beyond a distance-matched expectation. It would **not** by itself prove that competition causes the transition rule, that capture/release has no effect, or that the recorded sequence is a complete natural movement path.

The intended ecological contribution is narrower:

> **Spatial partitioning may persist in a mobile guild because movement is structured relative to habitat boundaries, not because individuals remain spatially static.**
