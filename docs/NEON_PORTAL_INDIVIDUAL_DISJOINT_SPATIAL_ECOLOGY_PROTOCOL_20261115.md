# Portal original small-mammal niche: fixed ecological test after source GO, 15 November 2026

ONE unified NEON ecology manuscript PR #23. Portal is a distinct field source in one Arizona landscape. Original 2026-11-12 pinned Portal six-file source GO in [GitHub Action #43677338828](https://github.com/zuizui0223/neon/actions/runs/43677338828): 436 eligible original plot × species × same-month adjacent-year comparisons after excluding shared observed individual IDs, 227 control / 209 kangaroo-rat exclusion, 13 / 11 original plots, 1996–2019, 35,059 identified granivore capture rows with valid ID+stake at full-QC sessions. These are PRE-OUTCOME SOURCE counts only. Do not claim niche maintenance on source data alone.

## Explicit prior art and novelty bar

Competitive release, niche segregation, experimental Dipodomys effects and Chaetodipus penicillatus patch relocation were investigated previously at Portal. In particular: 2019 Portal 22-year study on competitor-driven C. penicillatus habitat patches (https://pmc.ncbi.nlm.nih.gov/articles/PMC6899716/), and 2022 null-based spatial partitioning of six granivores (https://doi.org/10.1007/s00442-021-05104-5). Therefore the only potential distinct contribution here is a *species capture-space pattern after explicitly removing all overlapping observed individual IDs*, conditioning observed trapping opportunity and species-blind spatial propensities, and asking if the excess varies with experimental competitor access. Even that is a retrospective, previously public, single-landscape test and needs direct prior-art overlap audit.

## Ecological effect definitions, frozen BEFORE opening spatial overlap

Unit: same plot × identified target granivorous species × same calendar month in y and y+1, y=1996..2018, exactly one full-QC sampled 48–49-stake source census per year, unchanged original plot treatment control or Dipodomys exclosure; keep both taxon source groups and all years without outcomes-based selection. Exclude nonstandard negative period. For each pair, remove every observed individual ID appearing in BOTH censuses from both sides. A unique original ID with conflicting multiple stakes in the same one-night census is ambiguous: discard that ID before eligibility and preserve its count; do not silently choose the favorable stake. Retain only pairs having ≥5 disjoint IDs and ≥3 distinct stations each year. Never treat unobserved animals as truly absent or all 49 traps as documented operational at each minute.

Primary outcome, **cross-year station-collision probability**:

   O_j = sum_s p_{Ajs} p_{Bjs}

where p is the empirical fraction of distinct *newly observed*, tagged focal-species individuals captured at source stake s in year A or B; s ranges over the 49 permanent original stakes. O is probability two independently sampled **captured individuals**, one from each year, share a stake. It is NOT latent local niche use or survival.

Two frozen references, BOTH output:
- R0 uniform original 49 possible stakes: E0 = 1/49.
- R1 plot×census YEAR-specific all-identifiable target-granivore station capture mix: q_{t,s} = total distinct valid individual×taxon source encounters at station s / all such encounters, independent of focal label. E1_j = sum_s q_{A,s} q_{B,s}. This source contains focal observations, making it a conservative, species-blind reference for site opportunity/overall station preferences; it is NOT unbiased detector probability. NO post-result replacement by nonfocal-only weights or changed smoothing.
- primary descriptive excess D_j = O_j−E1_j; uniform reference excess O_j−1/49 as sensitivity.

Report all comparisons and positive/nonpositive signs, site-independent limitation, species code, plot treatment control vs exclosure, original comparisons with same IDs removed, ambiguous ID exclusions and all source year strata. Plot-equal summaries compute per-plot mean D and average across original experimental plot clusters. A noncausal treatment contrast = exclosure plot-equal mean D minus control plot-equal mean D, with 10,000 fixed-seed **whole-plot** bootstrap draws (plot IDs sampled with replacement; retain all intra-plot years/species, and each plot's within-year original treatment labels). State 95% descriptive intervals; no significance threshold or new p-value. Compare both reference classes without calling unadjusted O "niche".

Negative outcomes and no-control-source must remain visible; no rescue by inspecting plot/taxon/year subgroups after results. Original P. penicillatus, P. baileyi and D. merriami taxon-level counts are reported *as original source categories*, but not promoted to independent confirmation. A PIT-flag source sensitivity is optional only as a predeclared separate observation-quality exposure check; cannot redefine original mainline counts.

Precommitted source GO/STOP for response summarization: ≥30 retained original pairs and ≥4 experimental plot clusters in EACH group after multi-stake ID handling. This is separate from the original source receipt, whose 436 counts remain immutable. If the new ambiguity handling fails this sample gate: scientific STOP, report no ecological effect. DO NOT relax the original denominators, move years or change exclusions.

## How the result could advance mammal ecology

- Positive R0 but null/adverse R1: station recurrence is explainable by general trap opportunity/plot-wide capture structure, NOT a species niche signal.
- Positive R1 in both treatments: consistent with species-specific capture-station preference maintained across disjoint observed IDs, but still a possibly persistent species-dependent detector preference.
- Positive R1 whose degree differs across treatments: experimentally informative context-dependence of recorded spatial structure, but NOT causal competition release unless exchangeability, plot history, stable effort and local habitat validated.
- Null R1: evidence against a general claim that different observed individuals reconstruct exact species-stake locations in this landscape, NOT disproof of a species niche at 6.25m or other scales.

The primary biological follow-up (separate source / heldout) is whether measured habitat and competitor availability predicts this *individual-disjoint station recurrence* out of sample beyond an observation-conditioned reference; at site×year with co-located quadrat stakes, not just a positive regression selected after viewing old outcomes.

## No forbidden transfers

NEON old original 14-site/58-pair station Z=+0.795 and exploratory two-genus 30-site Z=+0.615 remain intact. Structural island 529 mapped ultrarare species graph log-loss and 96/79 adjacent layers are NOT this estimator and must not be pooled. Portal is one experimental geographic landscape, with correlated and repeatedly sampled plots. This is **retrospective exploratory**, not globally confirmatory. Original NEON density 5/8, patch p=.221, trap-operability 18/158, climate 79/80 and Structural biological HOLD remain unchanged.
