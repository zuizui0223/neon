# Temporal positional aliasing diagnostic v2

Primary change from v1: use the **within-occasion positional diameter**

`Delta_it = max_jk d(X_itj, X_itk)`

as the scale-aware diagnostic quantity. The first-to-last endpoint span remains reported, but is secondary.

Why: a sequence A→B→A has endpoint span zero although pooling the occasion creates a genuine multi-location ambiguity. In the held-out San Jacinto audit, 24 of 450 cross-trap conflict nights (5.33%) had this endpoint false-negative structure.

For any two rules that select one of the actually observed positions as the representative state, the selected positions within occasion t differ by at most `Delta_t`. Therefore:

`|d(R_t,R_u)-d(R'_t,R'_u)| <= Delta_t + Delta_u`

and, across individuals represented in one occasion,

`|MPD(R)-MPD(R')| <= 2 mean(Delta_i)`.

These are direct metric consequences and are not claimed as novel mathematics. Their methodological role is to make the full observed geometry, rather than an arbitrary pair of endpoints, the sensitivity scale.

The v1 first/last output is retained for backward compatibility and for directional questions in which time ordering itself matters.
