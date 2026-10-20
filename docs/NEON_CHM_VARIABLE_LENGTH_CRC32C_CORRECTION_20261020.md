# NEON AOP CHM provider CRC32C encoding correction — 2026-10-20

This is a source integrity fix, **not** an environmental ecology model.

## Observed failure
[GitHub Actions 39377992308](https://github.com/zuizui0223/neon/actions/runs/39377992308) recovered all 30 E5 references for the unchanged 58 mammal seasonal comparisons, but the CHM manifest failed at all 14 sites with an unrecognized provider CRC encoding. **No GeoTIFF tiles were downloaded and no canopy pixels were opened.** This was not evidence of absent imagery.

A source-only diagnostic of NEON's official advertised CHM monthly endpoint (WREF, 2023-06; [Actions 39384531490](https://github.com/zuizui0223/neon/actions/runs/39384531490)) found **265 source CHM files**. The checksum format is variable-width hexadecimal: 248 checksum strings of length eight, 15 of length seven and two of length six. Four of the eight-character strings contain digits only; these are interpreted as hexadecimal according to source encoding rather than decimal. The previous parser accepted only exactly eight hex digits (or four-byte base64) and therefore rejected genuine shorter strings.

## Fix, falsifying test and verification
The source parser now accepts one–eight unpadded hexadecimal characters, with optional 0x prefix, while preserving four-byte base64 as an alternative. Provider byte-size and ALL published MD5/CRC32/CRC32C checks remain mandatory and are compared with downloaded bytes before raster interpretation; missing/invalid checksum values or content mismatches remain failures. There is no fallback to local SHA256 as a substitute for provider integrity.

Synthetic test vector: CRC32C of bytes b'319' = hexadecimal 0011fd1e. NEON-compatible source representation is 11fd1e; the parser now reconstructs the same integer without ignoring the provider checksum. Corrupted bytes still fail. Tests were added before the fix: [RED GitHub Actions 39384838413](https://github.com/zuizui0223/neon/actions/runs/39384838413) failed specifically at that short-hex decoding assertion.

The corrected source is in analysis/neon_chm_monthly_source_v2.py and tests/test_neon_e5_chm_monthly_v2.py. The real raster workflow runs these tests first. A synthetic test PASS establishes correct decoding, not successful real CHM coverage; the latter is stated separately from the actual source-pilot receipt.

## Preserved scientific boundaries
- All 14 NEON sites, 30 plots and 58 seasonal pairs remain fixed, without canopy-value selection.
- Only the source E5 reference is sampled at this stage, never used as a surrogate for the full 100 trap-station locations.
- Unknown coordinate uncertainty is not converted to zero; no trap-coordinate rotation or historical location interpolation is performed.
- A canopy value of zero is not equivalent to bare ground or absence of shrubs, while no-data/masked cells are never zero-filled.
- The source raster pilot does not infer genus-specific habitat selection, detectability, territoriality or competition, and does not recalculate the previously frozen seasonal-recurrence endpoint.
- Original NEON density W/B eight-genus 5/8 failure and sealed MOSA outcomes remain unchanged.
