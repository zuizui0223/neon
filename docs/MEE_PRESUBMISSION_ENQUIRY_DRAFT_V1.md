# MEE pre-submission enquiry — draft v1

**Proposed article type:** Research Article

**Working title:** Diagnosing temporal positional aliasing in repeated-location ecological data

Dear Editors,

We would like to ask whether a manuscript introducing a diagnostic for **temporal positional aliasing** in repeated-location ecological data would be suitable for *Methods in Ecology and Evolution*.

Many ecological studies define an occasion (for example a night or survey visit) at a coarser temporal scale than the observations collected within it. When the same marked individual is observed at multiple locations within one occasion, subsequent analyses often require either splitting the occasion or collapsing those locations to a single spatial state. We treat that reduction as an observation-process assumption and provide a generic diagnostic for asking when it is spatially consequential.

The proposed paper has three methodological components.

1. **Scale-aware diagnostic.** For repeated observations of the same individual within an occasion, we quantify first-to-last positional span relative to a user-defined material spatial scale, report uncertainty in the fraction exceeding that scale, and distinguish repeat-observation-conditioned estimates from conservative all-occasion observed lower bounds.

2. **Sensitivity bounds.** Simple metric-geometry inequalities convert within-occasion positional span into deterministic upper bounds on the sensitivity of inter-occasion movement and population mean-pairwise-distance statistics to the representative-location rule. We present these as practical sensitivity bounds rather than mathematical novelty.

3. **Simulation and prospective validation.** A 72-cell simulation benchmark shows that the repeat-conditioned proportion is essentially unbiased when repeat observation is non-informative, but can be biased when repeat observation depends on positional span; the all-occasion directly observed fraction remains a lower bound under every simulated mechanism. We then prospectively validate the diagnostic in two held-out Cricetidae species from a public repeated-check live-trapping dataset.

In the held-out validation, a first-to-last shift of at least one 6.25-m trap spacing occurred on 72.6% of 485 repeat-observed nights for *Peromyscus maniculatus* (95% Wilson CI 68.4–76.4%) and 69.2% of 107 nights for *P. eremicus* (59.9–77.1%). The pre-specified spatial-replication criterion was satisfied in all 7 eligible grids for *P. maniculatus* and all 3 for *P. eremicus*. With all valid individual-nights as the denominator, directly observed material shifts provide conservative lower bounds of 28.9% and 24.6%, respectively.

The method is implemented as generic open-source code requiring only individual identifier, occasion identifier, within-occasion time, coordinates and a study-defined material spatial scale. It is intended for repeated-location ecological data more broadly, not only live trapping.

We have also tested a prospectively specified downstream home-range analysis, but its effect stage was not estimable under the frozen high-information support thresholds; we therefore do not use it to support the central claim.

Could you advise whether this combination of a general observation-process diagnostic, simulation benchmark, deterministic sensitivity framework and prospectively held-out empirical validation would be considered within scope for a Research Article?

Thank you for your consideration.
