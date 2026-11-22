# Direct contact-vs-capture ecological discriminator: source audit, 15 Nov 2026

Goal: stop treating NEON genus×trap recurrence and Finnish bank-vole dyad relative capture-centroid geometry as observed direct animal contact, social bonds or transmission. Find a directly measured, identity-linked second observation channel with the same population and time window.

## Literature-backed independent comparator

Davidson, Solomon, Keane & Dantzer (2025), Methods for measuring fine-scale social proximity in small mammals, *Journal of Mammalogy* 106(4):1035–1044 DOI 10.1093/jmammal/gyaf032. The study followed ONE semi-natural 0.1ha prairie vole (*Microtus ochrogaster*) enclosure, paired 24 individuals' Ugglan live-trap proximity network to a ProxLogs animal-borne proximity sensor recording within about 5–6cm. The already published trapping-vs-collar proximity matrix correlation was QAP r≈0.148; MRQAP explained variance R²≈0.02, despite statistically distinguishable links. This is published prior art, NOT a new positive NEON result, NOT Finnish source cohort, and NOT directly validated contacts from the earlier 2021 bank-vole recordings.

Baited trap station co-capture and direct 6cm proximity are distinct biologically meaningful observations. The sensor result suggests weak contact-network predictability from the capture network but its original sample was ONE fenced semi-natural enclosure; the logistic device effort varied and devices were often damaged/lost. If the raw files are not downloadable or lack deployment effort / collar crosswalk, no novel source-based inference is available; publication R² must not be relabelled as our result.

Public original data destination (as stated by authors):
https://figshare.com/projects/Journal_of_Mammalogy_-_Methods_for_measuring_fine-scale_social_proximity_in_small_mammals/228462

## Single source-only audit BEFORE opening any raw biological records

Use only public Figshare REST GET endpoints, with no credentials, no site automation, no POST, no raw file downloads and no animal IDs:
- GET https://api.figshare.com/v2/projects/228462 to verify exact source project identity.
- GET https://api.figshare.com/v2/projects/228462/articles?page=1&page_size=100 to list publicly published original articles (hard cap 35).
- GET https://api.figshare.com/v2/articles/{article_id} for public file metadata (filename, declared byte count, provider md5 and signed download URL if present).
- Publish only this exact manifest, sorted and SHA256 fingerprinted. Metadata filename screening is NOT validation of source biological column schema or completeness.

A further independently frozen test would require both raw animal/collar ID x event time x direct proximity detection and original trap session x individual tag x trap position, with a verified PIT/collar crosswalk and sensor active interval/recapture loss. Require same 24 original individuals and contemporaneous periods rather than borrowing data from another source. Do not download any ZIP whose documented bytes exceed fixed storage/time risk in a one-shot action; identify file roles from metadata and check exact provider hash before semantic read.

Only if exact paired data and source effort are both available can one ask whether matched-dyad TRAP-derived relative proximity ranks predict DIRECT 5–6cm logger-recorded dyad interactions under an exposure-aware model, with independent heldout windows. Otherwise mark source STOP. No causal competition, resource niche, host social behavior or infection is inferred from this metadata-only audit. The earlier Finnish cohort is independent and cannot validate an individual pair by identity against the Ohio animals. Structural mapped island mammals are a distinct macro-level endpoint and remain scientific HOLD.

No new A/B/method paper. Keep existing unified NEON draft and all original failed source gates intact.
