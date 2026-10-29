# 29 October 2026: independent longitudinal mammal observations and apparent continuity

## Completed real reanalysis

External source, independently published and already analysed in a separate 2025 paper: Lindsø et al., *Ecology and Evolution* (DOI 10.1002/ece3.71590), original 2025 Zenodo record **10.5281/zenodo.15312178 v5**. Exact public source file MD5 **56f71c980503a4e6043b4d3d424fd53c** verified in GitHub Actions #40837442932. The official dataset has 12 Norwegian forest camera sites, five campaigns from autumn 2018 through 2020, four species (bank vole, wood mouse, common shrew, pygmy shrew), **240 site×season×taxon cells**; the ordinary trapping had **cage and lethal snap** gear and occurred approximately within 20m of each camera, but not at exact NEON traps.

Detector discordance per 240 campaign/taxon cells: **84 camera positive / ordinary trap zero**, **10 capture positive / camera zero**, **66 both-positive**, **80 both-zero**. These are *recorded presence* labels, NOT comparable event-rate, true occupancy or sampling-effect-adjusted detection probabilities.

Across three fixed equal-season adjacent-year transitions (2018→2019 fall, 2019→2020 fall, 2019→2020 spring), there are **144** site×species×year comparisons. Camera detections in both years: **68**; ordinary trapping records in both years: **25**. The direction persists descriptively when ordinary gear was the same in both years: **55 camera both-year** vs **21 capture both-year** among 120 unchanged-gear transitions. Twenty-four transitions were in sites with switched cage/snap gear. The source identifies **eight** cases where an ordinary trap recorded a taxon in year 1 and zero in year 2 while a camera identified that same taxon in both years; converse camera apparent-loss despite ordinary captures in both years: **one**. Another 24 site×species transitions had camera positives in both years but NO ordinary captures in either year. These counterexamples indicate why observed local taxon disappearance/continuity is recording-method-dependent.

The independent-site mean of camera minus trap *both-year recorded positivity* was **+0.29861**, with a fixed-seed 10,000-resample bootstrap 95% interval +0.1667 to +0.4306, 10/12 sites positive, one negative, one tied. This is a descriptive estimate of observation-channel differences, not a preregistered inferential p-value or causal effect. Camera operated much longer than the 3-night ordinary trapping visits, and ordinary trap gear differed by site/year; normalizing 2025 source raw event counts as identical observation effort is invalid. Norway ecology cannot be used as an independent validation of original 58 NEON exact-trap genus recurrence or a proof of habitat memory.

## Interpretation and next biological discriminator

The historical original NEON empirical result remains genus-associated **observed capture-space** recurrence (14 original physical NEON sites Z+0.795; exploratory exact-two 30-site Z+0.615). The original independent 2026 Zenodo camera audit had **zero same-day overlap** at verified original NEON grids and is a legitimate source STOP, not overturned by the Norway data. The Norway finding instead supports the general observational warning that a detector can create apparent disappearance and apparent recurrence, even for the same small-mammal assemblage across adjacent years.

A true underlying ecology test requires new multisite paired camera/capture/understory observations at the SAME stations and seasons with known camera effort, trap-night status and separately identified taxa. Until then, distinguish (1) observed recurrences, (2) ecological processes of site/species turnover, (3) conditional camera/capture detection. Do not infer a stable local niche from one sensor and do not claim camera completeness or independent errors.

External source receipt: results/neon_external_norway_two_detector_longitudinal_receipt_20261029.json
Actions evidence: https://github.com/zuizui0223/neon/actions/runs/40837442932
Study: https://pmc.ncbi.nlm.nih.gov/articles/PMC12162949/
Original data: https://zenodo.org/records/15312178
