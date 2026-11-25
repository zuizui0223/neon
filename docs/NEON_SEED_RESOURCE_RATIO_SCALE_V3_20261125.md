# Does equal relative seed availability imply equal seed fate?
25 November 2026. Exploratory extension of the seasonal seed fate project, no change to the separate capture-space manuscript, no submission or merge.

## Prior art and scope
Xiao, Zhang & Krebs 2013 (https://doi.org/10.1111/1365-2745.12113; original PDF https://www.zoology.ubc.ca/~krebs/papers/276.pdf) already tested annual seed crop and metabolic rodent abundance separately and as their ratio, across eight years in one subtropical forest. Original Figures 2/3 (printed pp.1259–1260), Table 1 (p.1261), log10 predictor methods and Table 1 visually checked. Klinger & Rejmánek 2009 (https://doi.org/10.1890/07-2146.1) already linked seasonal and interannual food variation to numerical and functional responses in six Belize grids. Jansen et al. 2004 (https://doi.org/10.1890/03-4042) already showed poor early dispersal can be offset by greater cache survival under mast conditions. Neither the ratio nor stage compensation is a new theory. The focal new test is transferability of a ratio-only prediction to different joint scales and consumer guild composition. Annual contrasts are context evidence, not seasonal replication.

## New published-model calculation
Let S = crop per plant and D = metabolic rodent abundance index, not absolute food biomass or actual per capita intake. For each published logit outcome, unrestricted model logit(p) = alpha + a log10(S) + b log10(D). Express in terms x = log10(S/D) and z = (log10(S)+log10(D))/2: coefficients (a-b)/2 and a+b respectively. A log-linear ratio-only model imposes a+b=0. Both doubling at a constant ratio changes odds by exp(log10(2)*(a+b)). These are fixed-effect point contrasts within the published model, not empirical manipulations or new fitted parameters.

| Outcome | a+b | OR for simultaneous doubling | Conservative normal envelope for a+b |
|---|---:|---:|---|
| Removal | -1.868 | 0.569883 | [-6.59748,2.86148] |
| Primary cache | -1.579 | 0.621682 | [-5.24028,2.08228] |
| Secondary cache | -2.548 | 0.464393 | [-9.77452,4.67852] |
| Survival at source | 6.088 | 6.250557 | [-9.41560,21.59160] |
| Survival at cache | -2.363 | 0.490989 | [-6.82200,2.09600] |

Uncertainty: Table 1 reports estimate ± SD but values reproduce z ratios, treated here as approximate marginal SE. Covariance is not published; worst-case SE <= SE(a)+SE(b). Every conservative normal envelope includes zero; no covariance-robust exclusion of ratio-only constraint and no new significance test or cluster-calibrated CI. Eight years in one site, no generality. Script analysis/neon_seed_resource_ratio_scale_v3.py executed independently using the Python interpreter, identity assertions passed. No raw fit. Do not claim the ratio-only model is rejected.

Graphical illustration only: visually read 2008 and 2009 Fig.2 as roughly 115 vs 40 seeds/tree, ~180 vs ~65 metabolic rodent index, ratio near 0.6 in both; Fig.3c origin survival about 22% vs 4–5%. Values are approximate, not digitized source observations. Pair noticed after reading figure, not a frozen comparison. Year, crop, population composition, resource alternatives and measurement can all differ. Do not infer true causal abundance effect or include these estimates in a meta-analysis.

## Independent sources and eligibility
Merz, Record & Mortelliti 2026 Ecology DOI 10.1002/ecy.70312, https://doi.org/10.6084/m9.figshare.28207769: original study measured seed availability, density, individual identity and seed finding/removal in Maine. Figshare DOI returned HTTP403 through browser; API article 28207769 inaccessible through browser. Original data not retrieved, no new estimates; no repeated access workaround. Relevant prior art for separating encounter and movement; season matching and seed fate beyond removal not verified.
Sidhu & Datta 2015, https://doi.org/10.1371/journal.pone.0134658; Dryad https://doi.org/10.5061/dryad.5g18m: public data listing but original authors explicitly report confounding plant species and season. Not admissible as independent matched seasonal validation without verified repeated taxon/site/time cohorts.
Forget 1996 https://doi.org/10.1017/S0266467400009998: fruit abundance and within-fruiting-season changes, previous abstract-level evidence. Do not convert published averaged percentages into counts or multiply marginal means. Original data not acquired.
Haugaasen et al. 2010 publisher abstract says 900 marked seeds, not 900 per season; prior discussion of two 900-seed cohorts needs full methods reconciliation before denominator use. Maintain exclusion from common-denominator quantitative pooling.

## Next discriminating seasonal test (design; not confirmation)
Within matched landscape, focal seed species, comparable experimental protocol, follow-up and seasonal cohort: obtain actual independently measured S (natural focal and separately alternative seed availability), D (rodent abundance with effort or metabolic abundance); record disperser-capable and seed predator-only functional groups separately if actor evidence exists. Estimate matched stage probabilities with missing fates retained. Compare frozen ratio-only and ratio-plus-scale models with season/site structure; hold out landscape and year blocks rather than individual seeds; do not claim global transfer without independent landscapes. For ratio+scale use centered within-study log variables, and within-study covariance; no effect when only one year per season or confounded species/season. To distinguish season per se from resource state, compare prediction with calendar/phenological season and resource × season interaction only in cohorts where independent variation supports them. If data insufficient, preserve source STOP. No formal meta-analysis or causal link to NEON as yet.
