from __future__ import annotations

import hashlib
import itertools
import math
from collections import defaultdict
from typing import Any, Iterable

import numpy as np


def _xy(values: np.ndarray) -> np.ndarray:
    arr=np.asarray(values,dtype=float)
    if arr.ndim!=2 or arr.shape[1]!=2:
        raise ValueError("xy must have shape (n,2)")
    if not np.isfinite(arr).all():
        raise ValueError("xy must be finite")
    return arr


def mean_pairwise_distance(xy: np.ndarray) -> float:
    arr=_xy(xy)
    n=len(arr)
    if n<2:
        raise ValueError("at least two points required")
    diff=arr[:,None,:]-arr[None,:,:]
    d=np.sqrt(np.sum(diff*diff,axis=2))
    return float(np.mean(d[np.triu_indices(n,1)]))


def delta_mpd(xy: np.ndarray, male_mask: np.ndarray) -> float:
    arr=_xy(xy)
    mask=np.asarray(male_mask,dtype=bool)
    if len(mask)!=len(arr):
        raise ValueError("male_mask length mismatch")
    n_male=int(np.sum(mask))
    n_female=len(mask)-n_male
    if n_male<2 or n_female<2:
        raise ValueError("both sex groups require at least two individuals")
    return mean_pairwise_distance(arr[mask])-mean_pairwise_distance(arr[~mask])


def _stable_seed(
    xy: np.ndarray,
    strata: list[str],
    male_counts: dict[str,int],
) -> int:
    parts=[]
    for (x,y),stratum in zip(_xy(xy),strata):
        parts.append(f"{stratum}|{x:.12g}|{y:.12g}")
    counts=";".join(
        f"{key}:{male_counts[key]}"
        for key in sorted(male_counts)
    )
    payload="\n".join(parts)+"\n"+counts
    return int(hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16],16)


def _stratum_indices(strata: Iterable[object]) -> dict[str,list[int]]:
    out: dict[str,list[int]]=defaultdict(list)
    for i,value in enumerate(strata):
        out[str(value)].append(i)
    return dict(sorted(out.items()))


def permutation_space_size(
    strata: Iterable[object],
    sex: Iterable[object],
) -> int:
    strata_list=[str(x) for x in strata]
    sex_list=[str(x).upper() for x in sex]
    if len(strata_list)!=len(sex_list):
        raise ValueError("strata/sex length mismatch")
    by=_stratum_indices(strata_list)
    total=1
    for key,idx in by.items():
        n_male=sum(sex_list[i]=="M" for i in idx)
        n_female=sum(sex_list[i]=="F" for i in idx)
        if n_male+n_female!=len(idx):
            raise ValueError("sex must contain only M/F")
        total*=math.comb(len(idx),n_male)
    return int(total)


def _exact_masks(
    strata: list[str],
    sex: list[str],
):
    by=_stratum_indices(strata)
    options=[]
    for key,idx in by.items():
        n_male=sum(sex[i]=="M" for i in idx)
        combos=list(itertools.combinations(idx,n_male))
        options.append(combos)

    for selected_groups in itertools.product(*options):
        mask=np.zeros(len(strata),dtype=bool)
        for selected in selected_groups:
            mask[list(selected)]=True
        yield mask


def conditional_sex_space_z(
    *,
    xy: np.ndarray,
    sex: Iterable[object],
    strata: Iterable[object],
    exact_max_assignments: int=200_000,
    monte_carlo_draws: int=19_999,
) -> dict[str,Any]:
    """Detection-conditioned sex spatial contrast.

    The pooled captured individuals and their locations are fixed. Sex labels
    are randomized *within detector strata*, preserving the observed male count
    in every stratum. For Wyoming the intended stratum is trap_type x bait_type.
    """
    arr=_xy(xy)
    sex_list=[str(x).upper() for x in sex]
    strata_list=[str(x) for x in strata]
    n=len(arr)

    if len(sex_list)!=n or len(strata_list)!=n:
        raise ValueError("xy/sex/strata length mismatch")
    if any(x not in {"M","F"} for x in sex_list):
        raise ValueError("sex must contain only M/F")
    n_male=sum(x=="M" for x in sex_list)
    n_female=n-n_male
    if n_male<2 or n_female<2:
        return {
            "estimable":False,
            "non_estimable_reason":"fewer_than_two_per_sex",
            "n_male":n_male,
            "n_female":n_female,
        }

    observed_mask=np.asarray([x=="M" for x in sex_list],dtype=bool)
    observed=delta_mpd(arr,observed_mask)

    by=_stratum_indices(strata_list)
    male_counts={
        key:sum(sex_list[i]=="M" for i in idx)
        for key,idx in by.items()
    }
    space=permutation_space_size(strata_list,sex_list)
    if space<=1:
        return {
            "estimable":False,
            "non_estimable_reason":"no_within_stratum_sex_permutation",
            "n_male":n_male,
            "n_female":n_female,
            "observed_delta_mpd":observed,
            "permutation_space_size":space,
        }

    if space<=int(exact_max_assignments):
        values=np.fromiter(
            (delta_mpd(arr,mask) for mask in _exact_masks(strata_list,sex_list)),
            dtype=float,
            count=space,
        )
        mode="exact_stratified_sex_label_permutation"
        draws=int(space)
        seed=None
    else:
        draws=int(monte_carlo_draws)
        if draws<999:
            raise ValueError("monte_carlo_draws must be at least 999")
        seed=_stable_seed(arr,strata_list,male_counts)
        rng=np.random.default_rng(seed)
        values=np.empty(draws,dtype=float)
        keys=list(by)
        for draw in range(draws):
            mask=np.zeros(n,dtype=bool)
            for key in keys:
                idx=np.asarray(by[key],dtype=int)
                k=male_counts[key]
                if k:
                    chosen=rng.choice(idx,size=k,replace=False)
                    mask[chosen]=True
            values[draw]=delta_mpd(arr,mask)
        mode="deterministic_mc_stratified_sex_label_permutation"

    null_mean=float(np.mean(values))
    null_sd=float(np.std(values,ddof=0))
    if not math.isfinite(null_sd) or null_sd<=0:
        return {
            "estimable":False,
            "non_estimable_reason":"zero_conditional_null_variance",
            "n_male":n_male,
            "n_female":n_female,
            "observed_delta_mpd":observed,
            "null_mean_delta_mpd":null_mean,
            "null_sd_delta_mpd":null_sd,
            "permutation_space_size":space,
            "permutation_mode":mode,
            "permutation_draws":draws,
            "seed":seed,
        }

    z=(observed-null_mean)/null_sd
    centered=observed-null_mean
    return {
        "estimable":True,
        "non_estimable_reason":None,
        "n_male":n_male,
        "n_female":n_female,
        "observed_delta_mpd":observed,
        "null_mean_delta_mpd":null_mean,
        "null_sd_delta_mpd":null_sd,
        "centered_delta_mpd":centered,
        "sex_space_z":float(z),
        "permutation_space_size":space,
        "permutation_mode":mode,
        "permutation_draws":draws,
        "seed":seed,
        "stratum_count":len(by),
        "stratum_sizes":{key:len(idx) for key,idx in by.items()},
        "stratum_male_counts":male_counts,
    }
