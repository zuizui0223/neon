# NEON macro observation-process control: trap opportunity across both seasons
**Frozen 25 October 2026, after the positive two-genus recurrence result and prior source coverage, before opening any new same-station recurrence outcome under the common-six-night filter.**

## One rival explanation being tested

**Could changes in which physical trap stations were actually documented during both sampling seasons generate genus-associated capture-location recurrence in the original 2-genus comparison?**

The original study required ≥90 recorded trap positions on each of six trapping nights, but did **not** condition the exact two-row null on the set of stations that were *recorded* on all six nights. Stable sampling geometry is a necessary observation-process condition; it is **not** equivalent to a calibrated genus-specific capture-detection probability. A station with a row in `mam_pertrapnight` is a documented effort opportunity, **not** proof that its trap was operable if trapStatus indicates failure. The six-night test therefore diagnoses recorded station availability and cannot by itself rule out all trap faults or genus-dependent catchability.

## Original source population and strictly effect-blind first stage

- Exactly original NEON **RELEASE-2026 DP1.10072.001** 2015-04..2026-09, original **3,547** original inventory files / **21,363** plot rows / **1,505,827** trap rows as SHA/MD5+size verified by existing source loader.
- Exactly original **158** source-eligible two-genus adjacent-season comparisons, at **30 independent physical sites** across **15 ecological domains**; old **58** three-plus-genus comparisons unchanged and **not pooled**. Each paired event is exactly three original calendar nights, one earliest qualifying complete bout per site×plot×meteorological season. Shared observed tag identities are removed from both seasonal matrices as before.
- For each exact-two pair, reconstruct the six true original named nightly station sets `E_{A1}, E_{A2}, E_{A3}, E_{B1}, E_{B2}, E_{B3}` using canonical A1–J10 `trapCoordinate` for **all originally observed `mam_pertrapnight` rows**, regardless of capture. Compute the **recorded common opportunity** `C = E_{A1}∩E_{A2}∩E_{A3}∩E_{B1}∩E_{B2}∩E_{B3}`.
- Do not assume an unrecorded trap operated, synthesize stations from grid centres, or impute `trapStatus` from animal catches.
- Report the distributions and support of |C| over **all 158 pairs** and how many retain ≥2 observed occupied stations for **each of the two original genera in each season** after restricting `A` and `B` to C. Crucially, these are **within-season marginal counts**, not cross-season overlap or significance.
- Report only counts, source domain totals, source-year totals and summaries. Never leak original site, station, genus, plot, tag, file URL or exact capture-date values.
- Before opening a new same-trap cross-season effect, require **≥80** exact-two pairs with |C|≥90 and original genus/station support maintained, distributed across **≥18** physical sites and **≥10** NEON ecological domains. Newly set post-result source feasibility threshold; not retroactive original hypothesis gate.
- If fail, **STOP**, report why support is inadequate and do not soften a source threshold or manufacture source effort.

## Optional second stage ONLY if first-stage source supports GO

- Retain every source-eligible exact-two pair meeting the pre-effect common-recorded-station filter. In both seasons restrict each original already tag-disjoint genus×station incidence matrix to the **same** C.
- Use the pre-locked **mathematically exact 2-row fixed-row/column-margins hypergeometric null** (`analysis/neon_exact_two_row_fixedmargin_v1.py`). Retain C including empty and double-occupied genus columns; do not break station identities when subsetting.
- Before calculating any observed season A×B overlap, require exact-null nonzero variance in **≥75%** of the source-supported pairs, with **≥40** informative pairs and **≥12** independent physical sites. If fail STOP the ecological sensitivity with no new observed overlap.
- If GO, average standardized exact-null Z within each site and then sites equally. Retain all signs. Report both complete cohort and (only if ≥8 sites/≥20 informative pairs) a source-defined full-site exclusion for every physical site whose original site×plot×season is reused in any original exact-two pair.
- For inference do 20,000 same-site-equal null calibrations for each of two predeclared coupling mechanisms: unit-independent exact PMFs and within-site rank-comonotone stress. Rank coupling is NOT a proven upper bound for all joint dependence. Do not pool with original 58 three-plus group or claim independent second replication.
- Interpretation: positive source-matched evidence would argue against a trivial change in **documented station availability** causing all of the original conditional genus×trap recurrence, but would **NOT** resolve genus-specific catchability, capture-trap malfunction, environmental filtering or demographic turnover. A null/negative result would indicate the original observational pattern depends materially on station availability; report it faithfully.
- The original exact-two 158-pair effect and original corrected three-plus 58-pair result are untouched. The original density W/B universal 5/8 vs 6 failure stays failed.

## Priority to prevent method creep

This is **one observation-process sensitivity** directly relevant to the single NEON macroecology paper, not a separate statistical-method article. If the independent original tower air-temperature contrast currently running returns a null, do not replace it by opportunistic precipitation or another weather indicator. Neither this diagnostic nor climate can identify causation without independent measurement of trap-level habitat and genus-specific detection.

**Biological claim ceiling remains a conditional *capture-space* taxon signature, not true occupancy, population turnover, territory or competition.**
