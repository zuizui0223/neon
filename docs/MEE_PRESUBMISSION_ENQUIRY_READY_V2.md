# MEE pre-submission enquiry — send-ready draft v2

**Proposed article type:** Research Article  
**Working title:** *Diagnosing temporal positional aliasing in repeated-location ecological data*

Dear Editors,

We would like to ask whether a manuscript introducing a lightweight diagnostic for **temporal positional aliasing** in repeated-location ecological data would be suitable for *Methods in Ecology and Evolution*.

Ecological observations are often collected more frequently than the occasions used in analysis. When the same marked individual is observed at multiple locations within one occasion, analysts may split the occasion, retain a continuous-time process, or collapse the records to one representative spatial state. We focus on the decision point before that choice: are the alternative observed positions materially different at the scale of the planned analysis?

Our proposed Research Article contributes:

1. a generic diagnostic of first-to-last within-occasion positional span relative to a user-defined material spatial scale;
2. deterministic bounds translating observed positional span into maximum sensitivity of inter-occasion movement and population mean-pairwise-distance statistics;
3. a 72-cell simulation benchmark showing when repeat-observation-conditioned summaries are unbiased and how informative repeat observation can bias them;
4. a prospectively locked held-out validation in two Cricetidae species.

In simulation, non-informative repeat observation produced mean absolute bias of 0.00063 and 95.3% mean Wilson coverage. Informative repeat observation produced directional bias, whereas the all-occasion directly observed material-shift fraction remained a valid lower bound in every simulated replicate.

In the held-out validation, first-to-last shifts of at least one 6.25-m trap spacing occurred on 72.6% of 485 repeat-capture nights for *Peromyscus maniculatus* (95% Wilson CI 68.4–76.4%) and 69.2% of 107 nights for *P. eremicus* (59.9–77.1%). The pre-specified grid-level replication criterion passed in 7/7 and 3/3 eligible grids. Using all valid individual-nights as the denominator, directly observed material shifts provide conservative lower bounds of 28.9% and 24.6%, respectively.

We position the method as complementary to continuous-time capture–recapture and movement models, not as a replacement. It is intended as a scale-aware pre-analysis diagnostic that tells analysts when a one-state-per-occasion reduction is spatially non-negligible and should be retained, modelled at finer temporal resolution, or carried through sensitivity analysis.

The method is implemented as generic MIT-licensed code requiring only individual identifier, occasion identifier, within-occasion time, coordinates, and a study-defined material spatial scale. The paper includes simulation failure modes, a checked generic example, deterministic sensitivity bounds, and a prospectively held-out empirical validation.

A prospectively planned downstream MCP home-range analysis did not meet its frozen high-information support gate and was stopped before effect values were calculated; we therefore make no home-range-bias claim.

Would this combination of a general observation-process diagnostic, simulation benchmark, sensitivity framework and held-out empirical validation be within scope for a Research Article?

Thank you for your consideration.
