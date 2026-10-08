# San Jacinto local capture-order exploration (v1)

**State:** POST-RESULT EXPLORATORY; *not* a new confirmatory claim; **not part of the MEE aliasing manuscript**. No new branch was created.

## Why this question

The original San Jacinto analysis already established spatial partitioning in 8/32 grid-season comparisons, but found no temporal segregation and 7/32 cases of temporal aggregation (Oecologia, DOI 10.1007/s00442-021-05104-5). Thus a pooled diel-time analysis cannot establish that animals avoid one another *locally and sequentially*.

Prior-occupant effects on rodent trappability are also established (Brouard et al., PLoS ONE 2015, DOI 10.1371/journal.pone.0145006; see also 1992 and 1994 odour experiments). **A raw conspecific-previous-occupant effect is not a novel discovery**.

Residual candidate: within a species-rich trapping grid whose species overlap in clock time, do *different identified individuals* of the same species recur at a trap in immediate consecutive checks more often than expected from that trap's species-specific use on other nights of the same trapping bout?

This tests a capture-order association, **not** interference competition, social-information use or true wild-animal activity.

## Data source and design

- Use the original Figshare CSV, already SHA256-pinned by `analysis/san_jacinto_positional_aliasing_v1.py`.
- Published field design: 8 grids × 49 traps × 36 nights × 3 check intervals = **42,336 protocol-defined trap-intervals**. This number is *design effort*, not the number of verified zero-capture observations in the released capture-only CSV.
- The source `date` is treated as the trapping-night label; bins are `early`, `middle`, `late`.
- Include only grid-nights with at least one valid unambiguous recorded capture in **all three** check bins. Selection is capture-dependent, so do not generalize to empty or incompletely observed nights.
- Ambiguous trap×night×bin multiple-occupant cells are excluded. Exact duplicated entries are collapsed.
- **Never infer an animal's absence from a missing capture row.** Unrecorded check status and operational trap failure cannot be verified from capture rows.
- Traps were checked three times and animals released at capture site, but the dataset does not independently establish whether every trap was reset identically after every check.

## Frozen exploratory comparison (before first execution)

An eligible case is a pair of captures in the **same trap** in consecutive check bins on the same night, by **different tagged individuals**. Let `I_same` indicate that the two captured individuals belong to the same species.

For each eligible case, construct a species-reference probability from previous-bin captures at the *same grid and trap flag* on **other dates in the same calendar month**, matched to the identical earlier check bin. References involving the identical subsequently captured individual are excluded. Cases lacking a reference are omitted from both sides.

For each case `j`:

`d_j = I_same(j) − mean(I_reference_same_species(j))`

The descriptive estimand is the mean `d_j` across matched cases. Report total and early→middle and middle→late contrasts separately, with cluster bootstrap by grid×month. Record support counts, matched grid-bout clusters, and any ambiguous records before interpretation.

**Interpretation:** A non-zero conditional difference could reflect short-lived capture effects, microhabitat persistence, repeated exposure, nonstationary activity or species interactions. It is *not* a causal treatment effect; other-night controls may themselves retain prior-occupant cues. A zero result likewise does not prove absence of interactions.

## Stop and generality rules

1. If matched cases or independent grid-bout clusters are sparse, report support only.
2. If effect exists only after including repeated capture of the *same tagged individual*, discard it as evidence for inter-individual effects. This runner excludes identical individuals by design.
3. The test must **not** be promoted to the MEE manuscript, and cannot rescue any frozen aliasing gates.
4. It is not an independent replication of the original paper; **the same Figshare field records are reused**.
5. Future direct mechanism tests require time-resolved camera/radio observations and trap cleaning/reset manipulations; the existing records do not identify an odour mechanism.
6. If local capture ordering simply reproduces already-known prior-occupant trapping bias, classify as incremental and stop the ecological manuscript lane.

## Reproducible command

```bash
python -m unittest discover -s tests -p 'test_exploratory_san_jacinto_local_sequence_v1.py' -v
python analysis/exploratory_san_jacinto_local_sequence_v1.py \
  --download-source \
  --output build/san_jacinto_local_sequence_exploratory_v1.json
```

The runner downloads the checksum-locked source and writes the result only under `build/`. No real-data result is asserted by this protocol itself.
