# V17 — abundance versus per-seed fate under changing resource composition
26 Nov 2026. Reproducible published-model implications, not original-data refit or observed effect. Input Guo et al. 2026, Ecology and Evolution, DOI 10.1002/ece3.73611, Methods 2.3–2.5 and all six seed-size rows of Table 1. Artificial seed experiment: 80 seeds/patch, pair frequencies .1,.3,.5,.7,.9, four replicates per combination in each year. Original paper already reports frequency-dependent removal. V17 asks about absolute expected focal-seed removal count, not novelty of frequency dependence.

## Fixed-total-count replacement contrast
For total offered count N and focal fraction f, expected focal removal count Y=N f p(f). Under ordinary binomial logit with shared intercept a, p(f)=logistic(a+b f). When f increases .1→.9 (8→72 focal seeds), the risk ratio for an intercept shift d=b(.9-.1) lies between min(1,exp(d)) and max(1,exp(d)) for every finite intercept. Thus the expected count ratio lies between 9 min(1,exp(d)) and 9 max(1,exp(d)). This is an exact mathematical consequence of the assumed model, not proof that any particular patch or consumer exhibits it. For all six size pairings, even the unknown-intercept lower bound exceeds one. A negative linear slope must be below −2.74653 before this lower bound can permit a reversal for this ninefold focal count change. That is a necessary, not sufficient, condition for decreasing absolute removal count. For a two-stage product the log risk ratio bounds add. Quadratic endpoint shift is b Δf+c Δf².

| Focal/neighbor seed size | Removal odds ratio | Expected removal-count factor (point-model) | Lower bound with marginal-SE sensitivity |
|---|---:|---:|---:|
| large/medium | 0.568 | 5.112–9.000 | 3.411 |
| large/small | 0.545 | 4.904–9.000 | 2.896 |
| medium/large | 0.913 | 8.216–9.000 | 5.439 |
| medium/small | 1.568 | 9.000–14.109 | 9.000 |
| small/large | 1.977 | 9.000–17.793 | 9.000 |
| small/medium | 1.048 | 9.000–9.435 | 6.025 |

All six lower bounds remain above one under each marginal slope estimate ±1.96 SE considered separately; minimum 2.896. Not simultaneous or sampling-calibrated confidence intervals, not new hypothesis tests. Same random-intercept distribution would preserve these pointwise count-ratio bounds when integrating; different background conditions or unverified link/scale may not.

## Caching boundary
Methods define caching among removed seeds, but Table 1 lists n=1600 for each removal and caching model; result percentages/counts also conflict. Do not choose a denominator without raw records. Under the two hypothetical interpretations, compute N f p_cache if per release, and N f p_removal p_cache|removal if conditional. For large/medium: point-model count lower bounds 1.765 and 1.003; second is near the threshold. With marginal-normal sensitivities both permit decrease (0.596, 0.226). Only 3/6 rows have a positive lower bound under both hypothetical interpretations. These are not validated cache results; no pooling or final biological claim. No raw-data acquisition attempt on this source this turn.

## Resource quantity and composition
V16 beech rain ratio 9.1723 = total three-species rain ratio 3.5274 × beech fractional share ratio 2.6003. Log changes partition 56.88% vs 43.12%; arithmetic only, not causal estimates. Focal supply variation cannot be equated with total resource increase. Fixed seed-count experiment separates changes in composition from total seed count, not from total biomass/energy; focal and alternative counts still covary. Both the Austrian and artificial seed data motivate measuring absolute interaction flow alongside per-seed probability, not a new general law. Guo methods specify Nov 2024 and Apr 2025; Dryad README says November in each year. Timing discrepancy unresolved; published model pools two trials, so no seasonal contrast.

Next genuinely independent test: compare the fixed-count model implication against directly measured counts at replicated patches, using source-resolved release cohorts and both per-seed and absolute outcomes, ideally independent total-quantity × composition factorial. To relate seasonal resource changes to plant population dynamics, seed survival/viability and actual recruitment are required. No claim that more removal equals more successful dispersal. No formal meta-analysis, no merge/submission.