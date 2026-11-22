# NEON ecology decision — 19 October 2026
## Give the newly supported seasonal niche result its OWN ecology paper

**Action and status:** The full NEON seasonal genus-trap recurrence test was opened *after* its source eligibility and null were frozen. It passed the precommitted site-block inference (58/58 informative seasonal units; 14 independent physical NEON sites; 11 positive site means; mean Z=+0.800742; exact one-sided site sign-flip p=0.001159668). A separate previously frozen San Jacinto species-level test also passed at physical-grid level (10 units, six local grids, 5/6 positive, exact p=0.046875). These are independent datasets, not identical taxonomic estimands. **Do not create a narrative in which the failed original density hypothesis becomes successful.**

### Paper A — primary recommended trajectory: ecological persistence of lineage-specific trap use after observed individual replacement

**One question:** Are the same trap locations used disproportionately by the same mammal lineages across adjacent seasons, even when the observed tagged individuals are disjoint?

**Genuine current positive ecological conclusion:** In NEON, genus-associated trap-position occupancy recurs across adjacent seasons more often than expected from preserving each genus's season-B occupied-trap total and each trap's season-B richness. This is geographically repeated across 14 NEON sites, with exact site-blocked inference. San Jacinto provides a separate species-level positive precedent/source analysis over six grids in one region.

**Interesting nontrivial feature:** persistence of *where particular lineages are detected* is observed even when the *observed tagged animals* behind those locations differ; this goes beyond contemporaneous species separation or species-pool turnover. It is **NOT** proof of long-term demographic replacement (the same true animals may be missed, retagged or surviving without observation), habitat selection or social competition.

**Novelty boundary that cannot be ignored:**
- Goldingay & Price (1997, Conservation Biology 11:708–717, https://doi.org/10.1046/j.1523-1739.1997.95480.x) demonstrated temporally stable spatial segregation of sympatric Dipodomys in a small local trapping study. Temporal stability by itself is not novel.
- Chock et al. (2022, Oecologia, https://doi.org/10.1007/s00442-021-05104-5) demonstrated live-trap spatial niche partitioning and microhabitat differences among sympatric San Jacinto rodents using fixed-fixed co-occurrence nulls. Fixed-fixed nulls and spatial segregation are not novel.
- The distinctive claim is **season-to-season same-lineage trap-location recurrence among NONSHARED observed animal histories**, tested at independent-site level in the continent-spanning NEON source with pre-outcome frozen null and minimum support. It is a lineage-level statistical pattern, not evidence that lineages share one movement or territoriality mechanism.

**Current data-backed figures:**
1. Figure 1: transparent *conceptual* distinction between a returning individual and lineage-associated trap locations occupied by different captured individuals, explicitly illustrative only.
2. [Figure 2](../manuscript/figures/neon_crossseason_genus_site_means_v1.svg): 14 NEON site mean Zs (11 positive/3 negative), 58 nested units, grand +0.801, exact site p=0.00116.
3. Figure 3: separate San Jacinto species-vs-NEON genus source panels; 6 local grids versus 14 independent geographically separate sites; **never pool p-values or Z magnitudes** as one meta-analytic estimand.

**Current manuscript:** `manuscript/NEON_SPATIAL_TEMPLATE_REASSEMBLY_ECOLOGY_V0_2.md` (v0.1 retained as source history).
**Reproducible receipts:** `results/neon_crossseason_genus_template_support_receipt_20261019.json`, `results/neon_crossseason_genus_template_ecology_receipt_20261019.json`, `results/san_jacinto_crossseason_ecological_comparator_receipt_20261019.json`, `results/neon_crossseason_site_influence_exploratory_receipt_20261019.json`.

**Additional tested robustness:** the PRECOMMITTED 14-site exact site signflip is independently reproduced. POST-RESULT influence removal of any one site yields one-sided p<=0.00232; dropping the three most positive sites gives p=0.00928 with 11 remaining sites. These are supplementary influence checks and **not pre-registered separate confirmations**.

### Statistical-validity calibration completed after positive source result

The original exact 14-site **sign enumeration** p=0.001159668 is conditional
on sign-symmetry of the archived physical-site Z distributions, which was
not established by the original discrete fixed-fixed randomization. We
therefore **challenged this limitation after the positive result** without
reopening the ecology endpoint or choosing another taxon/season.

In [source-verified Actions 39217395939](https://github.com/zuizui0223/neon/actions/runs/39217395939),
all 58 original fixed-fixed null chains, 58 unit Zs, 14 sorted site
means and the original sign-flip p were reproduced exactly from the
unchanged source, original seed and original 2,000-draw per-unit nulls.
Under 20,000 independent-unit conditional null grand-site draws, **0**
replicates exceeded the observed grand Z (Monte Carlo p=**0.000049998**,
a resolution floor, not an exact zero probability). Under a strong
post-result rank-comonotone **within-site** dependence stress,
**28/20,000** replicates exceeded observed (Monte Carlo
p=**0.00144993**). Both are positive conditional-null robustness
results. But comonotonic dependence is not an empirically validated
model of linked original seasons or an upper bound on *all* dependence
structures. **Never pool these p-values, recode the original p, or label
post-result calibration a second prospective confirmation.**

This substantially addresses a specific reviewer threat (sign
symmetry), but **does not separate persistent habitat positions from
genus-specific capture propensity**, which needs independent
site/station-level source data.

Machine-readable receipt:
`results/neon_crossseason_direct_site_null_calibration_receipt_20261019.json`
and exact post-result planning specification:
`docs/NEON_CROSSSEASON_DIRECT_NULL_SITE_CALIBRATION_20261019.md`.

**Required editorial gates before submission:**
1. Independent review of the 2×2 fixed-fixed null and per-site season-level grouping; verify source history disjointness and no site pseudoreplication from complete documentation.
2. Quantify influence of genus-specific detection differences and local habitat stability with prospectively specified/independent data, or explicitly state that mechanisms are underdetermined. Do not retrofit a helpful positive habitat variable into the frozen primary endpoint.
3. A public source/data availability statement citing frozen NEON RELEASE-2026 and Figshare sources, plus DOI and GitHub commit/blob checksums. Confirm source code and any required identifiers are distributable.
4. Make the scope precise: genus in NEON, species at San Jacinto; 14 physical NEON sites, six San Jacinto local grids, not 20 independent geographic sites; observational turnover of *tags*, not verified biological death/emigration or genetic species identification.
5. Only then choose an appropriate journal and prepare a serious cover letter.

**Journal positioning, not a submission made:**
- **Oikos** — good ecological-process/community-assembly target for the already supported multi-site *pattern* with careful precedent and detection limitations; current first-choice trajectory after independent code review.
- **Journal of Animal Ecology** — strong scope match for a general mammal ecology hypothesis, but higher risk without explaining habitat/detectability or demonstrating more direct animal-level generality (official aims emphasize lasting ecological principles).
- **Ecography** — stronger fit if an independently tested geographic environmental-gradient mechanism or broad species-level extension becomes available. Do not inflate 14 sites to global biogeography.

No publication or editorial enquiry has been initiated.

### Paper B — keep SEPARATE and on HOLD: density-associated within/among-animal W/B space use

Original 1,326-session, eight-genus NEON density-accommodation test had pooled genus-equal-weight W slope −4.395 and B slope +4.977, but the precommitted >=6/8 positive-genus generality criterion FAILED at 5/8. The provisional Peromyscus subsequent event cohort failed the frozen positive-point sign, with wide intervals. The full 5-genus future study was not estimable. Subsequent source-only F/C/U work showed mathematical identifiability in Peromyscus but **ZERO literal same-season same-total and same-U composition-substitution pairs under conservative taxonomic uncertainty**. External MOSA repeat-support is adequate but biological individual identity unresolved; **no MOSA W/B ecological effects opened**.

Hence no shared-effect estimate, reclassified success, meta-analysis pooling or causal competition claim can be created by combining Paper B with the successful Paper A. **Paper B remains a separately published negative ecological test only if later original immutable data and enough independent replication justify publication.** It should not weaken Paper A or turn it back into an observational-methodological paper.

### Scientific next action

**Main objective now:** carry Paper A through independent analytical review and explicit ecological alternative explanations, without searching for new favorable endpoints in the already-opened NEON capture data.

**Later:** focal-congener experimental contrast may return once independently validated species IDs and sufficient same-N/U season-matched states exist. New NEON release support and MOSA author identity are external dependencies, not permission to retrofit Paper A or Paper B.
