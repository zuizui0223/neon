# Downstream home-range sensitivity — final stop

Date: 2026-09-29

The prospectively frozen support gate did not authorize MCP effect extraction.

- PEMA: 17 eligible individuals; required 20.
- PEER: 6 eligible individuals; required 15.

Eligibility required >=10 capture nights, >=5 unique FIRST flags, >=5 unique LAST flags, and non-collinear FIRST and LAST spatial geometry.

The downstream effect-analysis workflow was triggered prematurely twice while the support workflow was still queued. Both attempts stopped inside the analysis code at the frozen support gate before MCP areas or FIRST/LAST area ratios were calculated or persisted.

Therefore:

**decision = stop_downstream_home_range_not_estimable**

This is a sample-support limitation, not evidence that nightly representative-location choice does or does not affect home-range estimates.

The paper must not claim a downstream home-range effect from this dataset. The core contribution remains the generic positional-aliasing diagnostic, deterministic sensitivity bounds, prospectively held-out positional validation, and denominator/simulation analyses.
