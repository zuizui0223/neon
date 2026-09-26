# NEON small-mammal spatial continuity

Independent development repository for the ecological paper:

**Community spatial continuity is species-redundant rather than turnover-generated in small-mammal metacommunities**

## Scientific question

When local small-mammal assemblages turn over across space, does pooling species create spatial continuity absent from every individual species, or is apparent community continuity already carried redundantly by one or more species?

## Scientific result

### Confirmatory: continuity is not turnover-generated

- 16/16 fresh NSF NEON sites were scored.
- 0/16 sites had pooled-community continuity greater than the best individual species.
- Median community-minus-best-species continuity gain = 0.
- Preregistered null-adjusted sign test: p = 1.0.
- No strict emergent adjacency criterion occurred.
- At every site, at least one individual species satisfied every prespecified adjacency criterion.
- Cross-species-only local support was rare: median 0.0027, maximum 0.066.
- At 10/16 sites, one species occupied at least 80% of guild-positive traps.
- ORNL was the sole negative case: pooled continuity 0.25 versus best-species 1.0.

### Exploratory positive structure: carrier identity turns over among sites

Using only the frozen site summaries:

- 48 site × continuity-carrier records comprise **32 species**.
- **20/32** carrier species are carriers at one site only.
- no carrier species occurs at more than **3/16** sites.
- only **18/120** site pairs share any carrier species.
- median pairwise carrier-set Jaccard similarity = **0**.
- median redundancy depth = **2 species/site** (range 1–8).
- median fraction of eligible species individually sufficient for all criteria = **0.477**.

The emerging ecological picture is therefore:

> **within-site redundancy + among-site turnover in continuity-carrier identity**

Richer sites contain more individually sufficient species while single-species dominance declines, without a rising fraction of eligible species becoming sufficient.

## Ecology-facing endpoint

A **continuity fraction** is the proportion of prespecified trap-neighbourhood adjacency criteria under which every positive trap has at least one positive peer.

The manuscript does not require EOG terminology. Historical `eog.*` schema names are retained only in immutable provenance files.

## Project boundary

- Paper A — metacommunity redundancy + carrier turnover: **active mainline**
- Paper B — later small-mammal continuity shell: deferred until Paper A is resolved
- World-survival identifiability methods paper: stays outside this repository
- NEON camera-trap programme: terminally stopped and excluded

## Layout

- `manuscript/neon_metacommunity_redundancy/` — paper
- `data/derived/` — frozen site-level tables
- `validation/neon_metacommunity_connectivity_v1/` — immutable confirmatory provenance
- `analysis/` — standalone paper assets
- `tests/` — frozen-result integrity tests
- `docs/` — scientific and publication boundaries
