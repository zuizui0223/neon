# Literature boundary and downstream-analysis gap — v1

Date: 2026-09-29

## What is already standard

Spatial capture–recapture (SCR/SECR) explicitly distinguishes detector processes.

Efford & Boulanger (2019, Methods in Ecology and Evolution, DOI 10.1111/2041-210X.13239) describe trap data as binary animal × occasion records: an animal detained by a trap may be detected only once on an occasion. Efford, Borchers & Byrom (2009) likewise formulate a multi-catch-trap occasion as one trap index per individual, whereas proximity detectors may retain detections at multiple detectors in one occasion.

Therefore, when a repeated-check live-trapping protocol allows a marked animal to be caught at different traps within one night but the ecological analysis defines the night as one occasion, the analyst must either:
- split the night into finer occasions; or
- collapse multiple within-night locations into one spatial state.

That is an observation-process choice, not a biologically neutral file-format choice.

## Existing small-mammal spatial practice

Capture locations from live-trapping grids are routinely used as spatial observations for home-range analyses. For example, a recent large Peromyscus analysis used live-trapping locations to calculate kernel-utilization-distribution home-range areas and imposed a minimum number of adult captures to avoid unstable home-range estimates.

This supports home-range estimation as a realistic downstream target for the current diagnostic.

## Adjacent literature that does not close the gap

Existing interval-trapping work has quantified:
- nocturnal activity timing;
- recapture latency;
- disturbance or altered availability caused by trap checks;
- the effect of detector configuration and spatial recaptures on SCR precision.

Multiple-capture studies have also used capture data to study social associations.

These strands show that within-night capture process matters. They do not, however, directly answer the representative-state question tested here:

> If the same marked individual is observed at multiple trap locations within one night, how sensitive is a downstream spatial statistic to the choice of the single nightly location retained?

## Current empirical evidence

The prospectively held-out validation showed that one-trap-spacing-or-greater first-to-last shifts occurred on:
- 72.6% of 485 repeat-capture individual-nights for Peromyscus maniculatus;
- 69.2% of 107 repeat-capture individual-nights for Peromyscus eremicus.

Those proportions are conditional on repeat-capture nights.

An all-night denominator audit showed that repeat-capture nights represented:
- 39.8% of all valid P. maniculatus individual-nights;
- 35.5% of all valid P. eremicus individual-nights.

Even with all valid individual-nights in the denominator, directly observed >=1-spacing shifts occurred on at least:
- 28.9% of P. maniculatus nights;
- 24.6% of P. eremicus nights.

These all-night values are observational lower bounds because a single-capture night cannot reveal a first-to-last positional change.

## MEE fit boundary

Current Methods in Ecology and Evolution guidance states that:
- the new method or methodological approach, not the biological case-study result, must be central;
- computational methods normally should be evaluated with simulations or benchmark datasets;
- broad applicability across taxa/systems must be demonstrated.

Accordingly, this paper should not be framed as "two Peromyscus species move between traps within a night."

The method-level contribution is:
1. diagnose within-occasion positional span relative to a user-defined material spatial scale;
2. quantify uncertainty in the exceedance proportion;
3. propagate observed positional span into deterministic sensitivity bounds for movement and MPD-like statistics;
4. demonstrate a real downstream consequence in a familiar spatial analysis;
5. provide generic code independent of the San Jacinto schema.

## Critical next test

The next analysis is frozen separately before execution.

It asks whether FIRST-versus-LAST nightly collapse materially changes individual home-range estimates among animals with enough nights and spatial support for a non-degenerate polygon.

If downstream home-range estimates are insensitive despite common raw positional aliasing, the MEE claim becomes weaker and should be narrowed.

If downstream home-range estimates frequently change materially, the paper gains the missing bridge from observation-process diagnostic to ecological inference.

## References to retain in manuscript build

- Efford MG, Boulanger J. 2019. Fast evaluation of study designs for spatially explicit capture–recapture. Methods in Ecology and Evolution 10:1529–1535. DOI 10.1111/2041-210X.13239.
- Efford MG, Borchers DL, Byrom AE. 2009. Density estimation by spatially explicit capture–recapture: likelihood-based methods.
- Drickamer LC, Springer LM. 1998. Methodological aspects of the interval trapping method with comments on nocturnal activity patterns in house mice living in outdoor enclosures. Behavioural Processes 43:171–181. DOI 10.1016/S0376-6357(98)00012-6.
- Recent Peromyscus home-range network analysis using capture locations and minimum-location filtering: Oecologia (2025), "Uncovering multiple influences on space use by deer mice using large ecological networks."
