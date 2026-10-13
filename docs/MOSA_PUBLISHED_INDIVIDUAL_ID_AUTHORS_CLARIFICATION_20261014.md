# MOSA published individual-identity clarification request — 2026-10-14

**Purpose:** source provenance and correct identification of
Mastomys natalensis in the public 1994–2023 MOSA dataset. This is an
outcome-blind scientific-data integrity query, not a request to change
published results or to infer behavioral mechanisms.

## Fully reproducible materials

- Leirs et al. (2023), Scientific Data, DOI 10.1038/s41597-023-02700-3.
- Zenodo DOI 10.5281/zenodo.10049811, fixed original
  mosa_Feb2023_flags.csv, exact MD5 12c04902947b91922c3f6c98760ecb54,
  49,216 capture rows.
- The RMarkdown authors supplied reads the GitHub Joachimmarien/MOSA
  original capture CSV, and Git blob byte-level hashing establishes
  **exact equivalence** to the Zenodo file at the pinned 2023 commit.
- Author time-variable table has 363 primary 3-night occasions,
  1,089 unique trapping days, 59 crossing calendar months, all verified.
- Authors' two published encounter matrices and processing RMarkdown
  have also passed original archive MD5 checks.

## Identity questions that require an authoritative answer

1. The article reports 45,433 Mastomys captures of **19,850 unique
   Mastomys individuals**. The published source has exactly 45,433
   capture rows labeled MN, but **19,818 distinct verbatim fully
   qualified TOE strings** (prefixes and suffixes retained). Which
   archived or applied ID correction/mapping yields 19,850 biologically
   distinct MN individuals? A documented code/row mapping or an
   archived intermediate processed data file would resolve this.
2. The two author encounter matrices together have 19,850 rows:
   **19,692 labeled MN including 14 repeated MN TOE strings**, and
   **158 labeled NA (unknown species)**. Does the stated 19,850
   MN-individual count refer to a distinct-ID enumeration, an
   intermediate extraction, or a broader encounter-matrix row count?
   The arithmetic coincidence alone is not animal identity evidence.
3. Of 19,818 MN source TOE codes, 140 do not appear among the MN rows
   in those encounter matrices. Of those, 119 are captured exclusively
   outside the *authors' published* retained 1,089 trapping dates.
   Of the remaining 21, 11 have in-grid captures on retained dates,
   and 10 of those 11 occur under authors' species-NA rows. What is
   the documented taxonomic handling for the cases where a TOE is
   recorded under raw MN but an author encounter row is species NA?
   We will not automatically reclassify these animals.
4. After requiring >=2 distinct retained trapping dates, valid grid
   coordinates, no flags and absence from MN and NA encounter rows,
   a **single high-priority source TOE string** remains. Does its
   original capture row map to an explicitly removed NO_CAPTURE
   placeholder, a manual date deletion/correction, or an unpublished
   QC exclusion? We can supply exact row references privately if
   the authors can identify the authoritative mapping.
5. Which exact Git commit or intermediate processing product generated
   the archived encounter matrices? The published RMarkdown has many
   hard-coded capture-date exclusions and one date correction in 2004,
   so a map of source capture row to processed encounter row would
   distinguish data cleaning from true new animal identities.

## Inferential use while unresolved

- DO NOT manufacture 32 TOE identities, split repeated tags based on
  outcome-favorable gaps, reassign species-NA observations, or assume
  author matrix rows are independent marked animals.
- DO NOT open MNA, W/B or density-spatial effects for this one-site
  series while capture occasions and individual IDs are unresolved.
- This is a possible **one-species, one-site** external study. It cannot
  rescue the NEON 8-genus generality failure or the incompletely
  estimable frozen five-genus future comparison.
- The observational association, if ultimately estimable, would not
  itself imply competition, territoriality or adaptive crowding.

Provenance and current findings are in
results/mosa_author_occasion_mask_corrected_receipt_20261014.json
and docs/MOSA_AUTHOR_OCCASION_AND_IDENTITY_BOUNDARY_20261014.md.
