# Diagnosing when temporal aggregation changes spatial scale inference in repeated-location ecological data

**Target:** Methods in Ecology and Evolution — Research Article  
**Version:** v0.6  
**Status:** stationary-displacement closure revision; pre-submission enquiry remains on hold pending final consistency review

## Abstract

1. Ecological observations are often collected more frequently than the occasions used for spatial analysis. When several valid locations of the same marked individual are collapsed to one state, genuine positional variation is hidden. We call this **temporal positional aliasing** and ask when such aggregation changes the downstream quantity an ecologist would report.

2. We introduce a two-stage framework that separates positional non-uniqueness from estimator sensitivity. A scale-aware screen first quantifies first-to-last span relative to a prechosen material spatial scale, but the intended estimator is then tested directly under defensible temporal representations. The key diagnostic result is negative: span magnitude alone cannot identify either the existence or direction of representation sensitivity. Time reversal makes this explicit because span-only summaries are unchanged while directed FIRST-versus-LAST contrasts reverse sign.

3. In prospectively held-out validation, shifts of at least one 6.25-m trap spacing occurred on 72.6% of 485 repeat-capture nights for *Peromyscus maniculatus* and 69.2% of 107 nights for *P. eremicus*. Yet a post-stop exploratory SCR analysis of 19 estimable PEMA sessions gave sigma = 8.85 m under FIRST and 8.56 m under LAST (-3.3%). In those sessions, per-axis displacement RMS was compatible with a fixed-centre stationary-SCR reference, but trap changes were much less frequent than under independent checks. The same marginal displacement scale was therefore assembled from a different transition mixture: more zero-displacement repeats and longer moves conditional on changing traps.

4. Stationary SCR simulations preserved FIRST/LAST equivalence. Controlled ordered-state transitions produced substantial divergence, and reversing transition order reversed its direction. Thus frequent positional aliasing is a warning condition, not a bias estimate: consequential representation instability requires temporal asymmetry, not positional variation or serial dependence alone. The framework separates positional non-uniqueness, transition dependence and directional estimand instability before deciding whether coarse aggregation is defensible or finer temporal/state modelling is needed.

## Data/Code for peer review

An anonymized, self-contained review package containing the generic diagnostic, deterministic sensitivity bounds, frozen empirical result files, the post-stop PEMA representation-stability result, the SCR consequence benchmark, tests and figures is supplied as a single reviewer file. The third-party San Jacinto capture data are not redistributed in that package; they are publicly available from Figshare (DOI 10.6084/m9.figshare.18295520.v1), and the empirical pipeline verifies the frozen source-file checksum before analysis. A versioned archival code release and persistent identifier will replace the review-stage package record before final publication.

## Keywords

capture–recapture; observation process; repeated observations; spatial ecology; spatial scale; temporal aggregation; time-reversal symmetry; within-occasion variation

# 1. Introduction

Ecological data are often collected at finer temporal resolution than they are analysed. Automated detectors, telemetry, visual resightings and repeated live-trap checks can yield several valid locations for the same marked individual within one night, day or visit, whereas downstream analyses may require one spatial state per occasion. Collapsing those observations is therefore not always a neutral formatting step. We call hidden within-occasion variation among valid observed locations **temporal positional aliasing**. It is distinct from measurement error because the alternative positions are observed, and from reconstructing a movement path because sparse detections do not reveal the path between them.

Temporal aggregation and dependence are established problems in spatial capture–recapture (SCR/SECR). Detector processes differ in whether multiple locations can occur within an occasion (Efford et al. 2009; Efford & Boulanger 2019), and current `secr` software explicitly resolves conflicting locations when `multi` occasions are pooled by selecting the first, last or a random detector while pooling detector usage (Efford 2026). These options expose locational ambiguity, not when it matters inferentially. Coarser occasions also have direct small-mammal precedent (Romairone et al. 2018), while varying effort should be represented explicitly rather than absorbed into detection probability (Efford et al. 2013). Continuous-time SECR was developed partly because discretizing exact detection times discards information and makes occasion definition subjective (Borchers et al. 2014). Aggregation effects depend on the observation model (Milleret et al. 2018), and movement can induce residual correlation among detections even after conditioning on an activity centre (Stevenson et al. 2022). Recent continuous-time and history-dependent SCR models explicitly represent movement or dependence between detections (Panchaud et al. 2026; van Helsdingen & Jones-Todd 2026).

The unresolved issue here is narrower: **when do several valid positions within one nominal occasion actually make a downstream spatial estimand representation-dependent?** Existing aggregation and movement-dependence work shows that coarsening and serial correlation can matter, but observed displacement magnitude does not diagnose the sign or size of a representation effect. A large first-to-last span establishes positional non-uniqueness, but it does not by itself show that FIRST, LAST or finer check-level representations have different population-level consequences. Reverse-time methods also have a separate history in capture–recapture demography (Nichols 2016); our use of reversal concerns within-occasion spatial representation, not demographic time reversal.

A useful diagnostic therefore needs to do more than report distance. It should express span relative to a spatial scale fixed by the study design or inferential question, separate repeat-observation-conditioned quantities from claims about all occasions, remain interpretable when repeat observation is informative, and connect positional non-uniqueness to the estimator that will actually be reported.

We develop such a framework (Figure 1). For individual (i) in occasion (t), the first-to-last span is (delta_{it}=d(F_{it},L_{it})), compared with a prechosen **material spatial scale** (s), such as trap spacing, positional error or habitat-patch width. The framework then separates three questions. First, how often are materially different positions observed within an occasion? Second, does the within-occasion process contain serial dependence or directional temporal structure? Third, does the intended downstream estimator change under defensible temporal representations?

The key theoretical boundary is time-reversal symmetry. If the within-occasion observation law is invariant when check order is reversed, reversal exchanges FIRST and LAST while leaving the data law unchanged. Full temporal exchangeability is sufficient but not necessary; reversible serial dependence is allowed. Span-only summaries are invariant to reversal, whereas a directed FIRST-versus-LAST contrast changes sign. Thus positional span can flag potential sensitivity but cannot identify the existence or direction of downstream bias.

We combine this diagnostic with prospective empirical validation and generative SCR simulation. Positional non-uniqueness is tested in two held-out Cricetidae across trapping grids. Where estimation is supported, a clearly labelled post-stop PEMA analysis tests whether FIRST and LAST materially change fitted SCR sigma. Stationary simulations provide the reversal-symmetric null, while mirrored ordered-state simulations isolate the additional temporal asymmetry required for directional instability. The aim is not to declare FIRST or LAST biologically correct or to infer that handling caused observed shifts. It is to determine when coarse temporal representation is empirically benign and when finer-time or state-aware modelling is warranted.

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

## 2.2 Time-reversal symmetry and span non-identifiability

Let one ecological occasion contain ordered check-level detector outcomes \(Y_1,\ldots,Y_K\), with zero denoting no detection. FIRST is the detector on the earliest non-zero check and LAST the detector on the latest non-zero check.

A transparent process-level sufficient condition, weaker than full exchangeability, is time-reversal symmetry. Let \(R(Y_1,\ldots,Y_K)=(Y_K,\ldots,Y_1)\). If, conditional on the latent spatial state and observation design used by the downstream model,

\[
Y\overset{d}=R(Y),
\]

then time reversal exchanges FIRST and LAST while leaving the conditioning event of at least one detection unchanged. Therefore

\[
\mathrm{FIRST}\overset{d}=\mathrm{LAST}.
\]

Independent, identically distributed checks around a fixed activity centre are a sufficient special case, but not the only one: a stationary reversible process may be serially dependent and still satisfy the same reversal condition. FIRST and LAST can differ in any realized finite dataset, including by several detector spacings, but neither rule has a directional population-level advantage under a reversal-symmetric null.

The same argument exposes a limit of any span-only diagnostic. Reversing within-occasion time changes \((F_t,L_t)\) to \((L_t,F_t)\), but

\[
d(F_t,L_t)=d(L_t,F_t).
\]

Thus the material-shift fraction, span quantiles and any statistic based only on the unordered distribution of \(\delta_t\) are invariant to time reversal. By contrast, a directed downstream contrast \(T(L)-T(F)\) changes sign, and \(\log\{T(L)/T(F)\}\) changes to its negative. The direction of a representation effect is therefore not identifiable from positional-span summaries alone.

Temporal exchangeability can be broken by post-detection behavioural response, capture and release, changing detector effort, changing environmental conditions, directional within-occasion movement, or any other process that makes later checks sample a different state distribution. This distinction motivates the two-stage framework used here: the aliasing screen asks whether positional non-uniqueness is material; the downstream representation-stability analysis asks whether that non-uniqueness changes the intended estimand.

## 2.3 Deterministic sensitivity bounds

### 2.3.1 Inter-occasion movement

For two occasions $t$ and $u$, define the FIRST-based movement distance $d(F_t,F_u)$ and LAST-based movement distance $d(L_t,L_u)$. By the triangle inequality,

\[
|d(F_t,F_u)-d(L_t,L_u)|\le \delta_t+\delta_u.
\]

Thus the combined within-occasion spans provide a deterministic upper bound on how much an inter-occasion movement estimate can change solely because the representative-location rule changes from FIRST to LAST (Figure 1).

The bound does not assert that either representation is correct, that the bound is typically attained, or that $\delta$ is itself a movement path.

### 2.3.2 Population mean pairwise distance

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

## 2.4 Generic software implementation

The generic command-line implementation requires a tabular file containing:
1. a marked-individual identifier;
2. an occasion identifier;
3. a sortable within-occasion time;
4. one or more numeric coordinate columns; and
5. a prechosen material spatial scale.

For each individual-occasion, records are ordered by time with source-row order as a deterministic tie-breaker. Invalid or incomplete rows are reported in quality-control counts. Occasions with a single valid observation contribute to the all-occasion denominator but not to the first-to-last span distribution.

The software outputs the repeat-observed count, material-shift fraction and Wilson interval, span quantiles in original and material-scale units, and the deterministic movement and MPD sensitivity formulas. A checked-in synthetic CSV and expected JSON output provide an end-to-end example independent of the San Jacinto schema. Source code is released under the MIT License.

## 2.5 Empirically anchored SCR consequence benchmark

The original diagnostic-estimator simulation is retained in Supplementary Methods S3 because it establishes the interpretation of repeat-observation-conditioned proportions and Wilson intervals. The main downstream benchmark instead asks whether the observed within-night spatial variation can alter a fitted SCR spatial scale.

### 2.5.1 Empirical transition kernel

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

### 2.5.2 SCR simulation

We simulated multi-catch SCR data on the San Jacinto 7×7 detector array with 6.25-m spacing. The source protocol checked traps three times per night and released animals at the point of capture during each check (Chock et al. 2022). Each simulated session contained three nights. The stationary negative-control family generated all three within-night checks directly from a half-normal SCR model.

The empirical-transition family began from a baseline nightly SCR capture history. For each captured individual-night, repeat observation was imposed with the empirical probability 0.3895. Conditional on repeat observation, a material detector transition was imposed with probability 0.7196 by resampling an observed held-out displacement vector. Non-repeat nights contributed one randomly positioned check; repeat nights contributed an early and a late check. This family is therefore an empirically anchored **observation-process stress test**, not a quantitatively calibrated San Jacinto mechanism and not a correctly specified independent-check SCR generator: check-level encounter histories inherit within-night dependence because repeat checks are created conditional on a captured night. To avoid privileging FIRST by construction, we simulated two mirrored transition orientations. In POST simulations the baseline detector state occurred first and the displaced state last; in PRE simulations the displaced state occurred first and the baseline state last.

Generating sigma was fixed at 6.25, 12.5 or 25 m. The detection intercept was $g_0=0.15$. The buffered population density was increased from 20 to 60 animals ha$^{-1}$ after an effect-blind estimability run showed insufficient fitting support at the lower density; no sigma effects from the low-support run were used for inference. Each stationary and transition cell used 40 Monte Carlo replicates.

Each simulated record set was analysed three ways:
- **CHECK:** all three physical trap checks retained as separate occasions;
- **FIRST:** the three check intervals reduced to one nightly occasion, with the first observed detector retained when an individual was captured at more than one detector;
- **LAST:** the analogous nightly reduction retaining the last observed detector.

The FIRST/LAST reductions were implemented deterministically from the simulated event records, but match the corresponding conflict semantics documented for `secr::reduce.capthist` when `multi`-detector occasions are pooled.

All fits used `secr` 5.4.3 (Efford 2026), detector type `multi`, half-normal detection, conditional likelihood, $g_0\sim b$, $\sigma\sim1$, and a 100-m mask buffer.

### 2.5.3 Frozen diagnostics and interpretation

The stationary family was a mandatory implementation control: temporal representation was not considered consequential unless stationary FIRST and LAST remained approximately centred on the same generating sigma. We report median relative sigma bias, 95% interval coverage, and paired LAST/FIRST, CHECK/FIRST and CHECK/LAST sigma ratios.

A 10% relative difference was retained as the practical materiality scale used in the earlier frozen empirical SCR design. No empirical FIRST or LAST SCR sigma estimate was opened by this simulation.

## 2.6 Prospectively held-out empirical validation

### 2.6.1 Dataset

We used the public San Jacinto small-mammal dataset deposited with Chock, Shier & Grether (2022; Figshare DOI 10.6084/m9.figshare.18295520.v1). The raw capture table contained date, capture time, trapping grid, trap flag, species and unique individual identifier.

The original study used fixed 7×7 trapping grids with 6.25-m trap spacing and repeated trap checks within nights. We treated the source `date` field as the trapping-night label rather than as a literal timestamp date. A structural, effect-independent audit supported that interpretation: the raw grid × date grouping contained all three published activity bins (early, middle and late) in 250/290 groups (86.2%), whereas an alternative that moved midnight/post-midnight records to the previous calendar date produced only 142/405 complete groups (35.1%); median transformed capture times also ordered early < middle < late. Our analysis is a secondary analysis of public data and involved no new animal handling. Chock et al. (2022) reported compliance with applicable institutional animal-care guidelines.

### 2.6.2 Prospectively held-out taxa

The methodological question was first motivated by an exploratory heteromyid analysis, but those discovery species were excluded from confirmatory inference. An effect-blind support scan was then conducted for previously unopened Cricetidae. Before first-to-last outcomes were inspected, an effect lock selected two species with sufficient repeat-capture support:

- *Peromyscus maniculatus* (PEMA): 485 repeat-capture individual-nights across 8 grids and 12 trapping bouts;
- *Peromyscus eremicus* (PEER): 107 repeat-capture individual-nights across 3 grids and 10 bouts.

A third candidate cricetid lacked sufficient repeat-capture support and was excluded before outcomes were opened.

### 2.6.3 Frozen empirical endpoint and decision rule

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

## 2.7 All-occasion denominator audit

The confirmatory fraction is conditioned on repeat observation. We therefore conducted a post-result denominator audit that did not alter the frozen decision rule. For each held-out species we counted all valid individual-nights, the subset with at least two valid captures, and nights on which a $\ge 1$-spacing shift was directly observed.

We interpret

\[
\frac{\text{directly observed material-shift nights}}{\text{all valid individual-nights}}
\]

only as a lower bound. No assumption is made that single-capture nights had zero positional span.

## 2.8 Prospectively gated downstream MCP analysis

To test whether positional aliasing could be propagated empirically into a familiar downstream estimator, we pre-specified a 100% minimum convex polygon (MCP) sensitivity analysis. Eligibility required at least 10 capture nights, at least five unique FIRST flags, at least five unique LAST flags, and non-collinear FIRST and LAST geometries.

Before any MCP area was calculated, the support gate required at least 20 eligible PEMA and 15 eligible PEER individuals. The effect-blind support scan produced only 17 and 6, respectively. The downstream effect stage was therefore declared non-estimable and no MCP area effect is reported. This failed gate is retained as a transparency result and does not modify the primary positional-aliasing inference.

## 2.9 Post-stop PEMA SCR representation-stability analysis

The prospectively planned two-species SCR sigma comparison stopped before any empirical sigma was fitted because only PEMA passed the frozen species-level session-support gate. After that stop, we conducted one explicitly exploratory PEMA-only comparison to provide empirical context for the simulation result. This analysis cannot rescue or replace the stopped confirmatory programme.

We used the 19 PEMA species × grid × trapping-bout sessions that had passed the frozen effect-blind support gate, spanning five grids. FIRST and LAST capture histories contained exactly the same 525 individual × occasion observations and differed only in the retained trap location on repeat-capture nights. Each session used the fixed 7×7, 6.25-m multi-catch detector layout and a 100-m trap-buffer mask.

The pre-designated primary exploratory model was fitted in `secr` 5.4.3 with half-normal detection and conditional likelihood:

- \(g_0\sim b+\mathrm{grid}+\mathrm{bout}\);
- \(\sigma\sim 1\).

We report FIRST and LAST sigma estimates, their marginal 95% confidence intervals, and the ratio \(\sigma_{LAST}/\sigma_{FIRST}\). The existing 10% relative-change threshold is retained only as a contextual materiality benchmark; it is not an equivalence margin or a confirmatory test.

Because the same 19 sessions underlie both fits, the FIRST and LAST sigma estimates are paired. The frozen fit receipt, however, stores only marginal standard errors and not their joint covariance. We therefore did not construct a pseudo-paired interval from the two marginal confidence intervals. As a post-result uncertainty-sensitivity analysis, we applied a first-order delta method to \(\log(\sigma_{LAST}/\sigma_{FIRST})\) over assumed correlations \(\rho=0,0.25,0.5,0.75,0.9\) between the two sigma estimates. This calculation is descriptive only: it neither estimates \(\rho\) nor constitutes a formal paired confidence interval or equivalence test.

## 2.10 Post-result individual-dependence audit

The frozen confirmatory rule treated repeat-capture individual-nights as the binomial units and separately required replication across trapping grids. Because the same marked individual could contribute multiple nights, we conducted a post-result, non-rescuing dependence audit to test whether a small number of repeatedly observed individuals dominated the species-level fractions.

Within each species, identity was defined as grid × individual ID. We reported the number and size distribution of individual clusters, an equal-individual mean of individual-specific material-shift fractions, deterministic leave-one-individual fractions, and a grid-stratified cluster bootstrap. The bootstrap resampled individual clusters with replacement within each grid, retained all repeat nights from a sampled cluster, used 20,000 replicates and a fixed seed (20260930), and reported percentile 95% intervals. This audit was not part of the frozen confirmatory decision and could not rescue a failed primary result.

## 2.11 Post-result time-reversal symmetry audit

To ask whether the empirical first-to-last transitions contained a detectable arrow of time, we conducted a post-result, non-rescuing symmetry audit using the already-opened repeat-capture nights. For every changed night, the directed detector displacement vector \(v\) was paired with its reverse \(-v\) within trapping grid. We formed grid × unsigned-vector strata and calculated

\[
Q=\sum_s \frac{(n_{s,+}-n_{s,-})^2}{n_{s,+}+n_{s,-}},
\]

where \(n_{s,+}\) and \(n_{s,-}\) are the forward and reverse counts in stratum \(s\).

Because the same animal could contribute multiple nights, the randomization unit was grid × individual. In each of 500,000 Monte Carlo permutations, all changed nights from a sampled cluster had their temporal direction reversed together with probability one half. We report the upper-tail randomization probability, the mean directed displacement vector, and its magnitude relative to the RMS changed-night displacement. This exploratory audit cannot prove time-reversal symmetry and cannot rescue or replace any frozen empirical gate.

## 2.12 Post-result stationary-SCR displacement reference

We tested whether PEMA first-to-last displacement itself required an ordered within-night state shift, restricting this post-result diagnostic to the same 19 frozen sessions used for the exploratory SCR comparison (525 captured individual-nights; 218 repeat-observed).

The primary summary was per-axis RMS displacement,
\[
R_{axis}=\sqrt{\operatorname{mean}(\Delta x^2+\Delta y^2)/2},
\]
with the fraction changing by at least one 6.25-m trap spacing as a second endpoint. The stationary null used the same 7 × 7 array and `multi` observation model as the PEMA SCR fit, three independent checks, a fixed within-night activity centre and no state shift. Because the field devices were physically single-catch Sherman traps, this is a check of the fitted stationary SCR model, not a complete simulation of competition for occupied traps.

Sigma was fixed at the already-opened FIRST and LAST estimates (8.8515 and 8.5625 m) and their midpoint (8.707 m); scalar \(g_0\) values were varied without reference to displacement outcomes. Each replicate was matched to 218 repeat nights. Density only supplied enough independent individuals under the `multi` generator and was not interpreted biologically.

The diagnostic can show whether displacement magnitude exceeds the fitted stationary reference. It cannot identify handling effects, prove independence or exact reversibility, or reproduce the physical single-catch process.

As a post-result algebraic decomposition, we also separated the point mass at zero displacement from the distance scale conditional on a trap change. On the fixed detector lattice, same-trap repeats have \(R=0\), so
\[
E(R^2)=P(R>0)E(R^2\mid R>0).
\]
We therefore report the same-trap fraction and the changed-night RMS, \(\sqrt{E(R^2\mid R>0)}\), for the observed data and each supported stationary-reference cell. This decomposition introduces no new fitted model and is used only to describe how a similar marginal second moment can arise from a different transition mixture; it is not a preregistered endpoint or a causal movement model.

## 2.13 AI-assisted development and verification

OpenAI ChatGPT (GPT-5.6 Sol; accessed September–October 2026) assisted with code drafting and refactoring, statistical checks, literature discovery and manuscript editing. AI output was not treated as evidence or authorship. Claims and analyses were version-controlled and checked with frozen result receipts, tests, continuous integration, source checksums and simulation benchmarks; the authors retain responsibility for all scientific content.

# 3. Results

## 3.1 Prospectively held-out positional non-uniqueness

Both held-out Cricetidae passed the frozen positional-aliasing criterion by wide margins.

For *P. maniculatus*, 352 of 485 repeat-capture individual-nights exhibited a first-to-last shift of at least 6.25 m, corresponding to 72.6% (95% Wilson CI 68.4–76.4%). The median first-to-last span across repeat nights was 8.84 m and the 90th percentile was 25.0 m. All seven grids meeting the frozen replication support threshold exceeded the 25% grid-level material-shift threshold.

For *P. eremicus*, 74 of 107 repeat-capture nights exhibited a material shift, corresponding to 69.2% (95% Wilson CI 59.9–77.1%). The median span was 6.25 m and the 90th percentile 19.76 m. All three eligible grids exceeded the grid-level threshold.

Thus the frozen empirical programme decision for positional non-uniqueness was

\[
\texttt{authorize\_live\_trap\_positional\_aliasing\_result}.
\]

## 3.2 Frequent aliasing produced only a small PEMA sigma point contrast

The prospectively planned empirical two-species SCR programme remained stopped because PEER did not meet its session-support requirement. The subsequent PEMA-only analysis is therefore exploratory.

Across the 19 frozen eligible PEMA sessions, FIRST and LAST histories each contained 525 identical individual × occasion observations. Under the primary model, FIRST gave \(\hat\sigma=8.8515\) m (95% CI 8.0310–9.7559) and LAST gave \(\hat\sigma=8.5625\) m (7.7806–9.4229). The ratio was

\[
\hat\sigma_{LAST}/\hat\sigma_{FIRST}=0.9673,
\]

a relative change of -3.27%. This did not cross the existing 10% contextual materiality threshold.

The point estimate therefore separates the two questions motivating the framework: within-night position was frequently non-unique, yet the pooled PEMA SCR spatial scale changed little when the first rather than last nightly capture location was retained. This is not an equivalence test. Because the paired FIRST/LAST fits were not stored with their joint covariance, marginal standard errors alone cannot provide a formal paired confidence interval for the ratio. A post-result delta-method sensitivity analysis gave an approximate 95% ratio interval of 0.844–1.109 under a zero-correlation reference; the interval would lie fully inside the contextual 0.9–1.1 band only if the correlation between the two sigma estimates exceeded approximately 0.721.

The same data also reject a tempting quantitative interpretation of the raw span distribution. Among all valid PEMA individual-nights, directly observed material FIRST-to-LAST transitions occurred on 352/1,219 nights, and the RMS length of those material transitions was 17.08 m. If those vectors were treated as independent, zero-mean additive displacements applied after the FIRST state, the continuous second-moment benchmark using the FIRST estimate (sigma = 8.8515 m) would predict sigma_LAST / sigma_FIRST ≈ 1.240, or about +24.0%. The observed ratio was instead 0.967 (-3.3%). This model-dependent discrepancy is inconsistent with interpreting the observed FIRST-to-LAST vectors as an independent additive transition kernel for PEMA and reinforces that positional-span magnitude is not an empirical correction for SCR sigma.

The post-result reversal audit found no clear grid-stratified directional asymmetry. For PEMA, the cluster sign-flip randomization gave \(p=0.193\); the mean directed first-to-last vector had magnitude only 0.071 m compared with a 17.08-m RMS changed-night displacement (0.4%). For PEER, the corresponding values were \(p=0.735\), 1.68 m and 16.26 m (10.3%). These are consistency diagnostics rather than evidence that the process is exactly reversible, but the near-zero PEMA flux is concordant with the small FIRST/LAST sigma point contrast.

## 3.3 Empirical displacement magnitude was stationary-compatible, but repeat locations were more persistent

In the same 19 PEMA sessions, 218 of 525 captured individual-nights were repeat-observed. Their first-to-last per-axis RMS was 9.1231 m. Under the primary fixed-centre reference (\(\sigma=8.707\) m, \(g_0=0.15\)), the matched-repeat null median was 9.6852 m (95% interval 9.0102–10.3629 m); supported sensitivity cells likewise showed no upper-tail excess.

The empirical changed-trap fraction was 0.6972, far below the primary independent-check null (median 0.9174; 95% interval 0.8807–0.9495). Equivalently, same-trap repeats comprised 30.3% of the empirical repeat nights, compared with a primary-null median of 8.3% (95% interval 5.0–11.9%); the empirical value exceeded the 97.5th percentile in all nine \(\sigma\times g_0\) sensitivity cells.

Because the regular trap lattice makes every non-zero displacement a changed-trap event, the second moment can be decomposed exactly into the frequency of changing traps and the distance scale conditional on change. The observed changed-night RMS was 15.45 m, versus a primary-null median of 14.30 m (95% interval 13.43–15.30 m; upper-tail fraction 0.008). It exceeded the 97.5th percentile in five of nine sensitivity cells; across all nine cells, upper-tail fractions ranged from 0 to 0.104. This post-result decomposition therefore shows a redistribution of the transition distribution rather than simply a larger marginal movement scale: substantially more zero-displacement repeats, but longer displacements conditional on leaving the previous trap.

The empirical sequence therefore reached a broadly similar marginal displacement scale through a different temporal mixture. Displacement magnitude did not require an added post-capture state shift, but conditional independence within the night was also not a good description. Short-term positional persistence or other serial dependence can remain time-reversal symmetric and therefore need not create a systematic FIRST-versus-LAST sigma difference.

## 3.4 Reversal-symmetry null and ordered-state failure mode

The SCR simulations reproduced the distinction predicted by the time-reversal argument.

When all within-night checks sampled one stationary SCR state, FIRST and LAST did not separate systematically. Across generating \(\sigma=6.25\), 12.5 and 25 m, median LAST/FIRST sigma ratios were 1.007, 0.966 and 1.025, and the maximum absolute median relative bias across the three temporal representations was 3.95%.

We then broke time-reversal symmetry by imposing an ordered within-night state transition using the observed held-out displacement-vector distribution and repeat frequency. With the baseline state observed before the transition (POST), median LAST/FIRST sigma ratios were 1.347, 1.154 and 1.124 for generating \(\sigma=6.25\), 12.5 and 25 m. Reversing the temporal ordering (PRE) preserved the same displacement magnitudes but reversed the direction of the representation effect: corresponding ratios were 0.766, 0.856 and 0.894.

The mirror experiment is important because all span-only aliasing summaries are invariant to reversing the temporal labels. The downstream direction changed while the positional-span distribution did not, demonstrating that span magnitude alone cannot identify which representation, if either, is closer to a baseline spatial scale.

CHECK-level fits are not used to isolate state mixing because the stress generator also induces within-night encounter dependence. A separate sequential-check robustness route initially missed its 10% negative-control gate at 10.22% (by 0.22 percentage points); an independently seeded 96-replicate zero-shift-only rerun passed (maximum median bias 5.55%; LAST/FIRST ratios 0.9968, 1.0031 and 0.9992). The already-opened non-zero-shift cells remain non-promoted; full details are in Supplementary Methods S9.3.1.

## 3.5 Denominator context

Repeat-observed nights represented a substantial but incomplete subset of all valid individual-nights.

For *P. maniculatus*, 485 of 1,219 valid individual-nights were repeat-observed (39.8%). A material \(\ge6.25\)-m shift was directly observed on 352 nights, corresponding to at least 28.9% of all valid individual-nights.

For *P. eremicus*, 107 of 301 valid individual-nights were repeat-observed (35.5%). Seventy-four nights showed a material shift, corresponding to an all-night directly observed lower bound of 24.6%.

These values do not estimate latent aliasing on single-capture nights. They show only that directly observed positional non-uniqueness was not confined to a vanishingly small observation class.

## 3.6 Downstream MCP support gate

The prospectively gated MCP analysis did not reach its effect stage. Seventeen PEMA and six PEER individuals satisfied the frozen high-information eligibility rules, below the required thresholds of 20 and 15. No MCP areas, area ratios or inferential comparisons were authorized.

## 3.7 Individual-cluster sensitivity

The post-result dependence audit did not indicate that the confirmatory positional-aliasing fractions were driven by a few repeatedly sampled individuals. PEMA contained 170 grid-specific individual clusters; its equal-individual material-shift fraction was 71.1%, the grid-stratified cluster-bootstrap 95% interval was 68.0–77.0%, and the maximum single-individual contribution was 2.9% of repeat nights. PEER contained 34 clusters; its equal-individual fraction was 65.9%, the bootstrap interval was 61.3–78.9%, and the maximum individual contribution was 14.0%. These are robustness summaries only; the frozen Wilson/grid rule remains the confirmatory empirical analysis.

# 4. Discussion

## 4.1 Positional aliasing is a warning condition, not a bias estimate

The held-out validation showed frequent materially different detector states within a night, yet the PEMA sigma point estimate changed only -3.3% between FIRST and LAST. More strikingly, a naive independent-additive use of the observed transition energy predicted about +24% scale inflation, whereas the observed point contrast was negative and small. That discrepancy is the practical counterexample: large within-occasion displacement can be real and common without supplying a usable correction for downstream spatial scale. The -3.3% contrast is not a formal equivalence result: without the paired fit covariance, its uncertainty remains correlation-dependent. The stationary diagnostic further showed that the displacement RMS itself was not unusually large; instead, PEMA changed traps less often than independent stationary checks predicted.

The data separate spatial span, short-term serial dependence and directional temporal asymmetry. Span magnitude is not sufficient to diagnose representation sensitivity. A marginal spatial scale can be approximately right for the wrong temporal process, and a span-based correction can even point in the wrong direction. The aliasing screen identifies positional non-uniqueness; it does not estimate downstream bias.

## 4.2 Serial dependence need not imply directional representation instability

If the within-occasion data law is unchanged by reversing check order, FIRST and LAST are distributionally equivalent despite differing in a realized night. Full exchangeability is sufficient but unnecessary; reversible serial dependence also qualifies.

PEMA fits this distinction at the level of point estimates. Its displacement RMS was compatible with the fitted static kernel, but its changed-trap fraction was much lower than the independent-check expectation. The compensating mixture—more same-trap recurrence with a somewhat longer conditional non-zero tail—shows why agreement in a marginal second moment does not validate the assumed transition process. The field protocol released captured animals at the detector after each check (Chock et al. 2022), providing a biologically plausible source of short-term trap-centred persistence or trap response. However, release at a detector does not by itself identify an irreversible process: history dependence can remain time-reversal symmetric. Consistent with that caution, the simple release-centred transient-state calibration failed its independent observation-process gate and is not treated as the empirical mechanism. Serial dependence itself is established territory (Stevenson et al. 2022; van Helsdingen & Jones-Todd 2026); our distinction is between dependence that may remain reversal-symmetric and ordered asymmetry that changes a directional FIRST-versus-LAST estimand.

The directional audit supports that boundary: PEMA's mean first-to-last vector was only 0.071 m versus a 17.08-m RMS changed-night displacement, with no clear grid-stratified reversal asymmetry. This does not prove reversibility, but it argues against treating the observed vectors as a one-way additive post-capture shift.

## 4.3 An arrow of time breaks directional representation equivalence

The failure mode is not aggregation by itself but temporal asymmetry that makes later observations sample a different state distribution. In the ordered-transition simulations, the empirical displacement kernel was large relative to the generating spatial scale, and FIRST and LAST selected different mixtures of baseline and transitioned states.

The time-reversal result makes this mechanism especially transparent. PRE and POST simulations retained the same span distribution, material-shift frequency and displacement magnitudes. Only temporal ordering changed, yet the FIRST/LAST sigma contrast reversed direction. Therefore neither the sign nor the existence of a downstream representation effect can be inferred from span summaries alone.

The natural scale of the risk is the size and frequency of ordered state changes relative to the downstream spatial kernel. The existing second-moment approximation remains useful as a stress-test scale, but it should be interpreted as a model-dependent consequence benchmark rather than as a correction for the San Jacinto data.

We also attempted to calibrate a simple release-centred transient-state mechanism directly to the empirical observation process before fitting any downstream sigma. From 204 candidate cells, the 12 closest were re-simulated on independent validation seeds and required to match repeat frequency, material-shift frequency, median all-repeat span and median changed-night span simultaneously. Zero of 12 passed all four criteria, yielding the frozen decision `stop_v3_no_observation_process_match`. This negative result is important: the ordered-state simulation demonstrates a failure mode, but the available San Jacinto summaries do not support interpreting that simple transient-state generator as the empirical mechanism.

## 4.4 Why “use every trap check as an occasion” is sometimes right and sometimes incomplete

When the check-level process is approximately symmetric under time reversal around a static activity centre, retaining every check is the cleanest way to avoid discarding detections, provided effort and detector use are represented correctly. In that setting coarsening mainly loses information.

The answer changes when detections are temporally dependent because the latent spatial state itself evolves. Treating every check as an occasion retains the observations but does not make a static-centre SCR model correct. Continuous-time SECR already addresses information loss and subjective occasion definition (Borchers et al. 2014), and recent continuous-time SCR work explicitly models movement between detections when conditional independence around one activity centre is inadequate (Panchaud et al. 2026). Our contribution is therefore not a replacement for those models. It is a pre-analysis diagnostic for deciding whether a coarse representation appears benign, whether a simple representation-sensitivity analysis is sufficient, or whether a dynamic model is warranted.

## 4.5 Repeat-observation conditioning remains a separate sampling issue

The repeat-night material-shift fraction is conditional on being observed more than once. It estimates an all-occasion frequency only if repeat observation is non-informative with respect to the latent spatial process. The all-night directly observed fractions avoid pretending that single-capture nights are zero-shift, but they are lower bounds, not corrected prevalence estimates.

This sampling limitation is conceptually separate from representation stability. A repeat-conditioned aliasing fraction may be biased upward or downward while a downstream parameter remains stable, and conversely a modest aliasing fraction can be consequential if the displaced state is strongly ordered and large relative to the model's spatial scale.

## 4.6 The empirical stopping rules remain informative

Two prospectively planned downstream routes stopped for insufficient support. The MCP analysis failed its individual-level gate, and the two-species empirical SCR sigma programme failed because PEER had only two eligible sessions. We retain those stops. The PEMA-only sigma comparison is useful precisely because it is labelled as post-stop exploratory rather than presented as rescued confirmation.

The sequential robustness and observation-process calibration both retain their original stopping rules. The first sequential null missed its 10% gate narrowly before a larger zero-shift-only rerun passed, but already-opened non-zero cells remain non-promoted. Separately, none of 12 independently validated release-centred candidates reproduced all four empirical observation targets, and no sigma model was fitted in that calibration. These stops prevent a controlled failure mode from being relabelled as an empirically matched handling mechanism.

## 4.7 Generality and recommended workflow

The framework is not restricted to live trapping. Any repeated-location system can contain several valid states within one nominal analytical occasion: acoustic localization, camera detections, visual resightings, telemetry fixes, nest attendance, repeated plant or colony mapping, or other observation processes in which data are coarsened before analysis.

A practical workflow follows directly from the results:

1. define the ecological occasion and material spatial scale before inspecting the effect;
2. quantify within-occasion positional non-uniqueness, keeping repeat-conditioned estimates separate from all-occasion lower bounds;
3. compare the observed within-occasion transition pattern with a static-kernel reference before interpreting displacement as state change, and ask whether any remaining serial dependence is plausibly symmetric under time reversal;
4. if positional aliasing is material, re-run the intended downstream analysis under defensible temporal representations;
5. treat stable downstream estimates as evidence that the coarsening choice is not practically important for that estimand, and unstable estimates as a trigger for finer temporal or state modelling.

The central methodological point is deliberately narrower than “never aggregate”. The useful question is: **when does temporal representation change the spatial quantity we intend to infer?** The San Jacinto point estimates show that strong within-night dependence can coexist with a small FIRST/LAST spatial-scale contrast, while the ordered-state simulations show how directional asymmetry can make the same representation choice consequential. The downstream empirical comparison is restricted to PEMA within this single repeated-check trapping programme (19 sessions across five grids); its generality across taxa, detector systems and study designs remains untested, even though the positional-aliasing screen itself was prospectively replicated in both PEMA and PEER.

# 5. Data and code availability

The empirical source data are publicly available in Figshare (DOI 10.6084/m9.figshare.18295520.v1) with Chock et al. (2022). The analysis verifies the source file checksum before use.

The generic diagnostic, sensitivity-bound implementation, corrected simulation benchmark, empirical validation pipeline, tests and figure-generation scripts are released under the MIT License in the manuscript review repository. A versioned archival release and persistent repository identifier will be added before final submission.

# 6. Ethics statement

This study is a secondary analysis of previously collected public data and involved no new animal capture or handling. Chock et al. (2022) report compliance with applicable institutional guidelines for animal care and use in the original field study.

# Figure captions

**Figure 1. Temporal positional aliasing and deterministic sensitivity bounds.** A single ecological occasion can contain more than one valid observed spatial state for the same marked individual. For occasions $t$ and $u$, $F$ and $L$ denote first and last observed positions and $\delta$ the within-occasion positional span. The difference between FIRST→FIRST and LAST→LAST inter-occasion movement estimates is bounded by $\delta_t+\delta_u$; population MPD sensitivity is bounded by twice mean within-occasion span.

**Figure 2. Positional non-uniqueness and downstream representation stability are distinct.** A: stationary time-reversal-symmetric negative controls show median relative sigma bias for CHECK, FIRST and LAST encodings at generating sigma values of 6.25, 12.5 and 25 m; dashed lines denote ±10%. B: paired LAST/FIRST sigma ratios in a controlled ordered state-transition stress test using the empirical displacement-vector kernel in mirrored POST and PRE orientations; horizontal lines denote invariance and the ±10% band. C: post-stop exploratory PEMA FIRST and LAST sigma estimates with marginal 95% confidence intervals; the dotted line is the independent-additive second-moment benchmark (approximately +24.0%), whereas the observed LAST/FIRST ratio was 0.967 (-3.3%). D: observed PEMA per-axis RMS displacement and changed-trap fraction relative to the corresponding primary stationary-null medians; horizontal segments are null 95% intervals after scaling by each null median. RMS displacement is stationary-compatible, whereas trap changes are substantially less frequent than under independent stationary checks.

**Figure 3. Prospectively held-out positional-aliasing validation.** Species-level material-shift fractions and 95% Wilson intervals for PEMA and PEER; small points show eligible trapping-grid fractions. The vertical dashed line is the frozen 25% materiality threshold.

**Figure 4. Denominator context and positional-span magnitude.** A: fraction of all valid individual-nights that were repeat-observed and the conservative all-night fraction with directly observed $\ge 1$-spacing shifts. B: median and 90th-percentile first-to-last spans in trap-spacing units.

# References

Borchers DL, Distiller G, Foster RJ, Harmsen BJ, Milazzo L. 2014. Continuous-time spatially explicit capture–recapture models, with an application to a jaguar camera-trap survey. *Methods in Ecology and Evolution* 5:656–665. https://doi.org/10.1111/2041-210X.12196.

Chock RY, Shier DM, Grether GF. 2022. Niche partitioning in an assemblage of granivorous rodents, and the challenge of community-level conservation. *Oecologia* 198:553–565. https://doi.org/10.1007/s00442-021-05104-5.

Efford MG, Borchers DL, Mowat G. 2013. Varying effort in capture–recapture studies. *Methods in Ecology and Evolution* 4:629–636. https://doi.org/10.1111/2041-210X.12049.

Efford MG, Boulanger J. 2019. Fast evaluation of study designs for spatially explicit capture–recapture. *Methods in Ecology and Evolution* 10:1529–1535. https://doi.org/10.1111/2041-210X.13239.

Efford MG, Dawson DK, Borchers DL. 2009. Population density estimated from locations of individuals on a passive detector array. *Ecology* 90:2676–2682. https://doi.org/10.1890/08-1735.1.

Efford MG. 2026. *secr: Spatially explicit capture-recapture models*. R package version 5.4.3. DOI 10.32614/CRAN.package.secr.

Milleret C, Dupont P, Brøseth H, Kindberg J, Royle JA, Bischof R. 2018. Using partial aggregation in spatial capture recapture. *Methods in Ecology and Evolution* 9:1896–1907. https://doi.org/10.1111/2041-210X.13030.

Nichols JD. 2016. And the first one now will later be last: time-reversal in Cormack–Jolly–Seber models. *Statistical Science* 31:175–190. https://doi.org/10.1214/16-STS546.

Panchaud C, King R, Borchers D, Worthington H. 2026. Incorporating animal movement into continuous-time spatial capture-recapture models. arXiv:2608.17046.

van Helsdingen ABM, Jones-Todd CM. 2026. A spatial capture–recapture model with Hawkes-inspired detection rates to account for animal movement. *Journal of Agricultural, Biological and Environmental Statistics*. https://doi.org/10.1007/s13253-025-00724-3.

Stevenson BC, Fewster RM, Sharma K. 2022. Spatial correlation structures for detections of individuals in spatial capture–recapture models. *Biometrics* 78:963–973. https://doi.org/10.1111/biom.13502.

Romairone J, Jiménez J, Luque-Larena JJ, Mougeot F. 2018. Spatial capture-recapture design and modelling for the study of small mammals. *PLoS ONE* 13:e0198766. https://doi.org/10.1371/journal.pone.0198766.
