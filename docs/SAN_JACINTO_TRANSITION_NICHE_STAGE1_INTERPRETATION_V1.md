# San Jacinto transition-niche Stage 1 interpretation v1

**Status:** ecological route stopped by its frozen primary test  
**Branch:** `ecology/san-jacinto-transition-niche-v1`  
**Frozen design:** `docs/SAN_JACINTO_TRANSITION_NICHE_EXPLORATION_V1.md`  
**Result:** `results/san_jacinto_movement_direction_partitioning_v1.json`

## Result

The Stage-1 hypothesis was:

> for moves of the same length from the same starting locations, observed within-night movement directions preserve more interspecific spatial segregation than feasible random directions.

It was not supported.

The frozen analysis retained singleton individual-nights as fixed spatial background and randomized only FIRST-to-LAST directions of repeat-capture nights, while preserving the exact origin and squared grid displacement of every randomized move.

Support was ample for the declared test:

- 4,550 valid focal-species individual-nights;
- 18 eligible grid-seasons;
- all 18 had non-zero directional-null variance;
- 1,968 repeat nights were randomized;
- 1,415 / 1,968 = 71.9% of those repeat nights had more than one feasible direction at their observed displacement length.

The global standardized excess of observed LAST C-score over the distance-matched direction null was

[
T=-0.1966,
]

with one-sided Monte Carlo

[
p=0.8000.
]

The frozen decision is therefore:

`stop_no_directional_maintenance_support`.

Species-pair decomposition remains unopened.

## Biological meaning

The rejected mechanism is stronger and more specific than saying that animals move.

The result does **not** support the idea that the seasonal spatial segregation described for this rodent guild is continually rebuilt, move by move, because individuals preferentially direct their within-night movements toward destinations that maintain the community checkerboard pattern.

This matters because two ingredients were already known in this system:

1. direct interaction experiments showed a strong body-size dominance hierarchy and avoidance by small pocket mice of larger heterospecific competitors; and
2. the field community showed spatial niche partitioning and species-specific microhabitat associations, despite substantial temporal overlap.

The missing bridge was whether short-term movement direction itself carries that competitive segregation into the field pattern. The frozen Stage-1 analysis finds no community-level evidence for that bridge.

A defensible ecological interpretation is therefore:

> **Encounter-scale avoidance and seasonal community-level spatial segregation need not be linked by continual directional avoidance at every within-night move.**

The seasonal pattern may instead arise at another scale: species-specific habitat selection, burrow or activity-centre placement, settlement decisions, longer-term responses to competitors, or historical/current competitive sorting. The present data do not distinguish these alternatives.

## General principle

The broad ideas that movement affects coexistence, that station-keeping movement can structure communities, and that fine-scale interspecific avoidance can mediate coexistence are already established.

The narrower result here points to a scale-separation principle:

> **A spatially partitioned community does not require each short-term movement decision to preserve that partition. Aggregate niche segregation can be an emergent property of where individuals establish and repeatedly use space rather than a rule enforced at every movement step.**

This is not evidence that short-term movements are biologically irrelevant. It says that a static spatial niche pattern should not automatically be interpreted as a signature of continuous step-by-step avoidance.

## Literature boundary

Relevant prior work includes:

- Chock, Shier & Grether (2018), *Animal Behaviour* 137:197–204, doi:10.1016/j.anbehav.2018.01.015 — body size predicts interspecific dominance and pocket mice show heterospecific avoidance in simulated intrusion experiments.
- Chock, Shier & Grether (2022), *Oecologia* 198:553–565, doi:10.1007/s00442-021-05104-5 — the same granivorous guild is temporally overlapping but spatially segregated, with species-specific microhabitat associations.
- Schlägel et al. (2020), *Biological Reviews*, doi:10.1111/brv.12600 — movement-mediated community assembly/coexistence framework, including station-keeping movement, habitat selection and fine-scale interactions.
- Péron (2024), *Ecological Modelling* 487:110549, doi:10.1016/j.ecolmodel.2023.110549 — small-scale movement patterns can support coexistence without a simple functional trade-off.
- Stiegler et al. (2026), *Journal of Animal Ecology*, doi:10.1111/1365-2656.70320 — individual behaviour and niche width structure spatial interactions in a natural rodent community.

Thus neither “movement matters for coexistence” nor “rodents partition space” is novel. The distinctive contribution of Stage 1 is the explicit mechanistic bridge test, and its answer is negative.

## Impact assessment

This negative result is biologically informative but **does not by itself support a new high-impact ecology paper**.

Reasons:

1. recorded transitions are capture-to-recapture segments after live-trap handling, not complete untouched movement trajectories;
2. the Figshare record does not contain the trap-level vegetation/soil measurements needed to identify the alternative habitat mechanism directly;
3. the result rejects one plausible dynamic mechanism but does not identify the mechanism that generates the seasonal spatial pattern;
4. the original paper already established the static niche-partitioning pattern.

Accordingly, this route should not be expanded by trying alternative movement metrics or opening species pairs after the failed primary test.

The result can, however, strengthen the biological interpretation of the temporal-aliasing paper: large within-night positional turnover does not imply that community spatial organization is being directionally reorganized over the same time scale.

## Claim boundary

Do not claim:

- that competitors do not affect movement;
- that heterospecific avoidance is absent;
- that habitat filtering is proven;
- that handling has no effect;
- that the observed trap-to-trap segments are complete natural trajectories;
- that a lower-tail effect is supported (the preregistered test was one-sided in the positive direction);
- or that any species pair drives the null community result.

The route is closed at the community-level Stage-1 test.
