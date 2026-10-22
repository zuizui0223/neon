# When relatives become neighbors: what changes inside individuals and among their centres?

**Ecological hypothesis spine (18 October 2026).**
A distinct *prospective* question generated after the original NEON eight-genus development hypothesis FAILED its registered 6/8 criterion and its provisional Peromyscus held-out positive-sign prediction did not replicate. **No new F/C × W/B outcome has been opened.** The prior manuscript and its negative conclusions are unchanged.

## Question one can explain without a statistical recipe

Two mammal populations can have the same number of animals of one focal species but different numbers of related species sharing the trapping grid. Do they accommodate that difference by changing how far *each individual* ranges among trap stations, by changing where the animals' observed centres are distributed, or not at all?

The *ecological unit* is a focal small-mammal species repeatedly sampled in comparable seasons at the same site and plot. The unit of space is the actual fixed NEON trap-grid scale; no claim is made about full home ranges or undisturbed activity centres.

## Four density-response components, one pre-specified ecological contrast

Within a new, response-unconsumed sample define:

- `F`: species-labelled, adequately taxonomically validated focal conspecific minimum number known alive (MNKA).
- `C`: independently captured, adequately validated *other species of the same genus* at the same site/plot and event, counted as known alive.
- `U`: genus-known but species-uncertain captured animal histories (including explicit species-group assignments and ambiguous identification qualifiers). **Never split U to whichever category improves an effect.**
- `W`: variance of repeated, trap-observed locations within captured animals, using the original three-night spatial statistic; and `B`: centroid-debiased variance among those captured animals' observed centres, on the same m² scale.

The future observational model must estimate W and B against **F and C simultaneously**, with U handled by a separately frozen nuisance/sensitivity contract. Define the four coefficients:

| Density source | Within individual W slope | Among observed centres B slope |
|---|---|---|
| **Focal conspecifics F** | β(F,W) | β(F,B) |
| **Congeneric heterospecifics C** | β(C,W) | β(C,B) |

Define Δ(F)=β(F,B)−β(F,W), Δ(C)=β(C,B)−β(C,W), and the focal biological contrast Θ=Δ(F)−Δ(C).

**Primary question:** Is Θ distinguishable from zero under replication across sites? Use an explicitly two-sided hypothesis. A positive Θ would mean that an additional *observed known-alive* conspecific relates more strongly to the relative between-versus-within spatial allocation than an additional congener, not that it causes more territorial avoidance. Negative or null contrasts remain substantive possible outcomes.

A biologically useful distinction requires the **signs and magnitudes of W and B components**, not only Θ. One species could show within-individual contraction while among-centre dispersion remains constant, whereas adding congeners could affect the centroid arrangement but not individual use. Both could instead produce identical associations—or none after detection/season controls.

## Why this is not already answered

**Not new:** Wolff (1985) and Dooley & Dueser (1990, 1996) investigated interspecific interactions in *Peromyscus*; Casula, Luiselli and Amori (2019) directly compared conspecific versus other-species and total-density home-range associations in coexisting *Apodemus flavicollis* and *Myodes glareolus*, reporting home-range contractions associated with conspecific density. O'Fallon et al. (2025) used 2,420 NEON *Peromyscus* individuals to confirm density-associated home-range contraction under habitat/latitude/sex effects. Hence neither home-range shrinkage nor the distinction between intra- and interspecific density is original.

**Unanswered targeted gap:** Does the *source* of local mammal abundance modify the **joint response of within-captured-animal coordinate variance and among-captured-centre variance**, in the same physical coordinate system under replicated short sampling windows? Existing home-range or overlap endpoints cannot uniquely separate these two observed components. This is a potentially distinct empirical test, **only if independently reproduced**.

## Initial ecological feasibility evidence, NOT an ecological effect

The unchanged historical NEON RELEASE-2026 capture identities yield 948 species-labelled *Peromyscus* sessions in >=3-event series, 33 sites, 109 such series, and 74 with both conspecific and congeneric index variation. After nuisance fixed effects, the F/C predictor matrix has rank two and condition number 2.27, with residual predictor correlation −0.128. Among all 993 species-labelled candidate sessions, C>0 occurs in 378, U>0 in 432. The unresolved fraction of summed genus MNKA contributions is about 9.59%. The all-history predictor-only audit reproduced 1,536 original target structural sessions and 47,360 tag histories exactly. **These are observation-support statistics, not results for W, B or Θ.**

No other genus passed *all* frozen feasibility criteria: *Dipodomys* supplied variation at only four sites, *Myodes* and *Sigmodon* lacked independently varying resolved congeners. The temptation to select Peromyscus on the strength of its old W/B positive developmental slope is prohibited; it was prioritized because its ecology and cryptic species taxonomy make F versus C meaningful **before** any new F/C spatial response is observed.

## Barcode source validation status: not yet a genetic species classification

The original archived **COI barcoding data product** (DP1.10076.001) has been matched to box-trap `earSampleID`s using verified source files: 9,646 sample keys matched to both original BOLD taxonomy and voucher tables; 4,781 *Peromyscus* tag histories were unambiguously linked. Among *Peromyscus* histories with collected ear samples, this is 25.0% source-link coverage; it is **not** sequencing-based taxonomic validation and cannot be extrapolated to all captured individuals. In the original barcode taxonomy table **all 10,414 source records specify `identificationMethod=morphology`**, and 523 of the matched archive/field `taxonID` metadata values differ. Those are label differences, **not genetically established misidentifications**.

A preregistered single-sample BOLD public v5 API probe stopped with **HTTP 403** before any independent COI sequence could be obtained. This establishes a source-access dependency, not a biological absence of sequences. BOLD's public documentation permits a sampleID → public process/sequence query, and NEON states the underlying data are publicly available in BOLD, but the end-to-end molecular join is **not demonstrated** on the current authorized runtime.

Accordingly, neither a historical species-specific W/B effect nor the prospective focal-versus-congeneric Δ contrast has been estimated. For the next ecological study, verify whether a barcode record includes an independent molecular call with adequate COI quality and reference coverage, and use an explicit mitochondrial-introgression/hybrid caveat for cryptic *Peromyscus*; avoid treating archived morphological classifications as DNA confirmations. See the source-specific decision records `results/neon_barcode_capture_sample_key_linkage_receipt_20261018.json` and `results/neon_bold_public_coi_single_sample_probe_receipt_20261018.json`.

## What would distinguish biology from the observation process

The index `F` can vary because more marked conspecifics are truly present, because trapping/detection changes, or because taxonomic labels change. This is not the same estimand as density from independent spatial capture–recapture or telemetry. The focal response W/B is conditioned on which animals are caught repeatedly and itself can change with individual behaviour, trapping differences or community turnover.

A defensible prospective design must have all of:
1. Truly new NEON **event and night IDs** absent from both consumed RELEASE-2026 and previously opened 2025–2026 provisional observations; an immutable file/release manifest and frozen taxonomy corrections must be retained.
2. Species confirmation or predeclared credible ID-quality handling for cryptic *Peromyscus*, including all explicit `identificationQualifier` warnings and rank-species-group codes; stable species labels alone do not validate biological identity.
3. Within-species, within-site/plot repeats during comparable calendar seasons, with **independent residual variation in F and C** after the unchanged nuisance variables and any U handling. Multiple events in one series do not create new independent sites.
4. Detection and cohort-size sensitivity established before W/B unsealing, preferably calibration with independent known-animal detection or position data; adjusting for repeated-capture m is not automatically bias-free.
5. Joint intervals for β(F,W), β(F,B), β(C,W), β(C,B) and Θ using appropriate site/series clustering, preserving effect signs and negative results. Declare minimum effective site and season-synchronous contrasts *before* future outcome exposure.

## Freeze / exit conditions

- A predictor-only F/C rank-two GO on already consumed historic events authorizes **future-study design only**, not historical W/B re-analysis to rescue the failed original paper.
- Any qualifier-conservative source audit that removes enough resolved history variation to lose rank or geographic replication is an **identification STOP**, not permission to lower m/site/series thresholds or ignore taxonomic uncertainty.
- A subsequent genuine follow-up with weak within-species variation or a null Θ must remain a reported negative/non-identifiable finding, not recoded post hoc as territoriality or an environment-mediated signal.
- The original eight-genus generality rule stays **FAIL (5/8 of 6/8 required)**; the provisional Peromyscus positive sign was **not reproduced** with wide confidence bounds; full five-genus follow-up **not estimable**; MOSA's spatial ecological response stays SEALED.

## Source records and references

- `docs/CONSPECIFIC_VS_CONGENERIC_CROWDING_NEXT_GENERATION_20261018.md` — frozen predictor-only test, original threshold and source-literature boundary.
- `results/conspecific_congeneric_predictor_feasibility_receipt_20261018.json` — original-source verified feasibility (GitHub Actions 39091740732).
- `manuscript/NEON_MAMMAL_DENSITY_SPACE_ECOLOGY_V0_2.md` — original failed generality & imprecise holdout; a **separate** negative-result working manuscript.
- Casula et al. (2019), *Basic and Applied Ecology* 34:46–54, https://doi.org/10.1016/j.baae.2018.11.002
- O'Fallon et al. (2025), *Oecologia* 207:98, https://doi.org/10.1007/s00442-025-05731-2
- Wolff (1985), *Canadian Journal of Zoology* 63:2657–2662.
- Dooley & Dueser (1990), *Ecology* 71:788–796; (1996), *Oecologia* 105:81–86.

**Paper status:** *Prospective question only. No cross-scale density-source ecological effect estimated. Not submission-ready.*


## 19 October 2026: direct same-total composition comparison is not supported conservatively

The new fixed-N, fixed-U ecological question has been checked against the
original NEON source without fitting a spatial response. The original
948-session Peromyscus cohort, 109 repeated taxon×plot series and 33 sites
remain unchanged.

The baseline and qualifier-conservative two-predictor models both remain
algebraically **identifiable after adjusting for U**: conditional F/C rank
2, full F/C/U rank 3, and conditional information attributable to about
9.23 or 7.63 site-equivalents, respectively. These are **not biological
effects**, and the actual 33 physical sites carry uneven predictor
information.

However, a literal same genus-N, same uncertain-U, same focal taxon,
site, plot and calendar-month-of-year contrast with **different F/C** is
supported by only **four unordered original-event pairs, in two physical
sites, representing eight of 948 sessions** under the baseline field
labels. After conservatively treating explicit identification qualifiers
as U, **zero such pairs** remain. When the month-of-year restriction is
removed, the baseline has 18 pairs and the conservative source has just
one, but the lone conservative pair spans different calendar months and
must not be called a season-controlled replicate.

This distinction must drive the paper, rather than additional method
development. **The historical dataset supports a linear model coefficient
by borrowing identifying variation across N/U configurations; it does
not supply a direct, conservative matched neighbour-substitution
comparison.** This does not mean the fitted additive model necessarily
extrapolates *outside* the convex range of observed F/C/U, and does not
prove no biologically relevant effect; it means matched evidence is absent
under the exact precommitted criterion.

**Decision:** historical predictor-only rank GO, but **direct
fixed-total ecological observation support STOP** for the
qualifier-conservative model. Do not open historical consumed F/C×W/B to
claim a confirmed mechanism. A new study must obtain independent focal
species populations with validated identity and genuinely comparable
F/C composition shifts at fixed total/capture condition, ideally through
standardized repeated and independent sites or manipulative density
trials, before assigning ecological mechanism to the relative W/B
responses.

Documentation and reproducible source receipts:
- `docs/NEON_U_ADJUSTED_FIXED_TOTAL_SUPPORT_CONTRACT_20261019.md`
- `results/neon_u_adjusted_fixed_total_predictor_receipt_20261019.json`
- `results/neon_fixed_total_literal_composition_support_receipt_20261019.json`
- GitHub Actions 39202315974 and 39202963828.

The registered new `Θ` is unchanged and has **not been estimated on real
spatial responses**; previous original 6/8 genus generality failure,
imprecise Peromyscus nonreplication, and sealed MOSA effects remain unchanged.

