from __future__ import annotations

import hashlib
import itertools
import math
import random
from collections.abc import Iterable, Sequence


def world_survives(positive_nodes: set[int], edges: set[tuple[int, int]]) -> bool:
    if len(positive_nodes) < 2:
        return False
    degree = {x: 0 for x in positive_nodes}
    for a, b in edges:
        if a in positive_nodes and b in positive_nodes:
            degree[a] += 1
            degree[b] += 1
    return all(degree[x] > 0 for x in positive_nodes)


def is_carrier(positive_nodes: set[int], worlds: Sequence[set[tuple[int, int]]]) -> bool:
    return bool(worlds) and all(world_survives(positive_nodes, edges) for edges in worlds)


def deterministic_seed(site_code: str, species_name: str) -> int:
    token = f"carrier_prevalence_mechanism_v1|{site_code}|{species_name}".encode()
    return int(hashlib.sha256(token).hexdigest()[:16], 16)


def count_conditioned_carrier_probability(
    candidate_nodes: Sequence[int],
    positive_count: int,
    worlds: Sequence[set[tuple[int, int]]],
    *,
    replicates: int = 999,
    seed: int,
) -> float:
    nodes = tuple(candidate_nodes)
    n = len(nodes)
    k = positive_count
    if k < 2 or k > n:
        return 0.0

    total = math.comb(n, k)
    if total <= replicates:
        trials: Iterable[tuple[int, ...]] = itertools.combinations(nodes, k)
        hits = sum(is_carrier(set(x), worlds) for x in trials)
        return hits / total

    rng = random.Random(seed)
    hits = 0
    for _ in range(replicates):
        draw = set(rng.sample(nodes, k))
        hits += is_carrier(draw, worlds)
    return hits / replicates


def carrier_excess(
    observed_positive_nodes: set[int],
    candidate_nodes: Sequence[int],
    worlds: Sequence[set[tuple[int, int]]],
    *,
    replicates: int,
    seed: int,
) -> tuple[int, float, float]:
    observed = int(is_carrier(observed_positive_nodes, worlds))
    expected = count_conditioned_carrier_probability(
        candidate_nodes,
        len(observed_positive_nodes),
        worlds,
        replicates=replicates,
        seed=seed,
    )
    return observed, expected, observed - expected
