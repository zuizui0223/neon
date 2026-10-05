# Wisconsin independent footprint replication v1

**Status:** Stage 6A feasibility audit frozen before any spatial-overlap outcome is opened  
**Branch:** `ecology/wisconsin-footprint-replication-v1`  
**External dataset:** Jolly & Pauli (2024), Dryad DOI `10.5061/dryad.zpc866thw`

## Purpose

San Jacinto Stage 5B found that different conspecific individuals had more similar multi-night spatial footprints than heterospecific individuals after exact control for footprint size.

This branch asks whether that **individual-level footprint assortativity** replicates in an independent small-mammal community with different geography, habitat, trap spacing and sampling protocol.

The Wisconsin dataset was collected at nine sites in northern Wisconsin. Each site used a 5 × 5 trap grid with 10 m spacing and was trapped continuously for nine consecutive days in repeated summer/winter seasons. The deposited capture table stores an individual's initial capture date/trap and up to eight recapture date/trap pairs.

No San Jacinto threshold will be changed after Wisconsin spatial outcomes are viewed.

---

# Stage 6A — feasibility only

Stage 6A may inspect only data structure and support.

Allowed outputs:

1. deposited file names and source checksum;
2. raw row count and column names;
3. species roster and raw individual-row counts;
4. number of reconstructable individual capture histories;
5. number of individuals captured on at least two distinct dates;
6. counts of such multi-night individuals by species and site × season;
7. exact distribution of number of capture dates per individual;
8. exact distribution of number of distinct traps per multi-night individual;
9. number of site × season units meeting candidate replication support;
10. missingness / invalid trap-ID diagnostics.

Stage 6A must **not** calculate or display:

- pairwise footprint Jaccard similarity;
- conspecific versus heterospecific footprint overlap;
- spatial distance between traps;
- species-specific trap occupancy maps;
- any permutation statistic or p-value;
- association with habitat type or season.

## Candidate replication support rule

For support purposes only, define an individual multi-night history as an initial capture plus recapture records yielding at least **2 distinct capture dates** within the same deposited row.

A species is support-eligible within site × season if at least **3 multi-night individuals** are reconstructable.

A site × season is candidate-eligible if at least **3 species** meet that rule.

The full independent replication will proceed only if at least **8 site × season units** satisfy that support rule. This matches the minimum number of informative units frozen for San Jacinto Stage 5B.

If fewer than 8 units qualify, this Wisconsin route stops for support. Thresholds will not be relaxed after seeing spatial outcomes.

## Individual identity

The deposited CaptureMaster table is structured as one initial-capture row per animal with recapture date/trap columns. The row itself is therefore the primary history object.

Rows flagged `Remove == 1` are excluded because the Dryad metadata identifies them as recaptures of unknown identity or animals escaping before tagging that cannot be used in abundance estimates.

Ear tags are retained as provenance fields but are not required to merge rows during Stage 6A. Stage 6A audits duplicate/ambiguous tag combinations before the Stage 6B design is frozen.

## Spatial unit

The intended Stage 6B unit is **Site × Season**, corresponding to one 9-day grid deployment for that site in that summer/winter season. The deposited `Session` field is retained for audit but is not assumed to be a separate ecological replicate unless Stage 6A shows otherwise.

Trap IDs are treated only as categorical spatial locations in Stage 6A. No coordinate geometry is needed for the planned footprint-overlap replication.

---

# Stage 6B candidate — unopened

If Stage 6A passes support, freeze and run one replication only:

> **Within site × season, do conspecific multi-night individuals use more similar sets of traps than heterospecific multi-night individuals after controlling exactly for footprint size?**

The intended design is the San Jacinto Stage-5B statistic:

- footprint = set of distinct trap IDs used by one individual across capture dates;
- pair similarity = Jaccard overlap;
- unit contrast = mean conspecific Jaccard − mean heterospecific Jaccard;
- species labels permuted only among individuals with the same footprint size inside each site × season;
- site × season units weighted equally in the global standardized statistic;
- one-sided test for positive assortativity.

Exact permutation count, seed, eligible species roster and unit list will be frozen from Stage-6A support only, before any overlap value is calculated.

## Claim boundary

Even a successful Wisconsin replication would support a general **species-specific repeated-use footprint** pattern across two rodent/small-mammal systems. It would not show that competition causes those footprints.

Potential mechanisms remain habitat selection, resource distribution, refuge placement, territoriality, morphology, social behavior or other persistent spatial constraints.
