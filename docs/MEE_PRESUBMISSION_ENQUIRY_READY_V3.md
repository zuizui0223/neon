# MEE pre-submission enquiry — send-ready draft v3

**Proposed article type:** Research Article  
**Working title:** *Diagnosing temporal positional aliasing in repeated-location ecological data*

Dear Editors,

We would like to ask whether a manuscript introducing a lightweight diagnostic for **temporal positional aliasing** in repeated-location ecological data would be suitable for *Methods in Ecology and Evolution*.

Ecological observations are often collected more frequently than the occasions used in analysis. When the same marked individual is observed at multiple locations within one occasion, analysts may split the occasion, retain a continuous-time process, or collapse the records to one representative spatial state. We focus on the decision point before that choice: are the alternative observed positions materially different at the scale of the planned analysis?

Our proposed Research Article contributes:

1. a generic diagnostic of first-to-last within-occasion positional span relative to a user-defined material spatial scale;
2. deterministic bounds translating observed positional span into maximum sensitivity of inter-occasion movement and population mean-pairwise-distance statistics;
3. a 72-cell simulation benchmark separating the generating material-shift probability, the realized finite-dataset fraction and the repeat-observation-conditioned fraction;
4. a prospectively locked taxon-level holdout validation in two Cricetidae species from the same public trapping programme; these species were selected using effect-blind support counts and their first-to-last outcomes were unopened when the validation rule was frozen.

In the corrected simulation benchmark, non-informative repeat observation produced mean absolute bias of 0.00176 relative to the analytic generating probability and mean Wilson coverage of 95.2%. Cell-level coverage ranged from 86.0% to 99.5%, with the lowest value in an ultra-rare-event cell. Informative repeat observation produced directional bias (+0.0507 when larger spans increased repeat-observation probability and -0.0799 when they reduced it). The all-occasion directly observed fraction never exceeded the realized all-occasion material-shift fraction in any simulated replicate.

In the held-out validation, first-to-last shifts of at least one 6.25-m trap spacing occurred on 72.6% of 485 repeat-capture nights for *Peromyscus maniculatus* (95% Wilson CI 68.4–76.4%) and 69.2% of 107 nights for *P. eremicus* (59.9–77.1%). The pre-specified grid-level replication criterion passed in 7/7 and 3/3 eligible grids. Using all valid individual-nights as the denominator, directly observed material shifts provide conservative lower bounds of 28.9% and 24.6%, respectively. A post-result individual-cluster audit gave grid-stratified bootstrap intervals of 68.0–77.0% and 61.3–78.9%, indicating that the held-out fractions were not driven by a few repeatedly sampled individuals.

We position the method as complementary to continuous-time capture–recapture and movement models, not as a replacement. It is intended as a scale-aware pre-analysis diagnostic that tells analysts when a one-state-per-occasion reduction is spatially non-negligible and should be retained, modelled at finer temporal resolution, or carried through sensitivity analysis.

The method is implemented as generic MIT-licensed code requiring only individual identifier, occasion identifier, within-occasion time, coordinates and a study-defined material spatial scale. The paper includes simulation failure modes, a checked generic example, deterministic sensitivity bounds and a prospectively held-out empirical validation.

A prospectively planned downstream MCP home-range analysis did not meet its frozen high-information support gate and was stopped before effect values were calculated; we therefore make no home-range-bias claim.

Would this combination of a general observation-process diagnostic, corrected simulation benchmark, deterministic sensitivity framework and prospectively locked taxon-level empirical validation be within scope for a Research Article?

Thank you for your consideration.
