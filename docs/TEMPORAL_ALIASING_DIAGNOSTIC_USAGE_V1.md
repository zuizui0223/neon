# Temporal aliasing diagnostic — generic usage v1

The paper branch exposes a generic observation-process diagnostic independent of the San Jacinto column schema.

Required input per observation:
- marked individual identifier;
- night/session identifier;
- sortable numeric within-night time;
- one or more numeric coordinate columns.

Example:

```bash
python analysis/temporal_aliasing_diagnostic_v1.py \
  --input captures.csv \
  --individual-col animal_id \
  --night-col night_id \
  --time-col hours_since_sunset \
  --coordinate-col x_m \
  --coordinate-col y_m \
  --material-scale 10 \
  --output aliasing_diagnostic.json
```

The `material-scale` should be chosen from study design before interpreting the result—for example trap spacing, GPS error scale, or another spatial resolution below which positional differences are operationally negligible.

The diagnostic reports:
- number of single- versus repeat-observation individual-nights;
- first-to-last positional spans;
- fraction exceeding the prechosen material scale and a Wilson interval;
- span magnitudes expressed in material-scale units;
- deterministic FIRST-versus-LAST sensitivity bounds for inter-night movement, MPD, and standardized MPD.

Important: the span is protocol-conditioned positional uncertainty. It is not a reconstructed movement path.
