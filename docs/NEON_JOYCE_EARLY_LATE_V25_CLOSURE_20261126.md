# V25 closure — matched early-to-late prediction ready, source access STOP
26 November 2026. Joyce et al. (2024), DOI 10.1111/btp.13381, Dryad DOI 10.5061/dryad.05qfttfb9. Original methods and repository README confirm seed additions, early retention at 7–11 weeks and final living seedling counts at 12–15 months. 3024 offered seeds in 368 early records, 2880 in 352 final records. Sixteen quadrats lost at site HB following land-use change; no final imputation. Exact calendar month and species confounded; within-landscape site holdout only. Original authors already measured smaller final than early exclusion effects; no novelty claim from aggregate effect comparison.

Frozen design and executable pipeline commit 1fc333fb059ee840c2e2a9b3e3266e5d20263692. Run [45719995840](https://github.com/zuizui0223/neon/actions/runs/45719995840), job 139575612001, artifact 15071472172, reported ZIP SHA256 d47906aa2873d2aaae6dea5ae962da5f972f7543b90903a34645fc7ef2a3934c. Dryad API metadata version 3 and advertised public file-stream links verified, but every download returned HTTP403. Outcome gate closed. Workflow completed normally to record source STOP, not a scientific success. No raw source accepted or fit run. Do not attempt access bypass, repeated URL guesses, or replace the held-out test with published aggregate means.

## Exact external input required
The two original CSVs from the public dataset are sufficient for the locked primary prediction. The optional predator detections file is inventory only, not part of the primary model. Verify user-supplied bytes against the provider's SHA256 and exact sizes:

| File | Bytes | SHA256 |
|---|---:|---|
| seed_predator_detections.csv | 12967 | 9306def6d93b620a54d815ad5589d4688d54c46d38212359230d25077a079302 |
| seed_removal.csv | 13364 | 0a9fe6484953b591bb03fca3d0a20cfbf2fff553cbed28f4c12dfeb4a8be15c2 |
| seedling_establishment.csv | 12754 | a1b34061fb5703fe32b31bff15e0b165dcde28943c5e036a8f86d736c3cee183 |

Preserve exact keys, offered denominators and HB deletion. If the supplied files differ from these version-3 checksums, validate their version and source documentation separately before interpreting. README omits the exclosure field for the establishment table although study design and lost-quadrat note imply treatment; the actual column must be verified, not inferred. No confirmed early predation indicator: remaining seeds at a quadrat are an observation, not necessarily true survival; late seedling count is not an individual-level linked fate. Camera detections and natural resource supply have not been included in the model. No seasonality claim.

## Decision
Stop the sequence of new source acquisitions after repeated public-source access failures across projects. One useful externally provided input is the complete original Dryad ZIP for this study. V23's 4 landscapes/8 endpoint register remains unchanged. No new biological result or prediction performance. DRAFT/SUBMISSION HOLD, no merge/submission.