# Applicability matrix — temporal positional aliasing diagnostic v1

The empirical validation is specific to repeated-check live trapping. The diagnostic itself requires only repeated locations within a user-defined ecological occasion.

| Observation system | Individual identity available? | Multiple positions can occur within one ecological occasion? | Example occasion | Example material spatial scale | What the diagnostic can say | Important caveat |
|---|---:|---:|---|---|---|---|
| Repeated-check live traps | Yes | Yes, if animals are released and recaptured | Night | Trap spacing | Whether one-location-per-night reduction discards material observed position differences | Recapture mechanism can be behaviourally informative |
| RFID / PIT-tag antenna arrays | Yes | Yes | Night / day | Antenna spacing or habitat feature width | Whether multiple within-occasion antenna detections imply material positional ambiguity | Detector field may be anisotropic; Euclidean spacing may need replacement |
| Individual-recognized camera traps | Sometimes | Yes | Day / night / survey period | Camera spacing | Whether one detector location per occasion hides material multi-camera detections | Identity error and detection dependence must be handled separately |
| Acoustic localization of known individuals | Sometimes | Yes | Call bout / survey interval | Localization error or array spacing | Whether within-occasion localized positions differ at an inferentially relevant scale | Localization uncertainty should be incorporated into the material scale or model |
| High-frequency telemetry | Yes | Yes | Day / night | GPS error, habitat resolution, or chosen ecological scale | Whether a daily/nightly representative state is spatially sensitive to within-period observations | Continuous-time movement models may be preferable when fine-scale inference is required |
| Repeated visual resightings | Yes | Yes | Survey visit | Observer resolution / patch size | Whether one recorded position per visit is a material reduction | Observation effort and visibility may determine repeat observation |

## General decision logic

1. Define the ecological occasion independently of the observed span distribution.
2. Define a material spatial scale independently of the observed effect.
3. Preserve timestamped repeated positions.
4. Run the diagnostic.
5. If positional spans are negligible relative to the material scale, document and justify the collapse rule.
6. If spans are material, choose among finer occasion definition, continuous-time modelling, multi-state retention, or explicit representative-state sensitivity.

## Boundary

This table describes **applicability of the data structure**, not empirical evidence that positional aliasing is large in every listed system. The magnitude demonstrated in the manuscript is validated only for the San Jacinto repeated-check live-trapping protocol.
