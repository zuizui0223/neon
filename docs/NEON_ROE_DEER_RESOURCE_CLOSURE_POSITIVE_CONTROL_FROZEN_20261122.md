# Independent resource-closure experiment: positive mechanistic comparator, NOT a NEON finding

**22 November 2026. Prior published experimental result and source-verified reproduction design, not hypothesis discovery.** One NEON mammal ecology Draft PR #23; submission HOLD. This is not a second paper and not pooled with small-mammal capture-station data.

## Exact independent source and what it can establish

Ranc, Moorcroft, Ossi & Cagnacci (2021), *PNAS*, [DOI 10.1073/pnas.2014856118](https://doi.org/10.1073/pnas.2014856118) experimentally altered access to established food patches while tracking GPS-collared roe deer. The original authors published a mechanistic analysis comparing omniscient, perception-based and memory-based foraging models and found the memory model best predicted behavior. These results are **PRIOR ART**, NOT a NEON novelty claim. The original authors estimated spatial and resource attribute memory half-lives ~5.6 and 0.9 days, which require their mechanistic model—not the simpler state tabulation below.

Source [Zenodo DOI 10.5281/zenodo.4609649](https://doi.org/10.5281/zenodo.4609649), original public [GitHub repository `ranc-n/Ranc-et-al.-PNAS-2021` pinned tag v1.0 commit `58cd85c863d50346df0c7b0d3ecfde97f8a5dfdb`](https://github.com/ranc-n/Ranc-et-al.-PNAS-2021/tree/v1.0). Original SHA/Git blobs:
- `Ranc_et_al_2021_PNAS_data_population_ts.txt`: Git blob `18bebe5527828a9ff975d3f35c6b7553d67a3064`, **26,841 hourly state rows**, **25 source-defined animal-year `exp_id` series**. Original columns `exp_id,current_state_code,res_access_m,light_i,light_r,light_abs_r,min_temp`.
- `Ranc_et_al_2021_PNAS_data_population_tslv.txt`: Git blob `918f5b981b4dc55c71347549d72815cf0b8db497`, original columns `exp_id,tslv_m,tslv_a,access_m,access_a`, 25 initial series rows.

Original `current_state_code`: 1 = manipulated food station `M`, 2 = alternative food station `A`, 3 = vegetation `V`, -9999 = not observed state. Original `res_access_m`: 1 = manipulated food station **accessible**, 0 = **inaccessible**. Source-only scan (before any phase occupancy outcome) confirmed each of all 25 original animal-year trajectories follows **exactly three consecutive resource phases `1→0→1`**. Note that state 1 describes location at the manipulated feeding station, not necessarily successful feeding when access is closed.

## Reproduction frozen BEFORE within-phase state-use fractions are opened

Read original two text CSVs only from a GitHub Actions checkout of the immutable original commit. Verify exact head SHA and each raw Git blob SHA1 before parsing. Require exact headers, 25 identical source `exp_id` sets, 26,841 original hourly records, state code one of `1,2,3,-9999`, resource access exactly `0,1`, each series `1→0→1` and each of 75 source phases >=24 valid measured state hours. Any violation is explicit SOURCE STOP; no dropping unfavorable animals, shortening closures, selecting better time windows or handcoding missing state as vegetation.

For each animal-year, report only **three period fractions of observed hours at M, A, V** (exclude -9999 from denominators, but report count missing), and equal-animal-year mean differences in M use for `closed minus before`, `reopened minus closed`, and `reopened minus before`. Also report how many source animal-year series decrease M occupancy upon closure and increase M occupancy upon reopening, descriptive only. For pooled times, report total hours by phase, but do not confuse hours with independent animals. Do NOT assign causal memory solely from occupancy change: it shows resource access affected space use, while disentangling learning from perception needs the original paper's manipulated cue protocol and time-decay model.

**Prior published comparison** (use as sanity context, not validation threshold): authors described using manipulated sites ~31% preclosure vs ~5% during closure and memory better than visual/olfactory perception. Our source may show slightly different fractions due to state discretization and excluded -9999 or individual weighting; report discrepancies instead of changing the protocol.

No original animals' GPS coordinates, IDs, feeding site names, exact time stamps, source model parameter estimates or private location data exported to NEON. All sources are publicly published and original animal-year IDs remain internal to CI. No new P-value/bootstrap or dependence claim because 25 animal-years are not necessarily 25 independent roe deer.

## Ecological interpretation for NEON

**Positive experimental comparator:** manipulated resource availability can reorganize the *same* mammal's utilization of patches while individual identity is held constant, and separately the original authors demonstrated cognitive tracking by distinguishing memory from instantaneous perception. This is the kind of intervention necessary to discriminate three hypotheses. It is fundamentally different from NEON's positive taxon-by-live-trap recurrence and Portal's time-fragile plot-level plant-count association; none of those records directly manipulate natural food, and none measure learned site familiarity. The deer study contains no taxon turnover, competitive exclosure of another species, or NEON community-level spatial-role persistence, so cannot be meta-pooled as a confirmation.

Output `analysis/reproduce_ranc_2021_resource_closure_state_use_v1.py`, source-locking tests, dedicated original public checkout CI, and aggregate `results/neon_ranc2021_original_resource_closure_positive_control_20261122.json`. Main NEON paper remains Draft and SUBMISSION HOLD.
