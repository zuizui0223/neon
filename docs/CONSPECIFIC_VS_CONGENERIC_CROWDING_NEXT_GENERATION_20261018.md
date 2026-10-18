# Species-specific versus congeneric crowding: next-generation ecological test

**Defined:** 2026-10-18. **Scientific category:** hypothesis and effect-blind predictor-feasibility audit generated AFTER examining NEON RELEASE-2026 W/B effects and the 2025–2026 provisional held-out outcomes. NOT a prospective validation of the original eight-genus result. Those results remain fixed as documented; do not re-label the positive or negative historical effects confirmatory.

## One ecological question

**When more individuals of a small-mammal *species* are present, does their short-term within-individual trap-coordinate variance change differently from the dispersion of observed animal centres, and are those associations distinguishable from changes in abundance of *other species in the same genus*?**

The original study modeled W, debiased B and Δ=B−W against **genus-level** minimum number known alive (MNKA). A focal *Peromyscus* species's genus MNKA may include individuals of another species. The original coefficient therefore cannot isolate effects of conspecific crowding, or establish ecological causation. Moving to species-resolved predictors would address a genuine biological distinction, **not rescue** the prior failed 5/8 versus 6/8 generality rule.

## Fix the taxonomic interpretation before seeing new effects

The existing RELEASE-2026 target list contains 31 target species concepts and four species-group concepts (e.g., PEMA/PELE group). Each historical marked animal has a site × plot × tag identity and a set of target taxon IDs across captured events. For predictor-only feasibility use:

- **Resolved-species animal:** history assigned to exactly *one* target species taxon ID (taxon rank species, not a species-group label) across all eligible captures.
- **Unresolved genus animal:** history containing a species-group assignment OR multiple taxon labels *within* a genus; do not count it as a resolved animal of any species.
- **Cross-genus taxonomic conflict:** exclude from the genus MNKA predictor, exactly as the original frozen index did; report its count.
- **Known alive:** within the same exact-three-night standard site × plot event sequence, an animal is counted at every event from its first to last target capture, following the original genus-MNKA rule. Do not insert an animal outside this interval.

For focal resolved species s within genus g, at event e:
  * F(s,e) = MNKA of histories unambiguously assigned to s
  * C(s,e) = MNKA of histories unambiguously assigned to other species in g
  * U(g,e) = MNKA of unresolved, same-genus histories
  * N(g,e) = F(s,e) + C(s,e) + U(g,e), **exact identity** on the frozen event universe.

**F, C and U are availability/known-alive indices, not densities**, and even clearly labelled individuals can have detection error. Focal species-group response rows are not candidates for the species-specific primary inference; they remain in the historical original cohort.

## Outcome-blind RELEASE-2026 feasibility audit

Before touching any new W/B outcome:
- Reconstruct original checksum/version-tied complete three-night NEON events, 1536 target response sessions, 47360 target marked histories, 103 cross-genus excluded histories and 176 genus-MNKA varying series as invariant checks. **Never modify** the original W/B or fixed model scripts.
- For each *resolved focal species* × plot × event, calculate only N, F, C, U and reported identity counts; **do not compute spatial distances, W, B, Δ or test correlations with them**.
- Report by genus (and at sufficiently aggregated scale) series with >=3 events, >1 distinct focal F and other-congener C values, number of sites and predictor-only co-occurrence.
- Critically, diagnose residual predictor variation **after the unchanged series, site × calendar month, and year fixed effects**. A two-predictor design must have full rank; testing species-specific versus congeneric slopes when predictor variation is absorbed by the nuisance effects is prohibited.
- Do not choose a favorable genus from already-known W/B signs. *Peromyscus* is the predeclared feasibility priority **because its taxonomy explicitly includes multiple target species and cryptic pairs**; the other genera are fully reported as structural context. A "GO" only means **potential identifiability**, not that future data have enough statistical power or correct biological identities.
- **Pre-exposure predictor-only feasibility descriptor** (not a scientific success test): a genus can be called *candidate structurally identifiable* only with >=60 sessions for strictly resolved focal species, >=6 NEON sites, >=8 distinct focal taxon × site × plot series with at least three sessions, >=5 series showing both focal F and congener C variation, full conditional rank two after frozen fixed effects, and condition number <=30 for the two residualized predictors (no further threshold tuning after this audit). All these are **sample/predictor-only** gates: even a pass does not permit a W/B fit, prove power, or retrospectively choose a positive genus. Record both pass and fail for every genus, with *Peromyscus* discussed first regardless of outcome.
- Do not make the observed abundance range, site count or regression coefficient from RELEASE-2026 an independent confirmation. Historical data are already response-consumed.

## Prospective future-study hypotheses (only new, unconsumed trapping events)

Primary ecological estimand: within-species slope contrast for *true resolved-species* abundance F when allowing a separate congeneric abundance index C in the same model, using comparable-season repeat observations of the same species × site × plot.

Competing predictions, to be tested on **new events not contained in either RELEASE-2026 or any previously opened 2025–2026 provisional stream**:

1. **Conspecific competition/individual compression:** higher F is associated with W decreasing, potentially with B maintaining or increasing. A positive Δ_F alone is not proof of competition or territorial exclusion.
2. **Congeneric interaction/redistribution:** the relationship between C and W/B differs from the one for F (two-sided contrast Δ_C − Δ_F), if both index series have independent within-population adjusted variation. Differences may arise from ecological sorting or species turnover, not necessarily direct interference.
3. **No identifiable or no ecological association:** capture selection, habitat/seasonal composition or weak within-population variation accounts for the observed covariance. This must be treated as a substantive possible outcome, not rescued with an ad hoc threshold or genus subset.

Future release primary screening is based on *effect-blind predictor-support* criteria (full rank, fixed taxonomy rule, enough distinct site-level seasonal repeats, and trap completeness). Any formal minimum site/series number and expected detectable effect must be separately locked before opening future W/B outcomes. Use year- and site-cluster uncertainty, explicit detection sensitivity, and report W and B component slopes in addition to Δ. Distinguish observed trap coordinate variance from true home ranges.

## Novelty boundary: prior studies already separate intra- and interspecific density

This is **not** the first study to ask whether conspecific and other-species abundance affect rodent space use:

- Wolff (1985), *Canadian Journal of Zoology* 63:2657–2662, specifically studied density, food and interspecific interference in home-range size of **P. leucopus** and **P. maniculatus**. https://hero.epa.gov/reference/3180950/
- Dooley & Dueser (1990), *Ecology* 71:788–796, performed reciprocal-removal and telemetry comparisons for nest-site segregation of these two mice. Their evidence for nest-site separation did not establish strong resource-limitation causation. https://doi.org/10.2307/1940330
- Dooley & Dueser (1996), *Oecologia* 105:81–86, experimentally assessed the asymmetry of congeneric nest-site interactions. https://doi.org/10.1007/BF00328794
- Casula, Luiselli & Amori (2019), *Basic and Applied Ecology* 34:46–54, independently compared **conspecific density, sympatric other-species density and total density** using spatial capture–recapture home-range estimates for co-occurring *Apodemus* and *Myodes*. They reported associations with conspecific, rather than heterospecific or total density. https://doi.org/10.1016/j.baae.2018.11.002
- O'Fallon, Pinter-Wollman & Mabry (2025), *Oecologia* 207:98, used NEON *Peromyscus* home ranges (>=5 adult captures), primarily at genus level because field species identifications may be unreliable. https://doi.org/10.1007/s00442-025-05731-2

**Narrow prospective empirical distinction, conditional on new, high-quality evidence:** investigate whether *conspecific versus congeneric known-alive indices* have different associations with **two simultaneous components of short-window positional variance** (within individuals W versus among observed centres B), across repeated NEON sites. The novelty is NOT intra-/inter-specific density as predictors, home-range contraction, or nest-site competition themselves. A 3-night grid capture event with 2–3 detected locations cannot be called a telemetered or five-capture kernel home range.

Field-identified labels that are stable across events **do not prove true biological species identity**, especially the *P. maniculatus–P. leucopus* complex. Explicit species-group and conflicting taxon histories remain unresolved; any future confirmatory focal-species study requires a prespecified identification-quality sensitivity (and DNA barcode/other independent validation where available), not post-result favorable reassignment.

## Rationale and availability

NEON's publicly documented protocol uses **100 traps spaced 10 m** on standard 10 × 10 grids; complete three-night pathogen-grid bouts are scheduled multiple times per year with seasonality and lunar timing. Researchers identify species, sex, age and reproductive condition, and taxonomic identification history is tracked. Sampling and identification uncertainty must be confronted, not ignored. See:
- https://www.neonscience.org/data-collection/small-mammals
- https://www.neonscience.org/resources/learning-hub/tutorials/mammal-data-intro
- https://data.neonscience.org/data-api/endpoints/releases/
- https://www.neonscience.org/data-samples/data-notifications

A static data release is citable and versioned; since 2026-06-30 NEON downloads require a user login/API token. No exact next release date or future sample size is promised. New releases may correct 18 affected *geoNEON* trap-point coordinate maps: this does **not** alter nominal `trapCoordinate` labels or the existing purely nominal W/B lattice and should not be misrepresented as correcting those original W/B coefficients. It matters if later adding map-derived habitat/topography covariates.

## Explicit boundaries

- No changes to the original 8-genera denominator or already-opened results.
- No post-hoc new species or sex/habitat moderator model fitted on historical W/B in this audit.
- No inference that a difference in W/B indicates territoriality, individual avoidance, resource competition, predation or disease transmission.
- Do not claim independent future validation if observations or tagged histories are reused across releases.
- MOSA's 153-month predictor-only support does not solve biological identity issues or permit opening its sealed W/B effects.
- The ecological manuscript `manuscript/NEON_MAMMAL_DENSITY_SPACE_ECOLOGY_V0_2.md` remains Draft/HOLD.


## 18 October 2026: independent predictor-only feasibility result

[Source-verified GitHub Actions 39091740732](https://github.com/zuizui0223/neon/actions/runs/39091740732) **succeeded** after the seven synthetic source-free checks passed. Its source-immutable input reconstruction exactly reproduced:

- 1,536 original target taxon × plot × event structural sessions and 273 response series.
- 47,360 tagged-animal histories (43,162 strictly single species-labelled, 4,095 unresolved within genus, 103 conflicting across genera), with 104,322 target capture rows.
- The original genus-MNKA 176 series with repeated abundance variation and 1,408 corresponding sessions.
- The fixed target-roster's **31 species** and **four species-group** concepts. The full NEON target taxonomy includes other species-rank concepts, considered legitimate *other congeners* when interpreting C.

**Results are structural predictors only, without any W, B or density–space slope:**

| Genus | Species-labelled sessions in >=3-event series | Sites | Series with joint F and C variation | FE rank (F,C) | Condition number | Decision at frozen thresholds |
|---|---:|---:|---:|---:|---:|---|
| *Peromyscus* | **948** | **33** | **74** | **2** | **2.27** | **Candidate predictor-feasibility GO only** |
| *Dipodomys* | 116 | 4 | 7 | 2 | 1.84 | STOP: <6 sites |
| *Chaetodipus* | 45 | 3 | 2 | 2 | 30.21 | STOP: multiple support criteria |
| *Myodes* | 75 | 5 | 0 | 1 | undefined | STOP: C has no independent variation |
| *Sigmodon* | 65 | 7 | 0 | 1 | undefined | STOP: C has no independent variation |
| *Microtus* | 30 | 5 | 0 | 1 | undefined | STOP: insufficient joint variation |

Every other genus also failed at least one originally locked support threshold; **only Peromyscus was a candidate**. That classification reflects the availability of two distinguishable historical **predictors**, not a replicated biological pattern, a test of competition, a W/B coefficient or adequate prospective power.

Within *Peromyscus*, of **993** strictly species-labelled target structural sessions, **378** have an observed resolved other-congener C>0 and **432** have an unresolved U>0. Of those sessions, 948 belong to series with three or more observations. After original taxon×site×plot, site×calendar-month and year fixed effects, the residual sum of squares is **33,921.94 for F** and **6,734.19 for C**, with residual correlation **−0.128** and two-predictor condition number **2.27**. Thus congener variation does not simply duplicate focal-species variation in the historical predictors.

**Field identification caveat:** U contributes **1,892 of 19,723** event-weighted genus-MNKA index units summed across *Peromyscus* species-response sessions (**9.59%**). This is *not* the fraction of genetically uncertain individual animals or a representative error probability; the same animal can contribute to multiple sampling occasions. A stable named species in NEON capture files is not proof of correct biological classification, particularly for cryptic *Peromyscus*. The 993/948 species-labelled cohorts and the original 956 W/B genus development cohort are different analysis universes and **must not be conflated**.

### Prospective ecological interpretation after the feasibility result

At high local small-mammal abundance, the sign of an observed W/B change could depend on whether that increase comes from additional individuals of the focal species or from another congener. This is a *new future test*, not an explanation demonstrated by the historical positive average or negative heldout. Wolff (1985), Dooley & Dueser (1990, 1996) and Casula et al. (2019) already studied congeneric/interspecific competition and density effects on rodent home ranges. Only a **validated comparison of the density response of both W and B under distinct F and C predictors**, replicated across new sampling events/sites, could be an empirical advance.

**Future confounding guard:** F and C rank-two identification was checked **after the original fixed effects, without conditioning on U**. A future W/B model that includes ambiguous-label abundance U as a separate adjustment may be less identifiable; it requires an *effect-blind rank/support test before any new outcome opens*. Likewise, detection conditioning through number of repeatedly captured individuals m is not automatic causal bias correction. Under-specification of taxonomy/observation process remains a stop reason, not permission to transfer unknown U records into whichever species favours the effect.

Authoritative record:
`results/conspecific_congeneric_predictor_feasibility_receipt_20261018.json` (CI run 39091740732, artifact 12122368661). No original 8-genus result, provisional holdout finding, MOSA source seal, or ecological publication decision is changed.


## Frozen follow-up: identificationQualifier-conservative predictor sensitivity (18 October 2026)

**Registered after the first F/C *predictor-only* result and BEFORE its qualifier-based source audit.** This sensitivity does not change the original result, eligibility rules, 8-genus inference or any already-consumed W/B outcome.

NEON's `mam_pertrapnight.identificationQualifier` is present in the source reader but was not used to declare resolved historical F/C histories. A single consistently named species can carry an explicit uncertain-identification qualifier; thus the 948 original Peromyscus sessions are best understood as *single-species-labelled structural sessions*, not 948 independently verified species identities.

Predeclare a conservative history rule independent of ecological responses:
- `qualifier_warning=True` for a captured target history if **any** of its raw captured NEON rows in the original complete 3-night standard-grid event universe has a nonblank `identificationQualifier` other than neutral missing markers `NA`, `N/A` or `NULL` (case-insensitive); `UNKNOWN` is a warning.
- A previously single-species-labelled history with such a warning moves from its species-specific F/C contribution into the same genus's unresolved U component for this **sensitivity only**; do not change its genus, source taxonID, linked animal ID, original effect data, or the 1536 structural session universe.
- Species-group and multi-taxon histories remain U. Cross-genus histories remain excluded. **N=F+C+U must hold exactly** in every eligible site×plot×event; no animal is counted twice.
- Reconstruct fixed-series predictor-only F/C rank, condition number and co-occurrence for every genus under the same original m/session/site threshold contract; write original-baseline candidate and qualifier-conservative candidate results side-by-side without replacing one with the other. Both are *historical predictor feasibility*, not ecological effects.
- Report total and per-genus warning-history counts, number of formerly species-labelled histories reclassified, and for Peromyscus adjusted F/C nuisance-FE rank, condition number, joint varying series, C>0 and U>0 sessions. No individual/tag IDs, actual species coordinates, W, B, Δ, home ranges or MNA×space associations may be exported.
- Never interpret a blank qualifier as genetically confirmed species identification, nor a warning as proof that the label is wrong. Independent taxonomic verification would still be required for future causal interpretation.

**Science decision:** this is an identifiability stress test, not an effort to rescue a favorable ecological coefficient. If qualifiers erase F/C independence, report STOP for species-specific interpretation on these historical field labels and do not weaken the predeclared limits.


## Verified identificationQualifier sensitivity: field labels and ecological limits

A *second* source-verified GitHub Actions audit [39092640551](https://github.com/zuizui0223/neon/actions/runs/39092640551) applied the above precommitted nonblank-qualifier warning rule **without any W/B or abundance–space outcomes**. All seven earlier source-free and three new qualifier-focused synthetic tests passed, and 1,707 original trap-night source CSVs had the actual `identificationQualifier` field. The original 1,536 target structural sessions, 47,360 tagged animal histories, 104,322 captures and every event's original genus N remained unchanged.

- **29,101** target capture rows and **13,868** tagged-animal histories had at least one nonblank explicit identification qualifier. Of the original 43,162 single-species-labelled histories, **11,832** moved conservatively into same-genus unresolved U (not reclassified as a different species). The aggregate unresolved history count became **15,927** instead of 4,095; cross-genus exclusions remained 103.
- In *Peromyscus*, the original field-labelled 948 sessions, 109 repeat series and 33 independent sites are unchanged as structural sampling units. **62**, rather than 74, series retain joint F/C variation. Resolved other-congener C>0 now occurs in **255** sessions rather than 378. U>0 occurs in **757** rather than 432.
- The F/C predictor matrix retains **rank 2**, conditional on the frozen taxon/plot, site/calendar-month and year nuisance effects, with condition number **3.02** (2.27 before this classification sensitivity) and adjusted F/C correlation **−0.022**. The exact precommitted **Peromyscus-only predictor-feasibility GO** therefore survives; no other genus passes all original fixed support gates.
- Across *Peromyscus* species-labelled sampling sessions, U's share of summed event-level genus-N contributions becomes **53.35%**, versus 9.59% for species-group/taxon-switch histories alone. This is **not** a 53% genetic misidentification rate, not 53% of distinct animals, and not a demonstrated ecological effect. It is the consequence of a deliberately conservative interpretation of explicit taxonomic doubts in repeatedly counted known-alive histories.

NEON explicitly defines `identificationQualifier` as recording *uncertainty* in the taxonomic identification (official [small mammal box trapping Quick Start Guide](https://data.neonscience.org/api/v0/documents/quick-start-guides/NEON.QSG.DP1.10072.001v1?fallback=html&inline=true)). Previous published *Peromyscus* range analyses treated field species uncertainty seriously; the present audit supplies no DNA barcode or genotype confirmation.

**Interpretation:** the spatial-ecology question is now physically and mathematically feasible in historical predictor data, but **the biology cannot yet be assigned confidently to conspecific vs congeneric crowding**. Before any prospective F/C×W/B fit, taxonomic validation or a declared sensitivity retaining U as a separately identifiable nuisance/uncertainty component is mandatory. Qualifier-conservative rank-two F/C **without** conditioning on U does not guarantee that the full F/C/U design is identifiable, nor does any rank test establish a causal interaction. Future independent NEON data must pass that prior-to-outcome decision; negative or unsupported support must be reported as STOP rather than tuned away.

Source receipt: `results/conspecific_congeneric_qualifier_sensitivity_receipt_20261018.json`. The original failed generality and provisional heldout tests and the MOSA effects seal remain unchanged.
