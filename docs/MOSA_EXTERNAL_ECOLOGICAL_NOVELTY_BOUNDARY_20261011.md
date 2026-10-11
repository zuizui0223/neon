# MOSA external-data ecology audit: why the long time series matters (2026-10-11)

**Status: prospective external ecological question is frozen AFTER the NEON provisional sign mismatch but BEFORE MOSA W/B or new abundance–space effects.** Source byte/header validation is not the same as a successful ecological test.

## An independent, long-term mammal system

Leirs et al. (2023), *Scientific Data* 10:798, https://doi.org/10.1038/s41597-023-02700-3, document a 29-year monthly live-trap CMR database of *Mastomys natalensis* (1994–2023). Primary sessions use three consecutive nights, across one 300-station grid (30 × 10, spacing 10 m, area about 3 ha). Raw capture records are provided under CC-BY from https://doi.org/10.5281/zenodo.10049811.

The published data descriptor reports 49,216 capture records representing 21,927 marked individuals in the whole dataset. It does **not** imply that all months will support W calculated from two or more distinct nightly positions, or that sample inclusion can ignore temporal or detection selection. The capture CSV source byte size and hash must be verified against the published Zenodo inventory before trusting any schema.

## Direct prior work occupies much of the apparent novelty

Borremans et al. (2014), *Population Ecology* 56:109–118, https://doi.org/10.1007/s10144-013-0393-2, already analysed approximately 17 years of monthly CMR captures on this MOSA system and found density-related home-range size differences by sex/age, rising range overlap/visitation at greater densities, and little evidence for territorial exclusivity from their random-placement comparisons. These biological effects are **already known**. A new MOSA paper cannot headline “crowding changes home range/overlap”, “some demographic classes expand while others contract” or “promiscuous rodents can overlap strongly” as an original discovery.

## Distinct falsifiable question

Given an empirical system in which territorial exclusivity was not supported by previous analyses, does changing local abundance alter **the balance of intra-animal short-window positional variation W and inter-animal trap-centroid variation B**? Are apparent effects strong enough to survive the fixed recapture-selection diagnostics rather than merely altering how many animals are reobserved within each three-night bout?

Success would be limited to an independent **single-species, one-plot time-series** association, which cannot rescue the preregistered eight-genus or five-genus NEON replication failures. A positive NEON-style Δ in MOSA would not prove territoriality; a negative or null Δ would not prove universal absence of spatial density accommodation. Existing detailed CMR work makes taxon-composition and territorial explanations substantially less simple than the original NEON ecological manuscript proposed.

## Before outcome data

1. Confirm real Zenodo CSV bytes with official source size and digest; explicit fail-closed HTML checks (earlier Borneo false-green lesson).
2. Determine field mapping for dates, three-night bout, station coordinates, individual IDs, species and capture events. Do not treat ambiguous labels as observations.
3. Audit the same ≥5 individuals reobserved on ≥2 nights per 3-night bout, complete effort/coverage, within-year abundance variation, >60 eligible months across >10 years; no W/B or density-effect slopes opened before success.
4. Freeze geometric scale: 30×10 rectangle is not the NEON 10×10 square. Absolute B/W m² slopes are not numerically transportable across their different grids.
5. Precommit one observational density/space model with month-of-year, year/long-term period and within-plot serial autocorrelation handled; protect against within-animal recapture selection and changes in trap deployment.
6. Do not split the data by sex, habitat or calendar episode after seeing the effects to manufacture a successful mechanism. Previous published age/sex-dependent effects may motivate a separate, expressly **post-NEON** preregistered secondary check only if justified before MOSA outcomes.

## Claim boundaries

The single-site MOSA record has strong temporal depth but no site-level spatial replication. Across years/months, observations are dependent; neither 300 traps nor 49,216 captures count as independent populations. Published low territoriality makes the site an informative comparator, **not** proof of no individual avoidance on every capture occasion.

MOSA source discovery: Scientific Data (2023) and Borremans et al. (2014) are the only invoked biological priors here; no empirical MOSA W/B response or MNKA slope has been measured in this branch as of this contract.
