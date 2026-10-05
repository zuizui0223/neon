# Time-reversal symmetry, exchangeability and representation stability

Date: 2026-10-05

Status: exact conceptual result plus post-result empirical consistency audit for the live-trap positional-aliasing paper.

## 1. Why raw positional aliasing is not itself a bias estimate

Let one ecological occasion contain an ordered sequence of detector outcomes

\[
Y=(Y_1,\ldots,Y_K),
\]

where \(Y_j=0\) denotes no detection and \(Y_j\in\{1,\ldots,M\}\) denotes the detector at which an individual is observed on check \(j\).

Define FIRST as the detector on the earliest non-zero check and LAST as the detector on the latest non-zero check.

Large distances between FIRST and LAST show that a one-location representation is not unique. They do **not**, by themselves, imply that FIRST and LAST target different population-level spatial parameters.

## 2. A process-level sufficient condition: time-reversal symmetry

Let

\[
R(Y)=(Y_K,\ldots,Y_1)
\]

denote within-occasion time reversal. The logically weakest representation-level requirement is equality of the induced FIRST and LAST marginals. A transparent process-level sufficient condition that guarantees this equality is

\[
Y\overset{d}=R(Y)
\]

conditional on the latent state and observation design relevant to the downstream model.

Time reversal exchanges FIRST and LAST while leaving the event “at least one detection” unchanged. Therefore

\[
\mathrm{FIRST}\overset{d}=\mathrm{LAST}.
\]

For a full dataset \(\mathcal Y\), let \(R\mathcal Y\) reverse every within-occasion sequence. If the joint law is invariant under this operation, then for any downstream scalar functional \(T\),

\[
T_F(\mathcal Y)\overset{d}=T_L(\mathcal Y).
\]

Moreover, the directed contrast

\[
D(\mathcal Y)=T_L(\mathcal Y)-T_F(\mathcal Y)
\]

satisfies

\[
D(R\mathcal Y)=-D(\mathcal Y).
\]

Hence, under time-reversal symmetry,

\[
D\overset{d}=-D.
\]

The contrast distribution is symmetric about zero; if its expectation exists, \(E[D]=0\).

Full temporal exchangeability is also sufficient, but it is stronger than reversal symmetry. Reversal symmetry itself is **not logically necessary** for equal FIRST/LAST marginals: some non-reversible processes can produce the same FIRST and LAST marginal distributions. Independent identically distributed checks around a fixed activity centre are one special case; a stationary reversible Markov process can also satisfy the reversal condition despite serial dependence. Thus autocorrelation alone does not imply a systematic FIRST/LAST difference.

## 3. Time-reversal non-identifiability of span-only diagnostics

For an occasion with first and last detector positions \(F_t,L_t\), define the span

\[
\delta_t=d(F_t,L_t).
\]

Reverse the within-occasion time order. Then

\[
F_t'=L_t,\qquad L_t'=F_t,
\]

but

\[
\delta_t'=d(F_t',L_t')=d(L_t,F_t)=\delta_t.
\]

Thus all diagnostics depending only on unordered spans are invariant to time reversal, including:

- the fraction with \(\delta_t\ge s\);
- median and quantiles of \(\delta_t\);
- directly observed all-occasion lower bounds based on the same materiality event;
- any summary of the empirical distribution of \(\delta_t\).

By contrast, a directed downstream contrast exchanges sign under reversal. For a scalar estimator \(T\),

\[
C=T(\mathrm{LAST})-T(\mathrm{FIRST})
\]

becomes

\[
C'=-C.
\]

For a positive estimator, the log-ratio

\[
R_T=\log\{T(\mathrm{LAST})/T(\mathrm{FIRST})\}
\]

becomes \(-R_T\).

Therefore the sign of a FIRST-versus-LAST downstream effect is not identifiable from span-only aliasing summaries. This is an exact reason that the positional-aliasing screen and downstream stability check must be separate stages.

## 4. What breaks reversal symmetry

FIRST and LAST can become distributionally different when the observation process has an arrow of time, for example:

- capture or handling changes the subsequent spatial state;
- detector availability or effort changes through the occasion;
- attraction, avoidance or trap response begins after detection;
- natural movement creates a directional or non-stationary within-occasion state process;
- check timing samples systematically changing behavioural states;
- weather or other time-varying conditions alter the detection kernel.

The relevant issue is not movement or serial dependence per se. An animal may move substantially, and observations may be autocorrelated, while the within-occasion process remains approximately reversible. Directional FIRST/LAST divergence requires temporal asymmetry relevant to the fitted estimand.

## 5. San Jacinto: large spans with little directed flux

The held-out empirical screen found frequent positional non-uniqueness:

- PEMA: 72.6% of repeat-capture nights shifted by at least one trap spacing;
- PEER: 69.2%.

Yet the post-stop exploratory PEMA SCR comparison found:

- \(\sigma_{\mathrm{FIRST}}=8.8515\) m;
- \(\sigma_{\mathrm{LAST}}=8.5625\) m;
- LAST/FIRST = 0.9673;
- relative change = -3.27%.

A post-result, non-rescuing reversal audit then used only changed repeat nights. For each species, relative displacement vectors were paired with their reverse within grid. The randomization statistic summed squared forward-minus-reverse imbalances across grid × unsigned-vector strata. To preserve repeated contributions from marked animals, all changed nights from the same grid × individual cluster were reversed together in each of 500,000 sign-flip permutations.

Results:

- PEMA: grid-stratified reversal \(p=0.193\); mean directed vector magnitude = 0.071 m versus RMS displacement 17.08 m (0.4%);
- PEER: \(p=0.735\); mean directed vector magnitude = 1.68 m versus RMS 16.26 m (10.3%).

Failure to reject does not prove reversal symmetry, and sparse vector strata limit power. The audit is consistent with the central empirical pattern, especially in PEMA: large realized displacement magnitude coexists with very little net directional flux and a stable FIRST/LAST sigma estimate.

## 6. Ordered-state simulations deliberately break the symmetry

The stationary SCR simulations instantiate an exchangeable special case and show no systematic FIRST/LAST ordering advantage.

The ordered state-transition stress test deliberately introduces an arrow of time. Mirroring PRE versus POST keeps the same displacement magnitudes but reverses which representative samples the transitioned state. The FIRST/LAST sigma contrast reverses accordingly.

This is the computational demonstration of the reversal result: magnitude is invariant to reversal, while the directed representation effect is antisymmetric.

A separate observation-only calibration attempted to match a simple release-centred transient-state model to four San Jacinto summaries. Zero of 12 independently validated candidates selected from a 204-cell search passed all four criteria. The ordered-state stress test is therefore a controlled failure mode, not an empirically matched handling model.

## 7. Methodological workflow

### Stage A — positional non-uniqueness screen

Ask whether multiple observed states within one nominal occasion differ materially relative to a prechosen spatial scale.

This answers:

> Is temporal aggregation hiding spatial information that could matter?

It does not estimate downstream bias.

### Stage B — temporal-symmetry and representation-stability check

Ask whether the observation process has a plausible arrow of time relevant to the downstream model, and re-fit the intended analysis under defensible temporal representations.

This answers:

> Does temporal order change the downstream estimand?

A reversal audit can provide supporting evidence, but model-specific stability remains the decisive test.

## 8. Consequence for claims

The paper should not claim that positional aliasing generally biases SCR sigma.

A stronger and more general statement is:

> Frequent within-occasion positional aliasing is a warning condition, not a bias estimate. Time-reversal symmetry is a transparent sufficient condition under which FIRST and LAST are distributionally equivalent even when realized locations differ substantially. Systematic directional representation effects require temporal asymmetry, but reversal symmetry is not the only possible route to stable FIRST/LAST marginals. Positional magnitude, temporal asymmetry and downstream estimand stability must therefore be diagnosed separately.
