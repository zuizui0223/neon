# Time-reversal symmetry, exchangeability and representation stability

Date: 2026-10-05

Status: exact conceptual result plus post-result empirical consistency audit for the live-trap positional-aliasing paper.

## 1. Why raw positional aliasing is not itself a bias estimate

Let one ecological occasion contain an ordered sequence of detector outcomes

[
Y=(Y_1,ldots,Y_K),
]

where (Y_j=0) denotes no detection and (Y_jin{1,ldots,M}) denotes the detector at which an individual is observed on check (j).

Define FIRST as the detector on the earliest non-zero check and LAST as the detector on the latest non-zero check.

Large distances between FIRST and LAST show that a one-location representation is not unique. They do **not**, by themselves, imply that FIRST and LAST target different population-level spatial parameters.

## 2. The minimal symmetry condition is time reversal, not full exchangeability

Let

[
R(Y)=(Y_K,ldots,Y_1)
]

denote within-occasion time reversal. The minimal condition needed for FIRST/LAST representation symmetry is

[
Yoverset{d}=R(Y)
]

conditional on the latent state and observation design relevant to the downstream model.

Time reversal exchanges FIRST and LAST while leaving the event "at least one detection" unchanged. Therefore

[
mathrm{FIRST}overset{d}=mathrm{LAST}.
]

For a full dataset (mathcal Y), let (Rmathcal Y) reverse every within-occasion sequence. If the joint law is invariant under this operation, then for any downstream scalar functional (T),

[
T_F(mathcal Y)overset{d}=T_L(mathcal Y).
]

Moreover the directed contrast

[
D(mathcal Y)=T_L(mathcal Y)-T_F(mathcal Y)
]

satisfies

[
D(Rmathcal Y)=-D(mathcal Y).
]

Hence, under time-reversal symmetry,

[
Doverset{d}=-D.
]

The contrast distribution is symmetric about zero; if its expectation exists, (E[D]=0).

Full temporal exchangeability is a sufficient condition, but it is stronger than necessary. Independent identically distributed checks around a fixed activity centre are one special case. A stationary reversible Markov process can also satisfy the reversal condition despite serial dependence. Thus autocorrelation alone does not imply a systematic FIRST/LAST difference.

## 3. Time-reversal non-identifiability of span-only diagnostics

For an occasion with first and last detector positions (F_t,L_t), define

[
delta_t=d(F_t,L_t).
]

Under reversal,

[
F_t'=L_t,qquad L_t'=F_t,
]

but

[
delta_t'=delta_t.
]

Therefore all diagnostics depending only on unordered spans are invariant to reversal, including:

- the fraction with (delta_tge s);
- median and quantiles of (delta_t);
- directly observed all-occasion lower bounds based on the same materiality event;
- any statistic of the empirical distribution of (delta_t).

By contrast, a directed FIRST/LAST effect reverses sign. Two data-generating processes related only by time reversal can therefore have identical span distributions but opposite directed downstream effects.

No statistic based only on unordered within-occasion spans can identify the sign of a representation effect without an additional assumption about temporal ordering or state dynamics.

## 4. What breaks reversal symmetry

FIRST and LAST can become distributionally different when the observation process has an arrow of time, for example:

- capture or handling changes the subsequent spatial state;
- attraction, avoidance or trap response begins after detection;
- detector availability or effort changes systematically through the occasion;
- natural movement is directional or non-stationary at the occasion scale;
- check timing samples systematically changing behavioural states;
- weather or other conditions alter the detection kernel monotonically through time.

The relevant issue is not movement or serial dependence per se. An animal may move substantially, and observations may be autocorrelated, while the within-occasion process remains approximately reversible. Systematic FIRST/LAST divergence requires temporal asymmetry relevant to the fitted estimand.

## 5. San Jacinto: large spans with little directed flux

The held-out empirical screen found frequent positional non-uniqueness:

- PEMA: 72.6% of repeat-capture nights shifted by at least one trap spacing;
- PEER: 69.2%.

Yet the post-stop exploratory PEMA SCR comparison found:

- sigma_FIRST = 8.8515 m;
- sigma_LAST = 8.5625 m;
- LAST/FIRST = 0.9673;
- relative change = -3.27%.

A post-result, non-rescuing reversal audit then used only changed repeat nights. For each species, relative displacement vectors were paired with their reverse within grid. The randomization statistic summed squared forward-minus-reverse imbalances across grid × unsigned-vector strata. To preserve repeated contributions from marked animals, all changed nights from the same grid × individual cluster were reversed together in each of 500,000 sign-flip permutations.

Results:

- PEMA: grid-stratified reversal p = 0.193; mean directed vector magnitude = 0.071 m versus RMS displacement 17.08 m (0.4%);
- PEER: p = 0.735; mean directed vector magnitude = 1.68 m versus RMS 16.26 m (10.3%).

Failure to reject does not prove reversal symmetry, and sparse vector strata limit power. The audit is consistent with the central empirical pattern, especially in PEMA: large realized displacement magnitude coexists with very little net directional flux and a stable FIRST/LAST sigma estimate.

## 6. Ordered-state simulations deliberately break the symmetry

The stationary SCR simulations instantiate a stronger exchangeable special case and show no systematic FIRST/LAST ordering advantage.

The ordered state-transition simulations deliberately introduce an arrow of time. Mirroring PRE versus POST keeps the same displacement magnitudes but reverses which representative samples the transitioned state. The FIRST/LAST sigma contrast reverses accordingly.

This is the computational demonstration of the exact reversal result: magnitude is invariant to reversal, while the directed representation effect is antisymmetric.

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

> Frequent within-occasion positional aliasing is a warning condition, not a bias estimate. Under a time-reversal-symmetric observation process, FIRST and LAST are distributionally equivalent even when realized locations differ substantially. Systematic directional representation effects require an arrow of time in the observation or state process; therefore positional magnitude, temporal asymmetry and downstream estimand stability must be diagnosed separately.
