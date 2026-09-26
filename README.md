# NEON small-mammal spatial continuity

Independent development repository for the ecological paper:

**Community spatial continuity is species-redundant rather than turnover-generated in small-mammal metacommunities**

## Scientific question

When local small-mammal assemblages turn over across space, does pooling species create spatial continuity absent from every individual species, or is apparent community continuity already carried redundantly by one or more species?

## Frozen confirmatory result

- 16/16 fresh NSF NEON sites were scored.
- 0/16 sites had pooled-community continuity greater than the best individual species.
- Median community-minus-best-species continuity gain = 0.
- Preregistered null-adjusted sign test: p = 1.0.
- No strict emergent adjacency criterion occurred.
- At every site, at least one individual species satisfied every prespecified adjacency criterion.
- Cross-species-only local support was rare: median 0.0027, maximum 0.066.
- At 10/16 sites, one species occupied at least 80% of guild-positive traps.
- ORNL was the sole negative case: pooled continuity 0.25 versus best-species 1.0.

## Ecology-facing endpoint

A **continuity fraction** is the proportion of prespecified trap-neighbourhood adjacency criteria under which every positive trap has at least one positive peer.

The manuscript does not require EOG terminology. Historical `eog.*` schema names are retained only in immutable provenance files.

## Project boundary

- Paper A — metacommunity redundancy: **active mainline**
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
