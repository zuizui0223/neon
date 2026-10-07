# Trap-mediated niche: current ecological synthesis v1

Date: 2026-10-07

## What survives the first ecological tests

### 1. Strong same-trap temporal memory is real

All six focal species show excess same-species succession at a detector from one check to the next. Much of this is exact-individual recapture, but different-known-individual excess also remains for some species.

### 2. A directional KR -> LAPM sequence deficit is robust under the discovery null

Pooling DKR and SKR, KR -> LAPM same-trap transitions occur at 0.719 of the trap × bout × check-pair date-shuffle expectation, whereas LAPM -> KR is approximately null (1.022). Grid × bout block bootstrap gives:

- KR -> LAPM O/E 95%: 0.533–0.928
- LAPM -> KR O/E 95%: 0.869–1.195
- directional O/E ratio 95%: 0.523–0.888

The deficit decays spatially: O/E 0.719 at the same trap, 0.911 at Manhattan distance 1, and 1.029 at distance 2.

### 3. The effect is not a generic body-size dominance rule after stronger fixed effects

A stricter model with trap fixed effects and grid × date × transition fixed effects does not support a pooled kangaroo-rat suppression of all smaller species (OR 1.21, 95% CI 0.97–1.52). DKR -> LAPM remains below one (OR 0.55) but is imprecise; DKR -> PEER is lower (OR 0.52, 95% CI 0.27–0.99), whereas DKR -> CHFA and DKR -> PEMA are positive.

Therefore the data do **not** support the simple statement “larger kangaroo rats suppress all smaller rodents at the next check.”

### 4. Recapture history changes temporal activity profiles strongly

Within-night repeat fractions are highly species-specific:
- CHFA 75.6%
- DKR 73.3%
- SKR 72.5%
- LAPM 44.3%
- PEMA 39.9%
- PEER 35.5%

Removing later within-night recaptures shifts the first-capture temporal profile sharply toward EARLY, especially for CHFA, DKR and SKR.

Despite lower raw Czekanowski overlap after this removal, the preliminary RA3-style exact enumeration makes standardized temporal aggregation *more* frequent rather than revealing temporal segregation. This counter-intuitive result is being checked with EcoSimR itself before promotion.

## Current ecological interpretation

The strongest defensible gap is no longer “live trapping biases niche estimates.”

It is:

> **Coarse nightly niche overlap can coexist with directional, species-specific microtemporal interaction history at the scale of individual trap checks.**

This history may combine real local interactions, residual odour, release-site effects, bait/trap state and short-term space use. The exact-trap spatial decay argues against interpreting it as a broad exclusion zone.

## What would be genuinely strong

If EcoSimR confirms that coarse temporal-overlap inference remains or strengthens after removing repeat captures, while the KR -> LAPM sequence asymmetry remains highly local, the ecological story becomes:

> **Species can appear to share the same nightly activity niche while still avoiding one another asymmetrically at the scale of hours and metres.**

That is much more ecological than the original temporal-aliasing methods question, but remains exploratory until tested in independent data or an experiment.
