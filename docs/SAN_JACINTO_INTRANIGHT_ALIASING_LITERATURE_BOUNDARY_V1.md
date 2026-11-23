# Intra-night positional aliasing — literature and interpretation boundary v1

Date: 2026-09-29

## What is already known

Temporal aggregation of capture/detection records can discard information and make the definition of sampling occasions subjective. Continuous-time spatial capture-recapture methods explicitly preserve exact detection timing and can outperform discrete aggregation when within-occasion temporal structure matters.

Relevant background:
- Borchers et al. 2014, Methods in Ecology and Evolution 5:656–665, DOI 10.1111/2041-210X.12196: continuous-time SECR; exact detection times can be informative and temporal aggregation can lose information.
- Efford & Boulanger 2019, Methods in Ecology and Evolution 10:1529–1535, DOI 10.1111/2041-210X.13239: detector type determines whether repeated within-occasion detections are possible and how they should be represented.

Therefore the programme does not claim novelty for the general idea that temporal aggregation loses information.

## What the held-out result adds

The confirmatory San Jacinto result directly quantifies spatial instability of a one-location-per-night reduction in a repeated-check live-trapping protocol.

Frozen held-out result:
- Peromyscus maniculatus: 352/485 repeat-capture individual-nights changed trap flag (72.6%; 95% Wilson CI 68.4–76.4%); median first-to-last distance among changed nights 14.0 m.
- Peromyscus eremicus: 74/107 changed (69.2%; 95% Wilson CI 59.9–77.1%); median changed-night distance 12.5 m.
- both species passed the prospectively frozen >25% / lower-CI>25% / median-distance>=6.25 m gate.

## Observation-process boundary

These first-to-last displacements are **not** interpreted as undisturbed natural movement paths.

Animals were physically captured, handled and released. Recapture at another flag proves that the individual's observed trap location changed between detections, but handling or trap interaction may alter subsequent movement or detection.

Accordingly, the allowed primary object is:

> positional aliasing in the live-trapping observation process when repeated within-night detections are collapsed to one nightly location.

Not:
- natural nightly path length;
- home-range size;
- foraging distance;
- undisturbed movement speed;
- trap-independent behavioural displacement.

## Strongest allowed general statement

> In two held-out Cricetidae sampled under the same repeated-check live-trapping design, roughly seven in ten repeat-capture individual-nights changed trap location within a night. A one-location-per-night reduction therefore discards spatial information at a scale of multiple 6.25 m trap spacings.

## Generality limit

The result is internally replicated across two Cricetidae and follows an earlier heteromyid discovery sample, but all data come from one field protocol and study region. Generality across live-trapping protocols requires external replication.
