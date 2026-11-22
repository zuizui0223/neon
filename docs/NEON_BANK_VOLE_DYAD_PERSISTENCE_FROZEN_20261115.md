# Finland bank voles: dyad identity persistence versus group-level spatial displacement — frozen retrospective analysis
15 November 2026. ONE unified NEON mammal ecology manuscript PR #23, submission HOLD.

## Original biological question and strict novelty limit

Mistrick et al. (2024, JAE DOI 10.1111/1365-2656.14067) already published bank-vole food supplementation, deworming, home-range-size effects, per-month modeled spatial-overlap networks, and apparent mean overlap stability even while population density differed. DO NOT claim those original findings as new. They estimated within-month contact *opportunity*, not independent observed physical contact, and network weighted degree does not establish whether the same individual pairs remained close between summer and autumn.

The new *exploratory retrospective endpoint* is identity-specific relative placement of the SAME documented individuals across seasons: does a pair of voles that was near each other in SUMMER remain relatively near in AUTUMN, after the animals' seasonal observed capture centroids shift?

The previous source and summer/fall displacement outcomes were already viewed. Therefore this design can be frozen for reproducibility before THIS dyad-level outcome, but cannot be called pristine, prospective independent biological confirmation or a new preregistered ecological experiment. No post-result favorable cohort, threshold or null selection.

## Source and response scope

Re-use exact original external source and the immutable two file Git blob SHAs: jmistrick/vole-spatial-manuscript commit 47dc1e9b1f83ec2faaf7ba232e02e00f9e4cffb4. Must reproduce 2,012 capture records, 742 site/tag unique observed animals, 905 summer and 1,107 fall captures, 120 seen in both seasons, and **exact same 51 frozen animals with >=2 capture events per season**. Do not inspect new individuals to raise power.

Original 51 animals span 12 distinct Finland field sites, four original factorial cells fed/control 16, fed/deworm 12, unfed/control 15, unfed/deworm 8, with 3 sites per cell; the treatment metadata file lists 13 total sites but one has zero original 2021 capture rows. Original site/trap coordinates are fixed. Season-specific centroids are computed as arithmetic means of each animal's original captured local-grid x/y positions (not verified metre units).

PRIMARY prospective-on-analysis dyad sample gate: sites must have >=3 of the original 51 animals. Effect-blind source counts indicate 10 candidate physical sites and 102 original within-site unique individual pairs; two sites with only 2 observed repeated individuals are uninformative for the RELATIVE RANK of dyad distances. For each site, require >=3 nonidentical summer pair distances and >=3 nonidentical autumn pair distances so that Spearman rank correlation is defined; sites failing this source variation test are retained as NONESTIMABLE, NOT imputed to zero. SOURCE GO to calculate the primary aggregate requires >=8 estimable original physical sites, >=60 distinct within-site dyads, and at least two estimable original sites in each of the four frozen food×helminth factorial cells. Any violation is SOURCE STOP, no alternative cutoff or substitute response.

## Fixed primary: do the identities of spatially proximate vole pairs persist?

At each eligible original physical site:
1. compute the summer and autumn x/y centroids for every originally eligible individually tagged vole;
2. list all n(n−1)/2 unordered pairs of those same IDs; compute Euclidean distances between the two centroids for each pair, once per season;
3. compute Spearman rho across all within-site pairs, using deterministic average ranks for ties. All source pairs are one site-specific multivariate object; do NOT pretend edges are independent samples;
4. frozen reference: 2,000 fixed-seed permutations per original site that randomly relabel autumn *individual identities* within that same site, preserving all observed summer and autumn centroid configurations, the exact original n and all pairwise distance distributions. Calculate the mean permuted rank rho. Primary site-level **excess identity-specific partner geometry** = observed rho − mean permuted rho. This reference tests identity-specific spatial association conditional on captured-season point patterns; it does NOT preserve individual body size, sex, breeding condition, relatedness or animal-specific detectability.
5. primary aggregate = equal-weight mean site excess across qualified independent forest sites, with site-stratified 5,000-draw bootstrap resampling the original sites *within each original food×helminth source cell*, preserving that cell's number of source sites. Report descriptive 95% interval, site signs, observed rho and null rho. DO NOT compute an unsupported permutation p-value treating interdependent dyads as independent.

Hypothesis: if identity-specific pair geometry remains organized across seasons even when individuals' observed centroids move, observed rho should exceed its same-site identity-shuffled reference. If it does NOT, average spatial overlap stability can coexist with **partner rewiring**, which is potentially important for encounter-path and infection ecology, but never proof of direct contacts.

## Secondary (predeclared): coherent seasonal collective displacement versus individual repositioning

For the SAME eligible vole IDs at each original site, obtain observed seasonal displacement vectors Δ_i = centroid_fall − centroid_summer in source grid units. A site directional coherence C = norm(mean_i Δ_i) / mean_i norm(Δ_i), bounded 0..1, with zero when no observed shift. Compare to 2,000 fixed-seed independent random-angle rotations of each animal's displacement vector within site, holding the exact observed vector magnitude. Report C−mean(C_null), site-equal mean and its stratified site-bootstrap 95% descriptive interval, without selecting only sites with a favorable primary dyad response.

This secondary distinguishes collective directional motion from unrelated individual displacements only under a SOURCE capture-centroid proxy. It cannot distinguish attraction to a spatially shared habitat change from seasonal differences in detectability, original trap grid geometry, or an unmeasured external event. Any camera or telemetry interpretation is disallowed.

## Forbidden inference and response integrity

- NO raw animal ID, exact plot name, x/y or dyad source cell is exported. Site-count, pair-count, original factorial sample support and aggregate rho/coherence ONLY.
- NO original NEON 58/158 positive capture-Z, Portal 436 conditional non-support, original Finland 51 seasonal centroid outcome, Structural 529 rare species island map response, or original authors' spatial network figure is refitted/altered.
- No pooling effect sizes: the actual measured levels differ (individual seasonal positions, same-dyad relative geometry, species at exact stations, genus capture station, map-derived island source labels).
- A positive retained dyad spatial association is NOT direct physical contact, social affiliation, reproduction, transmission or niche persistence; a null source is NOT proof animals do not interact.
- No independent claim on food or parasite treatment signs in this new endpoint; four source groups enter bootstrap DESIGN only, not a post-hoc effect search.
- Keep one ecological paper in DRAFT/SUBMISSION HOLD. The paper's actual biological finding cannot be promoted from observational capture-space to habitat/competition/dispersal causation.

Source: https://github.com/jmistrick/vole-spatial-manuscript
Prior study: https://doi.org/10.1111/1365-2656.14067
