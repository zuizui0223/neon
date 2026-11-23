# Original NEON canopy-affinity source replay: REST stop and diagnosis

**2026-11-24 JST — scientific status: SOURCE STOP / ECOLOGICAL RESULT NOT OPENED.**

## Frozen ecological question (unchanged)

For source-distinct adjacent-season genus capture sets in the original `RELEASE-2026` small-mammal cohort, does genus-associated canopy-height affinity recur **at different original B-season trap positions**, excluding every same-genus A/B identical station from the B score? Fixed cohort: 58 original pairs (30 plots, 14 physical sites); prior source-only AOP qualification: 36 pairs (21 grids, 12 sites), 51 checksum-verified CHM tiles / 24,600 station-date pixel samples. The original pre-outcome 22 November frozen metric, fixed-margin null, site signflip, 15-pair/8-site gate and all publication restrictions remain unchanged.

## First executed workflow: failure with no ecological estimate

- GitHub Actions: https://github.com/zuizui0223/neon/actions/runs/45031613825
- Original job: `137236292538`; tested branch commit `2bfcbc57b49e9b2c2a86f50f8b05a4a088dde99a`.
- All eight synthetic fixed-metric/null/inference unit tests **passed**.
- Existing immutable CHM source receipt and nonempty `NEON_API_TOKEN` checks **passed** (token value never opened).
- Original source replay stopped at `ORIGINAL_REST_NAMED_STATIONS` with `RuntimeError` and `STOP_SOURCE_INFRASTRUCTURE_OR_ORIGINAL_COHORT` after ~3m21s of source execution.
- Anonymous STOP artifact `14758066280` is **not** an effect estimate.
- The previous runner discarded per-station fetch error categories. The original STOP cannot by itself distinguish repeated transport exhaustion, station-history absence, an original official station identity/schema problem, or another runtime error. No original 36-pair genus×canopy results were released.

## Non-biological diagnostic repair

On the same Draft PR #23 branch, source-only commits:

1. `821b06285cf20b2abff2c7c9c105e0ec09740831`: wrap the **same 3,000 requested official REST station histories** in an anonymous per-response diagnostic. Exhausted HTTP/transient retries, missing histories, station-name-not-found, identity mismatches, duplicate responses and unexpected source errors stop the **entire frozen cohort**. STOP JSON reports only aggregate error categories and requested/valid counts; no station, site, plot, genus, coordinates, source URLs, tags, or heights are exported.
2. `8544634c9c612440f739ec7021e35ec474f9e89b`: two additional synthetic checks for all-or-nothing STOP, source anonymity, successful complete-source preservation and duplicate station rejection. Existing eight scientific synthetic tests are not relaxed.

**Next observable requirement:** the newly triggered code-path run must either reverify all original 3,000 histories and proceed through frozen AOP source revalidation to the single prespecified ecological test, or return an anonymous categorized source STOP. Do not treat a transport fix as an ecological result.

No publication GO, confirmation, resource-biomass effect, competition effect, memory/learning inference or detection-corrected habitat preference follows from these code changes. `main` and all frozen previous results remain untouched.
