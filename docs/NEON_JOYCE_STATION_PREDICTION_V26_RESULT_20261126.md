# V26 empirical held-site-out test — mean gain, frozen gate not supported
26 Nov 2026. Joyce et al. 2024 Biotropica DOI 10.1111/btp.13381, Dryad DOI 10.5061/dryad.05qfttfb9. User supplied original version-3 ZIP; all six members matched pinned provider byte sizes and SHA256. Archive SHA256 334a72b18767888ae339504777837f8c04ed53301ae9fa9703c5747ae9702b03. Raw ZIP not committed.

## Source reconciliation and pre-outcome design
Original V25 strict parser stopped on the source: early table includes three N=9 records, final header exc rather than exclosure; actual final N=2879 rather than 2880, seven retained row denominators differ. All 352 final keys match early keys after documented arm-label crosswalk; 16 missing rows at HB as in README. Preserve strict V25 STOP. Separate V26 pre-outcome lock 3ddff290f44afbca90d63aecd8e8046bd7718b03: equal-station-weighted caged-minus-exposed rates at each stage using each observed denominator, all 176 pairs and 44 site×species×forest groups, 8 final physical sites. Original V25 held-site scoring and 75% gate unchanged. No imputation. Locally executed V26 script Git blob 88a01b9f9baca6a52d08bdacf708314b4e337e63 exactly matched committed source; unchanged V25 fit_score and parse_verified functions copied locally. Replay identical JSON bytes; derived 44 records archived and scores independently recomputed in JS (RMSE agreement <1e-12).

| Model | Equal-site RMSE |
|---|---:|
| Species × forest type stratum baseline | 0.247282 |
| Unchanged early contrast | 0.281410 |
| Baseline + early retention contrast | 0.200203 |

Mean RMSE reduction vs baseline 19.0383%; augmented beats both baselines. 5/8 sites improve vs stratum baseline (required ≥6/8). **Frozen joint gate NOT SUPPORTED.** Positive fitted within-stratum early slope in all eight training sets (range 0.3698–0.5413), but training sets strongly overlap and this is not independent replication. No claim of significance or stable transfer. Individual site errors are in the receipt. Denominator-matched-only sensitivity STOP: excluding seven affected station pairs leaves three contexts with only two stations, below locked minimum 3. No tuning or altered inclusion criteria.

## Interpretation
This is actual retrospective within-landscape prediction of a recorded treatment contrast in established seedlings using an earlier recorded treatment contrast in retained seeds, not confirmed predation, linked individual survival, causal mammal dispersal, net recruitment or seasonal generalization. Plant species and sowing month confounded; cage excludes vertebrates, not just mammals; no resource or independent consumer covariates used. Mean improvement is useful descriptive evidence, but the fixed reproducibility test failed and sensitivity could not run. Do not label the primary outcome GO or independent ecological confirmation.

All source and earlier synthesis stops remain. If pursuing predator observations, a genuinely distinct pre-effect design should use independently measured and effort-corrected camera detections to predict late contrasts and compare with the existing models; camera observation times, cohort keys and sparse support must first be verified, no post hoc selection to rescue V26. No merge/submission.