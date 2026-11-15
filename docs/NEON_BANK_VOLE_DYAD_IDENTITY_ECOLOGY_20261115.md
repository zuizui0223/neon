# 15 November 2026 — vole identity-specific relative-space persistence after centroid shifts

## Actual independently reproduced observation

A new retrospective source-frozen dyad-rank test was executed against the exact original Mistrick et al. 2024 JAE Finland bank-vole public source, rather than an untested theory. Public source Git commit 47dc1e9b1f83ec2faaf7ba232e02e00f9e4cffb4 and original capture/treatment Git blob SHAs verified; original 2012 capture records, 742 animals, 120 observed in both seasons, 51 with at least two captures in each season, 12 biological sites and 3 per original food×helminth factorial group all reproduced. Prior within-individual centroid shift result (+0.616 source-grid units) had already been opened, hence the new endpoint is **retrospective exploratory** and must not be called pristine confirmation. Original authors already published monthly overlap-networks and their mean-overlap result.

Ten of the original 12 sites had three or more repeat-captured animals, forming **102 within-site pair identities drawn from 47 voles**. Two sites each with two repeat individuals are uninformative for rank stability across multiple pairs. All 10 candidate sites had at least three different summer pair distances and at least three different fall pair distances; original source frozen gate ≥8 sites/60 dyads/two sites in each original experimental group passed. The 102 dyads are NOT independent samples; the site, not the pair, is the resampling unit.

### Frozen primary: identity-specific pair-distance rank continuity

For each original physical site, we ranked all pairwise distances between the observed individual summer capture centroids and compared those ranks for the same exact tagged individual pairs in fall. We used a tied-rank Spearman correlation and 2,000 source-fixed within-site **shuffles of fall individual IDs**, holding both summer/fall spatial point configurations unchanged. Precommitment: [original dyad protocol](docs/NEON_BANK_VOLE_DYAD_PERSISTENCE_FROZEN_20261115.md), before observing this dyad outcome.

Observed site-equal Spearman rho: **+0.46998685**; site-equal original fall-ID permutation mean **+0.00057549**. Identity-specific excess **+0.46941136** (treatment-stratified whole-site 5,000-draw descriptive 95% bootstrap CI **[+0.10759168,+0.81913629]**); **8/10 independent source sites had positive excess** (2 negative). Pairwise spatial position is thus associated with the same individual identities across seasons beyond reassigning autumn identity labels to the observed spatial cloud. These statistics describe recorded capture-centroid relative distances, not observed contacts, movement trajectories or actual stable resource niches.

### Secondary: co-directional seasonal centroid shifts?

The same ten sites' observed shifts, expressed as relative displacement vectors of original captured centroids, produced an average magnitude-normalized directional resultant **0.624257** vs **0.506056** after randomly orienting each individual's vector at fixed observed magnitude, 2,000 source-fixed rotations per site. Excess **+0.118201**, site-bootstrap 95% CI **[−0.034221,+0.255689]** (7 sites positive, 3 negative). Unlike pair-distance rank persistence, a site-level shared direction of observed seasonal shifts is NOT resolved.

### Why this matters biologically, and limits

A stable mean value of network spatial overlap (already shown by the authors) is not the same as retaining **the identities of close individual pairs**. The latter suggests relative spatial relationships among repeated animals may remain structured despite individual seasonal centroid shifts. This does NOT prove those individual pairs interact, recognize one another, co-occupy breeding territories or pass pathogens. Individual-level relative position stability may result from persistent home-range preferences, the capture apparatus/recording process, or shared habitat variation; neither a direct detector nor a fitness/movement outcome is available. The 47/10 pair cohort and the earlier 51/12 centroid-shift cohort differ. Only three of the initial 51 animals surpassed their own individual 97.5th-percentile randomization threshold for centroid shifts. Report all sample and spatial-reference limitations.

The original NEON 14-site genus-conditioned captured-station Z+0.795 and separate Portal 436 species exact-stake pairs' source-conditioned near-zero mean remain separate observations with distinct comparators. The Structural island mammal 529-species result relies on mapped IUCN-derived labels, not observed movement/colonization. None can be meta-pooled as a new general mammal niche persistence law.

A genuinely mechanistic next test would simultaneously measure (a) individual direct movement and habitat resources, (b) identities and co-presence of actual dyad encounters, (c) trap- and camera-specific observation effort, and (d) realized fitness or infection to distinguish ecological pair persistence from observation effects. Do not mine this already-opened cohort for positive treatment, sex or relationship subgroups. Original one NEON draft paper remains submission HOLD.

Source results:
- Source-frozen outcome JSON: results/neon_bank_vole_dyad_geometry_receipt_20261115.json
- Successful GitHub Action #43680491616: https://github.com/zuizui0223/neon/actions/runs/43680491616
- Original authors' code/source: https://github.com/jmistrick/vole-spatial-manuscript
- Original 2024 JAE: https://doi.org/10.1111/1365-2656.14067


## 15 November: independent physical proximity comparator (literature, NOT our new biology)

A 2025 *Journal of Mammalogy* published study (Davidson et al., DOI 10.1093/jmammal/gyaf032) compared a 24-animal prairie-vole live-trap co-occurrence network against animal-borne ProxLogs logging proximity at 5–6cm in ONE semi-natural enclosure. Authors reported QAP r=0.148 and MRQAP R²=0.02. This is **weak direct-contact network explanation**, even though the matrices are statistically related, and reinforces that Finnish captured-centroid same-tag dyad-rank rho+0.469 is NOT an observed social-contact network. Its experiment, species, and time period are distinct; no direct field-contact validation of the Finnish source or NEON has occurred. All published original results are prior art and should not be presented as new experimental confirmation.

The same project's original Figshare metadata were successfully recovered, including 9 provider MD5-declared public files and both raw modalities and collar lookup; see results/neon_prairie_vole_figshare_source_manifest_20261115.json. Raw contact and trap records are not yet admitted as an analyzable same-exposure pair; a public CSV source header/row quality audit is ongoing. Only a separate precommitted same-time collar+trap exposure model can generate a new ecological result.
