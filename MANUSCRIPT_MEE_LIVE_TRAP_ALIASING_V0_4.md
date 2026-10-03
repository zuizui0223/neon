# Diagnosing when temporal aggregation changes spatial scale inference in repeated-location ecological data

**Target:** Methods in Ecology and Evolution — Research Article  
**Version:** v0.4  
**Status:** downstream-consequence integrated manuscript draft; pre-submission enquiry remains on hold pending final review

## Abstract

1. Ecological observations are often aggregated to occasions such as nights, days or visits before spatial analysis. When the same marked individual is observed at multiple locations within one occasion, reducing those records to a single detector state introduces a spatial choice that can disappear during data preparation. We call the hidden within-occasion spatial variation **temporal positional aliasing**.

2. We introduce a scale-aware diagnostic that quantifies first-to-last positional span relative to a prechosen material spatial scale, reports repeat-observation-conditioned material-shift frequency and a conservative all-occasion directly observed lower bound, and supplies deterministic bounds on FIRST-versus-LAST sensitivity for selected spatial summaries. We then test the missing downstream question with an empirically anchored spatial capture-recapture (SCR) simulation using the San Jacinto 7×7, 6.25-m live-trap geometry, three checks per night, the observed repeat-capture frequency, and the observed distribution of within-night displacement vectors.

3. In a prospectively locked validation, one-trap-spacing-or-greater first-to-last shifts occurred on 72.6% of 485 repeat-capture individual-nights for *Peromyscus maniculatus* and 69.2% of 107 nights for *P. eremicus*, with the frozen spatial-replication criterion met in every eligible grid. In stationary SCR negative controls, median sigma bias remained within 4% and FIRST-versus-LAST sigma ratios remained close to one. After injecting the empirical within-night transition kernel, the representative-location rule became consequential. With transitions applied after the baseline state, median LAST/FIRST sigma ratios were 1.35, 1.15 and 1.12 for generating sigma values of 6.25, 12.5 and 25 m; reversing transition timing reversed the direction (0.77, 0.86 and 0.89). CHECK-level analyses retained all detections but did not consistently recover the baseline sigma once checks sampled more than one spatial state.

4. Temporal aggregation is therefore not intrinsically problematic: under a stationary observation process it mainly discards information. The risk arises when one nominal occasion mixes distinct observation-conditioned spatial states. In that case FIRST, LAST and check-level analyses can target different spatial scales. The diagnostic identifies when that estimand instability is plausible and when finer temporal modelling, multi-state treatment or explicit sensitivity analysis is warranted.

## Data/Code for peer review

An anonymized, self-contained review package containing the generic diagnostic, deterministic sensitivity bounds, frozen empirical result files, the empirically anchored SCR consequence benchmark, tests and figures is supplied as a single reviewer file. The third-party San Jacinto capture data are not redistributed in that package; they are publicly available from Figshare (DOI 10.6084/m9.figshare.18295520.v1), and the empirical pipeline verifies the frozen source-file checksum before analysis. A versioned archival code release and persistent identifier will replace the review-stage package record before final publication.

## Keywords

observation process; spatial ecology; temporal aggregation; capture–recapture; live trapping; positional uncertainty; repeated observations; sensitivity analysis; spatial scale; Peromyscus

# 1. Introduction

Ecological data are frequently collected at finer temporal resolution than they are analysed. Automated detectors may generate repeated detections within minutes, live traps may be checked repeatedly through a night, telemetry fixes may arrive irregularly, and observers may revisit the same marked individual several times during a survey interval. Yet many downstream analyses require a simpler unit: one state per night, visit, day or sampling occasion. The reduction from multiple observations to one state is often performed during data preparation and then disappears from the analytical description.

That reduction can be spatially consequential. Suppose a marked individual is detected twice within one ecological occasion, first at location (F_t) and later at (L_t). Both are valid observations, but an analysis that requires one location per occasion must either retain one of them, define a rule for combining them, or redefine the temporal occasion itself. If (F_t) and (L_t) differ substantially at the spatial scale of the ecological question, the retained state is not simply a formatting choice: it can alter distances, spatial overlap and population configuration passed to later analyses.

We call this **temporal positional aliasing**: within-occasion variation among valid observed locations that is hidden when multiple observations are collapsed to one representative spatial state. The term emphasizes the observation process rather than unobserved animal behaviour. Temporal positional aliasing is distinct from measurement error because the alternative positions are themselves recorded locations. It is distinct from reconstructing a movement path because two or several detections provide only sparse samples from that path. It is also distinct from temporal autocorrelation among successive observations, although all three issues may coexist.

Temporal aggregation is not a new problem in ecology. Spatial capture–recapture (SCR/SECR) methods explicitly distinguish detector processes and sampling occasions. Multi-catch traps detain animals and conventionally contribute at most one detector location per individual per occasion, whereas proximity detectors can generate multiple detector records within an occasion (Efford et al. 2009; Efford & Boulanger 2019). Current `secr` software makes the reduction choice explicit: when multiple old occasions are pooled to a `multi`-trap occasion and an animal has conflicting detector locations, `reduce.capthist` resolves the conflict by selecting the first, last or a random detector record, while pooling detector usage across the contributing occasions. Thus FIRST and LAST are not peculiar constructions of this study; they are explicit representations available when repeated trap checks are aggregated. Efford, Borchers & Mowat (2013) showed that variation in detector effort and sampling interval should be represented explicitly rather than absorbed silently into detection probability. Continuous-time SECR was developed in part because aggregating exact detection times into user-defined occasions discards information and introduces subjectivity in occasion definition (Borchers et al. 2014). Movement ecology likewise has a mature literature on temporal autocorrelation, irregular sampling and thinning. Interval-trapping studies have also used repeated within-night trap checks to study activity timing directly (Drickamer & Springer 1998).

The gap addressed here is therefore narrower than temporal aggregation itself. We ask whether alternative valid positions observed for the same marked individual within one ecological occasion are material relative to the spatial scale of the intended analysis, and—critically—whether defensible temporal representations remain *estimand-equivalent* downstream. The contribution is a scale-aware pre-analysis diagnostic plus an explicit estimand-stability test, not a claim that temporal aggregation or FIRST/LAST reduction is newly recognized.

A useful diagnostic should satisfy four requirements. First, it should be expressed relative to a spatial scale chosen from the study design or inferential context rather than rely on an arbitrary absolute distance. Second, it should distinguish what is observed among repeat-observed occasions from what can be claimed about all occasions. Third, it should remain useful when repeat observation is informative—that is, when the probability that an occasion is observed more than once depends on the underlying spatial process. Fourth, it should connect the raw positional span to interpretable FIRST-versus-LAST sensitivity of commonly used spatial summaries without requiring a full movement model.

Here we develop such a framework (Figure 1). For individual $i$ in occasion $t$, we define the first-to-last observed positional span $\delta_{it}=d(F_{it},L_{it})$. We compare this span with a user-defined **material spatial scale** (s), which may be trap spacing, detector resolution, positional error, habitat-patch width or another scale below which positional differences are operationally negligible for the planned analysis.

We then make three contributions. First, we provide a generic diagnostic that summarizes the frequency and magnitude of material positional spans, including both repeat-observation-conditioned estimates and a conservative all-occasion directly observed lower bound. Second, we derive deterministic metric-geometry bounds showing how unresolved within-occasion positional span bounds the difference between FIRST- and LAST-based inter-occasion movement distances and mean-pairwise-distance (MPD) summaries. These inequalities are not presented as new mathematics; their contribution is to turn an easily measured observation-process quantity into an interpretable sensitivity scale. Third, we connect the diagnostic to a downstream model parameter. Using prospectively held-out Cricetidae data, we first test whether material positional aliasing replicates across species and trapping grids. We then use the observed repeat frequency and displacement-vector distribution to construct an SCR consequence benchmark with known generating sigma.

This final step distinguishes **information loss** from **estimand instability**. If every within-night check samples the same stationary spatial kernel, collapsing three checks to FIRST or LAST should primarily reduce information. If capture and release, short-term behavioural response, or another within-occasion process shifts the spatial state being sampled, the same nominal night becomes a mixture of spatial kernels. FIRST, LAST and check-level analyses may then estimate different effective spatial scales even though all retained detector locations are valid observations.

Our aim is not to identify whether the first or last observation is biologically “correct”, nor to infer that handling caused the empirical within-night shifts. Instead, the framework asks whether the downstream estimand is stable to a defensible change in temporal representation. If within-occasion spans are negligible relative to the intended spatial scale, simple aggregation can be documented and defended; if spans are material and the observation process may change state within an occasion, finer temporal modelling, explicit state modelling or representative-rule sensitivity analysis may be warranted.

# 2. Materials and Methods

## 2.1 Diagnostic definition

Consider individual (i) during ecological occasion (t), with temporally ordered observed locations

\[
X_{it1}, X_{it2}, \ldots, X_{itK}.
\]

For an occasion with $K\ge 2$, define the first and last observed states

\[
F_{it}=X_{it1}, \qquad L_{it}=X_{itK},
\]

and the within-occasion positional span

\[
\delta_{it}=d(F_{it},L_{it}),
\]

where $d$ is an appropriate metric for the coordinate system. The generic software currently implements Euclidean distance, while the theoretical movement bound applies to any metric satisfying the triangle inequality.

Let $s>0$ be a prechosen **material spatial scale**. We define a material positional-aliasing event as

\[
I(\delta_{it}\ge s).
\]

The choice of $s$ is deliberately external to the observed effect. It should be fixed from detector spacing, location precision or the scale of the planned ecological analysis. In the empirical live-trapping validation below, $s$ was one adjacent-trap spacing (6.25 m), a protocol-defined spatial resolution.

For $R$ repeat-observed individual-occasions, the diagnostic reports the material-shift count and fraction, a two-sided 95% Wilson confidence interval, median and upper quantiles of $\delta$, and span expressed in units of $s$. The Wilson interval describes uncertainty in the repeat-observation-conditioned proportion; it does not by itself correct selection into the repeat-observed subset.

The diagnostic also reports the number $N$ of all valid individual-occasions and the quantity

\[
\frac{\#\{\text{directly observed material shifts}\}}{N}.
\]

This fraction is an observational lower bound on the latent all-occasion material-shift fraction. A singly observed occasion cannot reveal a first-to-last change; treating such occasions as unresolved rather than as zero-shift ensures that the numerator contains only events directly exposed by repeated observation.

## 2.2 Deterministic sensitivity bounds

### 2.2.1 Inter-occasion movement

For two occasions $t$ and $u$, define the FIRST-based movement distance $d(F_t,F_u)$ and LAST-based movement distance $d(L_t,L_u)$. By the triangle inequality,

\[
|d(F_t,F_u)-d(L_t,L_u)|\le \delta_t+\delta_u.
\]

Thus the combined within-occasion spans provide a deterministic upper bound on how much an inter-occasion movement estimate can change solely because the representative-location rule changes from FIRST to LAST (Figure 1).

The bound does not assert that either representation is correct, that the bound is typically attained, or that $\delta$ is itself a movement path.

### 2.2.2 Population mean pairwise distance

For $n$ individuals represented within an occasion by paired FIRST and LAST locations, define

\[
MPD(F)=\frac{2}{n(n-1)}\sum_{i<j} d(F_i,F_j)
\]

and $MPD(L)$ analogously. Pairwise application of the triangle inequality gives

\[
|d(F_i,F_j)-d(L_i,L_j)|\le \delta_i+\delta_j.
\]

Summing across pairs yields

\[
|MPD(F)-MPD(L)|\le 2\overline{\delta}.
\]

If a standardized packing score uses common $n$ and fixed null moments,

\[
z=\frac{MPD-\mu_n}{\sigma_n},
\]

then

\[
|z_F-z_L|\le\frac{2\overline{\delta}}{\sigma_n}.
\]

We verified the inequalities numerically using sharpness examples and random Euclidean configurations. The inequalities are upper sensitivity bounds and are not stochastic estimators.

## 2.3 Generic software implementation

The generic command-line implementation requires a tabular file containing:
1. a marked-individual identifier;
2. an occasion identifier;
3. a sortable within-occasion time;
4. one or more numeric coordinate columns; and
5. a prechosen material spatial scale.

For each individual-occasion, records are ordered by time with source-row order as a deterministic tie-breaker. Invalid or incomplete rows are reported in quality-control counts. Occasions with a single valid observation contribute to the all-occasion denominator but not to the first-to-last span distribution.

The software outputs the repeat-observed count, material-shift fraction and Wilson interval, span quantiles in original and material-scale units, and the deterministic movement and MPD sensitivity formulas. A checked-in synthetic CSV and expected JSON output provide an end-to-end example independent of the San Jacinto schema. Source code is released under the MIT License.

## 2.4 Empirically anchored SCR consequence benchmark

The original diagnostic-estimator simulation is retained in Supplementary Methods S3 because it establishes the interpretation of repeat-observation-conditioned proportions and Wilson intervals. The main downstream benchmark instead asks whether the observed within-night spatial variation can alter a fitted SCR spatial scale.

### 2.4.1 Empirical transition kernel

We pooled only already-opened observation-process summaries from the two held-out species. Across 1,520 valid captured individual-nights, 592 were repeat-observed and 426 repeat nights exhibited a first-to-last displacement of at least one 6.25-m trap spacing. Thus the empirical repeat probability was 592/1,520 = 0.3895, the material-change probability conditional on repeat observation was 426/592 = 0.7196, and the directly observed transition probability was 426/1,520 = 0.2803.

For the 426 material changes we retained the observed two-dimensional detector-to-detector displacement vectors. Their pooled median length was 12.5 m and root-mean-square length was 16.94 m. The mean vector was close to zero relative to this RMS scale.

As a continuous dense-detector benchmark, if a zero-mean isotropic transition vector $H$ occurs with probability $q$, then the per-axis second moment of a baseline half-normal kernel with spatial scale $\sigma$ becomes approximately

\[
\sigma_{\mathrm{eff}}^2
\approx
\sigma^2 + \frac{qE[R^2]}{2},
\]

where $R=\|H\|$. Therefore

\[
\frac{\sigma_{\mathrm{eff}}}{\sigma}
\approx
\sqrt{1+\frac{qE[R^2]}{2\sigma^2}}.
\]

For the observed transition kernel, this benchmark predicts approximately 42.5%, 12.1% and 3.2% scale inflation for baseline $\sigma=6.25$, 12.5 and 25 m, respectively. The corresponding 10% second-moment boundary occurs near $\sigma=13.84$ m. This calculation is an interpretive benchmark, not an empirical estimate of SCR sigma.

### 2.4.2 SCR simulation

We simulated multi-catch SCR data on the San Jacinto 7×7 detector array with 6.25-m spacing. The source protocol checked traps three times per night and released animals at the point of capture during each check (Chock et al. 2022). Each simulated session contained three nights. The stationary negative-control family generated all three within-night checks directly from a half-normal SCR model.

The empirical-transition family began from a baseline nightly SCR capture history. For each captured individual-night, repeat observation was imposed with the empirical probability 0.3895. Conditional on repeat observation, a material detector transition was imposed with probability 0.7196 by resampling an observed held-out displacement vector. Non-repeat nights contributed one randomly positioned check; repeat nights contributed an early and a late check. To avoid privileging FIRST by construction, we simulated two mirrored transition orientations. In POST simulations the baseline detector state occurred first and the displaced state last; in PRE simulations the displaced state occurred first and the baseline state last.

Generating sigma was fixed at 6.25, 12.5 or 25 m. The detection intercept was $g_0=0.15$. The buffered population density was increased from 20 to 60 animals ha$^{-1}$ after an effect-blind estimability run showed insufficient fitting support at the lower density; no sigma effects from the low-support run were used for inference. Each stationary and transition cell used 40 Monte Carlo replicates.

Each simulated record set was analysed three ways:
- **CHECK:** all three physical trap checks retained as separate occasions;
- **FIRST:** the three check intervals reduced to one nightly occasion, with the first observed detector retained when an individual was captured at more than one detector;
- **LAST:** the analogous nightly reduction retaining the last observed detector.

The FIRST/LAST reductions were implemented deterministically from the simulated event records, but match the corresponding conflict semantics documented for `secr::reduce.capthist` when `multi`-detector occasions are pooled.

All fits used `secr` 5.4.3, detector type `multi`, half-normal detection, conditional likelihood, $g_0\sim b$, $\sigma\sim1$, and a 100-m mask buffer.

### 2.4.3 Frozen diagnostics and interpretation

The stationary family was a mandatory implementation control: temporal representation was not considered consequential unless stationary FIRST and LAST remained approximately centred on the same generating sigma. We report median relative sigma bias, 95% interval coverage, and paired LAST/FIRST, CHECK/FIRST and CHECK/LAST sigma ratios.

A 10% relative difference was retained as the practical materiality scale used in the earlier frozen empirical SCR design. No empirical FIRST or LAST SCR sigma estimate was opened by this simulation.

## 2.5 Prospectively held-out empirical validation

### 2.5.1 Dataset

We used the public San Jacinto small-mammal dataset deposited with Chock, Shier & Grether (2022; Figshare DOI 10.6084/m9.figshare.18295520.v1). The raw capture table contained date, capture time, trapping grid, trap flag, species and unique individual identifier.

The original study used fixed 7×7 trapping grids with 6.25-m trap spacing and repeated trap checks within nights. We treated the source `date` field as the trapping-night label rather than as a literal timestamp date. A structural, effect-independent audit supported that interpretation: the raw grid × date grouping contained all three published activity bins (early, middle and late) in 250/290 groups (86.2%), whereas an alternative that moved midnight/post-midnight records to the previous calendar date produced only 142/405 complete groups (35.1%); median transformed capture times also ordered early < middle < late. Our analysis is a secondary analysis of public data and involved no new animal handling. Chock et al. (2022) reported compliance with applicable institutional animal-care guidelines.

### 2.5.2 Prospectively held-out taxa

The methodological question was first motivated by an exploratory heteromyid analysis, but those discovery species were excluded from confirmatory inference. An effect-blind support scan was then conducted for previously unopened Cricetidae. Before first-to-last outcomes were inspected, an effect lock selected two species with sufficient repeat-capture support:

- *Peromyscus maniculatus* (PEMA): 485 repeat-capture individual-nights across 8 grids and 12 trapping bouts;
- *Peromyscus eremicus* (PEER): 107 repeat-capture individual-nights across 3 grids and 10 bouts.

A third candidate cricetid lacked sufficient repeat-capture support and was excluded before outcomes were opened.

### 2.5.3 Frozen empirical endpoint and decision rule

For each valid repeat-capture individual-night, we retained the earliest and latest valid trap flags under a deterministic nocturnal time ordering. The primary outcome was

\[
I(d_{\mathrm{first,last}}\ge 6.25\,\mathrm{m}),
\]

where 6.25 m is exactly one adjacent-trap spacing.

The species-level confirmatory criterion was frozen as:
1. material-shift fraction (>0.25);
2. lower two-sided Wilson 95% bound (>0.25);
3. spatial replication in at least two grids with at least 20 repeat-capture nights and raw material-shift fraction (>0.25).

Both held-out species were required to pass. The 25% threshold was an operational materiality criterion selected before outcome inspection to distinguish widespread positional aliasing from a rare edge case; it was not fitted to the observed fractions.

Because the same marked individual could contribute repeat-capture nights on more than one occasion, the prospectively frozen Wilson interval is best viewed as a night-level binomial working interval rather than as the sole assessment of dependence-aware uncertainty. We therefore assessed repeated contributions separately with a grid-stratified individual-cluster bootstrap and deterministic leave-one-individual summaries (Section 2.8). That post-result audit could not alter or rescue the frozen decision rule.

Secondary, non-rescuing summaries included median, 75th and 90th percentile first-to-last span, maximum span, elapsed time between first and last capture, and grid-specific raw fractions.

## 2.6 All-occasion denominator audit

The confirmatory fraction is conditioned on repeat observation. We therefore conducted a post-result denominator audit that did not alter the frozen decision rule. For each held-out species we counted all valid individual-nights, the subset with at least two valid captures, and nights on which a $\ge 1$-spacing shift was directly observed.

We interpret

\[
\frac{\text{directly observed material-shift nights}}{\text{all valid individual-nights}}
\]

only as a lower bound. No assumption is made that single-capture nights had zero positional span.

## 2.7 Prospectively gated downstream MCP analysis

To test whether positional aliasing could be propagated empirically into a familiar downstream estimator, we pre-specified a 100% minimum convex polygon (MCP) sensitivity analysis. Eligibility required at least 10 capture nights, at least five unique FIRST flags, at least five unique LAST flags, and non-collinear FIRST and LAST geometries.

Before any MCP area was calculated, the support gate required at least 20 eligible PEMA and 15 eligible PEER individuals. The effect-blind support scan produced only 17 and 6, respectively. The downstream effect stage was therefore declared non-estimable and no MCP area effect is reported. This failed gate is retained as a transparency result and does not modify the primary positional-aliasing inference.

## 2.8 Post-result individual-dependence audit

The frozen confirmatory rule treated repeat-capture individual-nights as the binomial units and separately required replication across trapping grids. Because the same marked individual could contribute multiple nights, we conducted a post-result, non-rescuing dependence audit to test whether a small number of repeatedly observed individuals dominated the species-level fractions.

Within each species, identity was defined as grid × individual ID. We reported the number and size distribution of individual clusters, an equal-individual mean of individual-specific material-shift fractions, deterministic leave-one-individual fractions, and a grid-stratified cluster bootstrap. The bootstrap resampled individual clusters with replacement within each grid, retained all repeat nights from a sampled cluster, used 20,000 replicates and a fixed seed (20260930), and reported percentile 95% intervals. This audit was not part of the frozen confirmatory decision and could not rescue a failed primary result.

## 2.9 AI-assisted development and verification

OpenAI ChatGPT (GPT-5.6 Sol; accessed September 2026) was used interactively to assist with drafting and refactoring Python analysis, test and workflow code; checking mathematical and statistical logic; identifying potential failure modes; supporting literature discovery; and drafting and editing manuscript text. AI output was not treated as empirical evidence, an independent author or a substitute for source verification. Analysis decisions and claim boundaries were preserved in version-controlled design locks and frozen result receipts, and computational outputs were checked with deterministic unit tests, continuous-integration workflows, source checksums, simulation benchmarks and manuscript-value invariants. The authors retain responsibility for the scientific content, code, source attribution, interpretation and conclusions. Source files substantially drafted or refactored with AI assistance are annotated accordingly.

# 3. Results

## 3.1 SCR downstream consequence benchmark

The stationary negative controls passed the implementation diagnostic (Figure 2). Across all three generating sigma values and all three temporal representations, the maximum absolute median relative bias was 3.95%. Median LAST/FIRST sigma ratios were 1.007, 0.966 and 1.025 for generating $\sigma=6.25$, 12.5 and 25 m, respectively. Thus FIRST and LAST did not systematically separate when all checks sampled the same stationary SCR state.

The empirical-transition simulations produced a different pattern. In POST simulations, where the baseline state preceded the injected within-night transition, median LAST/FIRST sigma ratios were 1.347, 1.154 and 1.124 for generating $\sigma=6.25$, 12.5 and 25 m. In the mirrored PRE simulations the direction reversed: median LAST/FIRST ratios were 0.766, 0.856 and 0.894. The rule effect therefore followed the state ordering rather than an intrinsic preference for FIRST or LAST.

At $\sigma=6.25$ m, the POST median sigma biases were approximately -0.6% for FIRST and +38.8% for LAST; the mirrored PRE biases were +35.0% for FIRST and -0.7% for LAST. At $\sigma=12.5$ m, corresponding POST biases were -1.7% and +15.1%, and PRE biases +16.6% and approximately 0.0%. These values are close to the range predicted by the empirical transition scale being comparable with the generating sigma.

CHECK-level fits preserved all injected detections but did not consistently recover the baseline generating sigma once the three checks sampled more than one spatial state. Their direction and magnitude depended on generating sigma and transition orientation. In contrast, stationary CHECK fits remained close to the generating sigma. Thus redefining each trap check as an SCR occasion solves the record-discarding problem but not necessarily the state-mixture problem under a static-centre model.

The simulated observation process reproduced the main empirical scale: repeat fractions averaged about 0.39–0.42, material-change fractions about 0.71–0.73, and median changed-night spans were of the same order as the held-out detector transitions. All stationary and transition fits succeeded except one stationary LAST fit at $\sigma=12.5$ m.

## 3.2 Prospectively held-out validation

Both held-out Cricetidae passed the frozen confirmatory criterion by wide margins (Figure 3).

For *P. maniculatus*, 352 of 485 repeat-capture individual-nights exhibited a first-to-last shift of at least 6.25 m, corresponding to 72.6% (95% Wilson CI 68.4–76.4%). The median first-to-last span was 8.84 m, or 1.41 trap spacings, and the 90th percentile was 25.0 m (4.0 trap spacings). All seven grids meeting the frozen replication support threshold had raw material-shift fractions above 25%.

For *P. eremicus*, 74 of 107 repeat-capture nights exhibited a material shift, corresponding to 69.2% (95% Wilson CI 59.9–77.1%). The median span was 6.25 m and the 90th percentile 19.76 m (3.16 trap spacings). All three eligible grids exceeded the 25% grid-level threshold.

The frozen empirical programme decision was therefore

\[
\texttt{authorize\_live\_trap\_positional\_aliasing\_result}.
\]

## 3.3 Denominator context

Repeat-observed nights represented a substantial but incomplete subset of all valid individual-nights (Figure 4).

For *P. maniculatus*, 485 of 1,219 valid individual-nights were repeat-observed (39.8%). A material $\ge 6.25$-m shift was directly observed on 352 nights, so directly observed material shifts comprised at least 28.9% of all valid individual-nights.

For *P. eremicus*, 107 of 301 valid individual-nights were repeat-observed (35.5%). Seventy-four nights showed a material shift, corresponding to an all-night directly observed lower bound of 24.6%.

These all-night values do not estimate latent positional aliasing on single-capture nights. They instead show that the phenomenon is not confined to an extremely rare observation class: even under the conservative treatment of every unresolved single-capture night as unknown, approximately one quarter to three tenths of all valid individual-nights contained a directly observed one-spacing-or-greater positional difference.

## 3.4 Downstream MCP support gate

The prospectively gated MCP analysis did not reach its effect stage. Seventeen PEMA and six PEER individuals satisfied the frozen high-information eligibility rules, below the required thresholds of 20 and 15. No MCP areas, area ratios or inferential comparisons were authorized.

## 3.5 Individual-cluster sensitivity

The post-result dependence audit did not indicate that the confirmatory fractions were driven by a few repeatedly sampled individuals. PEMA contained 170 grid-specific individual clusters; the largest single individual contributed 2.9% of repeat-capture nights. Its equal-individual material-shift fraction was 71.1%, the grid-stratified individual-cluster bootstrap 95% interval was 68.0–77.0%, and the minimum leave-one-individual fraction was 71.9%.

PEER contained 34 individual clusters; the largest individual contributed 14.0% of repeat nights. Its equal-individual material-shift fraction was 65.9%, the cluster-bootstrap 95% interval was 61.3–78.9%, and the minimum leave-one-individual fraction was 67.6%. These post-result summaries are robustness diagnostics only; the prospectively frozen Wilson/grid replication rule remains the confirmatory analysis.

# 4. Discussion

## 4.1 A sampling occasion can contain multiple materially different spatial states

The held-out validation shows that a single live-trapping night frequently contained more than one observed spatial state for the same marked individual. Among nights on which this ambiguity was observable, roughly 70% differed by at least one trap spacing, and the result replicated across every eligible validation grid. Median first-to-last spans were one to one-and-a-half trap spacings, with upper quantiles extending several spacings.

The practical implication is not that animals moved a fixed distance on 70% of all nights. The protocol observes captures, not continuous paths, and repeat observation is selective. Rather, the data often do not support a unique one-location representation at the scale of the detector array.

## 4.2 The downstream problem is estimand instability, not aggregation alone

The SCR benchmark changes the interpretation of temporal positional aliasing. Under a stationary observation process, collapsing repeated checks to FIRST or LAST did not generate a systematic sigma difference. Temporal aggregation in that regime mainly discarded information.

The result changed when one nominal night contained more than one spatial state. Injecting the empirically observed transition frequency and displacement-vector distribution produced substantial FIRST-versus-LAST sigma separation. Mirroring whether the displaced state occurred before or after the baseline state reversed the direction of the effect. This symmetry is important: it shows that the result is not a constructed advantage for FIRST. The representative rule matters because it selects different spatial states.

The natural control parameter is the transition second moment relative to baseline sigma squared. In a continuous approximation,

\[
\sigma_{\mathrm{eff}}/\sigma
\approx
\sqrt{1+qE[R^2]/(2\sigma^2)}.
\]

For the held-out transition kernel, the 10% benchmark occurs near a baseline sigma of 14 m. This gives the diagnostic a downstream scale: the same raw within-occasion displacement can be negligible for a broad spatial kernel and consequential for a narrow one.

## 4.3 Why “use every trap check as an occasion” is not a universal repair

A natural response to nightly locational ambiguity is to define each trap check as a separate SCR occasion. That is a valid representation and is often preferable to silently discarding observations. Conversely, current `secr` documentation explicitly supports pooling occasions and resolving `multi`-trap locational conflicts by first, last or random selection. The existence of both representations is precisely why their inferential equivalence must be checked rather than assumed.

The simulation nevertheless shows why this is not a complete answer. CHECK retains both baseline and transition-state detections. When the observation protocol itself changes the state being sampled, a static-centre SCR model fitted to every check can estimate a mixture spatial scale rather than the baseline scale. In the stationary negative controls CHECK was close to the generating sigma; under injected state transitions it was not consistently so.

This distinction separates two problems. Finer occasions solve **information loss**. They do not automatically solve **model-state mismatch**. A study that can plausibly induce or sample transient states may need a behavioural, multi-state, continuous-time or otherwise state-aware model rather than only a finer occasion definition.

## 4.4 Repeat-observation conditioning remains a sampling issue

The repeat-conditioned material-shift fraction describes occasions on which positional aliasing is exposed. It is not automatically an estimator of the all-occasion probability because repeat observation may depend on movement, trap encounter, handling response or other behaviour.

The supplementary estimator benchmark shows the expected distinction: the conditional fraction is essentially unbiased under non-informative repeat observation but can shift upward or downward when repeat observation depends on span. The all-occasion directly observed fraction retains a simpler interpretation because every observed material shift is necessarily a realized shift. In San Jacinto, those conservative lower bounds were still approximately 29% and 25% of all valid individual-nights.

If the latent all-occasion transition probability itself is the target, the repeat-observation process must be modelled. The present diagnostic instead asks first whether the observed within-occasion spatial variation is large enough to threaten a downstream estimand.

## 4.5 The empirical transition is real; its cause remains unresolved

The empirical second and later captures occurred after animals had been captured, handled and released at the point of capture. It would therefore be inappropriate to interpret first-to-last displacement as an undisturbed movement trajectory. Handling could contribute to the observed spatial change. Natural within-night movement, trap attraction or avoidance, and stochastic recapture at neighbouring detectors could also contribute.

The simulation treats this ambiguity deliberately. The empirical displacement vectors are used as an **observation-process transition kernel**, not as natural movement. PRE and POST orientations are mirrored so the result does not assume that the first or last empirical capture is the biologically correct state.

The supported conclusion is consequently narrower but more useful: if an observation protocol mixes spatial states on the scale actually observed here, standard temporal representations can target different SCR spatial scales. Determining the biological cause of those states is a separate question.

## 4.6 Why the empirical MCP test still stops

A direct empirical bridge to home-range area was prospectively specified, but only 17 PEMA and six PEER individuals passed the frozen high-information MCP eligibility rules, below the required 20 and 15. No MCP area effects were opened.

That stop should remain visible. The SCR simulation supplies the missing causal demonstration under known truth; it does not retroactively make the sparse empirical MCP comparison estimable, and it does not create an empirical PEMA/PEER sigma estimate. The paper therefore combines a prospectively held-out observation-process result with a controlled downstream consequence benchmark rather than presenting a post hoc empirical effect.

## 4.7 Generality and recommended workflow

The empirical magnitude comes from one repeated-check live-trapping protocol and two held-out Cricetidae, so it should not be generalized numerically to all trapping studies. The diagnostic itself is broader because it requires only repeated locations, within-occasion ordering and a material spatial scale.

We recommend the following workflow:

1. **Preserve raw observations.** Retain individual ID, detector/location ID and timestamp for every detection or recapture.
2. **Define the ecological occasion explicitly.** State why observations are aggregated to a night, day, visit or other interval.
3. **Choose a material spatial scale before diagnosis.** Use detector spacing, location precision, habitat resolution or another inferentially meaningful scale.
4. **Quantify repeat-observation support and positional spans.** Report the repeat-conditioned material-shift fraction, magnitude distribution and all-occasion directly observed lower bound.
5. **Ask whether the occasion can mix spatial states.** Consider handling, behavioural response, temporal movement or protocol-induced changes rather than treating aggregation as a purely formatting decision.
6. **Scale the transition to the downstream model.** Compare within-occasion transition variance with the spatial scale or effect size that the downstream analysis attempts to estimate.
7. **Test estimand stability.** Refit defensible temporal representations such as FIRST, LAST and finer occasions; if they target meaningfully different quantities, use a state-aware model or report the sensitivity explicitly.
8. **Keep causal claims separate from sensitivity claims.** Large positional aliasing can demonstrate estimand instability without identifying the biological mechanism that generated the alternative states.

The objective is not to force every dataset into a continuous-time model. It is to make the reduction from multiple observed spatial states to one state visible, measurable and defensible, and to identify when that reduction changes the parameter being estimated.

# 5. Data and code availability

The empirical source data are publicly available in Figshare (DOI 10.6084/m9.figshare.18295520.v1) with Chock et al. (2022). The analysis verifies the source file checksum before use.

The generic diagnostic, sensitivity-bound implementation, corrected simulation benchmark, empirical validation pipeline, tests and figure-generation scripts are released under the MIT License in the manuscript review repository. A versioned archival release and persistent repository identifier will be added before final submission.

# 6. Ethics statement

This study is a secondary analysis of previously collected public data and involved no new animal capture or handling. Chock et al. (2022) report compliance with applicable institutional guidelines for animal care and use in the original field study.

# Figure captions

**Figure 1. Temporal positional aliasing and deterministic sensitivity bounds.** A single ecological occasion can contain more than one valid observed spatial state for the same marked individual. For occasions $t$ and $u$, $F$ and $L$ denote first and last observed positions and $\delta$ the within-occasion positional span. The difference between FIRST→FIRST and LAST→LAST inter-occasion movement estimates is bounded by $\delta_t+\delta_u$; population MPD sensitivity is bounded by twice mean within-occasion span.

**Figure 2. Temporal representation changes SCR spatial scale only when the within-night observation process changes state.** A: stationary negative controls show median relative sigma bias for CHECK, FIRST and LAST encodings at generating sigma values of 6.25, 12.5 and 25 m; dashed lines denote ±10%. B: paired LAST/FIRST sigma ratios after injecting the empirical transition kernel in mirrored POST and PRE orientations. The solid line at one denotes rule invariance and dashed lines at 0.9 and 1.1 denote the pre-specified 10% sensitivity band. Each cell used 40 Monte Carlo replicates.

**Figure 3. Prospectively held-out positional-aliasing validation.** Species-level material-shift fractions and 95% Wilson intervals for PEMA and PEER; small points show eligible trapping-grid fractions. The vertical dashed line is the frozen 25% materiality threshold.

**Figure 4. Denominator context and positional-span magnitude.** A: fraction of all valid individual-nights that were repeat-observed and the conservative all-night fraction with directly observed $\ge 1$-spacing shifts. B: median and 90th-percentile first-to-last spans in trap-spacing units.

# References

Borchers DL, Distiller G, Foster RJ, Harmsen BJ, Milazzo L. 2014. Continuous-time spatially explicit capture–recapture models, with an application to a jaguar camera-trap survey. *Methods in Ecology and Evolution* 5:656–665. https://doi.org/10.1111/2041-210X.12196.

Chock RY, Shier DM, Grether GF. 2022. Niche partitioning in an assemblage of granivorous rodents, and the challenge of community-level conservation. *Oecologia* 198:553–565. https://doi.org/10.1007/s00442-021-05104-5.

Drickamer LC, Springer LM. 1998. Methodological aspects of the interval trapping method with comments on nocturnal activity patterns in house mice living in outdoor enclosures. *Behavioural Processes* 43:171–181. https://doi.org/10.1016/S0376-6357(98)00012-6.

Efford MG, Borchers DL, Mowat G. 2013. Varying effort in capture–recapture studies. *Methods in Ecology and Evolution* 4:629–636. https://doi.org/10.1111/2041-210X.12049.

Efford MG, Boulanger J. 2019. Fast evaluation of study designs for spatially explicit capture–recapture. *Methods in Ecology and Evolution* 10:1529–1535. https://doi.org/10.1111/2041-210X.13239.

Efford MG, Dawson DK, Borchers DL. 2009. Population density estimated from locations of individuals on a passive detector array. *Ecology* 90:2676–2682. https://doi.org/10.1890/08-1735.1.
