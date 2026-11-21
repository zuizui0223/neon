# NEON genus-level three-night re-encounter propensity: source-gated single comparator
**Frozen on 26 October 2026 after exact-trap recurrence and six-night operability source STOP, before inspecting any new subsequent-night capture outcomes.**

## Biological question

Could observed genus differences in repeated trapping contribute to persistent taxon-to-exact-trap capture signatures, without implying a true movement or microhabitat template? NEON pathogen grids are sampled for three consecutive nights. The observable response is the fraction of marked animals **captured on the first night** that are *recorded again on either of nights 2 or 3 of that same bout*. This is **conditional within-bout recorded re-encounter**, NOT individual detection probability, survival, availability, full home range, demographic turnover, or evidence that catchability causes historical spatial recurrence.

A source-only all-six-night function-coded status 4/5/6 restriction previously STOPPED at **18/158 pairs, 8 sites and 7 domains** versus 80/18/10 required. That gate remains FAILED. This question is genuinely different; it does not try to rescue that previous source restricted effect by changing its threshold.

## Frozen source cohort

- Original checksum-pinned NEON DP1.10072.001 RELEASE-2026, 2015-04 through 2026-09. Rebuild 158 exact-two-genus adjacent-season pairs at 30 physical sites and 15 NEON domains; 293 unique original three-night capture bouts. Preserve all old source and ecology results and the original 58 strict three-plus-genus group untouched.
- For each unique event use the exact three original collectDate-to-nightuid assignments in chronological order. Do NOT infer first night by lexicographic nightuid sorting.
- Include only official trapStatus code 4 (multiple capture) or 5 (capture), authoritative target taxonID resolving to a genus, valid tagID and canonical named 10x10 grid coordinate. For each original event and tag exclude if conflicting genus, ambiguous multiple stations on a night, or conflicting genus over different original bouts in the same site×plot.
- Include only genus labels belonging to at least one original exact-two source pair containing that unique bout, with repeated bout exposure deduplicated. Existing tagged animals from an earlier bout may be included as first-night marked captures here; they are NOT necessarily newly tagged individuals.
- Source-only stage may count qualified FIRST-night tags by site, bout and genus. It MUST NOT inspect whether those tags appear on either later sampling night, and never calculate a new observed re-encounter outcome or ecological recurrence score. Do not export site/plot/trap/animal/tag/day identifiers.

## One source feasibility decision, fixed before outcomes

To consider a cross-genus comparison require at least **400 first-night uniquely marked animals across 15 physical sites**. Select a pair of genera ONLY by SOURCE counts, each with at least **100 first-night marked individuals in ≥6 sites**, and with a common set of **≥6 independent physical sites** each containing at least **5 first-night animals of BOTH genera**. Among all pairs passing, choose the pair maximizing the smaller total first-night tagged cohort, then total combined cohort, then genus name alphabetical for ties. If no pair passes, record SOURCE STOP. No alternative top-ranked taxa, species subgroup, years, or reduced sample gates to rescue inference.

The preselected physical sites are exactly those with at least five first-night captured individuals of each chosen genus. No outcome-driven site selection by old positive Z, observed re-encounters, habitat, weather or density.

## One outcome, only if source passes

Count each first-night tagged animal as subsequent encounter = 1 if its original tag is found again at least once on either day 2 or day 3 in the **same** site×plot×original three-night bout with a consistently assigned original genus and trapStatus code4/5; otherwise 0. Duplicate same-night captures still count once. After original cross-night taxonomy and tag conflicts are enforced, any remaining source gate failure STOPs without choosing another genus pair.

Compute the per-site re-encounter fraction in each genus, and one **site-equal difference** between the source-selected genera across their exactly shared source sites. Produce 2,000 whole-site bootstrap replicates (seed 2026102601), a 95% percentile interval, all source counts and site support, including any negative or zero differences. Do not turn this into a claim that the genus causes capture differences. The result is a same-release, post-result exploratory observation-process comparison; **not independent biological validation** of old genus×trap recurrence.

## Limitations and immutability

The existing source loader does not carry capture fate (release, death/voucher), behavioral state or independent radio-/video-detection. Recorded subsequent re-encounters of a first-night tagged animal depend on actual availability, true station use, trap operability, movement, release fate and capture propensity. A non-reencounter is not proof the animal was absent. Thus **observed re-encounter propensity is not an identifiable genus-specific trap-level detection p**. Even a strong genus difference cannot establish it accounts for cross-season exact-station recurrence.

The old strict 3+ genus 14-site and exact-two 30-site conditional recurrence results stay unchanged; the 10 m neighbor patch non-support after season reuse exclusion (p=.221), failed eight-genus density 5/8 generality, original tower thermal 79<80 QC STOP, and all-six-function-confirmed 18/158 STOP remain unchanged.

This is a bounded component of ONE unified mammal spatial macroecology paper, not separate A/B studies or a method-only manuscript.
