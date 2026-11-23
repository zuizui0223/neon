# A night is not a point: repeated-check live trapping reveals intra-night positional aliasing in small mammals

## Abstract

Ecologists commonly reduce repeated animal detections within a sampling occasion to a single location. Continuous-time capture-recapture theory shows that temporal aggregation can discard information, but the spatial magnitude of that loss is rarely measured directly in live-trapping studies. We used public small-mammal trapping data from eight fixed 7 × 7 grids in the San Jacinto Wildlife Area, California, where traps were checked repeatedly within nights and captures were recorded with time, individual identity, and 6.25-m trap-grid position. An exploratory analysis in four heteromyid rodents revealed strong sensitivity to the choice of nightly representative location. We therefore froze a held-out confirmatory analysis in two previously uninspected Cricetidae, Peromyscus maniculatus and P. eremicus. Before opening their first-to-last positional outcomes, we required each species to have at least 100 repeat-capture individual-nights across multiple grids and trapping bouts, and prospectively defined practically important positional aliasing as a changed-location fraction exceeding 25% with a 95% Wilson lower bound above 25% and a median changed-night displacement of at least one trap spacing. Both species exceeded these criteria by large margins. The estimand is explicitly conditional on nights in which the same individual was captured at least twice; it does not estimate the fraction of all individual-nights that moved. P. maniculatus changed trap location on 352 of 485 repeat-capture nights (72.6%, 95% CI 68.4–76.4%), with a median changed-night displacement of 14.0 m. P. eremicus changed location on 74 of 107 nights (69.2%, 95% CI 59.9–77.1%), with a median displacement of 12.5 m. Leave-one-grid-out estimates remained high in both species. These displacements should not be interpreted as undisturbed movement paths because animals were captured, handled, and released. Instead, they quantify an observation-process problem: in a repeated-check live-trapping protocol, a nominal nightly location can depend strongly on when within the night it is sampled. Preserving within-night detection sequences, or at minimum auditing positional aliasing before reducing detections to one state per night, can prevent avoidable loss of spatial information.

## Introduction

Animal movement is continuous, whereas ecological sampling is usually discrete. Capture-recapture studies divide time into occasions, telemetry studies thin trajectories to regular intervals, and spatial analyses often require one position per individual per sampling unit. These reductions are frequently necessary, but they can remove information about the process being measured.

The information cost of temporal aggregation is well established theoretically. Continuous-time spatially explicit capture-recapture models were developed partly because exact detection times are often discarded when detections are grouped into occasions; except in special cases, aggregation can lose information and introduce subjectivity into occasion definition (Borchers et al. 2014). Detector models also differ in whether repeated detections within an occasion are possible and how they are represented (Efford & Boulanger 2019). These developments motivate retaining temporal information when it is available.

A less quantified problem arises in conventional live trapping when a protocol allows the same animal to be captured, released, and captured again during the same nominal occasion. If multiple spatial detections occur within one night, reducing them to one location requires a rule: first capture, last capture, an arbitrary record, or some aggregate. The biological and statistical consequences of that choice depend on how often within-night locations differ and by how much.

The San Jacinto Wildlife Area rodent study provides an unusual opportunity to measure this directly. Eight fixed 7 × 7 grids with 6.25-m spacing were trapped repeatedly from August 2015 through July 2016. Traps were checked three times during the night, animals were released at the point of capture after each check, and the public capture table retained individual identity, time, grid, and trap flag (Chock et al. 2022; Figshare 18295520 v1). Thus, repeat-captured individuals can have multiple observed spatial states within the same night.

We arrived at the present question through a separate analysis of four heteromyid rodents in the same dataset. In that exploratory sample, changing the nightly representative position from the first to the last capture altered a repeated-night movement estimate substantially. We did not treat that exploratory result as confirmation. Instead, before examining first-versus-last outcomes in the remaining common Cricetidae, we froze an independent held-out test.

Our confirmatory question was deliberately simple: is within-night positional instability large enough that reducing a repeat-capture night to one trap location is practically consequential? We prospectively required replication in both Peromyscus maniculatus and P. eremicus, a changed-location fraction above 25% with a lower 95% confidence bound above 25%, and a median changed-night displacement of at least one 6.25-m trap spacing. This design tests the magnitude of positional aliasing in the observation process rather than undisturbed animal movement.

## Methods

### Study system and public data

We analyzed the public dataset associated with Chock, Shier & Grether (2022), “Niche partitioning in an assemblage of granivorous rodents, and the challenge of community-level conservation” (Oecologia 198:553–565, DOI 10.1007/s00442-021-05104-5). The capture data are archived as Figshare article 18295520 v1 (DOI 10.6084/m9.figshare.18295520.v1).

The field study used eight trapping grids separated by at least 200 m. Each grid contained 49 Sherman live traps arranged in a 7 × 7 array with 6.25-m spacing. Traps were opened before dusk and checked repeatedly during the night. Captured animals were processed and released at the point of capture. Monthly sampling was conducted for consecutive nights around the new moon.

We pinned the source file 'year round trap data.csv' by SHA256 checksum ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301. The table contains capture date, clock time, grid, trap flag, species, individual identifier, capture history, sex, and additional biological measurements.

### Discovery and held-out confirmation

The confirmatory analysis was separated from the exploratory discovery sample. Four heteromyid species had already contributed first-versus-last positional information in an earlier analysis and were excluded from confirmation.

The held-out confirmatory taxa were Peromyscus maniculatus (PEMA) and Peromyscus eremicus (PEER). A third Cricetidae, Reithrodontomys megalotis, was screened only for effect-blind support and excluded before outcome inspection because it had no repeat-capture individual-nights meeting the structural definition.

### Capture-time ordering

Dates with two-digit years were interpreted as 2000–2099. Clock times were ordered on a nocturnal scale so that evening captures preceded midnight and post-midnight captures: hours 7–11 were mapped to 19–23, hour 12 to 24, and hours 0–6 to 24–30.

For each grid × species × individual × date, we retained all valid capture records with a canonical A1–G7 trap flag. A repeat-capture individual-night was defined as an identity-date combination with at least two valid captures. All primary proportions are therefore conditional on repeat-capture nights. This conditioning can select individuals or nights with relatively high activity or trappability, so the analysis does not estimate positional instability among all animals or all nights.

The first nightly location was the trap flag of the earliest valid capture; the last nightly location was the latest. Original source-row order broke exact time ties.

### Effect-blind support gate

Before first-versus-last outcomes were inspected, we required a held-out species to have at least 100 repeat-capture individual-nights, repeat-capture nights on at least two grids, and repeat-capture nights spanning at least six trapping bouts.

Both PEMA and PEER passed. PEMA contributed 485 repeat-capture individual-nights across eight grids and 12 bouts; PEER contributed 107 nights across three grids and 10 bouts.

### Primary outcome

For each repeat-capture individual-night we defined changed as 1 when the first and last capture flags differed and 0 otherwise.

For each species we estimated the changed fraction and a two-sided 95% Wilson interval.

Before outcomes were opened, practically important intra-night positional aliasing was defined as satisfying all of:

1. changed fraction > 0.25;
2. lower 95% Wilson bound > 0.25;
3. median Euclidean first-to-last distance among changed nights ≥ 6.25 m;
4. the frozen support requirements above.

Both species were required to pass.

Euclidean distances were calculated from the fixed grid coordinates, with adjacent trap flags separated by 6.25 m.

### Secondary robustness summaries

Secondary, non-rescuing summaries were specified in advance: mean, median, 90th percentile, and maximum first-to-last distance; fractions moving at least one, two, and three trap spacings; changed fraction by grid and trapping bout; leave-one-grid-out changed fractions; and individual-level changed fractions for individuals with repeated repeat-capture nights.

Because repeat-capture nights are clustered within individuals, grids, and bouts, we additionally audited equal-weight cluster summaries after the primary result. For each clustering axis, changed fractions were first calculated within clusters and then averaged with equal cluster weight; uncertainty was summarized with Student-t intervals across clusters. This post-result robustness check cannot change the frozen decision.

### Reproducibility

The confirmatory analysis was run independently on Ubuntu and macOS GitHub Actions runners. The resulting JSON summary and night-level CSV were byte-identical across platforms.

## Results

### Held-out confirmation

Both held-out Cricetidae passed every prospectively frozen criterion.

For Peromyscus maniculatus, first and last trap flags differed on 352 of 485 repeat-capture individual-nights, a changed fraction of 0.726 (95% Wilson CI 0.684–0.764). Among changed nights, the median first-to-last distance was 13.98 m.

For Peromyscus eremicus, 74 of 107 repeat-capture nights changed trap flag, a fraction of 0.692 (95% Wilson CI 0.599–0.771). The median changed-night distance was 12.5 m.

The frozen programme decision was confirm_intranight_positional_aliasing_across_cricetids.

### Spatial magnitude

The positional differences were not confined to adjacent traps. For PEMA, 45.2% of all repeat-capture nights had first-to-last distances of at least 12.5 m and 23.3% were at least 18.75 m. For PEER, the corresponding proportions were 38.3% and 20.6%.

Across all repeat-capture nights, including nights with no flag change, median first-to-last distance was 8.84 m for PEMA and 6.25 m for PEER. Maximum observed distances were 53.0 m and 39.5 m, respectively.

### Spatial and temporal robustness

PEMA repeat-capture nights spanned all eight trapping grids and 12 trapping bouts. PEER spanned three grids and 10 bouts.

Leave-one-grid-out changed fractions remained high. PEMA estimates ranged from approximately 0.695 to 0.741. PEER estimates ranged from approximately 0.648 to 0.718. Thus, the confirmatory result was not driven by a single grid.

Among individuals represented by at least three repeat-capture nights, the median individual changed fraction was 0.75 in PEMA and 0.90 in PEER.

The result also remained well above the 25% practical threshold when nights were not treated as the only replication unit. For PEMA, the equal-individual changed fraction was 0.711 (95% t interval 0.655–0.767), the equal-grid mean was 0.691 (0.563–0.820), and the equal-bout mean was 0.694 (0.601–0.787). For PEER, the corresponding estimates were 0.659 (0.519–0.799), 0.681 (0.448–0.913), and 0.654 (0.473–0.834). Thus, all cluster-based lower confidence bounds remained above the prospectively defined 25% practical threshold.

### Cross-platform reproducibility

The locked analysis produced byte-identical scientific outputs on Ubuntu and macOS runners. The result JSON had SHA256 61a3afbd548da12182cd76ac6831e6d004d0bdb7cfd2e6ff74846856bd9783a4; the night-level CSV had SHA256 29628e62adbb336e629a3d44026b8d567d7f878beddf338812e1aee1083ee158.

## Discussion

Repeated-check live trapping can generate more than one spatial state for the same individual within a nominal sampling night. Conditional on nights in which an individual was captured at least twice, this was not a rare edge case in two prospectively held-out Cricetidae: roughly seven in ten repeat-capture individual-nights began and ended at different trap flags, and changed nights typically spanned about two 6.25-m trap intervals.

The inference is deliberately about the observation process. These distances are not unbiased samples of undisturbed animal movement. Capture, handling, release, bait, trap availability, and the timing of trap checks can all affect subsequent detection. Nevertheless, that limitation is precisely why the result matters methodologically: if an analysis compresses a repeat-capture night to one location, the chosen record is not merely a duplicate representation of a stable nightly point. It can select among spatially distinct observations generated over several hours of the trapping protocol.

This empirical result complements continuous-time capture-recapture theory. Borchers et al. (2014) showed that aggregating exact detection times into discrete occasions can lose information. Our analysis quantifies one spatial manifestation of that general problem in a conventional live-trapping setting. We do not propose that all capture-recapture analyses require continuous-time models. Rather, when multiple detections per occasion are possible, the raw sequence should be retained long enough to determine whether collapsing it is innocuous.

A practical diagnostic follows directly. For repeat-detected individuals, investigators can report: (i) the fraction of occasions in which first and last detector locations differ, (ii) a confidence interval for that fraction, and (iii) the distribution of first-to-last distances relative to detector spacing. If these quantities are small, a one-location-per-occasion reduction may be defensible. If they are large, downstream movement or spatial-state estimates should preserve within-occasion sequence or explicitly model the aggregation rule.

The San Jacinto result also illustrates why “one night” should not automatically be treated as a biological point in time. The original protocol checked traps repeatedly and released animals after capture, creating multiple opportunities to observe different spatial states. Similar issues may arise in any design with repeated detections within an analytical occasion, including proximity detectors, camera arrays, acoustic arrays, or intensive live-trapping schedules, although the magnitude observed here should not be generalized beyond the present protocol without external replication.

Our confirmatory inference is strengthened by its discovery/holdout structure. The heteromyid discovery sample motivated the question, but the primary test was frozen before positional outcomes were opened in two Cricetidae. Both species passed a deliberately conservative threshold by a wide margin, and the effect was spatially distributed across grids. An additional cluster-based robustness audit addresses non-independence among repeated nights from the same individual.

The main limitation is equally important: repeat-capture nights are a selected subset of all individual-nights. Animals must interact with traps often enough to be observed repeatedly, and handling or release may influence subsequent detections. The magnitude reported here therefore characterizes positional aliasing among repeat-captured observations under this protocol, not the natural movement distribution of the full population.

The central recommendation is modest: preserve temporal order before choosing a representative location. A sampling occasion is an analytical construct. When the underlying data contain repeated spatial detections, reducing that occasion to one point should be treated as a modelling decision whose information cost can be measured rather than assumed.

## References

Borchers, D. L., Distiller, G., Foster, R. J., Harmsen, B. J. & Milazzo, L. (2014). Continuous-time spatially explicit capture–recapture models, with an application to a jaguar camera-trap survey. Methods in Ecology and Evolution, 5, 656–665. DOI 10.1111/2041-210X.12196.

Chock, R. Y., Shier, D. M. & Grether, G. F. (2022). Niche partitioning in an assemblage of granivorous rodents, and the challenge of community-level conservation. Oecologia, 198, 553–565. DOI 10.1007/s00442-021-05104-5.

Efford, M. G. & Boulanger, J. (2019). Fast evaluation of study designs for spatially explicit capture–recapture. Methods in Ecology and Evolution, 10, 1529–1535. DOI 10.1111/2041-210X.13239.

## Data and code availability

The source capture data are publicly archived at Figshare article 18295520 v1 (DOI 10.6084/m9.figshare.18295520.v1). The analysis pins the source CSV by checksum and records pre-outcome design locks, workflow provenance, confirmatory results, and cross-platform reproducibility receipts in the accompanying repository.
