# Supplementary Methods — temporal positional aliasing v0.3

Date: 2026-10-03

## S1. Deterministic sensitivity bounds

### S1.1 Inter-occasion movement

Let $F_t$ and $L_t$ be two valid within-occasion positions for an individual in occasion $t$, and define $\delta_t=d(F_t,L_t)$. For occasions $t$ and $u$,

\[
d(F_t,F_u)
\le d(F_t,L_t)+d(L_t,L_u)+d(L_u,F_u)
=\delta_t+d(L_t,L_u)+\delta_u.
\]

Therefore

\[
d(F_t,F_u)-d(L_t,L_u)\le \delta_t+\delta_u.
\]

Exchanging FIRST and LAST gives the reverse inequality, so

\[
|d(F_t,F_u)-d(L_t,L_u)|\le \delta_t+\delta_u.
\]

The bound is sharp in a metric space. On a line, choose (F_t=0), (L_t=1), (L_u=9), (F_u=10). The FIRST-based distance is 10, the LAST-based distance is 8, and $\delta_t+\delta_u=2$.

### S1.2 Population mean pairwise distance

For $n$ individuals represented by paired FIRST and LAST positions,

\[
MPD(F)=\frac{2}{n(n-1)}\sum_{i<j} d(F_i,F_j)
\]

and $MPD(L)$ analogously. For every pair,

\[
|d(F_i,F_j)-d(L_i,L_j)|\le \delta_i+\delta_j.
\]

Summing over unordered pairs, each $\delta_i$ appears $n-1$ times. Hence

\[
|MPD(F)-MPD(L)|
\le
\frac{2}{n(n-1)}(n-1)\sum_i \delta_i
=
2\overline{\delta}.
\]

For a standardized MPD score $z=(MPD-\mu_n)/\sigma_n$, when FIRST and LAST use the same $n$ and the same null moments,

\[
|z_F-z_L|
=
\frac{|MPD(F)-MPD(L)|}{\sigma_n}
\le
\frac{2\overline{\delta}}{\sigma_n}.
\]

The implementation is verified by equality cases and random Euclidean tests.

## S1.3 Time-reversal symmetry and span non-identifiability

Let an occasion contain ordered detector outcomes

\[
Y=(Y_1,\ldots,Y_K),
\]

where zero denotes no detection. Let \(F(Y)\) and \(L(Y)\) be the first and last non-zero detector states, and let

\[
R(Y)=(Y_K,\ldots,Y_1)
\]

denote time reversal.

A transparent process-level sufficient condition for FIRST/LAST equivalence is

\[
Y\overset{d}=R(Y)
\]

conditional on the latent state and observation design relevant to the downstream model. Full temporal exchangeability is also sufficient, but is stronger than the reversal condition. Reversal symmetry itself is not logically necessary: FIRST and LAST can have equal marginals under some non-reversible processes. Independent identically distributed checks around a fixed activity centre are one special case; a stationary reversible process may also satisfy the reversal condition despite serial dependence.

Because reversal exchanges the representative rules,

\[
F\{R(Y)\}=L(Y),\qquad L\{R(Y)\}=F(Y),
\]

and therefore

\[
F(Y)\overset{d}=L(Y).
\]

For a full dataset \(\mathcal Y\), if the joint law is invariant under reversing every within-occasion sequence, then any downstream scalar functional satisfies

\[
T_F(\mathcal Y)\overset{d}=T_L(\mathcal Y).
\]

The directed contrast

\[
D(\mathcal Y)=T_L(\mathcal Y)-T_F(\mathcal Y)
\]

obeys

\[
D(R\mathcal Y)=-D(\mathcal Y),
\]

so under reversal symmetry \(D\overset d=-D\). Its distribution is symmetric about zero, and its expectation is zero when the expectation exists.

The same transformation gives the identification limit for span-only diagnostics. Because

\[
d\{F(RY),L(RY)\}=d\{F(Y),L(Y)\},
\]

any statistic using only unordered within-occasion spans is invariant to time reversal, whereas a directed FIRST-versus-LAST contrast changes sign. Two processes related only by reversal can therefore have identical span distributions and opposite directed downstream effects.

No span-only statistic can identify the sign of a representation effect without an additional assumption about temporal ordering or state dynamics. This is why the positional-non-uniqueness screen and downstream stability analysis are separate stages.

## S1.4 Repeated exposure, detection-kernel closure and detector effort

The time-reversal result concerns which observed detector location is retained when several valid locations occur within one nominal occasion. A separate algebraic issue arises when repeated exposures are pooled into an at-least-one-detection event.

Write

\[
h(d;\sigma)=\exp\{-d^2/(2\sigma^2)\}.
\]

For a one-check probability half-normal detector,

\[
p(d)=g_0 h(d;\sigma).
\]

If \(K\) independent checks at the same detector are reduced to a binary at-least-one-detection event, then

\[
p_K(d)=1-\{1-g_0h(d;\sigma)\}^K.
\]

For \(K>1\) and \(0<g_0<1\), this pooled curve is not obtained merely by replacing \(g_0\) with another probability-half-normal intercept while leaving the rest of the one-check formulation implicit. By contrast, for a hazard half-normal representation,

\[
\lambda(d)=\lambda_0h(d;\sigma),\qquad
p(d)=1-\exp\{-\lambda(d)\},
\]

independent exposure adds hazards, giving

\[
p_K(d)=1-\exp\{-K\lambda_0h(d;\sigma)\}.
\]

This algebraic distinction should **not** be read as a claim that the current `secr` implementation mishandles pooled effort. In `secr`, numeric detector `usage` is interpreted as effort and is incorporated as a known linear coefficient on the hazard scale (Efford et al. 2013); when occasions are pooled by `reduce.capthist`, detector usage is summed across the contributing occasions. Thus an analysis that preserves pooled usage does not need to pretend that \(K\) physical checks were a single unit-effort Bernoulli exposure.

The practical implication for this paper is narrower. Exposure accounting and location/state representation are different problems. Correctly summed usage can preserve the amount of detector effort, but it cannot resolve a `multi`-detector conflict when the same animal occupies different detector locations within the pooled occasion, and it cannot make a static-state SCR model correct if the latent spatial state itself changes through time. The FIRST/LAST and time-reversal results concern these latter problems.

Outside `secr`, or whenever repeated exposure is pooled while the corresponding effort information is discarded, the non-closure of a probability-scale detection curve can itself change the effective observation model. We therefore retain the algebra as a caution about effort-preserving aggregation, not as an additional claim that probability half-normal SCR is intrinsically unsafe to aggregate.
## S2. Generic diagnostic algorithm

Input observations require:
- individual identifier;
- ecological occasion identifier;
- sortable within-occasion time;
- spatial coordinates;
- a material spatial scale $s>0$.

For each individual-occasion:
1. discard rows lacking required structural fields;
2. order valid rows by time with source-row order as deterministic tie-breaker;
3. if only one valid observation remains, retain the occasion in the all-occasion denominator but mark the within-occasion span as unresolved;
4. if at least two observations remain, retain first and last locations and calculate $\delta=d(F,L)$;
5. classify a material shift when $\delta\ge s$.

Across repeat-observed occasions, calculate:
- material-shift count and fraction;
- two-sided 95% Wilson interval;
- median, 75th and 90th percentile, and maximum span;
- span divided by $s$.

Across all valid occasions, calculate the fraction with a **directly observed** material shift. This is a lower bound because unresolved single-observation occasions cannot contribute to the numerator.

## S3. Diagnostic-estimator simulation benchmark (supplementary)

### S3.1 Parameter grid

The benchmark crosses:
- $N\in\{100,500\}$;
- displacement component SD / material scale $\in\{0.25,0.5,1,2\}$;
- baseline repeat-observation probability $q\in\{0.25,0.5,0.75\}$;
- repeat-observation dependence $\beta\in\{-1,0,+1\}$.

This yields 72 parameter cells. Each cell uses 400 replicates.

### S3.2 Latent span

For each occasion, independent Gaussian $x$ and $y$ displacement components generate a latent Euclidean span $\delta$. The material scale is one simulation unit, so the latent material-shift indicator is $I(\delta\ge1)$.

### S3.3 Repeat-observation mechanism

For normalized span $r=\delta/s$,

\[
p_{\mathrm{repeat}}
=
\operatorname{logit}^{-1}
\left[
\operatorname{logit}(q)+\beta(r-1)
\right].
\]

Thus:
- $\beta=0$: non-informative repeat observation;
- $\beta>0$: span-enriched repeat observation;
- $\beta<0$: span-depleted repeat observation.

### S3.4 Corrected benchmark targets and diagnostics

For Gaussian displacement components with common SD $\sigma$, radial span follows a Rayleigh distribution. With material scale $s=1$, the generating material-shift probability is

\[
p_* = P(\delta\ge1)=\exp\left[-\frac{1}{2\sigma^2}\right].
\]

For each replicate, v2 distinguishes:
- analytic generating probability $p_*$;
- realized finite-sample all-occasion material-shift fraction;
- repeat-conditioned material-shift fraction;
- conditional bias relative to $p_*$;
- Wilson 95% coverage of $p_*$;
- directly observed material shifts / all occasions;
- whether that directly observed fraction exceeds the realized all-occasion fraction.

The directly observed fraction is a deterministic lower bound on the realized finite dataset; it is not treated as a confidence bound on $p_*$.

Corrected benchmark summary:
- non-informative mean absolute bias vs $p_*$: 0.001756;
- non-informative mean Wilson coverage of $p_*$: 0.9521;
- non-informative cell coverage range: 0.860–0.995;
- span-enriched mean bias vs $p_*$: +0.05075;
- span-depleted mean bias vs $p_*$: -0.07988;
- realized lower-bound violations: 0.

The lowest Wilson coverage occurred in an ultra-rare-event cell and is retained as a finite-sample/discreteness limitation rather than hidden by the mean coverage summary.

## S4. Empirical source and prospective holdout

### S4.1 Source

The empirical source is the public Figshare dataset associated with Chock, Shier & Grether (2022), DOI 10.6084/m9.figshare.18295520.v1.

The capture file checksum frozen for the analysis is:

`ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301`.

The trapping design uses fixed 7×7 grids with 6.25-m spacing and three repeated checks per night.

We audited the temporal meaning of the source `date` field without inspecting ecological effects. Under the raw grid × date grouping, 250/290 groups (86.2%) contained captures from all three source activity bins (early, middle and late). Under an alternative interpretation in which midnight/post-midnight records were reassigned to the preceding literal calendar date, only 142/405 groups (35.1%) contained all three bins. Median transformed capture times also followed the expected nocturnal sequence (early 22.37 h, middle 25.40 h, late 28.25 h). We therefore treated the source date as the trapping-night label.

### S4.2 Discovery versus confirmatory taxa

A separate exploratory heteromyid analysis motivated the positional-aliasing question but does not contribute to the confirmatory result.

The confirmatory taxa were selected from an effect-blind support scan:
- PEMA — *Peromyscus maniculatus*;
- PEER — *P. eremicus*.

Before first-to-last outcomes were inspected, the frozen support counts were:
- PEMA: 485 repeat-capture individual-nights across 8 grids and 12 bouts;
- PEER: 107 repeat-capture individual-nights across 3 grids and 10 bouts.

### S4.3 Frozen materiality rule

The material scale was one adjacent-trap spacing, 6.25 m.

A species passed only when:
1. material-shift fraction (>0.25);
2. lower 95% Wilson bound (>0.25);
3. at least two grids with at least 20 repeat-capture nights each independently had shift fraction (>0.25).

Both species were required to pass.

## S5. Held-out confirmatory result

PEMA:
- 485 repeat-capture nights;
- 352 one-spacing-or-greater shifts;
- fraction 0.7258;
- 95% Wilson interval 0.6844–0.7636;
- median span 8.84 m;
- 90th percentile 25.0 m;
- 7/7 eligible grids passed.

PEER:
- 107 repeat-capture nights;
- 74 one-spacing-or-greater shifts;
- fraction 0.6916;
- 95% Wilson interval 0.5987–0.7712;
- median span 6.25 m;
- 90th percentile 19.76 m;
- 3/3 eligible grids passed.

Frozen decision:

`authorize_live_trap_positional_aliasing_result`.

## S6. All-occasion denominator audit

PEMA:
- 1,219 all valid individual-nights;
- 485 repeat-observed nights (39.8%);
- 352 directly observed material-shift nights;
- all-night directly observed lower bound: 28.9%.

PEER:
- 301 valid individual-nights;
- 107 repeat-observed nights (35.5%);
- 74 directly observed material-shift nights;
- all-night directly observed lower bound: 24.6%.

These lower bounds make no claim about unresolved single-capture nights.

## S7. Prospectively gated downstream MCP test

A downstream minimum convex polygon analysis was specified before MCP effects were inspected.

Individual eligibility required:
- at least 10 capture nights;
- at least 5 unique FIRST flags;
- at least 5 unique LAST flags;
- non-collinear FIRST geometry;
- non-collinear LAST geometry.

Programme support thresholds required:
- at least 20 eligible PEMA individuals;
- at least 15 eligible PEER individuals.

Effect-blind support counts were:
- PEMA: 17;
- PEER: 6.

The frozen decision was:

`stop_downstream_home_range_not_estimable`.

Two effect workflows were triggered prematurely while the support run was still queued. Both stopped inside the analysis code at the frozen support gate before MCP area effects were calculated or persisted.

## S8. Post-result individual-cluster sensitivity

This non-rescuing audit assessed whether repeat nights from a small number of marked individuals dominated the confirmatory species fractions.

PEMA:
- 170 grid-specific individual clusters;
- maximum single-individual contribution: 2.9% of repeat nights;
- equal-individual shift fraction: 0.711;
- grid-stratified individual-cluster bootstrap 95% interval: 0.680–0.770;
- minimum leave-one-individual raw fraction: 0.719.

PEER:
- 34 individual clusters;
- maximum single-individual contribution: 14.0%;
- equal-individual shift fraction: 0.659;
- grid-stratified cluster-bootstrap 95% interval: 0.613–0.789;
- minimum leave-one-individual raw fraction: 0.676.

The bootstrap used 20,000 replicates and seed 20260930. This post-result sensitivity does not replace or alter the prospectively frozen Wilson/grid replication criterion.

## S8.1 Post-result time-reversal symmetry audit

A second non-rescuing audit asked whether changed repeat nights contained a detectable arrow of time.

For each changed night, the directed first-to-last displacement vector \(v\) was paired with its reverse \(-v\) within trapping grid. We formed grid × unsigned-vector strata and used the statistic

\[
Q=\sum_s\frac{(n_{s,+}-n_{s,-})^2}{n_{s,+}+n_{s,-}}.
\]

To preserve dependence among repeated nights from the same marked animal, the randomization unit was grid × individual: in each of 500,000 Monte Carlo permutations, all changed nights from a cluster had their temporal direction reversed together with probability one half.

PEMA:
- changed nights: 352;
- changed grid-specific individual clusters: 143;
- grid × unsigned-vector strata: 150;
- cluster sign-flip \(p=0.1932\);
- mean directed vector: (0.000, -0.071) m;
- directed-vector magnitude: 0.071 m;
- RMS changed-night displacement: 17.08 m;
- mean-vector / RMS ratio: 0.0042.

PEER:
- changed nights: 74;
- changed clusters: 27;
- strata: 40;
- cluster sign-flip \(p=0.7348\);
- mean directed vector: (-1.605, 0.507) m;
- directed-vector magnitude: 1.68 m;
- RMS changed-night displacement: 16.26 m;
- mean-vector / RMS ratio: 0.1035.

These are exploratory consistency diagnostics. Failure to reject does not prove time-reversal symmetry, especially with sparse vector strata. The very small PEMA mean directed vector is nevertheless consistent with the empirical finding that large first-to-last displacement magnitude did not translate into a material FIRST/LAST sigma contrast.

## S9. Empirically anchored SCR downstream-consequence benchmark

### S9.1 Empirical observation-process kernel

The main-text downstream benchmark uses only observation-process quantities that had already been opened in the held-out analysis. Across PEMA and PEER there were 1,520 valid captured individual-nights, of which 592 were repeat-observed. Among repeat nights, 426 had a FIRST-to-LAST displacement of at least one 6.25-m trap spacing.

Thus:
- repeat-observation probability = 592/1,520 = 0.3895;
- material-change probability conditional on repeat observation = 426/592 = 0.7196;
- directly observed material-transition probability = 426/1,520 = 0.2803.

The 426 material transitions retained their observed two-dimensional detector-to-detector displacement vectors. The pooled median transition length was 12.5 m, the 90th percentile was 25.77 m, and the RMS length was 16.94 m. The mean displacement vector had magnitude only about 0.28 m, small relative to the RMS scale.

For a zero-mean isotropic transition vector $H$ with length $R$ that occurs with probability $q$, the continuous dense-detector second-moment approximation is

\[
\frac{\sigma_{\mathrm{eff}}}{\sigma}
\approx
\sqrt{1+\frac{qE[R^2]}{2\sigma^2}}.
\]

For the empirical transition kernel this gives predicted scale inflation of approximately 42.45%, 12.13% and 3.17% for baseline $\sigma=6.25$, 12.5 and 25 m. Solving for 10% inflation gives a benchmark boundary near $\sigma=13.84$ m. This is an analytic sensitivity benchmark, not an empirical estimate of SCR sigma.

### S9.2 Generative SCR simulation

The simulation used `secr` 5.4.3 (Efford 2026) with:
- 7×7 multi-catch detector grid;
- 6.25-m spacing;
- three trap checks per night;
- three nights;
- half-normal generating and fitted detection function;
- $g_0=0.15$;
- conditional likelihood;
- fitted model $g_0\sim b$, $\sigma\sim1$;
- 100-m buffer;
- generating $\sigma\in\{6.25,12.5,25\}$ m.

An initial effect-blind estimability check at 20 animals ha$^{-1}$ yielded insufficient fitting support. Before interpreting downstream sigma effects, density alone was increased to 60 animals ha$^{-1}$. The spatial kernel, empirical transition probabilities, transition vectors, sigma grid, fitting model and materiality threshold were not selected from the resulting sigma effects.

The stationary-negative-control family generated all nine check-level occasions directly from a static SCR process.

The empirical-transition family first generated one baseline SCR detector state per captured individual-night. A night was expanded to repeated observations with probability 0.3895; conditional on repeat observation, a material detector transition was introduced with probability 0.7196 by resampling an observed held-out displacement vector. Edge-incompatible vectors were resampled, with a deterministic nearest-distance fallback after repeated failures. Because this expansion occurs conditional on a baseline captured night, the resulting CHECK histories are intentionally not independent check-level draws from the fitted static SCR model. They reproduce empirical repeat frequency and transition scale as an observation-process stress test, and therefore combine state mixing with within-night encounter dependence.

Two mirrored orientations were used:
- **POST:** baseline detector state first, transitioned state last;
- **PRE:** transitioned state first, baseline detector state last.

This mirror is essential: it prevents the simulation from defining FIRST as correct by construction.

For every generated record set, the same observations were represented as:
- **CHECK:** each physical check retained as a separate occasion;
- **FIRST:** one state per night using the first observed detector;
- **LAST:** one state per night using the last observed detector.

Each cell used 40 Monte Carlo replicates.

### S9.3 Downstream results

The stationary controls passed. Across generating sigma values and temporal representations, the largest absolute median relative bias was 3.95%. Paired median LAST/FIRST ratios were:
- 1.007 at $\sigma=6.25$ m;
- 0.966 at $\sigma=12.5$ m;
- 1.025 at $\sigma=25$ m.

The empirical-transition family produced material rule sensitivity.

POST median LAST/FIRST ratios:
- 1.347 at $\sigma=6.25$ m;
- 1.154 at $\sigma=12.5$ m;
- 1.124 at $\sigma=25$ m.

PRE median LAST/FIRST ratios:
- 0.766 at $\sigma=6.25$ m;
- 0.856 at $\sigma=12.5$ m;
- 0.894 at $\sigma=25$ m.

At $\sigma=6.25$ m, POST median relative biases were -0.6% for FIRST and +38.8% for LAST; under PRE they were +35.0% for FIRST and -0.7% for LAST. At $\sigma=12.5$ m, POST biases were -1.7% and +15.1%, and PRE biases were +16.6% and approximately 0.0%.

CHECK retained all injected detections but did not consistently recover baseline sigma under the empirical-transition stress process. Because repeat checks are generated conditional on a captured night, this deviation cannot be decomposed uniquely into a state-mixture component and a within-night encounter-dependence component. It is used only to show that finer occasions are not automatically sufficient when the observation process departs from a stationary, conditionally independent check-level model.

### S9.3.1 Sequential-check null robustness diagnostic

A separate robustness generator simulated each physical check directly through `secr::sim.capthist` around a persistent within-night state centre. Before any state-shift result could be interpreted, a frozen zero-shift gate required the maximum absolute median sigma bias across CHECK, FIRST and LAST to be below 10%.

In the first 24-replicate run, the gate failed narrowly: the maximum absolute median bias was 10.22%. The non-zero-shift cells from that run were therefore not promoted.

To determine whether the null failure itself was reproducible, we then ran an independent diagnostic restricted to the zero-shift condition only, using seed 20261005 and 96 replicates per generating sigma. No non-zero-shift cell was re-run or used in this diagnostic. The second run gave:

- maximum absolute median relative bias: **5.55%**;
- LAST/FIRST = **0.9968** at generating sigma 6.25 m;
- LAST/FIRST = **1.0031** at 12.5 m;
- LAST/FIRST = **0.9992** at 25 m;
- maximum absolute LAST/FIRST deviation from one: **0.32%**.

Thus the original 10.22% null excursion was not reproduced at higher Monte Carlo replication, and the sequential static generator itself satisfies the frozen null criterion in the independent diagnostic. This does not retroactively authorize the already-opened non-zero-shift cells from the failed-gate run; they remain non-promoted.

### S9.3.2 Observation-process calibration stop

A separate v3 calibration asked whether a simple release-centred transient-state generator could reproduce the empirical observation process closely enough to justify a quantitative San Jacinto downstream simulation.

The calibration stage fitted **no SCR sigma model**. It searched 204 parameter cells varying baseline sigma, detection intercept, transient-state RMS displacement and response probability. Search-stage results were used only to select the 12 closest cells. Those 12 cells were then re-simulated on an independent seed range for 50 replicates each.

A validation cell had to satisfy all four frozen criteria simultaneously:

1. repeat-capture fraction in [0.3265, 0.4265];
2. material-shift fraction among repeat nights in [0.65868, 0.75868];
3. median all-repeat first-to-last distance in [6.25, 8.84] m;
4. median changed-night first-to-last distance in [12.5, 14.0] m.

No validation cell passed all four criteria. The frozen decision was

`stop_v3_no_observation_process_match`.

The claim boundary is therefore stricter than the generative stress test: an ordered transient state can make temporal representations diverge, but this simple release-centred mechanism did not reproduce the San Jacinto observation summaries well enough to be promoted as an empirical mechanism or quantitative calibration.

### S9.3.3 PEMA FIRST/LAST ratio uncertainty sensitivity

The exploratory PEMA fit receipt reports marginal standard errors for FIRST and LAST sigma but not the covariance between those estimates, although both fits use the same 19 sessions. We therefore do not infer a paired confidence interval by combining the marginal 95% intervals.

As a post-result transparency analysis, let \(r=\log(\hat\sigma_{LAST}/\hat\sigma_{FIRST})\), with first-order marginal standard errors \(a=SE_F/\hat\sigma_F\) and \(b=SE_L/\hat\sigma_L\). For an assumed correlation \(\rho\) between the paired sigma estimates,

\[
SE(r)\approx\sqrt{a^2+b^2-2\rho ab}.
\]

With FIRST = 8.8515 m (SE 0.4396) and LAST = 8.5625 m (SE 0.4186), the zero-correlation reference gives an approximate 95% LAST/FIRST ratio interval of **0.844–1.109**. The interval lies fully inside the contextual 0.9–1.1 band only when the assumed correlation exceeds approximately **0.721**. This calculation does not estimate that correlation and is not a formal paired confidence interval or equivalence test. Its purpose is to prevent the -3.3% point contrast from being overinterpreted as demonstrated equivalence.

### S9.4 Claim boundary

The benchmark supports the conditional methodological statement that temporal representation can change fitted SCR spatial scale when a nominal occasion contains multiple observation-conditioned spatial states. It does not show:
- that handling caused the empirical San Jacinto transitions;
- that FIRST or LAST is universally the correct state;
- that empirical PEMA or PEER sigma was biased;
- that every live-trapping protocol mixes states;
- that CHECK-level analysis is intrinsically biased.

The real-data two-species SCR gate remains stopped, and no empirical FIRST/LAST sigma effect is opened.

## S10. Reproducibility files

Core generic method:
- `analysis/temporal_aliasing_diagnostic_v1.py`
- `analysis/temporal_aliasing_bounds_v1.py`
- `analysis/simulate_temporal_aliasing_diagnostic_v2.py`

Generic tests:
- `tests/test_temporal_aliasing_diagnostic.py`
- `tests/test_temporal_aliasing_bounds.py`
- `tests/test_temporal_aliasing_simulation_v2.py`
- `tests/test_temporal_aliasing_example.py`

Empirical validation:
- `analysis/san_jacinto_positional_aliasing_v1.py`
- `tests/test_san_jacinto_positional_aliasing.py`
- `results/san_jacinto_positional_aliasing_result_v1.json`
- `results/temporal_aliasing_simulation_benchmark_v2.json`
- `validation/live_trap_aliasing_v1/individual_cluster_sensitivity_v1.json`\n- `analysis/audit_time_reversal_symmetry_v1.py`\n- `results/time_reversal_symmetry_audit_v1.json`

SCR downstream consequence:
- `analysis/simulate_scr_sigma_consequence_v1.R`
- `docs/SCR_SIGMA_CONSEQUENCE_SIMULATION_DESIGN_V1.md`
- `docs/SCR_SIGMA_EMPIRICAL_SCALE_BENCHMARK_V1.md`
- `docs/SCR_SIGMA_MIXTURE_THEORY_V1.md`
- `results/scr_sigma_consequence_simulation_v1.json`
- `results/scr_sigma_consequence_replicates_v1.csv`
- `results/scr_sigma_dynamic_state_zero_shift_v2_1.json`
- `analysis/simulate_scr_sigma_dynamic_state_zero_shift_v2_1.R`\n- `analysis/calibrate_san_jacinto_observation_process_v3.R`\n- `docs/SAN_JACINTO_OBSERVATION_CALIBRATION_V3.md`\n- `validation/san_jacinto_scr_sigma_v1/observation_calibration_v3.json`

Review-package workflows verify these files independently of unrelated NEON project analyses.


## Supplementary references

Efford MG. 2026. *secr: Spatially explicit capture-recapture models*. R package version 5.4.3. DOI 10.32614/CRAN.package.secr.
