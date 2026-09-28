# Public mammal sex-packing null amendment — v2

Date: 2026-09-29

Status: frozen before any sex-specific ecological outcome extraction.

## 1. Why an amendment is required

The v1 estimability gate passed before any sex-specific Packing_z effect was calculated.
The subsequent prespecified v1 mechanical audit failed on two of three representative
geometries:

- Portal 7 x 7, 6.25 m: rho = -0.3119397335
- NEON 10 x 10, 10 m: rho = -0.2477168472
- NEON 7 x 7, 10 m: rho = -0.0458734902

The frozen warning threshold remains |rho| <= 0.2.

The corresponding mean Delta values across design points were approximately 0.0010,
0.0164, and -0.0296. Therefore the failed rank statistic is not evidence of a
meaningful non-zero null sex effect. It reflects the use of finite Monte Carlo estimates
of near-zero design-point means followed by a rank correlation: making Monte Carlo
noise smaller does not guarantee a rank correlation of near-tied noisy means tends to
zero.

The v1 failure is retained in
validation/public_mammal_sex_packing_v1/mechanical_null_v1_failure_receipt.json.
It is not overwritten or reclassified as a pass.

At this amendment:
- ecological sex effects inspected: **false**
- ecological sex model fits: **0**

## 2. Exact finite-population null

For M active trap locations, let h_a be the distance associated with trap-pair a,
K = C(M,2), and let an n-individual null placement be a uniformly sampled n-subset
of the active traps. Let q = C(n,2) and

U = (1/q) * sum_a I_a h_a,

where I_a indicates that both endpoints of trap-pair a are selected.

Then:

E[U] = (sum_a h_a) / K.

This mean is exactly independent of n.

For the second moment, define:
- S1 = sum_a h_a
- S2 = sum_a h_a^2
- A = sum h_a h_b over unordered edge pairs sharing one trap
- T = (S1^2 - S2)/2
- D = T - A, the corresponding sum over disjoint edge pairs
- p_k = C(n,k)/C(M,k)

Then:

E[U^2] = (p2*S2 + 2*p3*A + 2*p4*D) / q^2

and

Var(U) = E[U^2] - E[U]^2.

The implementation is deterministic and seed-free. Small-grid exhaustive enumeration
must match the analytic mean and standard deviation to numerical precision.

## 3. v2 mechanical gate

The biological null property is unchanged:

Delta_sex_packing = Packing_z_male - Packing_z_female

must have null expectation zero for every prespecified male/female count combination.

Under exact sex-specific null moments:
- E[Packing_z_male] = 0 exactly;
- E[Packing_z_female] = 0 exactly;
- E[Delta_sex_packing] = 0 exactly.

The original |rho| <= 0.2 threshold is retained. The v2 audit evaluates the exact
expected Delta across the same sex-count design points and the same three representative
geometries. Because the expected Delta is identically zero, its sex-ratio rank correlation
is defined operationally as zero.

No observed male/female spatial arrangement is read by this audit.

## 4. Observed-support fail-closed rule

The exact finite-population null samples trap locations without replacement. Therefore
an observed sex-specific configuration containing duplicate retained trap coordinates is
not on the null support and is non-estimable under v2.

Before ecological effect extraction:
1. reconstruct the retained male and female trap coordinates for every candidate session;
2. require no duplicate retained trap coordinate within either sex;
3. require no duplicate retained trap coordinate in the male+female union;
4. recompute the N>=3/sex estimability counts after this support check;
5. re-run the frozen family and cross-source estimability gates.

If the updated estimability gate fails, the study stops. No effect is inspected to change
this rule.

The existing Portal Phase-1 receipt contains five N=2 sessions with observed MPD = 0 m,
showing that duplicate-location support is a real data-QC issue in the wider data. Those
sessions are outside the sex primary threshold, but v2 does not assume the problem is
absent in the primary subset.

## 5. What does not change

Unchanged:
- Heteromyidae scope;
- N_male >= 3 and N_female >= 3 primary threshold;
- >=2/sex and >=5/sex sensitivities;
- Portal and NEON source pins;
- directional biological hypothesis;
- family and cross-source advance gates;
- movement-validation plan;
- |rho| <= 0.2 mechanical warning threshold;
- claim boundaries.

The stopped public_mammal_space_use_v1 programme remains frozen and is not recomputed
with this v2 metric.

## 6. Authorization boundary

The next permitted actions are:
- exact-v2 mechanical tests and audit;
- coordinate-support reconstruction;
- post-support estimability re-freeze.

Sex-specific Packing_z values, Delta values, coefficients, confidence intervals, and
p-values remain unauthorized until both the v2 mechanical audit and the post-support
estimability gate pass and their receipts are committed.
