# Diagnosing temporal positional aliasing in repeated-location ecological data

**Target:** Methods in Ecology and Evolution — Research Article  
**Version:** v0.3  
**Status:** corrected pre-submission-enquiry manuscript draft

## Abstract

1. Ecological observations are often aggregated to occasions such as nights, days or visits before spatial analysis. When the same marked individual is observed at multiple locations within one occasion, reducing those records to a single location introduces an often-unreported analytical choice. We call the hidden within-occasion spatial variation **temporal positional aliasing**.

2. We introduce a generic, scale-aware diagnostic that quantifies first-to-last positional span relative to a user-defined material spatial scale. The diagnostic reports repeat-observation-conditioned material-shift frequency with Wilson uncertainty, an all-occasion directly observed lower bound, and deterministic metric-geometry bounds on the sensitivity of inter-occasion movement and population mean-pairwise-distance statistics. We evaluate the diagnostic in a 72-cell simulation benchmark that varies sample size, true positional span, baseline repeat-observation probability and dependence of repeat observation on span.

3. Under non-informative repeat observation, the repeat-conditioned material-shift fraction was essentially unbiased for the analytic generating probability (mean absolute bias 0.00176), and mean Wilson coverage was 95.2% across benchmark cells. Coverage ranged from 86.0% to 99.5%, with the lowest value in an ultra-rare-event cell. Informative repeat observation produced directionally predictable bias: mean bias was +0.0507 when larger spans increased repeat-observation probability and -0.0799 when larger spans reduced it. The all-occasion directly observed material-shift fraction never exceeded the realized all-occasion material-shift fraction in any simulated replicate. In a prospectively locked empirical validation using two held-out Cricetidae species, one-trap-spacing-or-greater first-to-last shifts occurred on 72.6% of 485 repeat-capture individual-nights for *Peromyscus maniculatus* (95% Wilson CI 68.4–76.4%) and 69.2% of 107 nights for *P. eremicus* (59.9–77.1%), with the pre-specified spatial-replication criterion met in 7/7 and 3/3 eligible trapping grids. Across all valid individual-nights, material shifts were directly observed on at least 28.9% and 24.6%, respectively.

4. Temporal positional aliasing is therefore a measurable property of repeated-location observation protocols, not merely a theoretical possibility. The diagnostic does not reconstruct movement paths or identify a uniquely correct representative location. Instead, it provides a lightweight pre-analysis screen for deciding when within-occasion spatial variation is material relative to the intended analytical scale, when finer temporal modelling or sensitivity analysis may be warranted, and how much selected downstream spatial statistics can change solely because of the representative-location rule. Open-source code and a generic command-line implementation are provided.

## Data/Code for peer review

An anonymized, self-contained review package containing the generic diagnostic, deterministic sensitivity bounds, corrected simulation benchmark, frozen empirical result files, tests and figures is supplied as a single reviewer file. The third-party San Jacinto capture data are not redistributed in that package; they are publicly available from Figshare (DOI 10.6084/m9.figshare.18295520.v1), and the empirical pipeline verifies the frozen source-file checksum before analysis. A versioned archival code release and persistent identifier will replace the review-stage package record before final publication.

## Keywords

observation process; spatial ecology; temporal aggregation; capture–recapture; live trapping; positional uncertainty; repeated observations; sensitivity analysis; spatial scale; Peromyscus

# 1. Introduction

Ecological data are frequently collected at finer temporal resolution than they are analysed. Automated detectors may generate repeated detections within minutes, live traps may be checked repeatedly through a night, telemetry fixes may arrive irregularly, and observers may revisit the same marked individual several times during a survey interval. Yet many downstream analyses require a simpler unit: one state per night, visit, day or sampling occasion. The reduction from multiple observations to one state is often performed during data preparation and then disappears from the analytical description.

That reduction can be spatially consequential. Suppose a marked individual is detected twice within one ecological occasion, first at location (F_t) and later at (L_t). Both are valid observations, but an analysis that requires one location per occasion must either retain one of them, define a rule for combining them, or redefine the temporal occasion itself. If (F_t) and (L_t) differ substantially at the spatial scale of the ecological question, the retained state is not simply a formatting choice: it can alter distances, spatial overlap and population configuration passed to later analyses.

We call this **temporal positional aliasing**: within-occasion variation among valid observed locations that is hidden when multiple observations are collapsed to one representative spatial state. The term emphasizes the observation process rather than unobserved animal behaviour. Temporal positional aliasing is distinct from measurement error because the alternative positions are themselves recorded locations. It is distinct from reconstructing a movement path because two or several detections provide only sparse samples from that path. It is also distinct from temporal autocorrelation among successive observations, although all three issues may coexist.

Temporal aggregation is not a new problem in ecology. Spatial capture–recapture (SCR/SECR) methods explicitly distinguish detector processes and sampling occasions. Multi-catch traps detain animals and conventionally contribute at most one detector location per individual per occasion, whereas proximity detectors can generate multiple detector records within an occasion (Efford et al. 2009; Efford & Boulanger 2019). Efford, Borchers & Mowat (2013) showed that variation in detector effort and sampling interval should be represented explicitly rather than absorbed silently into detection probability. Continuous-time SECR was developed in part because aggregating exact detection times into user-defined occasions discards information and introduces subjectivity in occasion definition (Borchers et al. 2014). Movement ecology likewise has a mature literature on temporal autocorrelation, irregular sampling and thinning. Interval-trapping studies have also used repeated within-night trap checks to study activity timing directly (Drickamer & Springer 1998).

The gap addressed here is therefore narrower. Before an analyst commits to continuous-time modelling, finer occasion definitions, thinning, or a particular one-state collapse rule, there is no routine, scale-aware diagnostic that asks whether the alternative valid positions observed within an occasion are *material* relative to the spatial scale of the intended analysis, and then links the observed positional span to transparent sensitivity bounds for downstream spatial statistics.

A useful diagnostic should satisfy four requirements. First, it should be expressed relative to a spatial scale chosen from the study design or inferential context rather than rely on an arbitrary absolute distance. Second, it should distinguish what is observed among repeat-observed occasions from what can be claimed about all occasions. Third, it should remain useful when repeat observation is informative—that is, when the probability that an occasion is observed more than once depends on the underlying spatial process. Fourth, it should connect the raw positional span to interpretable changes in commonly used spatial summaries without requiring a full movement model.

Here we develop such a framework (Figure 1). For individual $i$ in occasion $t$, we define the first-to-last observed positional span $\delta_{it}=d(F_{it},L_{it})$. We compare this span with a user-defined **material spatial scale** (s), which may be trap spacing, detector resolution, positional error, habitat-patch width or another scale below which positional differences are operationally negligible for the planned analysis.

We then make three contributions. First, we provide a generic diagnostic that summarizes the frequency and magnitude of material positional spans, including both repeat-observation-conditioned estimates and a conservative all-occasion directly observed lower bound. Second, we derive deterministic metric-geometry bounds showing how unresolved within-occasion positional span can propagate into inter-occasion movement distances and mean-pairwise-distance (MPD) summaries. These inequalities are not presented as new mathematics; their contribution is to turn an easily measured observation-process quantity into an interpretable sensitivity scale. Third, we evaluate the framework using simulation and a prospectively locked empirical holdout. Simulation quantifies how repeat-observation selection affects the conditional estimator. The empirical validation tests whether material positional aliasing replicates across two previously unopened Cricetidae species and independent trapping grids.

Our aim is not to identify whether the first or last observation is the biologically “correct” state. Nor do we propose a universal correction. Instead, the framework is a pre-analysis diagnostic: if within-occasion spans are negligible relative to the intended spatial scale, simple aggregation can be documented and defended; if spans are material, the observation process should be retained, modelled at finer temporal resolution, or carried through explicit sensitivity analysis.

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

## 2.4 Simulation benchmark

### 2.4.1 Data-generating process

We evaluated the diagnostic in a factorial simulation independent of the empirical values. Each simulated individual-occasion had a latent first-to-last displacement with independent Gaussian (x) and (y) components. The Euclidean span was compared with a material scale fixed to one simulation unit.

We varied:
- number of occasions ($N=100,500$);
- displacement component SD relative to material scale: 0.25, 0.5, 1.0 and 2.0;
- baseline repeat-observation probability: 0.25, 0.50 and 0.75;
- dependence of repeat observation on positional span: $\beta=-1,0,+1$.

Each of the 72 parameter cells used 400 replicates and a fixed reproducible random seed sequence.

### 2.4.2 Repeat-observation mechanisms

Let $q$ be the baseline repeat-observation probability and $r=\delta/s$ the span expressed in material-scale units. We generated the probability that an occasion was repeat-observed as

\[
p_{\mathrm{repeat}}=
\operatorname{logit}^{-1}
\left[
\operatorname{logit}(q)+\beta(r-1)
\right].
\]

When $\beta=0$, repeat observation was independent of positional span. When $\beta>0$, large spans were preferentially repeat-observed; when $\beta<0$, large spans were preferentially absent from the repeat-observed subset. The latter two scenarios were deliberate failure modes rather than assumptions of the proposed diagnostic.

### 2.4.3 Performance metrics

For every simulated replicate we distinguished three quantities:
- the analytic generating probability $p_*$;
- the realized all-occasion material-shift fraction in that finite simulated dataset;
- the repeat-observation-conditioned material-shift fraction.

We evaluated bias of the conditional fraction and two-sided Wilson 95% coverage against $p_*$. Separately, we calculated the directly observed material-shift count divided by all occasions and tested whether that observed fraction ever exceeded the realized all-occasion fraction.

The final event should be impossible except for numerical error because directly observed material shifts are a subset of realized material shifts within the same finite dataset. Its empirical violation count therefore served as a consistency check. Wilson intervals were evaluated against the generating probability, not against the random realized fraction. Binomial boundary intervals were set exactly to zero when $k=0$ and exactly to one when $k=n$.

## 2.5 Prospectively held-out empirical validation

### 2.5.1 Dataset

We used the public San Jacinto small-mammal dataset deposited with Chock, Shier & Grether (2022; Figshare DOI 10.6084/m9.figshare.18295520.v1). The raw capture table contained date, capture time, trapping grid, trap flag, species and unique individual identifier.

The original study used fixed 7×7 trapping grids with 6.25-m trap spacing and repeated trap checks within nights. Our analysis is a secondary analysis of public data and involved no new animal handling. Chock et al. (2022) reported compliance with applicable institutional animal-care guidelines.

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

## 3.1 Simulation benchmark

The corrected simulation benchmark produced the expected distinction between non-informative and informative repeat observation (Figure 2). Across $\beta=0$ cells, the mean absolute bias of the repeat-conditioned material-shift fraction relative to the analytic generating probability was 0.00176. Mean Wilson coverage of the generating probability was 95.2%.

Coverage was not uniformly nominal in every discrete finite-sample cell. Across non-informative cells it ranged from 86.0% to 99.5%; the lowest coverage occurred when the generating material-shift probability was extremely small. Thus the benchmark supports near-nominal average Wilson performance under non-informative repeat observation while explicitly retaining rare-event discreteness as a limitation.

When repeat observation was span-enriched ($\beta=+1$), the conditional fraction was biased upward, with mean bias +0.0507 relative to the generating probability. When repeat observation was span-depleted ($\beta=-1$), bias was downward, averaging -0.0799. The magnitude of bias varied with baseline repeat probability, span distribution and sample size, and Wilson coverage could deteriorate sharply under strongly informative repeat observation.

The directly observed material-shift count divided by all occasions never exceeded the realized all-occasion material-shift fraction in any simulated replicate. Across the full 72-cell benchmark and all replicates, the lower-bound violation count was zero.

These results establish two distinct interpretations. The repeat-conditioned fraction can be an approximately unbiased estimator of the generating all-occasion material-shift probability when repeat observation is non-informative. In contrast, under informative repeat observation it is a descriptive property of the repeat-observed subset. The all-occasion directly observed fraction retains a deterministic lower-bound interpretation for the realized finite dataset in either case.

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

The held-out validation shows that a single live-trapping night frequently contained more than one observed spatial state for the same marked individual. Among nights on which this ambiguity was observable, roughly 70% differed by at least one trap spacing, and the result replicated across every eligible validation grid. The median span was one to one-and-a-half trap spacings, with upper quantiles extending several spacings.

The practical implication is not that animals “moved 6.25 m” on 70% of all nights. The protocol observes captures, not continuous paths, and repeat observation is selective. Rather, the result demonstrates that, for a large fraction of repeat-observed occasions, the data themselves do not support a unique one-location representation at the scale of the detector array.

This is an observation-process property. An analyst who retains FIRST, LAST, a random within-night capture or a temporally aggregated occasion is making a spatial-state choice even though each candidate location is directly observed.

## 4.2 Repeat-observation conditioning is both informative and diagnosable

The corrected simulation benchmark clarifies how to interpret the empirical proportions. When repeat observation is independent of positional span, the repeat-conditioned fraction is approximately unbiased for the generating all-occasion material-shift probability. Mean Wilson coverage was near 95%, although the most extreme rare-event cell showed discrete undercoverage. When repeat observation depends on span, the conditional fraction can be biased upward or downward and its Wilson interval should not be interpreted as uncertainty for the all-occasion generating probability.

This matters because live-trap recapture is rarely guaranteed to be missing completely at random with respect to behaviour. More mobile individuals may encounter more traps and become more likely to be observed repeatedly, but capture, handling and temporary trap unavailability can also suppress subsequent detections. The proposed diagnostic does not solve this selection mechanism.

Instead, the framework separates three quantities. The generating probability is the population-level target in simulation. The repeat-conditioned fraction characterizes occasions on which positional aliasing is exposed. The all-occasion directly observed fraction is a conservative lower bound on the realized finite-dataset fraction because every directly observed material shift is necessarily a realized material shift. In San Jacinto, those lower bounds were still approximately 29% and 25% of all valid individual-nights.

The held-out result was also robust to repeated contributions from the same marked individuals. This dependence audit is important because the prospectively frozen Wilson intervals use individual-nights as the working binomial units and therefore do not themselves model within-individual correlation across nights. Grid-stratified individual-cluster bootstrap intervals remained far above the pre-specified 25% materiality threshold in both species, although these post-result intervals do not replace the frozen confirmatory rule.

If a study requires the latent all-occasion aliasing probability itself, then a model of repeat-observation probability is needed. The diagnostic identifies when that extra modelling effort may be worth undertaking.

## 4.3 A diagnostic before thinning, aggregation or continuous-time modelling

Temporal aggregation already has principled solutions. Continuous-time SECR can retain exact detection times and avoid arbitrary occasion definitions when the detection process and inferential goal justify that complexity (Borchers et al. 2014). Telemetry analyses can model continuous-time movement or explicitly account for temporal autocorrelation and irregular sampling. Other workflows thin data to a coarser temporal schedule.

Our diagnostic is complementary to those approaches. It is intended for the decision point *before* an analyst chooses among them.

If observed within-occasion spans are small relative to detector spacing, location uncertainty or the ecological scale of interest, collapsing to one spatial state may be an acceptable simplification. If spans are large, the diagnostic does not prescribe a universal replacement model. Instead it flags that the collapse rule is material and should be addressed by finer occasion definition, continuous-time modelling, multi-state retention or explicit sensitivity analysis.

The user-defined material scale is central to this interpretation. A 5-m positional span may be irrelevant to a landscape-scale analysis but decisive on a dense live-trapping grid. Expressing spans in units of (s) therefore makes the diagnostic portable across protocols and taxa.

## 4.4 Propagating positional uncertainty rather than choosing a correct state

The deterministic bounds offer a simple way to connect raw positional ambiguity with downstream statistics. For inter-occasion movement, the difference between FIRST-based and LAST-based distances can never exceed the sum of the two within-occasion spans. For population MPD, the representative-state difference is bounded by twice the mean individual span.

These bounds deliberately avoid a claim that FIRST or LAST is closer to a latent “true” location. In many protocols neither is privileged. Capture can itself alter subsequent activity, yet the first capture can also occur after substantial unobserved movement. A centroid or mean location would introduce a different state not necessarily corresponding to a detector observation.

The more defensible question is therefore: *how sensitive can the downstream statistic be to the unresolved within-occasion state?* The bounds answer that question without requiring a movement model.

They are upper bounds, not expected biases. In many datasets the downstream difference will be much smaller because individual positional changes cancel geometrically. Conversely, large bounds relative to the effect size of interest are a warning that the chosen representative state can matter enough to warrant direct re-analysis.

## 4.5 Why the downstream home-range test stopped

A direct empirical bridge to home-range area would have strengthened the example, so we froze a high-information MCP sensitivity analysis before inspecting any area values. The support requirement was intentionally conservative because polygons from sparse locations are unstable and could create an apparent FIRST/LAST effect from sampling geometry alone.

Only 17 PEMA and six PEER individuals passed the eligibility rules, and the pre-specified programme thresholds were 20 and 15. We therefore stopped before calculating MCP effects.

This non-estimability result is useful for defining the paper's boundary. The present study demonstrates positional aliasing and supplies generic downstream sensitivity bounds; it does not empirically demonstrate a home-range bias. Future applications with denser individual histories can test estimator-specific consequences prospectively.

## 4.6 Generality and limitations

The confirmatory empirical data come from one repeated-check live-trapping protocol and two held-out Cricetidae. The magnitude of the observed span distribution should not be generalized to all small mammals, live-trapping designs, detector types or ecological systems.

The method is broader than the case study because it only requires repeated locations, within-occasion ordering and a material spatial scale. Candidate applications include repeated detector encounters within survey visits, high-frequency acoustic or visual detections later aggregated to visits, dense telemetry data deliberately collapsed to daily or nightly states, or any other observation process in which multiple valid locations are reduced to one.

Generality of *applicability* should not be confused with generality of *empirical magnitude*. The paper validates that the diagnostic can expose a strong problem in held-out biological data and shows by simulation how selection into repeated observation affects interpretation. Applications to other observation systems remain an important next step.

A second limitation is that first-to-last span underestimates the full within-occasion spatial extent whenever intermediate observations extend beyond both endpoints. We use first and last because they are deterministic, interpretable and directly tied to representative-state choices. A future extension could use maximum pairwise span, convex hull diameter or a time-weighted within-occasion dispersion statistic.

Finally, the materiality scale (s) must be chosen transparently. We recommend fixing it from the study design or ecological resolution before examining the span distribution, as done here with one trap spacing.

## 4.7 Recommended workflow

We recommend that studies collecting repeated locations within ecological occasions report and evaluate the following sequence:

1. **Preserve raw observations.** Retain individual ID, detector/location ID and timestamp for every detection or recapture.
2. **Define the ecological occasion explicitly.** State why observations are being aggregated to a night, day, visit or other interval.
3. **Choose a material spatial scale before diagnosis.** Use detector spacing, location precision, habitat resolution or another inferentially meaningful scale.
4. **Quantify repeat-observation support.** Report how many individual-occasions can reveal within-occasion positional variation.
5. **Diagnose positional spans.** Report the material-shift fraction among repeat-observed occasions, Wilson uncertainty, magnitude distribution and the all-occasion directly observed lower bound.
6. **Assess observation-process informativeness.** Avoid interpreting the repeat-conditioned fraction as an all-occasion probability unless repeat observation is plausibly non-informative or modelled explicitly.
7. **Propagate sensitivity.** Compare deterministic positional-span bounds with the scale of downstream movement or spatial statistics.
8. **Choose the analysis resolution deliberately.** If spans are negligible, document the collapse rule. If they are material, consider finer occasions, continuous-time methods or representative-state sensitivity analyses.

The objective is not to force every dataset into a continuous-time model. It is to make the reduction from multiple observed spatial states to one state visible, measurable and defensible.

# 5. Data and code availability

The empirical source data are publicly available in Figshare (DOI 10.6084/m9.figshare.18295520.v1) with Chock et al. (2022). The analysis verifies the source file checksum before use.

The generic diagnostic, sensitivity-bound implementation, corrected simulation benchmark, empirical validation pipeline, tests and figure-generation scripts are released under the MIT License in the manuscript review repository. A versioned archival release and persistent repository identifier will be added before final submission.

# 6. Ethics statement

This study is a secondary analysis of previously collected public data and involved no new animal capture or handling. Chock et al. (2022) report compliance with applicable institutional guidelines for animal care and use in the original field study.

# Figure captions

**Figure 1. Temporal positional aliasing and deterministic sensitivity bounds.** A single ecological occasion can contain more than one valid observed spatial state for the same marked individual. For occasions $t$ and $u$, $F$ and $L$ denote first and last observed positions and $\delta$ the within-occasion positional span. The difference between FIRST→FIRST and LAST→LAST inter-occasion movement estimates is bounded by $\delta_t+\delta_u$; population MPD sensitivity is bounded by twice mean within-occasion span.

**Figure 2. Corrected simulation benchmark for informative repeat observation.** Mean bias of the repeat-conditioned fraction relative to the analytic generating material-shift probability, and Wilson coverage of that generating probability, across span-depleted, non-informative and span-enriched repeat-observation mechanisms. Under non-informative repeat observation, bias is concentrated near zero and mean coverage is near nominal, with discrete undercoverage in the most extreme rare-event cell; informative repeat observation produces directional bias.

**Figure 3. Prospectively held-out positional-aliasing validation.** Species-level material-shift fractions and 95% Wilson intervals for PEMA and PEER; small points show eligible trapping-grid fractions. The vertical dashed line is the frozen 25% materiality threshold.

**Figure 4. Denominator context and positional-span magnitude.** A: fraction of all valid individual-nights that were repeat-observed and the conservative all-night fraction with directly observed $\ge 1$-spacing shifts. B: median and 90th-percentile first-to-last spans in trap-spacing units.

# References

Borchers DL, Distiller G, Foster RJ, Harmsen BJ, Milazzo L. 2014. Continuous-time spatially explicit capture–recapture models, with an application to a jaguar camera-trap survey. *Methods in Ecology and Evolution* 5:656–665. https://doi.org/10.1111/2041-210X.12196.

Chock RY, Shier DM, Grether GF. 2022. Niche partitioning in an assemblage of granivorous rodents, and the challenge of community-level conservation. *Oecologia* 198:553–565. https://doi.org/10.1007/s00442-021-05104-5.

Drickamer LC, Springer LM. 1998. Methodological aspects of the interval trapping method with comments on nocturnal activity patterns in house mice living in outdoor enclosures. *Behavioural Processes* 43:171–181. https://doi.org/10.1016/S0376-6357(98)00012-6.

Efford MG, Borchers DL, Mowat G. 2013. Varying effort in capture–recapture studies. *Methods in Ecology and Evolution* 4:629–636. https://doi.org/10.1111/2041-210X.12049.

Efford MG, Boulanger J. 2019. Fast evaluation of study designs for spatially explicit capture–recapture. *Methods in Ecology and Evolution* 10:1529–1535. https://doi.org/10.1111/2041-210X.13239.

Efford MG, Dawson DK, Borchers DL. 2009. Population density estimated from locations of individuals on a passive detector array. *Ecology* 90:2676–2682. https://doi.org/10.1890/08-1735.1.
