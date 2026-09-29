# Diagnosing temporal positional aliasing in repeated-location ecological data

**Target:** Methods in Ecology and Evolution — Research Article  
**Status:** v0.1 manuscript skeleton  
**Word-count target:** 7,000–8,000 words including references, captions and statements

## Abstract

1. Ecologists routinely collapse repeated observations within a sampling occasion to a single spatial state. When the same marked individual is observed at multiple locations within that occasion, this reduction can introduce **temporal positional aliasing**: downstream spatial analyses depend on which within-occasion location is retained, even when the biological observations themselves are unchanged.

2. We introduce a generic diagnostic that quantifies first-to-last positional span relative to a study-defined material spatial scale, reports repeat-observation-conditioned exceedance with Wilson uncertainty, and supplies deterministic geometry bounds for the maximum sensitivity of inter-occasion movement and mean-pairwise-distance statistics. A simulation benchmark evaluates when the repeat-observation-conditioned proportion is representative of all occasions and when informative repeat observation can bias it.

3. Under non-informative repeat observation, the diagnostic was essentially unbiased in simulation (mean absolute bias 0.00063) with 95.3% mean Wilson coverage. Informative repeat observation produced directionally predictable bias, whereas the fraction of all occasions with a directly observed material shift remained a valid lower bound in every simulated replicate. We then prospectively validated the diagnostic in two held-out Cricetidae from a public repeated-check live-trapping dataset. One-trap-spacing-or-greater first-to-last shifts occurred on 72.6% of 485 repeat-capture nights for *Peromyscus maniculatus* (95% Wilson CI 68.4–76.4%) and 69.2% of 107 nights for *P. eremicus* (59.9–77.1%), with pre-specified spatial replication across 7/7 and 3/3 eligible trapping grids. Across all valid individual-nights, directly observed material shifts provided conservative lower bounds of 28.9% and 24.6%, respectively.

4. Temporal positional aliasing is therefore an observable property of repeated-location sampling protocols, not merely a theoretical concern. The diagnostic does not reconstruct movement paths or identify a uniquely correct representative location; instead, it reveals when within-occasion positional uncertainty is large relative to the spatial resolution of an ecological analysis and provides transparent sensitivity bounds for downstream statistics. We provide generic open-source code applicable to repeated-location data from live trapping and other ecological observation systems.

## Data/Code for peer review

Code is provided under the MIT License. The generic diagnostic is implemented in `analysis/temporal_aliasing_diagnostic_v1.py`; deterministic bounds are in `analysis/temporal_aliasing_bounds_v1.py`; the simulation benchmark is in `analysis/simulate_temporal_aliasing_diagnostic_v1.py`. The empirical example uses the public Figshare dataset associated with article 18295520 v1. A clean review repository/export should be provided at submission.

## Keywords

observation process; spatial ecology; live trapping; capture–recapture; repeated observations; positional uncertainty; temporal aggregation; sensitivity analysis; Peromyscus

# 1. Introduction

Spatial ecological data are often analysed at a coarser temporal resolution than they are collected. A night, survey visit, day, or sampling occasion may be represented by one location even when the underlying protocol records the same marked individual repeatedly within that interval.

This reduction is usually treated as data preparation. It is not necessarily neutral. If alternative valid observations within the same occasion occupy different locations, choosing the first, last, nearest, or otherwise selected observation changes the spatial state passed to the downstream analysis.

We call this **temporal positional aliasing**: unresolved within-occasion variation in observed location that is hidden when multiple observations are collapsed to one representative state.

The problem is distinct from location measurement error. The alternative positions are each observed detector locations. It is also distinct from estimating an unrestricted movement path: repeated trap detections reveal only a sparse subset of the animal's trajectory. The methodological question is narrower—whether assigning a single spatial state to an occasion discards positional variation that is material at the scale of the ecological statistic being analysed.

Existing capture–recapture and live-trapping methods already recognize that detector process, trapping occasions, trap availability, capture timing and recapture structure matter [CITE]. In standard multi-catch SCR/SECR formulations, detained animals generally contribute at most one detector location per occasion, whereas repeated-check protocols may expose multiple within-occasion locations if traps are reset [CITE]. Yet there is no routine diagnostic for asking whether collapsing those locations to one state is spatially consequential.

Here we contribute three linked components.

First, we define a simple, scale-aware diagnostic based on the first-to-last within-occasion positional span
`delta_t = d(F_t,L_t)`
and a user-defined **material spatial scale** such as trap spacing or another resolution relevant to the planned analysis.

Second, we derive deterministic sensitivity bounds showing how unresolved within-occasion positional span can propagate into inter-occasion movement and population mean-pairwise-distance statistics. The bounds are consequences of metric geometry; their contribution is practical interpretation rather than new mathematics.

Third, we evaluate the diagnostic using both simulation and a prospectively locked empirical holdout. The simulation separates non-informative from informative repeat-observation mechanisms. The empirical validation asks whether material first-to-last shifts replicate across two held-out Cricetidae and independent trapping grids.

Our goal is not to identify whether the first or last observation is biologically correct. Rather, we provide a diagnostic for deciding when a single-state reduction should itself be treated as an analytical assumption and carried forward into sensitivity analysis.

# 2. Materials and Methods

## 2.1 General diagnostic

Consider individual `i` during occasion `t`, observed at ordered locations

`X_it1, ..., X_itK`.

For occasions with at least two valid observations, define:

`F_it = X_it1`

`L_it = X_itK`

and positional span

`delta_it = d(F_it,L_it)`.

Let `s > 0` be a study-defined material spatial scale. Define a material aliasing event when

`delta_it >= s`.

For `R` repeat-observed individual-occasions, report:
- the number and fraction exceeding `s`;
- a two-sided 95% Wilson interval;
- median, upper quantiles and maximum `delta`;
- spans expressed in units of `s`;
- the fraction of all valid individual-occasions for which a material shift is directly observed.

The last quantity is a lower bound on the latent all-occasion material-shift fraction because a singly observed occasion cannot expose a first-to-last difference.

## 2.2 Deterministic downstream sensitivity bounds

For two occasions `t` and `u`:

`|d(F_t,F_u) - d(L_t,L_u)| <= delta_t + delta_u`.

For `n` individuals represented by paired first and last locations within an occasion:

`|MPD(F) - MPD(L)| <= 2 mean(delta_i)`.

If a standardized packing score is

`z = (MPD - mu_n)/sigma_n`

with common `n` and fixed null moments, then

`|z_F-z_L| <= 2 mean(delta_i)/sigma_n`.

Proofs and sharpness examples are given in the Supplementary Methods / theory note. The inequalities are upper bounds, not expected biases.

## 2.3 Simulation benchmark

### 2.3.1 Data-generating process

**Present this section before the empirical example to match MEE expectations for computational methods.**

For each simulated individual-occasion, generate a 2-D first-to-last displacement with independent Gaussian components. The Euclidean span is compared with a material scale fixed to one simulation unit.

Parameter grid:
- number of occasions: 100, 500;
- shift SD / material scale: 0.25, 0.5, 1.0, 2.0;
- baseline repeat-observation probability: 0.25, 0.5, 0.75;
- relationship between span and repeat-observation probability: beta = -1, 0, +1;
- 400 replicates per cell.

### 2.3.2 Observation mechanisms

For beta = 0, repeat observation is independent of positional span.

For beta > 0, large spans are preferentially repeat-observed.

For beta < 0, large spans are preferentially missed from the repeat-observed subset.

### 2.3.3 Simulation performance metrics

For each cell calculate:
- true latent material-shift fraction;
- repeat-observation-conditioned material-shift fraction;
- conditional-estimator bias;
- Wilson 95% coverage for the latent fraction;
- directly observed material shifts divided by all occasions;
- whether the observed all-occasion fraction ever exceeds the latent fraction.

The final metric must have zero violations by construction and provides a robust interpretation when repeat observation is informative.

## 2.4 Prospectively held-out empirical validation

### 2.4.1 Dataset and sampling design

Use the public San Jacinto repeated-check small-mammal live-trapping dataset [CITE DATA/PAPER].

The source contains repeated nightly trap checks on fixed 7 x 7 trapping grids with 6.25 m spacing. Individual identity, species, trap flag and capture time are retained.

The empirical outcome was locked before inspection for:
- *Peromyscus maniculatus* (PEMA);
- *Peromyscus eremicus* (PEER).

These species were selected from an effect-blind support scan. Their first-to-last positional outcomes had not been inspected when the confirmatory lock was frozen.

### 2.4.2 Frozen primary endpoint

For each repeat-capture individual-night, calculate Euclidean distance between the earliest and latest valid trap flag.

Primary material scale:
`s = 6.25 m`,
exactly one adjacent-trap spacing.

A species passed prospectively if:
1. the material-shift fraction exceeded 0.25;
2. the lower 95% Wilson bound exceeded 0.25;
3. at least two grids with >=20 repeat-capture nights independently had material-shift fraction >0.25.

Both species were required to pass.

### 2.4.3 Denominator audit

Because the primary estimate is conditional on repeat observation, also report:
- total valid individual-nights;
- repeat-observed fraction;
- directly observed material-shift nights divided by all valid individual-nights.

The final quantity is interpreted only as an observational lower bound.

## 2.5 Generic implementation

Describe required input schema:
- individual ID;
- occasion/night ID;
- sortable within-occasion time;
- numeric spatial coordinates;
- material scale.

Describe outputs and failure checks.

## 2.6 Pre-specified downstream home-range test

A downstream MCP sensitivity analysis was prospectively planned with high-information eligibility thresholds before MCP values were inspected. The support gate required at least 20 eligible PEMA and 15 eligible PEER individuals. Only 17 and 6, respectively, qualified. The downstream effect was therefore declared non-estimable and no MCP effect values were retained.

This failed support gate is reported for transparency and is not used to modify the primary positional-aliasing result.

# 3. Results

## 3.1 Simulation benchmark

Across non-informative repeat-observation cells, mean absolute bias of the repeat-conditioned material-shift fraction was 0.00063 and mean Wilson coverage was 95.3%.

When large spans increased repeat-observation probability, mean bias was +0.0508. When large spans decreased repeat-observation probability, mean bias was -0.0799.

The all-occasion directly observed material-shift fraction exceeded the latent fraction in **0 simulated replicates** across the full benchmark.

Interpretation: repeat-conditioned fractions estimate an all-occasion latent fraction only when the repeat-observation mechanism is sufficiently non-informative. The all-occasion directly observed fraction retains a robust lower-bound interpretation under all simulated observation mechanisms.

## 3.2 Held-out PEMA validation

- 485 repeat-capture individual-nights;
- 352 >=6.25 m shifts;
- 72.6%;
- 95% Wilson CI 68.4–76.4%;
- 7/7 eligible grids passed;
- median span 8.84 m;
- q90 25.0 m.

## 3.3 Held-out PEER validation

- 107 repeat-capture individual-nights;
- 74 >=6.25 m shifts;
- 69.2%;
- 95% Wilson CI 59.9–77.1%;
- 3/3 eligible grids passed;
- median span 6.25 m;
- q90 19.76 m.

The frozen empirical decision was:

`authorize_live_trap_positional_aliasing_result`.

## 3.4 All-night denominator context

PEMA:
- 1,219 valid individual-nights;
- 485 repeat-observed (39.8%);
- >=1-spacing positional shift directly observed on at least 28.9% of all valid nights.

PEER:
- 301 valid individual-nights;
- 107 repeat-observed (35.5%);
- >=1-spacing shift directly observed on at least 24.6% of all valid nights.

These values are observational lower bounds, not latent all-night movement estimates.

## 3.5 Downstream home-range support gate

Only 17 PEMA and 6 PEER individuals met the frozen high-information MCP eligibility rules, below the required 20 and 15. The downstream home-range effect analysis was therefore not authorized.

# 4. Discussion

## 4.1 A single occasion can contain multiple spatial states

The held-out validation shows that positional span among repeat-observed nights can be large relative to trap spacing and is spatially replicated. A nightly representative location should therefore be regarded as an explicit reduction rule rather than an automatically neutral state.

## 4.2 What repeat-conditioned proportions can and cannot estimate

Simulation gives the paper an important boundary: the high repeat-conditioned empirical fractions should not be extrapolated directly to all nights unless repeat observation is plausibly non-informative with respect to positional span.

The denominator audit provides the safer statement. Even treating every single-capture night as unresolved rather than shifted, material shifts were directly observed on roughly one quarter to three tenths of all valid individual-nights.

## 4.3 Propagating positional uncertainty rather than choosing a 'correct' state

The deterministic bounds provide a generic way to translate within-occasion span into a maximum downstream sensitivity. This avoids an artificial contest between FIRST and LAST as if one must represent the true nightly location.

The recommended workflow is:
1. preserve all timestamped locations;
2. define the ecological occasion;
3. choose a material spatial scale;
4. diagnose within-occasion spans;
5. if spans are negligible, collapse with documented rules;
6. if spans are not negligible, split occasions or carry representative-state sensitivity through downstream analysis.

## 4.4 Scope and limitations

This empirical validation concerns one repeated-check live-trapping design and two held-out Cricetidae species. Broad applicability lies in the diagnostic and bounds, not in a claim that the empirical magnitude generalizes to all taxa or protocols.

Repeat capture is informative in many real protocols. The diagnostic exposes rather than solves that observation process. If an all-occasion latent aliasing rate is required, an explicit model for repeat-observation probability is needed.

First-to-last distance is also not a movement path. It is a lower-dimensional description of positional ambiguity among observed detections.

## 4.5 Implications for ecological data collection and analysis

Recommended reporting items:
- exact occasion definition;
- whether detectors are reset within an occasion;
- all within-occasion timestamps and locations;
- fraction of occasions with repeated observations;
- material spatial scale;
- positional-span distribution;
- rule used to collapse observations;
- sensitivity analysis when spans are non-negligible.

# Figure plan

**Figure 1.** Observation-process schematic and deterministic sensitivity bounds.

**Figure 2.** Simulation benchmark: conditional-estimator bias and Wilson coverage under non-informative, span-enriched and span-depleted repeat observation.

**Figure 3.** Held-out PEMA/PEER material-shift proportions with Wilson intervals plus grid-level replication.

**Figure 4.** First-to-last span distributions in units of trap spacing and all-night denominator lower bounds.

# Supplementary material

- Mathematical proofs and sharpness examples.
- Full simulation grid.
- Prospective held-out effect lock.
- Grid-specific empirical results.
- Denominator audit.
- Failed downstream MCP estimability receipt.
- Generic CLI example.
