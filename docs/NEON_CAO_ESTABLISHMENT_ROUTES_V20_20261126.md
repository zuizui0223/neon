# V20 — Parallel establishment routes, not dispersal alone
26 Nov 2026. Cao, Guo & Chen 2017, DOI 10.1111/1749-4877.12213. Institutional full PDF extracted Table 1–3 and narrative pp. 5–7, Fig. 2; screenshot requests failed (cache miss), so text-only transcription/cross-check, not visual table verification. Data and executable JavaScript arithmetic archived. No individual-level source acquired. Equal 540 *Pittosporopsis kerrii* seeds (18×30) and 400 *Camellia kissi* seeds (8×50) each year, total 1880. Both late August/early September releases; monitoring weeks 2–16 and following-year March/July/September; actual comparable terminal duration unverified. One forest, two years, not seasonal replication. Original authors already report species-dependent post-removal outcomes and discuss radicle pruning/regeneration, so do not claim discovery of that mechanism.
 
Community seed rain 0.85→10 seeds/m² in 110 half-m² traps (47→550 actual seeds collected); reported captured rodents 27→7 with 600 nominal trap-nights each. Community crop ratio 11.765; captured-count ratio 0.259; relative rain/capture index ratio 45.378, not edible seeds per individual. Camellia reported crop per sampled plant 113.1→112.1, different sampled plants (18/15); not equivalence or actual population-wide seed production. Pittosporopsis 2007 plant crop unmeasured.
 
## Recorded establishment accounting
Let R=recorded removal fraction, A=recorded establishment at release stations per released seed, B=recorded establishment after removal per released seed, p=A/(1−R), q=B/R. Observed T=A+B=(1−R)p+Rq. A and R use rounded published station means (equal initial seeds per station); B exact reported post-removal seedling counts divided by known release N. Zero establishment in prose preserved. No reconstruction of integer counts from rounded means. Total is recorded establishment across two routes, not natural recruitment or a causal mammal benefit.
 
| Species | R 2007→2008 (%) | A (%) | B (%) | T (%) | change T (pp) |
|---|---|---|---|---|---:|
| Pittosporopsis kerrii | 98.700 to 76.800 | 0.000 to 12.600 | 0.000 to 2.222 | 0.000 to 14.822 | 14.822 |
| Camellia kissi | 76.200 to 21.000 | 0.000 to 2.500 | 0.750 to 0.000 | 0.750 to 2.500 | 1.750 |
 
Camellia: recorded removal and post-removal establishment decrease, yet recorded overall establishment increases. The +2.5 pp source-route gain is 3.333 times the −0.75 pp loss of observed post-removal establishment, leaving +1.75 pp overall. Pittosporopsis: both recorded establishment routes increase despite lower removal; recorded after-removal share of total establishment in 2008 approximately 15%. Camellia's recorded post-removal share shifts 100%→0%; based on only three recorded post-removal establishments in 2007, ten-ish source events implied by rounded proportion in 2008 (do not infer exact count). These are descriptive pathway balances, not individual changes or identified causal compensatory mechanisms.
 
## Symmetric decomposition
Exact identity ΔT = ΔR (q̄−p̄) + (1−R̄)Δp + R̄Δq. First term reflects recorded pathway weights, others conditional recorded establishment within routes. It is not an intervention on removal. Numerical checks passed directly in JS.
 
| Species | Route-allocation component (pp) | Nonremoved-route component (pp) | Removed-route component (pp) | sum (pp) |
|---|---:|---:|---:|---:|
| Pittosporopsis kerrii | 5.630 | 6.653 | 2.539 | 14.822 |
| Camellia kissi | 0.602 | 1.627 | -0.478 | 1.750 |
 
Rounding-only endpoint corner sensitivity recorded in JSON, no sampling uncertainty or calibrated CI. Complete missing after-removal fate counts unavailable. Allowing all removed seeds to establish gives deliberately broad outer ceilings (including potentially known consumed seeds), so true total direction not identified. Net additional unrecorded low-year minus high-year establishment of 14.822 or 1.750 pp would suffice to tie the observed gains for the two species; do not infer that these missing seedlings existed. No estimate of real dispersal success or conditional cache survival beyond reported counts. Actual fate tracking horizons and seedling survival after study differ or unknown.
 
## Manuscript implication
Treat dispersal as one route, not the sole measure of plant recruitment. Distinguish (i) seasonal interaction allocation and downstream conversion (V5–V12), (ii) resource quantities/composition (V16–V18), (iii) proportional versus absolute recorded outcomes (V19), and now (iv) substitution between establishment at source and after movement (V20). This is a new accounting of published results, not a new ecological experiment, systematic meta-analysis or new evidence for causal animal mutualism. Retain NEON/Portal/Guo/Pillay strict STOPs. Future test needs same tracked release cohort, independent resource measurements, stage-specific consumers, full missing-fate partition, matched horizon, and replicated seasonal contrasts. No merge/submission.