"""Clock-only correction for the archived NEON canopy-affinity analysis.

The v1 response, source cohort, exclusion, margins and site aggregation are
unchanged. Count ALL lazy proposals, including rejections. Reuse the already
audited symmetric proposal kernel; two chains diagnose finite sampling.
This same-data calibration cannot create independent confirmation.
"""
from random import Random
from statistics import mean, stdev
from analysis.neon_crossseason_template_null_v1 import TRAPS, _bits
from analysis.neon_nonidentical_trap_CHM_affinity_v1 import (
    rank100, exclusive_score, from_masks, require, SEED
)
from analysis.neon_proposal_clock_v2 import proposal_step, _rhat, _ess

DRAWS_PER_CHAIN = 2000
BURN_PROPOSALS = 10000
SPACING_PROPOSALS = 100
MIN_ESS_PER_CHAIN = 200
MAX_RHAT = 1.05

SAMPLER_METADATA = {
    "null_algorithm": "uniform-stationary lazy symmetric fixed-margin proposal clock",
    "source_pair_rng_seed": SEED,
    "chains_per_unit": 2,
    "null_draws_per_chain": DRAWS_PER_CHAIN,
    "burn_proposals_per_chain": BURN_PROPOSALS,
    "spacing_proposals": SPACING_PROPOSALS,
    "batch_means_minimum_ESS_per_chain": MIN_ESS_PER_CHAIN,
    "maximum_split_Rhat_exclusive": MAX_RHAT,
    "all_rejected_proposals_and_lazy_holds_counted": True,
    "finite_MCMC_not_exact_independent_uniform_draws": True,
    "same_data_calibration_only_no_confirmatory_promotion": True,
}

def corrected_unit_test(A, B, heightA, heightB, *, seed,
                        n_draws=DRAWS_PER_CHAIN, burn=BURN_PROPOSALS,
                        thin=SPACING_PROPOSALS, min_ess=MIN_ESS_PER_CHAIN):
    require(all(type(x) is int for x in (seed, n_draws, burn, thin, min_ess))
            and n_draws >= 20 and burn >= 0 and thin >= 1 and min_ess >= 1,
            "INVALID_PROPOSAL_CLOCK_SETTINGS")
    ra, rb = rank100(heightA), rank100(heightB)
    base = {
        "genus_count": len(A),
        "source_original_100_CHM_midrank_stations": 100,
        "season_B_genus_row_and_station_column_margins_fixed": True,
        "B_exact_original_genus_same_station_hits_excluded_from_score": True,
        "source_CHM_may_follow_animal_capture": True,
        "one_sided_positive_canopy_affinity_direction_fixed": True,
    }
    if len(set(heightA.values())) == 1 or len(set(heightB.values())) == 1:
        return {**base, "status": "UNINFORMATIVE_ONE_CANOPY_HEIGHT"}
    observed, n_novel = exclusive_score(A, B, ra, rb)
    base["original_genera_with_novel_B_stations"] = n_novel
    if n_novel < 2:
        return {**base, "status": "UNINFORMATIVE_FEWER_THAN_TWO_NOVEL_B_GENERA"}

    labels = sorted(B)
    origin = [_bits(B[g]) for g in labels]
    def margins(rows):
        return ([m.bit_count() for m in rows],
                [sum((m >> i) & 1 for m in rows) for i in range(len(TRAPS))])
    want = margins(origin)
    chains = []
    moves = 0
    for chain in range(2):
        rng = Random(seed + 1_000_003 * chain)
        current = origin.copy()
        for _ in range(burn):
            moves += proposal_step(current, rng)
        values = []
        for _ in range(n_draws):
            for _ in range(thin):
                moves += proposal_step(current, rng)
            score, _ = exclusive_score(A, from_masks(labels, current), ra, rb)
            values.append(score)
        require(margins(current) == want, "CORRECTED_NULL_MARGINS_CHANGED")
        chains.append(values)
    draws = chains[0] + chains[1]
    sd = stdev(draws)
    mu = mean(draws)
    ess = [_ess(c) for c in chains]
    rh = _rhat(chains)
    out = {
        **base, "null_draws": len(draws), "proposal_attempts": 2*(burn+n_draws*thin),
        "accepted_moves": moves, "all_rejected_proposals_and_lazy_holds_counted": True,
        "observed_nonidentical_trap_canopy_affinity_score": observed,
        "null_score_mean": mu, "null_score_sd": sd,
        "split_Rhat": rh, "batch_means_ESS_per_chain": ess,
        "z": None,
    }
    if sd <= 1e-12:
        out["status"] = "UNINFORMATIVE_ZERO_NULL_VARIANCE"
    elif rh is None or rh >= MAX_RHAT or min(ess) < min_ess:
        out["status"] = "UNINFORMATIVE_CORRECTED_NULL_MIXING"
    else:
        out.update(status="INFORMATIVE_NONIDENTICAL_TRAP_CANOPY_NULL",
                   z=(observed-mu)/sd)
    return out
