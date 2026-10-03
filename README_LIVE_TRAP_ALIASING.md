# Temporal positional aliasing diagnostic

This review branch contains a lightweight diagnostic for repeated-location ecological data.

## What problem does it address?

If the same marked individual has multiple valid spatial observations inside one ecological occasion, an analysis that keeps only one location must choose a representative state. That choice can be spatially material even when every retained observation is valid.

The diagnostic measures the first-to-last within-occasion positional span and compares it with a study-defined material spatial scale.

## Minimal input

A CSV with:

- marked individual identifier;
- ecological occasion identifier;
- sortable within-occasion time;
- numeric spatial coordinates.

## Quick start

```bash
python analysis/temporal_aliasing_diagnostic_v1.py \
  --input examples/repeated_locations_example.csv \
  --individual-col animal_id \
  --night-col night_id \
  --time-col time_hours \
  --coordinate-col x_m \
  --coordinate-col y_m \
  --material-scale 5 \
  --output aliasing_diagnostic.json
```

## Core output

- repeat-observed individual-occasion count;
- first-to-last span distribution;
- fraction exceeding the material scale;
- Wilson 95% interval;
- spans expressed in material-scale units;
- deterministic FIRST-versus-LAST representative-location sensitivity bounds for inter-occasion movement and MPD.

## Interpretation

The repeat-observation-conditioned exceedance fraction characterizes the repeat-observed subset. It should not be generalized automatically to all occasions.

The fraction of **all** valid occasions with a directly observed material shift is a conservative lower bound because singly observed occasions cannot expose first-to-last change.

Observed first-to-last span is protocol-conditioned positional uncertainty. It is not a reconstructed movement path.

## Empirical validation

A prospectively locked held-out validation in two Cricetidae species showed one-trap-spacing-or-greater shifts on:

- 72.6% of 485 repeat-capture nights for *Peromyscus maniculatus*;
- 69.2% of 107 nights for *P. eremicus*.

All eligible validation grids passed the pre-specified spatial-replication criterion.

## Downstream SCR consequence

The main downstream benchmark uses the San Jacinto trap geometry and the held-out empirical transition kernel. In stationary negative controls, CHECK, FIRST and LAST representations recover the same generating SCR spatial scale. Once a nominal night is allowed to contain an empirical-scale spatial-state transition, FIRST and LAST can yield materially different fitted sigma values, and reversing the state order reverses the direction of the difference. CHECK retains all detections but does not automatically recover the baseline spatial scale in the empirically calibrated stress process, which contains both alternative within-night spatial states and encounter dependence created by repeat observations conditional on a captured night.

The earlier 72-cell simulation of repeat-observation conditioning is retained as a supplementary diagnostic-estimator benchmark.

## License

MIT.

## Review manuscript

See `MANUSCRIPT_MEE_LIVE_TRAP_ALIASING_V0_4.md` and `SUPPLEMENTARY_METHODS_MEE_LIVE_TRAP_ALIASING_V0_3.md`. The MEE pre-submission enquiry is currently on HOLD pending final consistency review.
