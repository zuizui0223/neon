# Wyoming external cross-scale replication — design lock v2

Date: 2026-09-29

Status: frozen before the Wyoming ZIP schema and before any species-specific support count or effect is opened.

## Why v2 supersedes the earlier N>=5 lock

The completed NEON/Portal programme originally showed a positive N>=5/sex movement sensitivity in all three species. A later uncertainty audit correctly propagated site-level uncertainty into the family mean and widened that N>=5 family interval to approximately -0.22 to +0.60. The sign concordance remains descriptive, but N>=5 is no longer confirmatory evidence.

Therefore the external replication returns to the **original primary threshold N_male>=3 and N_female>=3**. N>=5 is retained only as a high-information sensitivity.

## Two species roles

### Confirmatory external replication

*Dipodomys ordii* is intentionally included, despite being studied previously, because the Wyoming dataset is wholly independent. Its prior outcomes define the hypothesis; the Wyoming outcome is an out-of-sample replication.

### Held-out extension

*Perognathus fasciatus* has no inspected sex-specific outcome in the completed programme. It is a secondary held-out extension and cannot rescue a failed *D. ordii* external replication.

## Estimability gate

Packing:
- unit = site x trapping night;
- >=3 retained males and >=3 retained females;
- >=10 eligible site-nights across >=5 sites.

Movement:
- unit = site four-night trapping session;
- individual identity and sex stable;
- >=2 distinct capture nights per eligible individual;
- >=3 eligible males and >=3 eligible females;
- >=5 sites.

Cross-scale:
- packing and movement must both be estimable in >=5 overlapping sites.

Failure decision: `stop_wyoming_external_not_estimable`.

Passing the count-only gate only authorizes a second effect-analysis lock; it does not authorize immediate effect calculation.

## Packing geometry

The published field design is 4 x 20 grid points spaced 25 m apart. Havahart and Sherman traps were colocated at each point (<0.5 m), and Longworth traps were added on one line in 2016.

Therefore active support is trap-unit identity (`site x night x grid point x trap type`), not unique XY coordinate. Distinct colocated traps may legitimately share coordinates.

## If a later effect lock is authorized

Movement contrast:
`male - female median(log1p individual median successive-night displacement)`.

Movement is confirmed positive only if its site-level 95% Student-t CI lower bound is >0.

Packing contrast:
`Packing_z_male - Packing_z_female`.

The smallest effect of interest is frozen as |Delta Packing_z| = 0.5. Packing is treated as practically equivalent only if its **two-sided 95% CI lies entirely within [-0.5,+0.5]**.

Cross-scale classification:
- movement positive + packing equivalent -> `decoupled`;
- movement positive + packing positive -> `coupled_positive`;
- movement positive + packing negative -> `opposed`;
- otherwise -> `unresolved`.

The v2 design does not privilege decoupling: a positive packing replication is an allowed outcome.

## Current status

- Wyoming source schema inspected: false
- species support counts inspected: false
- sex-specific effects inspected: false
- movement distances inspected: false
- packing effects inspected: false
- ecological effect models fit: 0
