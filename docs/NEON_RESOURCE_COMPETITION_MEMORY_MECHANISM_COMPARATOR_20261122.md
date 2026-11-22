# Which ecological mechanism is demonstrated? Resource, interactions or memory — corrected evidence ledger, 22 November 2026

**Scientific goal:** determine what maintains taxon-associated mammal space use despite individual turnover. This is ONE NEON ecology study, Draft PR #23; submission HOLD. The results below distinguish *proven published external interventions* from *present NEON capture-record associations* and from *source feasibility only*. No incomparable effect sizes are pooled.

## 1. A useful NEGATIVE/source boundary in the 2026 small-mammal seed study

Original Merz, Record & Mortelliti (2026), *Ecology* DOI `10.1002/ecy.70312`; Figshare `28207769 v2` five MD5-pinned original CSVs, already passed corrected **288-station + 3 exact summary rows** source v2 and **2,077** event-to-capture original PIT×GRID×year matching records. These source matches are OBSERVATIONAL source availability.

The follow-up gate `docs/NEON_FIGSHARE_2026_PRIOR_PATCH_VISIT_SOURCE_GATE_20261122.md` was locked before any source return-visit support was read. It used exact original `Grid×Site×Session×Night×Visit.ID` source composites, not raw seed-interaction rows. [Actual original source run 45012285913](https://github.com/zuizui0223/neon/actions/runs/45012285913) found:

| Source grain, not a new ecological effect | Actual exact original record support |
|---|---:|
| Original seed-interaction source rows | 3,243 |
| Original distinct station-night-Visit.ID composites | **2,079** |
| Composites with unambiguous original PIT | 1,348 |
| Composites with consistent PIT + original Date + original Time.start and parseable clock | **843** |
| Distinct PITs found again at same literal Grid×Site on a LATER source calendar date | **28** across 6 forest grids |
| Later composite visits at an already encountered literal Grid×Site with source numeric observed seed metadata | **317** |

But source consistency for PIT-identifiable composites was only **843/1,348=62.54%**, FAILING the predeclared **80%** source GO requirement. All other predeclared source thresholds passed (≥15 PIT with separate station-night visits, ≥8 literal patch returning PIT, ≥3 grids, ≥50 later source visit rows with observed seed metadata, ≥20 grid-session-night with alternative stations). This remains **SOURCE_REPEAT_PATCH_SUPPORT_STOP_NO_LEARNING_ESTIMATE**, NOT a null biological effect. Of 843 clean composites, 615 also matched original station `Date` exactly, underscoring the earlier published date ambiguity. A literal `Site` label does not on its own validate a stable physical feeding patch across several sessions.

The original published `Main Analysis - Clean.R` (file ID 51823913, 68,819 bytes, original published MD5 `b5f99bfd6b800cdecb435dfb23f6e6b9`) was separately fetched and checksum-verified WITHOUT running the published outcome models. [Static source audit 45012422647](https://github.com/zuizui0223/neon/actions/runs/45012422647) found **no literal code use of `Visit.ID`, `Time.start` or `Time.end`**, while `Unique_station_ind_ID` is used in 24 lines and `First.Visit...` fields in 54. Thus the original published model does **not** supply a code-validated declaration that one 5-field `Visit.ID` composite is one chronologically identifiable independent animal visit. Do not infer learning from the 317 repeated composites or try to rescue the failed 80% source threshold by retaining favorable subsets.

**What small-mammal source actually measures:** visitation and seed searching at provisioned seed stations with potentially repeated marked animals, original offered/remaining seed states and source-event metadata. The main ecological effects of resource abundance, personality and community richness were already published, so are PRIOR ART. Natural standing food biomass, risk-free independent camera effort and experimentally randomized remembered rewards are not observed.

## 2. POSITIVE resource manipulation comparator: 25 source animal-years of GPS-tracked roe deer

To show the kind of evidence that *can* causally isolate one mechanism, we reproduced a separate **already published** resource-access experiment, Ranc et al. (2021), *PNAS* DOI `10.1073/pnas.2014856118`. The original study changed access to known food resources while monitoring collared deer, and originally fitted separate omniscience, perception and memory models. We did not republish or refit the original memory model.

Original publicly archived repository `ranc-n/Ranc-et-al.-PNAS-2021` Git pinned tag v1.0, commit `58cd85c863d50346df0c7b0d3ecfde97f8a5dfdb`; original hourly source Git blob SHA1 `18bebe5527828a9ff975d3f35c6b7553d67a3064`, original initialization blob `918f5b981b4dc55c71347549d72815cf0b8db497`. Source had **26,841 hourly records** for **25 original animal-year trajectories**, each exactly `resource M accessible (1) → closed (0) → reopened (1)`. State `M` means location at manipulated food station, NOT actual eating when inaccessible; invalid state code `-9999` was excluded (109 hour records) and not imputed into vegetation. No GPS coordinates or identifiers released in NEON artifacts.

| Same source animal-year equally weighted mean | Food resource site M | Alternative food station A | Vegetation V |
|---|---:|---:|---:|
| Before closure, resource accessible | **31.262%** | 2.964% | 65.774% |
| Closed, resource inaccessible | **5.173%** | 15.239% | 79.587% |
| Reopened, resource accessible | **19.557%** | 8.203% | 72.240% |

The original manipulated-site use fell **−26.089 percentage points** from before to closure (25/25 animal-year series negative) and rose **+14.383 points** when reopened (22/25 positive), while post-reopening M occupancy remained **11.705 points below** preclosure average. These are DESCRIPTIVE time series averages, not tests on 26,841 independent animal samples and not 25 guaranteed independent roe deer.

[Original source-locked GitHub Actions 45012781533](https://github.com/zuizui0223/neon/actions/runs/45012781533) passed **7 synthetic tests**, provider original Git commit and two Git blob checks, reproducing the previously published ~31%→5% closure effect. Original [PNAS paper](https://doi.org/10.1073/pnas.2014856118) already reports resource manipulation and uses a mechanistic comparison to support memory over perception/omniscience, with reported resource-attribute and reference memory half-lives around 0.9 and 5.6 days. Our SOURCE state-fraction tabulation **DOES NOT reproduce that mechanistic memory-vs-perception likelihood comparison** and therefore does not independently establish cognitive learning. This is a **published positive control for experimentally established resource dependence**, not a novel NEON mammal ecological effect.

Machine receipt: `results/neon_ranc2021_original_resource_closure_positive_control_20261122.json`, frozen plan `docs/NEON_ROE_DEER_RESOURCE_CLOSURE_POSITIVE_CONTROL_FROZEN_20261122.md`, original-source script `analysis/reproduce_ranc_2021_resource_closure_state_use_v1.py`.

## 3. Correct research decision for the three candidate mechanisms

| Hypothesis | What actually holds | What is NOT established for NEON |
|---|---|---|
| **Resource access** | Experimentally altered food availability can strongly reorganize SAME-animal space use in roe deer (published positive control) | Whether original NEON small-mammal same-station genus recurrence is driven by local seed/food biomass; Portal plant-count×competition coefficient reverses when 2022 is omitted |
| **Biotic interactions** | Portal kangaroo-rat exclosures provide context but 2020–25 observational plant-change association is highly year-dependent and cannot isolate competition | A stable, geographically general competitive spatial template underlying NEON's site Z |
| **Learning and spatial memory** | Original Ranc et al. paper uses experimental cue/resource manipulation and mechanistic memory-vs-perception comparison supporting memory in roe deer; small mammal original source has repeated *recorded* PITs | Any NEON learning coefficient or social spatial fidelity. Original small-mammal Visit.ID sequencing gate fails 80% consistency and same SITE label might not mean same stable patch |
| **Observation process** | Original Merz station source is 288 unique nights + 3 summary footers, 2,077 PIT-source matches; Gu seed-fate source has independent actor-versus-fate missingness | A calibrated individual/site-level probability of actual spatial use versus trap/camera observation; recorded positives and missing seeds are not exhaustive visits |

**NEON's publishable biological principle remains to be tested, not confirmed:** Distinguish true species/taxon location recurrence with individual turnover from repetition induced by persistent resource placement, interference by other organisms and learned remembered resource locations. Published field resource manipulation shows that space use can reorganize even without turnover, providing a counterfactual benchmark for NEON rather than proof of its generality.

## 4. Clear next external-data admission gate

Do **not** continue post hoc subsetting of the Merz 2026 `Visit.ID` source or invent site-visit order. A genuinely valid test needs spatially stable patches with independent resource observations at times BEFORE each actual animal choice, simultaneous known alternative stations and independent camera uptime, plus actual marked identities/competitor context or manipulation. One intended mechanistic comparison:
`independent held-out site-year prediction of real animal use ~ contemporaneous accessible food + competitor context + tracked pre-choice patch experience`.
The experience term is only called learning if reward relocation or cue reversal was randomized and on/off detectors independently verified. A marker-specific positive in one single study forest is not transferable generality.

**Editorial state:** README and unified manuscript retain all original positive/negative NEON/Potal/Finland results unchanged; integrate this as a mechanistic evidence-boundary note only, not a second paper, an abstract claim or a new animal-law assertion. Draft / **SUBMISSION HOLD**.

## Exact audit receipts

- `results/neon_figshare_2026_repeat_patch_visit_source_STOP_20261122.json`
- `results/neon_figshare_2026_original_R_visit_ontology_20261122.json`
- `results/neon_ranc2021_original_resource_closure_positive_control_20261122.json`
