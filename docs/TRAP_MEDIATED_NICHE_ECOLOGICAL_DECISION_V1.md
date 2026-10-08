# Trap-mediated niche ecological decision — October 8, 2026

## Publication decision

**Do not promote the San Jacinto capture-sequence exploration to a stand-alone causal competition or within-night interaction-network paper.** The public data support a structured, detector-local sequence signal but not an identified natural dominance hierarchy or statistically demonstrated temporal rewiring. This is a scientific HOLD, not a computational failure.

The MEE temporal-aliasing manuscript is a distinct, completed methodological route and must remain unchanged by this exploratory ecological audit.

## Hypothesis-by-hypothesis ledger

### H1. The original published spatial niche segregation was manufactured by within-night recaptures
**Not supported.** The all-capture spatial SIM9 endpoint reproduces the published 8/32 segregated grid-seasons exactly; removing subsequent identified individual-night recaptures leaves 8/32 and causes 0/32 classification changes. This rules out a large classification-level artifact under that sensitivity, not all possible detection biases.

### H2. Captures artificially conceal temporal segregation
**Not supported.** Temporal RA3 representation sensitivity is real, but no robust pattern of new temporal segregation emerges across ALL, FIRST, LAST, RANDOM or individual-night-normalized records. The published 7/32 aggregated count did not reproduce exactly under ALL (the rerun found 4/32), so exact significance-count statements must remain qualified.

### H3. Recent kangaroo-rat occupancy generically suppresses the next capture of all smaller rodents
**Not supported.** In the trap + grid-date-transition fixed-effect model, the pooled small-species odds after kangaroo occupancy versus EMPTY were OR 1.212 (95% CI 0.968–1.519). Target-specific contrasts have mixed directions. This is incompatible with claiming a universal short-term competitive exclusion coefficient.

### H4. The same trap carries an asymmetric species history
**Exploratory support, model-dependent.** In the trap × bout date-shuffle reference, KR→LAPM observed/expected = 0.719 (grid × bout bootstrap 95% 0.533–0.928), versus LAPM→KR = 1.022 (0.869–1.195). The spatial deficit was localized to the exact trap (0.719 at distance 0; 0.911 at one Manhattan spacing; 1.029 at two). Stronger fixed effects reduce clarity: DKR→LAPM OR 0.546, 95% CI 0.143–2.087; the generic pooled kangaroo effect is not below one. Do not call this causal avoidance or robust cross-model dominance.

### H5. The pooled six-species directed capture-sequence order aligns with known body-size dominance
**Exploratory concordance, not a new biological hierarchy.** The best pooled order SKR > DKR > PEMA > CHFA > LAPM > PEER satisfies 14/15 date-shuffle signs and 15/15 fixed-effect signs. The fixed-effect optimum remains among optima after 7/8 grid omissions; the date-shuffle order remains among optima after 8/8. The empirical body-mass order scores 13/15 fixed-effect dyads (2.78% of rank permutations score at least this well). The rank was selected after outcomes were seen, effect-size uncertainties differ by edge, and these are trap-mediated observations. Chock et al. (2018) had already found body-size-associated dominance in behavioural experiments on part of this guild.

### H6. That interaction network reconfigures within a night
**Not established; retract as a headline.** The original descriptive 9/15 sign concordance is insufficient. In a common 250 grid-night support set of 24,408 adjacent trap-state transitions, paired 5,000-replicate grid×bout bootstrap showed 0/15 dyad interval differences with a 95% interval excluding zero, and 0/15 passing exploratory BH q<0.10. KR→LAPM O/E was 0.629 early→middle and 0.816 middle→late; their smoothed log-O/E contrast was −0.252, 95% −0.778 to 0.245. Exact-three-night-bout sensitivity also showed no BH-surviving differences. Lack of detection is not proof of temporal constancy.

## Prior-art / external-replication boundary

Brouard et al. (2015; PLOS ONE 10:e0145006) already demonstrated previous-occupant species effects on rodent trappability, including differences by habitat and diel period, and modelled downstream capture-composition biases. Their S1 Data (DOI 10.1371/journal.pone.0145006.s010) provides trap ID, check number, previous occupant and three species capture flags. However field voles occurred almost exclusively in grassland and bank voles in woodland, so it does not provide a directly comparable 3-species coexisting interaction network, let alone an independent 6-species dominance hierarchy. It can at most test another two-species detector-history comparison if the schema audit supports it.

### What an ecological paper would need

1. A genuinely independent capture system with ≥3 simultaneously sampled rodent species, check-level trap and individual identity, and reliable effort/empty state records; freeze directed sign predictions **before** opening new outcomes.
2. Or a randomized experimental contrast manipulating previous-occupant scent/trap cleaning/release location so that temporal trap-history effects are identified rather than inferred from observations.
3. A bridge from detector-local sequence to independent natural encounters, displacement, resource use, or fitness/establishment, ideally replicated across guilds.

## Current honest ecological conclusion

**Small-mammal capture histories contain local directional structure invisible to symmetric nightly overlap summaries, but the available observational data cannot tell whether it is natural interaction, residual scent, release history, or detector artefact; and there is no reliable evidence of within-night rewiring.**

This is a hypothesis-generating ecological result. It is not yet a new general law of competition or a ready high-impact ecological manuscript.

## Reproducibility

- `results/trap_mediated_niche_sequence_summary_v1.json`
- `results/san_jacinto_previous_occupant_fixed_effects_summary_v1.json`
- `results/san_jacinto_capture_history_niche_sensitivity_summary_v1.json`
- `results/trap_sequence_hierarchy_robustness_v1.json`
- `results/trap_sequence_interval_rewiring_summary_v1.json`
- `docs/TRAP_SEQUENCE_INTERVAL_REWIRING_RESULT_V1.md`
- `analysis/audit_trap_sequence_interval_rewiring_v1.py`
