# MEE novelty boundary after Baer et al. (2026) — v1

Date: 2026-10-03

Status: current-literature correction. This note narrows, rather than expands, the novelty claim.

## New literature that materially changes the positioning

Baer, Borchers & Distiller (2026), *Capture history analysis for spatial wildlife surveys with detection times* (arXiv:2607.28455), develops a counting-process likelihood for individually identifiable wildlife surveys when capture times and locations are known.

The framework explicitly includes:
- proximity detectors;
- multi-catch traps;
- single-catch traps;
- removal traps.

For SCR with physical traps, the at-risk process records when an animal is detained and when it is released/reset into the population. Thus repeated captures after release can in principle be represented directly in continuous time rather than forcing a one-location-per-night collapse.

This means the present paper must **not** claim:
- that there is no exact-time method for repeated physical-trap captures;
- that repeated checks must be converted into separate discrete SCR occasions;
- that post-capture history dependence is absent from modern SCR methodology.

## Important limitation of the new exact-time framework

Baer et al.'s central multiplicative-intensity assumption is violated when post-capture behaviour changes capture intensity as a function of capture history.

They explicitly discuss this case, cite the continuous-time memory SCR work of Panchaud et al. (2024), and note that analogous history-dependent intensities can be derived. Their possum application includes a post-first-capture change in baseline hazard.

Therefore "post-capture behaviour can matter" is also not a novelty claim for this paper.

## The San Jacinto protocol is not exact-event-time data

The San Jacinto field protocol used Sherman live traps opened before dusk and **checked three times during each night** to classify early, middle and late activity. The documented times are trap-check times. Animals were detained in the trap until a check.

Consequently, for an animal found in a trap at a check, the actual entry/capture event occurred at an unknown time after the previous reset/opening and before the check.

The natural event-time representation is therefore **interval censored**, not exact.

This distinction matters because Baer et al. explicitly identify capture times known only to lie within an occasion (interval-censored capture time) as future work.

## Revised gap

The defensible gap is no longer a missing likelihood.

It is a **diagnostic and decision problem for interval-censored repeated-check data**:

> Before choosing a coarse discrete occasion, a finer check-level approximation, or a time/history-dependent model, can the analyst determine whether the observed within-occasion location ambiguity is large enough to change the downstream spatial estimand?

The present framework addresses that gap by combining:

1. a scale-aware empirical diagnostic of within-occasion location ambiguity;
2. an all-occasion lower-bound treatment that does not label singly observed nights as zero movement;
3. held-out empirical evidence that the ambiguity is frequent at a real live-trap spatial scale;
4. a downstream SCR simulation showing that a single stationary state is robust to FIRST/LAST reduction, whereas observation-conditioned state mixing creates representative-rule sensitivity;
5. a dimensionless state-mixing diagnostic,
   A_sigma = sqrt(q E[R^2]/2) / sigma_ref,
   linking observed transition energy to an independently chosen/reference SCR scale;
6. an explicit routing rule: retain ordinary discrete aggregation when aliasing is negligible; otherwise use sensitivity analysis or a time/history-aware model when the data support it.

## Relation to Panchaud et al. (2024)

Panchaud et al. develop continuous-time memory SCR in which capture intensity depends on the previous observed location and time.

That work reinforces the interpretation that standard SCR can target the wrong process when observations are temporally/spatially dependent.

It does not remove the present diagnostic niche because:
- its motivating data are continuously observed remote-sensor detections rather than live-trap detections censored to checks;
- it is a full inferential model, not a pre-analysis scale diagnostic;
- it presumes the relevant detection time/location history is available at the resolution needed by the model.

## Strongest manuscript positioning

Avoid:
> We introduce a method for handling repeated within-night live-trap captures.

Prefer:
> We introduce a scale-aware diagnostic for deciding when reducing interval-censored repeated-check locations to one state per ecological occasion is inferentially consequential, and we connect that diagnostic to downstream SCR estimand stability.

The paper's contribution is therefore **triage / diagnostic methodology**, not a replacement likelihood.

## Consequence for the "make every check an occasion" objection

That objection should be answered in three layers:

1. **Stationary process** — check-level occasioning is a reasonable information-preserving approximation and the simulation negative control shows no meaningful systematic FIRST/LAST sigma bias.
2. **History-dependent process** — check-level occasioning alone does not guarantee correct inference if post-capture response is ignored; a behaviour/history-aware model may be required.
3. **Exact-time versus check-time** — the San Jacinto protocol supplies check times, not exact trap-entry times, so an exact-event-time likelihood cannot simply be applied without addressing interval censoring.

This turns the objection into the paper's decision framework rather than a fatal counterexample.

## References to include

- Baer BR, Borchers DL, Distiller G. 2026. Capture history analysis for spatial wildlife surveys with detection times. arXiv:2607.28455.
- Panchaud C, King R, Borchers DL, Worthington H, Durbach I, Van Dam-Bates P. 2024. Incorporating Memory into Continuous-Time Spatial Capture-Recapture Models. arXiv:2408.17278.
- Borchers DL et al. 2014. Continuous-time spatially explicit capture-recapture models. Methods in Ecology and Evolution 5:656–665.
- Distiller G, Borchers DL. 2015. A spatially explicit capture-recapture estimator for single-catch traps. Ecology and Evolution 5:5075–5087.
- Chock RY, Shier DM, Grether GF. 2022. Niche partitioning in an assemblage of granivorous rodents, and the challenge of community-level conservation. Oecologia 198:553–565.
