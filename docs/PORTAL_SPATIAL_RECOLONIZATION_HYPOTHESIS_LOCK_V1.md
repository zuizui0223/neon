# Portal competitor-return spatial legacy — frozen design v1

Date: 2026-10-08. Scientific status: response-blind, effect not opened.

## Existing research boundary

Christensen et al. (2019), Established rodent community delays recovery of dominant competitor following experimental disturbance, already analysed changes in Dipodomys abundance, immigration and plant community following March 2015 Portal treatment switches. Do NOT sell delayed plot-level demographic recolonization as new.

The Portal rodent data have 49 stakes at 6.25 m spacing per plot, but only one nightly survey per plot per monthly census, so they CANNOT replicate San Jacinto's same-night previous-occupant effect.

## New ecological question

Does the spatial distribution of returning dominant competitors recover as quickly as their plot-level numbers? Established subordinate communities may restrict the *breadth of spatial use* of returning Dipodomys even after counts rise.

Before response access, fix the directional prediction: after reopening, count-standardized Dipodomys trap-location dispersion is initially lower in plots already occupied by subordinate rodents than in plots reopened after total rodent removal, and the difference subsequently declines. This is a hypothesis, not a known finding or a causal interference claim.

## Treatment cohorts frozen from source treatment metadata

- KR-return: plots 6, 13, 18 (kangaroo-rat exclosure to control, April 2015).
- Rodent-return: plots 5, 7, 24 (total removal to control, April 2015).
- Long-term controls: plots 4, 11, 14, 17.
- Source period: 2013–2018; post-switch starts April 2015.

Other plots excluded from primary analysis.

## Support gate before spatial positions are opened

Source files pinned at weecology/PortalData commit 171f9441c02c5a95e7dd1a6fafe3e4b063c36c14. Verify raw schema, treatment, trapping effort.

Include normal-census records with period >= 1 and sampled=1, qcflag=1, effort>=47. Count identifiable Dipodomys codes DM, DO, DS only with a valid 7×7 stake. Use eight *nonoverlapping* six-month windows from April 2015. A supported plot-window has >=10 identified captures.

Proceed only if EACH treatment group has >=2 independent plots, each with >=2 supported post-switch windows. If not, stop the frozen spatial endpoint. No threshold changes after capture-count support is opened.

## Only if support passes: primary spatial endpoint

For each supported plot-window, draw 10 capture locations without replacement from the observed eligible captures, seeded and repeated for uncertainty, and compute mean pairwise distance of their 7×7 locations. Keep plot as the experimental replication unit. Compare early versus later post-switch MPD between KR-return, rodent-return and controls, conditioning on time/window and qualifying support. Use plot-level uncertainty rather than individual-capture pseudoreplication. Report failure to estimate honestly.

This does not prove natural movement, interactions, scent responses or stable home ranges. It estimates **capture-position spatial dispersion**, conditional on capture number. Habitat, fences/gates, treatment assignments and the low number of switched plots remain potential explanations/confounders. No extrapolation to San Jacinto check-level effects.

## Sources

PortalData Rodents/README.md, SiteandMethods/Methods.md, Rodents/Portal_rodent_trapping.csv, SiteandMethods/Portal_plots.csv; Christensen et al. 2019 (PMC6939914).
