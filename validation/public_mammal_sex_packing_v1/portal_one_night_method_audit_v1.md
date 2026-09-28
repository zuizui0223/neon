# Portal one-night support audit for sex-specific packing

Date: 2026-09-29

Source:
- weecology/PortalData
- pinned commit: 72d7ff8568052763bf6899dc462e285684cf20f6
- SiteandMethods/Methods.md

## Ruling

The Portal Phase-3 unit `species × plot × positive census period` is compatible with a one-trap-location-per-retained-individual support model.

The Portal methods state that monthly rodent surveys are conducted around the new moon. A survey spans two nights across the experiment, but **each plot is trapped for one night only**. Treatments are divided across the two survey nights. When a plot is surveyed, gates are closed, one Sherman live-trap is placed at each of the 49 permanent stakes, traps are collected the following morning, and captured individuals are processed.

Therefore, within one plot-period:
- the spatial observation is a one-night trap-grid configuration;
- a trap stake cannot legitimately contribute two simultaneously captured individuals under the normal protocol;
- duplicate retained trap locations are inconsistent with the exact without-replacement trap-support null and are appropriately excluded fail-closed in support v2.

## Consequence for wording

For Portal, the allowed description is a **one-night plot-level trapping configuration** within the monthly survey.

For NEON primary diversity grids, the analysis also uses one-night events.

Thus the cross-source endpoint can be described as a one-night captured population spatial configuration, not as individual home range or longer-term movement.

This audit changes no data, threshold, effect, confidence interval, or Phase-3 decision.
