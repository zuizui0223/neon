# NEON × Structural island-mammal cross-scale ecological bridge — evidence-limited design (7 November 2026)

## Decision and scope

**The two projects can connect through a falsifiable cross-scale ecological question, but they are NOT independent replications and their old results must not be pooled.** This note is a cross-repository scientific design handoff, NOT a newly estimated empirical effect, manuscript merger, or method-only publication. Keep the one unified NEON small-mammal macroecology manuscript in Draft/SUBMISSION HOLD and the Structural global-mammal scientific HOLD intact.

> When organism/population identity, local occupancy state, or source availability changes, under what conditions does the spatial arrangement of ecological opportunity retain predictive information, and when can replacements preserve an apparent spatial role?

Key reason for the bridge: NEON documents an observational taxon-to-capture-station recurrence despite nonshared tagged individuals; Structural shows conditional source-configuration information for sparse mapped island-mammal species but does not validate temporal rescue, a realized dispersal graph or irreplaceable donor territories. These are different manifestations of **reference-conditioned spatial organization**, not equivalent causal mechanisms.

## Exact empirical comparisons and boundaries

| Evidence class | NEON local small mammals | Structural global island mammals |
| --- | --- | --- |
| Space | 90×90m grid, 100 official named live traps | 5,401 island units; 1,275 pilot and 4,126 heldout island units |
| Source/response | Three-night NEON original RELEASE-2026 individual capture records; station×genus apparent structure | IUCN-2017 range polygons mapped to island polygons with manual revisions and some historical/now-extirpated native labels, not independently surveyed current animal occurrence |
| Positive original conditional pattern | 58 strict adjacent-season comparisons / 30 plots / 14 independent physical sites; fixed-margin corrected mean genus-associated same-station Z=+0.794664; 11/14 site means positive; nonshared observed animal tags | 529 ultrarare species (1–4 pilot-positive island cells); presence-specific heldout C−R3 log-loss = −0.596259, block CI [−0.743855,−0.464457]; geography-derived original kNN graph better than 20/20 matched rewired graphs, original−rewired C = −0.058525 |
| Independent/exploratory breadth | Exactly-two genus group 150 informative pairs/30 sites, exploratory Z=+0.614711 and 25/30 positive site means; not new biological detector | 96 mapped rare (5–12 pilot cells) did not replicate overall source-network effect or topology specificity; 79 higher-occupancy species have exploratory overall source-context gain without specific observed kNN advantage |
| Important negative correction | Beyond exact same trap, 10m neighboring-station recurrence after season-key reused-site exclusion Z=+0.182589, p=0.220539; true habitat use and genus-dependent station catchability remain unseparated | Mean rewired C accounts for ~90.18% of original C-vs-R3 *point-estimate* improvement; only ~9.82% is original-graph-specific under this matched-null family. This is **not** a causal variance decomposition. |
| Spatial source redundancy | Individual turnover without loss of taxon-specific *recorded* trap association. DO NOT call individual animal a dispersal source or source-island node. | Response-free v1.181 source-identity turnover alpha/beta analysis mean actual-minus-null beta = −0.2620, 95% CI [−0.3167,−0.2076], i.e. source influence is more overlapping than matched-null placements, NOT demonstrated distinct irreplaceable source territories |
| Direct mechanism validation | 30/58 original season comparisons have both actual dated CHM pixel support and two field-plant visits (12 sites, 19 grids), but plant base plots generally ~150±50m offset from mammal traps; 53/58 comparisons use the same aerial source month across seasons. Camera observations near original trap stations in the published external source had ZERO simultaneous original trapping-day matches; independent genus-detection p remains unknown. | Source-adjacent constructed kNN graph is **not an observed movement network**. The mapped mammal response contains shared polygon provenance, and external species×island independent field validation is not admitted (v1.196 scientific HOLD). Temporal BALA arthropod test for source-loss consequence C−R2 = +0.000674, CI [−0.02130,+0.02558], did NOT support the prespecified claim; different taxa/system. |

Evidence authority:
- NEON: results/neon_uniform_null_correction_receipt_20261020.json; results/neon_exact_two_genus_ecological_receipt_20261025.json; results/neon_macro_10m_patch_conditional_20261025.json; results/neon_exact_joint_chm_plant_source_receipt_20261028.json; results/neon_zenodo_camera_independent_source_receipt_20261029.json
- Structural: https://github.com/zuizui0223/Structural/blob/main/docs/OCCUPANCY_REGIME_ISLAND_ECOLOGY_SYNTHESIS_V1_119.md
- Structural graph and polygon semantics: https://github.com/zuizui0223/Structural/blob/main/development/global_mammals_graph_semantics_audit_v1_185.json and https://github.com/zuizui0223/Structural/blob/main/development/global_mammals_response_ontology_audit_v1_187.json
- Graph effect accounting: https://github.com/zuizui0223/Structural/blob/main/development/global_mammals_graph_gain_accounting_v1_197.json
- Redundancy/target-space turnover: https://github.com/zuizui0223/Structural/blob/main/development/global_mammals_distributed_irreplaceability_freeze_v1_181.json
- Independent biological admission: https://github.com/zuizui0223/Structural/blob/main/development/independent_biological_evidence_admissibility_v1_196.json

## Main cross-scale ecological model: identity turnover versus spatial-role redundancy

The interesting tension is **NOT** that island sources and NEON trap stations are the same biological unit: they are not. Rather:

- At NEON's *organism identity* level, nonshared recorded animal identities can coexist with genus-specific recurring capture locations. A taxon's apparent spatial role persists despite turnover in observed individuals. But the observation process or persistent habitat may generate this.
- At Structural's *population-source position* level, source placement carries more mapped occurrence information when pilot positives are very sparse; individual island sources also show overlapping modelled target-space access, not uniquely irreplaceable territories. But this does not show observed present-day source populations or demographic rescue.
- A nontrivial future explanation is **spatial role substitutability**: spatial organization can remain stable across replacement of carriers if alternate carriers or sources cover the same functional opportunities; dependence on exact position rises when effective alternatives are limited. Crucially, functional substitution and temporal rescue are currently hypotheses in both systems.

### Candidate hypotheses for genuinely unseen datasets

**H1 — Role substitution under turnover.** After holding total taxon detections, station operability, habitat, regional conditions and observation method fixed, *newly observed individuals* retain a taxon-specific station-use distribution when suitable habitat opportunities are stable. A confirmatory independent detection stream must distinguish true use from repeated trap catchability; NEON historical observation alone is insufficient.

**H2 — Opportunity scarcity changes dependence on configuration.** The predictive increment from a specific source/opportunity configuration over a strong conditional reference is larger when the number of genuinely available alternative source populations or habitat patches is smaller; this is NONMONOTONIC until shown otherwise. NEON cannot import Structural's 1–4/5–12/≥13 island-species thresholds or infer habitat-patch counts from camera/trap encounters. The first such local test would be on a *prospectively fixed NEW cohort*, with sample-size-conditioned genus/trap station nulls and independent detection effort.

**H3 — Spatial-role signal must survive a stronger observation/geometry reference.** Constructed graph proximity plus shared range polygon provenance may inflate Structural's apparent island role signal; stable local trap catchability may inflate NEON's exact-station recurrence. The new nulls must preserve biological sampling opportunities appropriate to each system (source-aware geography/rewired kNN for Structural versus six-night functioning/source-season/site conditioned station opportunities for NEON). A cross-system prediction is that nominal structural signals can disappear when an adequate observation/reference layer is added. This is a falsifiable possibility, NOT a confirmed finding.

## Non-equivalence and cross-paper comparison plan

Do not pool or compare raw Z with log loss. Define only a *conceptual* common test: does a prespecified spatial representation add independent or heldout information beyond the strongest feasible appropriate reference? The estimands are distinct:

1. NEON: conditional genus×station **capture** recurrence across heldout seasons; standardized fixed-margin Z; independent field detector effort and true local habitat use required for mechanism attribution.
2. Structural: source-aware R3 vs constructed C incremental heldout binary log loss on **map-derived** island-species occurrence labels, and original kNN C vs degree/length-matched surrogates. Independent species-by-island field observations required for biological occupancy confirmation.
3. Temporal ecological consequence is a **third endpoint**: newly lost source positions and independent later 0→1/1→0 field-state transitions with repeated detection; this cannot be inferred from either dataset's static or same-visit association.

The two empirical denominators are independent but the biological evidence is NOT a validation pair: local within-site NEON trap captures versus global derived island species range labels; ecology, sampling effort and observation process differ. NEON's unrelated 2018–2020 Norway external camera study has different 30-day pre-capture versus three-day trap windows and is not a rescue of the missing same-date detector source.

## Action and scope decision

**NOW:** preserve this crosswalk as the common higher-level hypothesis only. Keep separate single primary paper per repository, do not create an additional methods paper, do not refit the already-inspected NEON 58/158 seasonal comparisons or Structural 529/96/79 species heldout outcomes, do not reopen Structural's pristine 5,592-island mammal response, and do not retune previously failed density/10m/operability/weather/source-loss/eBird controls.

**FUTURE:** before seeking another p-value, freeze a dataset-independent joint admission rubric:
- own observation denominator and evidence class;
- time-resolved true animal occupancy/use versus protocol-positive detection;
- measured source identity/habitat availability and explicit spatial support;
- spatially independent heldout blocks, enough positive and negative response opportunities;
- strong conditionally sufficient reference and original null family specified before outcome;
- separate tests for source opportunity structure, organism-level role substitution and later temporal persistence;
- stop the causal claim if direct field evidence or independent detection channel is missing.

A future cross-system synthesis might then ask: **When do interchangeable carriers preserve ecological spatial organization, and when do noninterchangeable source positions make configuration matter?** That is a potentially original macroecological paper question, but NOT something the two historical results have yet established.
